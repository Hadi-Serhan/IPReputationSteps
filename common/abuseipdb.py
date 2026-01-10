from typing import Any, Dict
import requests

CHECK_ENDPOINT_URL = "https://api.abuseipdb.com/api/v2/check"

# Fetches data from the API and returns as a json
def fetch_check_data(ip: str, api_key: str, timeout: int = 60, url: str = CHECK_ENDPOINT_URL) -> Dict[str, Any]:
    headers = {
        "Accept": "application/json",
        "Key": api_key
    }
    params = {
        "ipAddress": ip
    }
    
    response = requests.get(url, headers=headers, params=params, timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    return payload["data"]

# Risk level logic
def compute_risk_level(score, threshold):
    if score >= threshold:
        return "HIGH"
    elif score >= 25:
        return "MEDIUM"
    else:
        return "LOW"

# Construct the output from the API response
def pretty_check_data(data, threshold, include_public=True, include_ip=True) -> Dict[str, Any]:
    score = float(data["abuseConfidenceScore"])
    risk = compute_risk_level(score, threshold)
    
    out: Dict[str, Any] = {}

    if include_ip:
        out["ip"] = data["ipAddress"]

    out["risk_level"] = risk
    out["abuse_confidence_score"] = score
    out["total_reports"] = int(data.get("totalReports", 0))
    out["country_code"] = data.get("countryCode")
    out["isp"] = data.get("isp")

    if include_public:
        out["is_public"] = data.get("isPublic")

    return out

# Output structure
def build_output(code, message, api_object):
    return {
        "step_status": {"code": code, "message": message},
        "api_object": api_object if api_object is not None else {}
    }
