import ipaddress
from typing import Optional
import requests
import typer
import json
from common.abuseipdb import fetch_check_data, pretty_check_data, build_output
app = typer.Typer()

@app.callback(invoke_without_command=True)
def ip_check_batch(IP_ADDRESSES: Optional[str] = typer.Option(None, envvar="IP_ADDRESSES", help="Comma-separated IP addresses"),
            ABUSEIPDB_API_KEY: Optional[str] = typer.Option(None, envvar="ABUSEIPDB_API_KEY", help="Your AbuseIPDB API key"),
            CONFIDENCE_THRESHOLD: float = typer.Option(70, envvar="CONFIDENCE_THRESHOLD", help="Score threshold for HIGH risk classification")):

    ip_list = split_ips(IP_ADDRESSES) if IP_ADDRESSES else []
    
    # Validating IP formats
    errors: dict[str, str] = {}
    valid_ips: list[str] = []
    for ip in ip_list:
        if not is_valid_ip(ip):
            errors[ip] = "Invalid IP address format"
        else:
            valid_ips.append(ip)
    
    # Call API per valid ip
    results: dict[str, dict] = {}   # IP->API response pair
    risk_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    
    if ABUSEIPDB_API_KEY is None or ABUSEIPDB_API_KEY.strip() == "":
        for ip in valid_ips:
            errors[ip] = "Missing API Key"
    else:
        # Call API only if we have a key
        for ip in valid_ips:
            try:
                data = fetch_check_data(ip, ABUSEIPDB_API_KEY)
                entry = pretty_check_data(data, CONFIDENCE_THRESHOLD,
                                          include_public=False, include_ip=False)
                results[ip] = entry  
                risk_counts[entry["risk_level"]] += 1
            except (requests.exceptions.RequestException, ValueError, KeyError):
                errors[ip] = "API error"
    
    api_object = build_batch_api_object(ip_list, results, errors, risk_counts)
    code, msg = decide_batch_status(valid_ips, results, errors)
    
    typer.echo(json.dumps(build_output(code, msg, api_object), indent=2))
    raise typer.Exit(code=code)

# IPs are comma-separated
def split_ips(raw):
    parts = [p.strip() for p in raw.split(",")] if raw else []
    return [p for p in parts if p != ""]

# Validate IP address
def is_valid_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

# Build the API object for the batch request
def build_batch_api_object(ip_list, results, errors, risk_counts):
    summary = {
        "total": len(ip_list),
        "successful": len(results),
        "failed": len(errors),
        "risk_counts": risk_counts,
    }
    return {"summary": summary, "results": results, "errors": errors}


def decide_batch_status(valid_ips, results, errors):
    # code 1: input validation error (no valid IPs provided)
    if len(valid_ips) == 0:
        return 1, "failed"

    # code 2: all API requests failed (valid IPs exist, but no successes)
    if len(valid_ips) > 0 and len(results) == 0:
        return 2, "failed"

    # code 0 partial_success: some succeeded, some failed
    if len(errors) > 0:
        return 0, "partial_success"

    # code 0 success: everything succeeded
    return 0, "success"
    
    
if __name__ == "__main__": # pragma: no cover
    app()
