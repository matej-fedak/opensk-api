"""Resource limits and safe XML/HTTPS handling for offline import tooling."""

from __future__ import annotations

import math
import time
import zipfile
from urllib import parse, request
from xml.etree import ElementTree as ET
from xml.parsers import expat


def read_bounded(source, limit: int, label: str = "input", *, max_seconds: float = 300) -> bytes:
    """Bound bytes and elapsed streaming time, including slow-drip responses.

    HTTPResponse.read1 performs at most one buffered/raw read, allowing a
    deadline check between socket reads instead of waiting to fill a huge read.
    The opener's socket timeout separately bounds an individual stalled read.
    """
    if not isinstance(limit, int) or isinstance(limit, bool) or limit < 0:
        raise ValueError("byte limit must be a non-negative integer")
    validate_timeout(max_seconds)
    deadline = time.monotonic() + max_seconds
    read = getattr(source, "read1", source.read)
    payload = bytearray()
    while True:
        if time.monotonic() >= deadline:
            raise TimeoutError(f"{label} exceeded acquisition time budget")
        chunk = read(min(65536, limit + 1 - len(payload)))
        if time.monotonic() >= deadline:
            raise TimeoutError(f"{label} exceeded acquisition time budget")
        if not chunk:
            return bytes(payload)
        payload.extend(chunk)
        if len(payload) > limit:
            raise ValueError(f"{label} exceeds {limit} byte limit")


def check_zip_limits(archive: zipfile.ZipFile, *, member_limit: int,
                     total_limit: int, max_members: int = 2048,
                     max_ratio: int = 200) -> None:
    members = archive.infolist()
    if len(members) > max_members:
        raise ValueError("ZIP has too many members")
    if sum(item.file_size for item in members) > total_limit:
        raise ValueError("ZIP uncompressed size exceeds limit")
    for item in members:
        if item.file_size > member_limit:
            raise ValueError("ZIP member uncompressed size exceeds limit")
        if item.file_size > max(item.compress_size, 1) * max_ratio:
            raise ValueError("ZIP member compression ratio exceeds limit")


def reject_xml_declarations(raw: bytes, *, element_limits: dict[str, int] | None = None) -> None:
    """Use the XML parser's encoding detection, not an ASCII byte scan.

    Expat calls StartDoctypeDecl before reading the internal subset or expanding
    entities. This preflight creates no tree and rejects all DTDs, including
    external subsets, in any encoding the parser supports.
    """
    parser = expat.ParserCreate(namespace_separator="}")

    def reject(*args):
        raise ValueError("DTD/entity declarations are forbidden")

    parser.StartDoctypeDeclHandler = reject
    parser.EntityDeclHandler = reject
    parser.ExternalEntityRefHandler = reject
    if element_limits:
        counts: dict[str, int] = {}

        def count_element(name, attrs):
            local = name.rsplit("}", 1)[-1]
            if local in element_limits:
                counts[local] = counts.get(local, 0) + 1
                if counts[local] > element_limits[local]:
                    raise ValueError(f"XML {local} element count exceeds limit")

        parser.StartElementHandler = count_element
    try:
        parser.Parse(raw, True)
    except expat.ExpatError as exc:
        raise ValueError(f"not well-formed XML: {exc}") from exc


def safe_xml_fromstring(raw: bytes, *, element_limits: dict[str, int] | None = None) -> ET.Element:
    reject_xml_declarations(raw, element_limits=element_limits)
    return ET.fromstring(raw)


def validate_timeout(timeout: float) -> None:
    if not math.isfinite(timeout) or not 0 < timeout <= 300:
        raise ValueError("timeout must be finite and between 0 and 300 seconds")


def validate_https_url(url: str, allowed_hosts: set[str] | None = None) -> None:
    parts = parse.urlsplit(url)
    if (parts.scheme != "https" or not parts.hostname or parts.username is not None
            or parts.password is not None or parts.fragment or parts.port not in (None, 443)):
        raise ValueError("source and redirect URLs must be HTTPS without credentials or non-HTTPS ports")
    if allowed_hosts is not None and parts.hostname.lower() not in allowed_hosts:
        raise ValueError("redirect destination is outside the source host policy")


def open_https(url_or_request, *, timeout: float, allowed_hosts: set[str] | None = None):
    """CLI acquisition: allow HTTPS sources, checking every redirect before I/O.

    These are operator-configured URLs, not a public URL-fetching API. No DNS or
    private-network filtering is intended here.
    """
    validate_timeout(timeout)
    url = url_or_request.full_url if isinstance(url_or_request, request.Request) else url_or_request
    validate_https_url(url, allowed_hosts)

    class RedirectPolicy(request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            validate_https_url(newurl, allowed_hosts)
            return super().redirect_request(req, fp, code, msg, headers, newurl)

    return request.build_opener(RedirectPolicy()).open(url_or_request, timeout=timeout)
