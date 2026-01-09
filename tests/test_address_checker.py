import pytest
import json
import requests
from typer.testing import CliRunner


from addressChecker import app

runner = CliRunner()

class DummyResponse:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload or {}
        
        
    def raise_for_status(self):
        if self.status_code >= 400:
            err = requests.exceptions.HTTPError(f"HTTP {self.status_code} Error")
            err.response = self
            raise err

    def json(self):
        return self._payload
    
def parse_json_stdout(result):
    return json.loads(result.stdout)

def test_missing_ip_returns_code_1(monkeypatch):
    monkeypatch.delenv("IP_ADDRESS", raising=False)
    monkeypatch.setenv("ABUSEIPDB_API_KEY", "dummy")
    monkeypatch.setenv("CONFIDENCE_THRESHOLD", "50")
    
    # Invoke the CLI app with no commands
    result = runner.invoke(app, [])
    out = parse_json_stdout(result)
    
    assert result.exit_code == 1
    assert out["step_status"]["code"] == 1
    assert out["api_object"] == {}

def test_empty_ip_returns_code_1(monkeypatch):
    monkeypatch.setenv("IP_ADDRESS", "")
    monkeypatch.setenv("ABUSEIPDB_API_KEY", "dummy")
    monkeypatch.setenv("CONFIDENCE_THRESHOLD", "50")

    result = runner.invoke(app, [])
    out = parse_json_stdout(result)

    assert result.exit_code == 1
    assert out["step_status"]["code"] == 1
    assert out["api_object"] == {}


def test_invalid_ip_returns_code_1(monkeypatch):
    monkeypatch.setenv("IP_ADDRESS", "999.999.999.999")
    monkeypatch.setenv("ABUSEIPDB_API_KEY", "dummy")
    monkeypatch.setenv("CONFIDENCE_THRESHOLD", "50")

    result = runner.invoke(app, [])
    out = parse_json_stdout(result)

    assert result.exit_code == 1
    assert out["step_status"]["code"] == 1
    assert out["api_object"] == {}


def test_missing_api_key_returns_code_2(monkeypatch):
    monkeypatch.setenv("IP_ADDRESS", "118.25.6.39")
    monkeypatch.delenv("ABUSEIPDB_API_KEY", raising=False)
    monkeypatch.setenv("CONFIDENCE_THRESHOLD", "50")

    result = runner.invoke(app, [])
    out = parse_json_stdout(result)

    assert result.exit_code == 2
    assert out["step_status"]["code"] == 2
    assert out["api_object"] == {}
    

@pytest.mark.parametrize("status_code", [401, 429, 500])    # Auth error, rate limit, server error
def test_http_error_returns_code_2(monkeypatch, status_code):
    monkeypatch.setenv("IP_ADDRESS", "118.25.6.39")
    monkeypatch.setenv("ABUSEIPDB_API_KEY", "dummy")
    monkeypatch.setenv("CONFIDENCE_THRESHOLD", "50")

    def fake_get(*args, **kwargs):
        return DummyResponse(status_code=status_code)

    monkeypatch.setattr(requests, "get", fake_get)

    result = runner.invoke(app, [])
    out = parse_json_stdout(result)

    assert result.exit_code == 2
    assert out["step_status"]["code"] == 2
    assert out["api_object"] == {}


def test_timeout_returns_code_2(monkeypatch):
    monkeypatch.setenv("IP_ADDRESS", "118.25.6.39")
    monkeypatch.setenv("ABUSEIPDB_API_KEY", "dummy")
    monkeypatch.setenv("CONFIDENCE_THRESHOLD", "50")

    def fake_get(*args, **kwargs):
        raise requests.exceptions.Timeout()

    monkeypatch.setattr(requests, "get", fake_get)

    result = runner.invoke(app, [])
    out = parse_json_stdout(result)

    assert result.exit_code == 2
    assert out["step_status"]["code"] == 2
    assert out["api_object"] == {}
    
    
