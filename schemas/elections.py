"""Closed NRSR2023 aggregate-only contracts and materialized-data invariants."""

from datetime import date, datetime
from decimal import Decimal, DecimalException, ROUND_DOWN
from typing import Annotated, Literal

from pydantic import ConfigDict, Field, model_validator

from schemas.common import PublicModel


class ElectionModel(PublicModel):
    model_config = ConfigDict(extra="forbid", strict=True)


Count = Annotated[int, Field(ge=0, strict=True)]
Text = Annotated[str, Field(min_length=1, pattern=r"^\S(?:.*\S)?$")]
Percent = Annotated[str, Field(pattern=r"^(?:[0-9]{1,2}\.[0-9]{2}|100\.00)$")]
SHA256 = Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]
COUNTS = ("precinctCount", "confirmedPrecinctCount", "registeredVoters", "participatingVoters",
          "submittedEnvelopes", "validVotes")
EXPECTED_TOTALS = dict(zip(COUNTS, (6014, 6013, 4388872, 3007123, 3002948, 2967896)))
EXPECTED_FILES = {f"NRSR2023_SK_{code}.csv": rows for code, rows in
                  (("tab0c", 2927), ("tab02d", 2927), ("tab01", 1), ("tab03a", 25), ("tab0a", 25))}
LIMITATIONS = [
    "Final NR SR 2023 selected unit summaries and national party results only; not all Slovak elections or live reporting.",
    "No municipality-party cells, precinct results, candidate/preference/elected-person or voter records.",
    "Small-area aggregates may permit contextual inference with external information; no anonymity or zero-risk claim.",
    "599999 / Cudzina is foreign voting, not a Slovak municipality; no PortalVS/current-geography mapping.",
    "Prešov precinct 34 was excluded by State Commission decision; 6013 of 6014 configured precincts confirmed.",
]
SOURCE_PAGE = "https://volby.statistics.sk/nrsr/nrsr2023/sk/subory_na_stiahnutie.html"
LICENCE_URL = "https://creativecommons.org/licenses/by/4.0/"
ATTRIBUTION = ("Zdroj: Štatistický úrad SR – výsledky príslušných volieb. "
               "Licencia: Creative Commons Attribution 4.0 (CC BY 4.0). "
               "Údaje boli ďalej spracované projektom OpenSK.")
TRANSFORMATION = "Selected CSV tables to JSON, normalized field names, election-native territory join; aggregate-only projection."
NON_ENDORSEMENT = "OpenSK nie je oficiálnou službou Štatistického úradu SR. No endorsement of OpenSK or downstream applications is implied."


def check_percent(value: str, numerator: int, denominator: int) -> None:
    try:
        expected = ((Decimal(numerator) * 100 / denominator).quantize(Decimal(".01"), rounding=ROUND_DOWN)
                    if denominator else Decimal("0.00"))
    except DecimalException as exc:
        raise ValueError("count magnitude cannot be represented as a percentage") from exc
    if Decimal(value) != expected:
        raise ValueError("source percentage does not match truncated count ratio")


class ElectionAggregate(ElectionModel):
    precinctCount: Count = Field(description="Configured precincts; need not equal confirmedPrecinctCount.")
    confirmedPrecinctCount: Count
    confirmedPrecinctPercent: Percent
    registeredVoters: Count
    participatingVoters: Count
    turnoutPercent: Percent
    submittedEnvelopes: Count
    submittedEnvelopePercent: Percent
    validVotes: Count
    validVotePercent: Percent = Field(description="Source percentage of participating voters, not envelopes; truncated to two decimals.")

    @model_validator(mode="after")
    def count_relationships(self):
        if not 0 < self.precinctCount or self.confirmedPrecinctCount > self.precinctCount:
            raise ValueError("confirmed precincts must not exceed positive configured precincts")
        if not self.validVotes <= self.submittedEnvelopes <= self.participatingVoters <= self.registeredVoters:
            raise ValueError("invalid aggregate count relationships")
        for percentage, numerator, denominator in (
            ("confirmedPrecinctPercent", "confirmedPrecinctCount", "precinctCount"),
            ("turnoutPercent", "participatingVoters", "registeredVoters"),
            ("submittedEnvelopePercent", "submittedEnvelopes", "participatingVoters"),
            ("validVotePercent", "validVotes", "participatingVoters"),
        ):
            check_percent(getattr(self, percentage), getattr(self, numerator), getattr(self, denominator))
        return self


