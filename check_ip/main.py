import requests
import json
import typer
import ipaddress
from typing import Optional
from common.abuseipdb import fetch_check_data, pretty_check_data, build_output

app = typer.Typer()

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

    try:
        data = fetch_check_data(IP_ADDRESS, ABUSEIPDB_API_KEY)
        api_object = pretty_check_data(data, CONFIDENCE_THRESHOLD)
        # No errors occurred
        typer.echo(json.dumps(build_output(0, "success", api_object), indent=2))
        return 

    # Raised from response, API error
    except (requests.exceptions.RequestException, ValueError, KeyError) as e:
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



if __name__ == "__main__": # pragma: no cover
    app()