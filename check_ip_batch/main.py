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

    # Invalid API key
    if ABUSEIPDB_API_KEY is None or ABUSEIPDB_API_KEY.strip() == "":
        typer.echo(json.dumps(build_output(2, "failed: missing API key", None), indent=2))
        raise typer.Exit(code=2)

    ip_list = split_ips(IP_ADDRESSES) if IP_ADDRESSES else []
    
    # Validating IP formats
    errors: dict[str, str] = {}
    valid_ips: list[str] = []
    for ip in ip_list:
        if not is_valid_ip(ip):
            errors[ip] = "Invalid IP address format"
        else:
            valid_ips.append(ip)

    # If no IPs are valid, then we need to return status code 1
    if len(valid_ips) == 0:
        api_object = {
            "summary": {
                "total": len(ip_list),
                "successful": 0,
                "failed": len(errors),
                "risk_counts": {"HIGH": 0, "MEDIUM": 0, "LOW": 0 }
                },
                "results": {},
                "errors": errors,
            }
        typer.echo(json.dumps(build_output(1, "failed", api_object), indent=2))
        raise typer.Exit(code=1)
    
    # Call API per valid ip
    results: dict[str, dict] = {}   # IP->API response pair
    risk_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    
    for ip in valid_ips:
        try:
            data = fetch_check_data(ip, ABUSEIPDB_API_KEY)
            entry = pretty_check_data(data, CONFIDENCE_THRESHOLD, include_public=False, include_ip=False)   # Build the json
            
            results[ip] = entry
            risk_counts[entry["risk_level"]] += 1

        except (requests.exceptions.RequestException, ValueError, KeyError):
            errors[ip] = "API error"
    
    summary = {
        "total": len(ip_list),
        "successful": len(results),
        "failed": len(errors),
        "risk_counts": risk_counts,
    }
    api_object = {"summary": summary, "results": results, "errors": errors}

    # If results is empty, that means all API calls failed
    if len(results) == 0:
        typer.echo(json.dumps(build_output(2, "failed", api_object), indent=2))
        raise typer.Exit(code=2)

    # If there are any errors, we return a partial success
    if len(errors) > 0:
        typer.echo(json.dumps(build_output(0, "partial_success", api_object), indent=2))
        raise typer.Exit(code=0)
    
    typer.echo(json.dumps(build_output(0, "success", api_object), indent=2))
    return

# Helper: IPs are comma-separated
def split_ips(raw):
    parts = [p.strip() for p in raw.split(",")] if raw else []
    return [p for p in parts if p != ""]

# Helper: Validate IP address
def is_valid_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False
    
    
if __name__ == "__main__": # pragma: no cover
    app()