class ElectionUnit(ElectionAggregate):
    regionCode: Annotated[str, Field(pattern=r"^[1-9]$")]
    regionName: Text
    territorialCircuitCode: Annotated[str, Field(pattern=r"^[0-9]{3}$")]
    territorialCircuitName: Text
    districtCode: Annotated[str, Field(pattern=r"^[0-9]{3}$")]
    districtName: Text
    municipalityCode: Annotated[str, Field(pattern=r"^[0-9]{6}$")]
    municipalityName: Text
    unitType: Literal["domestic", "foreign"]

    @model_validator(mode="after")
    def native_membership(self):
        if any(code[0] != self.regionCode for code in (self.districtCode, self.territorialCircuitCode)):
            raise ValueError("native parent/region mismatch")
        if self.municipalityCode == "599999":
            if (self.unitType, self.regionCode, self.territorialCircuitCode, self.districtCode) != ("foreign", "9", "900", "900"):
                raise ValueError("foreign unit requires native 9/900/900 hierarchy")
            if any(name != "Cudzina" for name in (self.regionName, self.territorialCircuitName,
                                                  self.districtName, self.municipalityName)):
                raise ValueError("foreign unit must retain Cudzina labels")
        elif self.unitType != "domestic" or self.regionCode == "9":
            raise ValueError("only 599999 may use foreign scope/hierarchy")
        return self


class ElectionParty(ElectionModel):
    partyNumber: Annotated[str, Field(pattern=r"^(?:[1-9]|1[0-9]|2[0-5])$", description="NRSR2023 election-local list number, not a global political-party identifier.")]
    name: Text
    abbreviation: Text
    validVotes: Count
    votePercent: Percent = Field(description="Exact source decimal string; share of national valid votes, truncated to two decimals.")
    seats: Count | None = Field(description="Source allocated mandates; null preserves a blank source cell, not an inferred zero.")