def test_success_returns_code_0_and_expected_fields_high(monkeypatch):
    monkeypatch.setenv("IP_ADDRESS", "118.25.6.39")
    monkeypatch.setenv("ABUSEIPDB_API_KEY", "dummy")
    monkeypatch.setenv("CONFIDENCE_THRESHOLD", "50")

    payload = {
        "data": {
            "ipAddress": "118.25.6.39",
            "abuseConfidenceScore": 87,
            "totalReports": 1542,
            "countryCode": "CN",
            "isp": "Tencent Cloud Computing",
            "isPublic": True,
        }
    }

    def fake_get(*args, **kwargs):
        return DummyResponse(status_code=200, payload=payload)

    monkeypatch.setattr(requests, "get", fake_get)

    result = runner.invoke(app, [])
    out = parse_json_stdout(result)

    assert result.exit_code == 0
    assert out["step_status"]["code"] == 0
    assert out["step_status"]["message"] == "success"

    api = out["api_object"]
    assert api["ip"] == "118.25.6.39"
    assert api["abuse_confidence_score"] == 87
    assert api["total_reports"] == 1542
    assert api["country_code"] == "CN"
    assert api["isp"] == "Tencent Cloud Computing"
    assert api["is_public"] is True
    assert api["risk_level"] == "HIGH"  # 87 >= threshold(50)
    
def test_success_returns_code_0_and_expected_fields_medium(monkeypatch):
    monkeypatch.setenv("IP_ADDRESS", "118.25.6.39")
    monkeypatch.setenv("ABUSEIPDB_API_KEY", "dummy")
    monkeypatch.setenv("CONFIDENCE_THRESHOLD", "50")

    payload = {
        "data": {
            "ipAddress": "118.25.6.39",
            "abuseConfidenceScore": 40,
            "totalReports": 1542,
            "countryCode": "CN",
            "isp": "Tencent Cloud Computing",
            "isPublic": True,
        }
    }

    def fake_get(*args, **kwargs):
        return DummyResponse(status_code=200, payload=payload)

    monkeypatch.setattr(requests, "get", fake_get)

    result = runner.invoke(app, [])
    out = parse_json_stdout(result)

    assert result.exit_code == 0
    assert out["step_status"]["code"] == 0
    assert out["step_status"]["message"] == "success"

    api = out["api_object"]
    assert api["ip"] == "118.25.6.39"
    assert api["abuse_confidence_score"] == 40
    assert api["total_reports"] == 1542
    assert api["country_code"] == "CN"
    assert api["isp"] == "Tencent Cloud Computing"
    assert api["is_public"] is True
    assert api["risk_level"] == "MEDIUM"  # 40 < threshold(50)


def test_success_returns_code_0_and_expected_fields_low(monkeypatch):
    monkeypatch.setenv("IP_ADDRESS", "118.25.6.39")
    monkeypatch.setenv("ABUSEIPDB_API_KEY", "dummy")
    monkeypatch.setenv("CONFIDENCE_THRESHOLD", "50")

    payload = {
        "data": {
            "ipAddress": "118.25.6.39",
            "abuseConfidenceScore": 12,
            "totalReports": 1542,
            "countryCode": "CN",
            "isp": "Tencent Cloud Computing",
            "isPublic": True,
        }
    }

    def fake_get(*args, **kwargs):
        return DummyResponse(status_code=200, payload=payload)

    monkeypatch.setattr(requests, "get", fake_get)

    result = runner.invoke(app, [])
    out = parse_json_stdout(result)

    assert result.exit_code == 0
    assert out["step_status"]["code"] == 0
    assert out["step_status"]["message"] == "success"

    api = out["api_object"]
    assert api["ip"] == "118.25.6.39"
    assert api["abuse_confidence_score"] == 12
    assert api["total_reports"] == 1542
    assert api["country_code"] == "CN"
    assert api["isp"] == "Tencent Cloud Computing"
    assert api["is_public"] is True
    assert api["risk_level"] == "LOW"  # 12 < threshold(50)