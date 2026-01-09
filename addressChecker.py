import requests
import json
import typer
from typing import Optional
import ipaddress

app = typer.Typer()


# API endpoint (Check)
CHECK_ENDPOINT_URL = 'https://api.abuseipdb.com/api/v2/check' 


@app.callback(invoke_without_command=True)
def ip_check(IP_ADDRESS: Optional[str] = typer.Option(None, envvar="IP_ADDRESS", help="IP address to check (e.g., 118.25.6.39)"),
            ABUSEIPDB_API_KEY: Optional[str] = typer.Option(None, envvar="ABUSEIPDB_API_KEY", help="Your AbuseIPDB API key"),
            CONFIDENCE_THRESHOLD: float = typer.Option(70, envvar="CONFIDENCE_THRESHOLD", help="Score threshold for HIGH risk classification")):
        
    # Checking inputs only
    error = validate_inputs(IP_ADDRESS, ABUSEIPDB_API_KEY)
    if error:
        code, msg = error
        typer.echo(json.dumps(build_output(code, msg, None), indent=2))
        raise typer.Exit(code=code)
        
    # Passing with request    
    querystring = {
        'ipAddress': IP_ADDRESS,
    }
    headers = {
        'Accept': 'application/json',
        'Key': ABUSEIPDB_API_KEY
    }

    try:
        response = requests.get(url=CHECK_ENDPOINT_URL, headers=headers, params=querystring, timeout=60)
        response.raise_for_status()
        payload = response.json()
        data = payload["data"]

        # Calculating risk level according to provided logic
        if data["abuseConfidenceScore"] >= CONFIDENCE_THRESHOLD:
            risk_level = "HIGH"
        elif data["abuseConfidenceScore"] >= 25 and data["abuseConfidenceScore"] < CONFIDENCE_THRESHOLD:
            risk_level = "MEDIUM"
        elif data["abuseConfidenceScore"] < 25:
            risk_level = "LOW"
        
        # Building the api object structure
        api_object = {
            "ip": data["ipAddress"],
            "risk_level": risk_level,
            "abuse_confidence_score": data["abuseConfidenceScore"],
            "total_reports": data["totalReports"],
            "country_code": data["countryCode"],
            "isp": data["isp"],
            "is_public": data["isPublic"]
        }
        
        # No errors occurred
        typer.echo(json.dumps(build_output(0, "success", api_object), indent=2))
        return 

    # Raised from response, API error
    except requests.exceptions.RequestException as e:
        typer.echo(json.dumps(build_output(2, f"failed: API error ({type(e).__name__})", None), indent=2))
        raise typer.Exit(code=2)


def validate_inputs(ip, api_key):
    # IP validation - code 1
    if ip is None or ip.strip() == "":
        return 1, "failed: missing IP address"
    try:
        ipaddress.ip_address(ip.strip())
    except ValueError:
        return 1, f"failed: invalid ip address '{ip}'"

    # API key validation - code 2
    if api_key is None or api_key.strip() == "":
        return 2, "failed: missing API key"

    return None


def build_output(code, message, api_object):
    return {
        "step_status": {"code": code, "message": message},
        "api_object": api_object if api_object is not None else {}
    }


if __name__ == "__main__": # pragma: no cover
    app()