class ElectionInfo(ElectionModel):
    id: Literal["NRSR2023"]
    name: Text
    type: Literal["parliamentary"]
    electionDate: Literal["2023-09-30"]
    status: Literal["definitive"]
    surfaces: list[Literal["unit-summary", "national-summary", "national-parties"]]
    sourceSnapshotDate: str = Field(pattern=r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$", description="OpenSK manual acquisition/verification date, not election day or source publication date.")
    limitations: list[Text]

    @model_validator(mode="after")
    def reviewed_info(self):
        date.fromisoformat(self.sourceSnapshotDate)
        if self.surfaces != ["unit-summary", "national-summary", "national-parties"] or self.limitations != LIMITATIONS:
            raise ValueError("unreviewed election scope/limitations")
        return self


class ElectionCatalogueEntry(ElectionInfo):
    national: ElectionAggregate


class ElectionSourceFile(ElectionModel):
    filename: Text
    sha256: SHA256
    bytes: Annotated[int, Field(gt=0, strict=True)]
    rowCount: Annotated[int, Field(gt=0, strict=True)]


class ElectionProvenance(ElectionModel):
    profile: Literal["nrsr2023-aggregate-v1"]
    publisher: Literal["Štatistický úrad Slovenskej republiky"]
    sourcePage: Literal["https://volby.statistics.sk/nrsr/nrsr2023/sk/subory_na_stiahnutie.html"]
    sourcePublishedAt: Literal["2023-10-01T14:30:00"]
    sourcePublicationTimezone: None = Field(description="Timezone not established in retained page evidence; timestamp is not assumed UTC.")
    manuallyAcquired: Literal[True]
    manuallyAcquiredAt: str
    acquisitionTimePrecision: Literal["exact", "approximate-minute"]
    acquisitionTimeBasis: Text
    verifiedOn: str
    acquisitionMode: Literal["MANUAL_OFFICIAL_DOWNLOAD_ONLY"]
    licence: Literal["CC-BY-4.0"]
    licenceUrl: Literal["https://creativecommons.org/licenses/by/4.0/"]
    publisherReplyReceivedOn: Literal["2026-10-30"]
    attribution: Text
    transformation: Text
    nonEndorsement: Text
    files: list[ElectionSourceFile]

    @model_validator(mode="after")
    def evidence(self):
        timestamp = datetime.fromisoformat(self.manuallyAcquiredAt.replace("Z", "+00:00"))
        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise ValueError("manual acquisition timestamp requires timezone")
        verified = date.fromisoformat(self.verifiedOn)
        if verified < timestamp.date() or verified < date(2026, 10, 30):
            raise ValueError("verification precedes acquisition/reuse clearance")
        if len(self.files) != 5 or {r.filename: r.rowCount for r in self.files} != EXPECTED_FILES:
            raise ValueError("exact five reviewed source files/cardinalities required")
        if self.attribution != ATTRIBUTION or self.transformation != TRANSFORMATION or self.nonEndorsement != NON_ENDORSEMENT:
            raise ValueError("required attribution/transformation/non-endorsement notices missing")
        return self


class ElectionDataset(ElectionModel):
    election: ElectionInfo
    national: ElectionAggregate
    parties: list[ElectionParty]
    units: list[ElectionUnit]
    provenance: ElectionProvenance

    @model_validator(mode="after")
    def reconciliation(self):
        if len(self.units) != 2927 or len({u.municipalityCode for u in self.units}) != 2927:
            raise ValueError("expected 2927 unique election-native units")
        keys = [(u.regionCode, u.territorialCircuitCode, u.districtCode, u.municipalityCode) for u in self.units]
        if keys != sorted(keys):
            raise ValueError("units must use stable native geography/code ordering")
        foreign = [u for u in self.units if u.unitType == "foreign"]
        if len(foreign) != 1 or foreign[0].validVotes != 57856:
            raise ValueError("foreign voting contribution mismatch")
        parents = {}
        for u in self.units:
            for key, value in ((("region", u.regionCode), u.regionName),
                               (("circuit", u.territorialCircuitCode), (u.regionCode, u.territorialCircuitName)),
                               (("district", u.districtCode), (u.regionCode, u.territorialCircuitCode, u.districtName))):
                if key in parents and parents[key] != value:
                    raise ValueError("inconsistent election-native hierarchy/labels")
                parents[key] = value
        for field, expected in EXPECTED_TOTALS.items():
            if getattr(self.national, field) != expected or sum(getattr(u, field) for u in self.units) != expected:
                raise ValueError(f"national aggregate reconciliation mismatch: {field}")
        unconfirmed = [(u.municipalityCode, u.precinctCount, u.confirmedPrecinctCount) for u in self.units
                       if u.precinctCount != u.confirmedPrecinctCount]
        if unconfirmed != [("524140", 66, 65)]:
            raise ValueError("expected documented Prešov 65/66 confirmation exception only")
        if [p.partyNumber for p in self.parties] != [str(n) for n in range(1, 26)]:
            raise ValueError("expected 25 unique numerically ordered national party numbers")
        if sum(p.validVotes for p in self.parties) != self.national.validVotes:
            raise ValueError("party vote sum does not reconcile")
        if sum(p.seats or 0 for p in self.parties) != 150:
            raise ValueError("allocated mandates must sum to 150")
        for party in self.parties:
            check_percent(party.votePercent, party.validVotes, self.national.validVotes)
        if self.election.sourceSnapshotDate != self.provenance.verifiedOn:
            raise ValueError("snapshot freshness must match verification date")
        return self
