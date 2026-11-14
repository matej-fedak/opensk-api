import re
import subprocess
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_private_env_variants_are_ignored_but_examples_are_not():
    for name in (".env", ".env.local", ".env.production", "local.key", "local.p12", "id_ed25519", "credentials.json"):
        result = subprocess.run(["git", "check-ignore", "--quiet", "--no-index", name], cwd=ROOT, check=False)
        assert result.returncode == 0, name
    for name in (".env.example", ".env.production.example"):
        result = subprocess.run(["git", "check-ignore", "--quiet", "--no-index", name], cwd=ROOT, check=False)
        assert result.returncode == 1, name


def test_workflows_use_interpreter_file_and_immutable_action_references():
    for name in ("ci.yml", "public-smoke.yml"):
        text = (ROOT / ".github/workflows" / name).read_text(encoding="utf-8")
        assert "python-version-file: .python-version" in text
        assert "persist-credentials: false" in text
        references = re.findall(r"uses:\s*(\S+)", text)
        assert references
        assert all(re.fullmatch(r"[^@]+@[0-9a-f]{40}", value) for value in references)


def test_secret_scanner_retains_defaults_and_only_narrow_hash_exemption():
    config = tomllib.loads((ROOT / ".gitleaks.toml").read_text(encoding="utf-8"))
    assert config["extend"]["useDefault"] is True
    exemption, = config["allowlists"]
    assert exemption["condition"] == "AND"
    assert exemption["regexTarget"] == "line"
    assert len(exemption["paths"]) == len(exemption["regexes"]) == 1
    assert "sourceOpenapiSha256" in exemption["regexes"][0]


def test_render_build_uses_locked_runtime_and_checks_passed_deploy():
    text = (ROOT / "render.yaml").read_text(encoding="utf-8")
    assert "--require-hashes -r requirements.txt" in text
    assert "autoDeployTrigger: checksPass" in text
    assert "--no-access-log" in text


def test_development_lock_preserves_runtime_pins():
    def pins(name):
        text = (ROOT / name).read_text(encoding="utf-8")
        assert "--hash=sha256:" in text
        return dict(re.findall(r"^([a-zA-Z0-9_-]+)==([^\s;\\]+)", text, re.M))

    runtime = pins("requirements.txt")
    development = pins("requirements-dev.txt")
    assert runtime
    assert all(development.get(name) == version for name, version in runtime.items())
    assert not runtime.keys() & {"pytest", "httpx", "httpx2", "ruff", "pip-audit"}
