import json
from typer.testing import CliRunner
import requests
import check_ip_batch.main as batch_main
from check_ip_batch.main import app

runner = CliRunner()

def parse_json_stdout(result):
    # Typer prints to stdout
    return json.loads(result.stdout.strip())

def test_missing_api_key_returns_code_2(monkeypatch):
    monkeypatch.setenv("IP_ADDRESSES", "8.8.8.8")
    monkeypatch.delenv("ABUSEIPDB_API_KEY", raising=False)

    result = runner.invoke(app, [])
    out = parse_json_stdout(result)

    assert result.exit_code == 2
    assert out["step_status"]["code"] == 2

    api = out["api_object"]
    assert api["results"] == {}
    assert "errors" in api
    assert api["errors"].get("8.8.8.8")  # exists
    assert api["summary"]["total"] == 1
    assert api["summary"]["successful"] == 0
    assert api["summary"]["failed"] == 1
    
def test_no_valid_ips_returns_code_1(monkeypatch):
    monkeypatch.setenv("ABUSEIPDB_API_KEY", "dummy")
    monkeypatch.setenv("IP_ADDRESSES", "invalid-ip,also-bad,")
    monkeypatch.setenv("CONFIDENCE_THRESHOLD", "50")

    result = runner.invoke(app, [])
    out = parse_json_stdout(result)

    assert result.exit_code == 1
    assert out["step_status"]["code"] == 1
    assert out["api_object"]["summary"]["total"] == 2
    assert out["api_object"]["summary"]["successful"] == 0
    assert out["api_object"]["summary"]["failed"] == 2
    assert out["api_object"]["results"] == {}
    assert "invalid-ip" in out["api_object"]["errors"]


def test_all_api_requests_fail_returns_code_2(monkeypatch):
    monkeypatch.setenv("ABUSEIPDB_API_KEY", "dummy")
    monkeypatch.setenv("IP_ADDRESSES", "8.8.8.8,1.1.1.1")
    monkeypatch.setenv("CONFIDENCE_THRESHOLD", "50")

    # Mock fetch_check_data to always raise a RequestException
    def fake_fetch(*args, **kwargs):
        raise requests.exceptions.RequestException("boom")

    monkeypatch.setattr(batch_main, "fetch_check_data", fake_fetch)

    result = runner.invoke(app, [])
    out = parse_json_stdout(result)

    assert result.exit_code == 2
    assert out["step_status"]["code"] == 2
    assert out["api_object"]["summary"]["successful"] == 0
    assert out["api_object"]["summary"]["failed"] == 2
    assert len(out["api_object"]["errors"]) == 2
    
def test_partial_success_mixes_results_and_errors(monkeypatch):
    monkeypatch.setenv("ABUSEIPDB_API_KEY", "dummy")
    monkeypatch.setenv("IP_ADDRESSES", "8.8.8.8,invalid-ip,1.1.1.1")
    monkeypatch.setenv("CONFIDENCE_THRESHOLD", "50")

    def fake_fetch(ip, api_key, *args, **kwargs):
        if ip == "1.1.1.1":
            raise requests.exceptions.RequestException("rate limit")
        # minimal payload to satisfy pretty_check_data
        return {
            "ipAddress": ip,
            "abuseConfidenceScore": 0,
            "totalReports": 0,
            "countryCode": "US",
            "isp": "Example ISP",
        }

    monkeypatch.setattr(batch_main, "fetch_check_data", fake_fetch)

    result = runner.invoke(app, [])
    out = parse_json_stdout(result)

    assert result.exit_code == 0
    assert out["step_status"]["code"] == 0
    assert out["step_status"]["message"] == "partial_success"

    api_object = out["api_object"]
    assert api_object["summary"]["total"] == 3
    assert api_object["summary"]["successful"] == 1
    assert api_object["summary"]["failed"] == 2

    assert "8.8.8.8" in api_object["results"]
    assert "invalid-ip" in api_object["errors"]
    assert "1.1.1.1" in api_object["errors"]
    
def test_success_all_ips_ok(monkeypatch):
    monkeypatch.setenv("ABUSEIPDB_API_KEY", "dummy")
    monkeypatch.setenv("IP_ADDRESSES", "8.8.8.8,1.1.1.1")
    monkeypatch.setenv("CONFIDENCE_THRESHOLD", "50")

    def fake_fetch(ip, api_key, *args, **kwargs):
        return {
            "ipAddress": ip,
            "abuseConfidenceScore": 80 if ip == "1.1.1.1" else 0,
            "totalReports": 10,
            "countryCode": "US",
            "isp": "Example ISP",
        }

    monkeypatch.setattr(batch_main, "fetch_check_data", fake_fetch)

    result = runner.invoke(app, [])
    out = parse_json_stdout(result)

    assert result.exit_code == 0
    assert out["step_status"]["code"] == 0
    assert out["step_status"]["message"] == "success"
    assert out["api_object"]["summary"]["successful"] == 2
    assert out["api_object"]["summary"]["failed"] == 0
    assert out["api_object"]["summary"]["risk_counts"]["HIGH"] == 1
    
def test_duplicate_ips_handling_success(monkeypatch):
    monkeypatch.setenv("ABUSEIPDB_API_KEY", "dummy")
    monkeypatch.setenv("IP_ADDRESSES", "8.8.8.8,8.8.8.8,1.1.1.1")
    monkeypatch.setenv("CONFIDENCE_THRESHOLD", "50")
    
    calls = []

    def fake_fetch(ip, api_key, *args, **kwargs):
        calls.append(ip)
        return {
            "ipAddress": ip,
            "abuseConfidenceScore": 0,
            "totalReports": 10,
            "countryCode": "US",
            "isp": "Example ISP",
        }
    monkeypatch.setattr(batch_main, "fetch_check_data", fake_fetch)
    result = runner.invoke(app, [])
    out = parse_json_stdout(result)

    assert result.exit_code == 0
    assert out["step_status"]["code"] == 0
    assert out["step_status"]["message"] == "success"

    assert out["api_object"]["summary"]["total"] == 2
    assert out["api_object"]["summary"]["successful"] == 2
    assert out["api_object"]["summary"]["failed"] == 0

    assert "8.8.8.8" in out["api_object"]["results"]
    assert "1.1.1.1" in out["api_object"]["results"]

    # proves dedupe (only two calls)
    assert calls == ["8.8.8.8", "1.1.1.1"]