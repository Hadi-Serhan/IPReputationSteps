# IP Reputation Steps (AbuseIPDB)

Two production-style CLI “steps” that query **AbuseIPDB** and print **normalized JSON** to stdout.

- **Step 1** (`check_ip`): check a **single** IP address
- **Step 2** (`check_ip_batch`): check **multiple** IP addresses and return an aggregated summary

The tools are designed to run the same way locally, in CI, and inside Docker containers (inputs via env vars, output via stdout).

---

## What each step does

### Step 1 — Single IP check (`check_ip`)
Reads inputs from environment variables, calls the AbuseIPDB `/check` endpoint, and prints:

```json
{
  "step_status": { "code": 0, "message": "success" },
  "api_object": {
    "ip": "118.25.6.39",
    "risk_level": "LOW",
    "abuse_confidence_score": 8,
    "total_reports": 2,
    "country_code": "CN",
    "isp": "Tencent Cloud Computing (Beijing) Co., Ltd",
    "is_public": true
  }
}
```

**Status codes**
- `0` — success  
- `1` — failed: IP input validation error (missing/invalid IP)
- `2` — failed: missing API key **or** API/network/auth/rate-limit errors

### Step 2 — Batch IP check (`check_ip_batch`)
Splits and validates a comma-separated list of IPs. For each valid IP it calls AbuseIPDB and returns:

- `summary` (counts + risk buckets)
- `results` (map keyed by IP → normalized data)
- `errors` (invalid IPs and/or per-IP API errors)

```json
{
  "step_status": {
    "code": 0,
    "message": "partial_success"
  },
  "api_object": {
    "summary": {
      "total": 4,
      "successful": 3,
      "failed": 1,
      "risk_counts": {
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 3
      }
    },
    "results": {
      "118.25.6.39": {
        "risk_level": "LOW",
        "abuse_confidence_score": 8.0,
        "total_reports": 2,
        "country_code": "CN",
        "isp": "Tencent Cloud Computing (Beijing) Co., Ltd"
      },
      "8.8.8.8": {
        "risk_level": "LOW",
        "abuse_confidence_score": 0.0,
        "total_reports": 33,
        "country_code": "US",
        "isp": "Google LLC"
      },
      "1.1.1.1": {
        "risk_level": "LOW",
        "abuse_confidence_score": 0.0,
        "total_reports": 197,
        "country_code": "HK",
        "isp": "APNIC and Cloudflare DNS Resolver project"
      }
    },
    "errors": {
      "invalid-ip": "Invalid IP address format"
    }
  }
}
```

**Status codes**
- `0` + `success` — all IPs checked successfully
- `0` + `partial_success` — some succeeded, some failed (invalid format and/or API errors)
- `1` + `failed` — input validation error (**no valid IPs provided**)
- `2` + `failed` — **all** API requests failed (valid IPs exist, but none succeeded)

> Note: `risk_counts` counts only successful lookups.

---

## Inputs (Environment Variables)

### Step 1
| Variable | Required | Default | Description |
|---|---:|---:|---|
| `IP_ADDRESS` | ✅ | - | IP address to check |
| `ABUSEIPDB_API_KEY` | ✅ | - | AbuseIPDB API key |
| `CONFIDENCE_THRESHOLD` | ❌ | `70` | Score threshold for `HIGH` risk |

### Step 2
| Variable | Required | Default | Description |
|---|---:|---:|---|
| `IP_ADDRESSES` | ✅ | - | Comma-separated IP addresses |
| `ABUSEIPDB_API_KEY` | ✅ | - | AbuseIPDB API key |
| `CONFIDENCE_THRESHOLD` | ❌ | `70` | Score threshold for `HIGH` risk |

---

## Risk level logic

Let `score = abuse_confidence_score`:

- `HIGH` if `score >= CONFIDENCE_THRESHOLD`
- `MEDIUM` if `25 <= score < CONFIDENCE_THRESHOLD`
- `LOW` if `score < 25`

---

## Running locally

### Linux / macOS
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export ABUSEIPDB_API_KEY="your-key"
export CONFIDENCE_THRESHOLD="50"

# Step 1
export IP_ADDRESS="118.25.6.39"
python -m check_ip.main

# Step 2
export IP_ADDRESSES="118.25.6.39,8.8.8.8,invalid-ip,1.1.1.1"
python -m check_ip_batch.main
```

### Windows (PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

$env:ABUSEIPDB_API_KEY="your-key"
$env:CONFIDENCE_THRESHOLD="50"

# Step 1
$env:IP_ADDRESS="118.25.6.39"
python -m check_ip.main

# Step 2
$env:IP_ADDRESSES="118.25.6.39,8.8.8.8,invalid-ip,1.1.1.1"
python -m check_ip_batch.main
```

---

## Testing + coverage

Tests are written with **pytest** and use Typer’s `CliRunner` to exercise the CLI end-to-end while mocking HTTP calls.

Run all tests with coverage:
```bash
pytest -q --cov=check_ip --cov=check_ip_batch --cov=common --cov-report=term-missing --cov-fail-under=90
```

Run just one module’s tests:
```bash
pytest -q tests/test_check_ip_batch.py --cov=check_ip_batch --cov-report=term-missing
```

Tests validate the end-to-end CLI output (exit codes + JSON structure) while mocking HTTP requests. A coverage gate (≥90%) helps ensure the main paths—input validation, API failures, and partial-success aggregation—remain tested as the code evolves.

---

## Docker

A single multi-stage `Dockerfile` builds **two images** (one per step) using build targets.

### Build
```bash
docker build --target check-ip -t check-ip .
docker build --target check-ip-batch -t check-ip-batch .
```

### Run (Step 1)
```bash
docker run --rm \
  -e ABUSEIPDB_API_KEY="your-key" \
  -e IP_ADDRESS="118.25.6.39" \
  -e CONFIDENCE_THRESHOLD="50" \
  check-ip
```

### Run (Step 2)
```bash
docker run --rm \
  -e ABUSEIPDB_API_KEY="your-key" \
  -e IP_ADDRESSES="118.25.6.39,8.8.8.8,invalid-ip,1.1.1.1" \
  -e CONFIDENCE_THRESHOLD="50" \
  check-ip-batch
```

> Note: in CI smoke tests, a missing API key is expected to exit with code `2`. We use `set +e` / `set -e` so the job can keep going while still validating the JSON output.

---

## Project layout

```
common/            Shared API client + normalization helpers
check_ip/          Step 1 CLI entrypoint (single IP)
check_ip_batch/    Step 2 CLI entrypoint (batch)
tests/             Pytest suite (mocks HTTP calls; checks output JSON)
.github/workflows/ CI (tests + coverage + Docker build + smoke tests)
Dockerfile         Multi-stage build (one target per step)
```

---

## Notes on error handling

- **Network / auth / rate-limit** issues surface as HTTP/Request exceptions and are treated as API errors.
- **Invalid IP format** is treated as an input error (Step 1 code `1`; Step 2 counted under `errors` and can lead to code `1` if none are valid).
- If AbuseIPDB returns an unexpected payload (non-JSON or missing keys), the code treats it as an API error.

---

## Security

- API keys are **never** hardcoded; use env vars.
- `.dockerignore` excludes local venvs, caches, and tests from Docker build context.
