# IP Reputation Steps (AbuseIPDB)

Two production-style CLI “steps” that query **AbuseIPDB** and print **normalized JSON** to stdout.

- **Step 1** (`check_ip`): check a **single** IP address
- **Step 2** (`check_ip_batch`): check **multiple** IP addresses and return an aggregated summary

The tools are designed to run the same way locally, in CI, and inside Docker containers (inputs via env vars, output via stdout).

---
>Prerequisites
* Git installed
* Python 3.12+ (recommended)
* Optional: Docker
---
## Choose your setup

- [Linux/macOS — Run locally](#quickstart-linuxmacos---locally)
- [Linux/macOS — Run with Docker](#quickstart-linuxmacos---docker)
- [Windows PowerShell — Run locally](#quickstart-windows-powershell---locally)
- [Windows PowerShell — Run with Docker](#quickstart-windows-powershell---docker)
- [Information](#what-each-step-does)
---
## Quickstart (Linux/macOS) - Locally

### 1) Clone the repo
Open a terminal, then run:

```bash
git clone https://github.com/hadiserhan/IPReputationSteps.git
cd IPReputationSteps
```

### 2) Create and activate a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3) Set up your environment variables
> You need an AbuseIPDB API key from your AbuseIPDB account.
```bash
export ABUSEIPDB_API_KEY="PASTE_YOUR_KEY_HERE"

# Optional (default value is 70)
export CONFIDENCE_THRESHOLD="50" 
```

### 4) Run Step 1 (Single IP)
```bash
export IP_ADDRESS="8.8.8.8"
python -m check_ip.main
```

### 5) Run Step 2 (Batch)
```bash
export IP_ADDRESSES="118.25.6.39,8.8.8.8,invalid-ip,1.1.1.1"
python -m check_ip_batch.main
```

### 6) Testing + Coverage
Run:
```bash
pytest -q --cov=check_ip --cov=check_ip_batch --cov=common --cov-report=term-missing --cov-fail-under=90
```
---
### Quickstart (Linux/macOS) - Docker
> Prerequisite: Install Docker from the official download page: https://docs.docker.com/get-docker/

### Option A - Pull from Docker Hub
```bash
docker pull hadiserhan/check-ip:latest
docker pull hadiserhan/check-ip-batch:latest
```

### Run Step 1 (Single IP)
```bash
docker run --rm \
  -e ABUSEIPDB_API_KEY="PASTE_YOUR_KEY_HERE" \
  -e IP_ADDRESS="8.8.8.8" \
  -e CONFIDENCE_THRESHOLD="50" \
  hadiserhan/check-ip:latest
```

### Run Step 2 (Batch)
```bash
docker run --rm \
  -e ABUSEIPDB_API_KEY="PASTE_YOUR_KEY_HERE" \
  -e IP_ADDRESSES="118.25.6.39,8.8.8.8,invalid-ip,1.1.1.1" \
  -e CONFIDENCE_THRESHOLD="50" \
  hadiserhan/check-ip-batch:latest
```
---
### Option B - Build the images locally
### 1) Clone the repo
Open a terminal, then run:

```bash
git clone https://github.com/hadiserhan/IPReputationSteps.git
cd IPReputationSteps
```

```bash
docker build --target check-ip -t check-ip .
docker build --target check-ip-batch -t check-ip-batch .
```

### Run Step 1 (Single IP)
```bash
docker run --rm \
  -e ABUSEIPDB_API_KEY="PASTE_YOUR_KEY_HERE" \
  -e IP_ADDRESS="118.25.6.39" \
  -e CONFIDENCE_THRESHOLD="50" \
  check-ip
```

### Run Step 2 (Batch)
```bash
docker run --rm \
  -e ABUSEIPDB_API_KEY="PASTE_YOUR_KEY_HERE" \
  -e IP_ADDRESSES="118.25.6.39,8.8.8.8,invalid-ip,1.1.1.1" \
  -e CONFIDENCE_THRESHOLD="50" \
  check-ip-batch
```
---
## Quickstart (Windows PowerShell) - Locally

### 1) Clone the repo
Open a terminal, then run:

```bash
git clone https://github.com/hadiserhan/IPReputationSteps.git
cd IPReputationSteps
```

### 2) Create and activate a virtual environment
```bash
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3) Set up your environment variables
> You need an AbuseIPDB API key from your AbuseIPDB account.
```bash
$env:ABUSEIPDB_API_KEY="PASTE_YOUR_KEY_HERE"

# Optional (default value is 70)
$env:CONFIDENCE_THRESHOLD="50"
```

### 4) Run Step 1 (Single IP)
```bash
$env:IP_ADDRESS="8.8.8.8"
python -m check_ip.main
```

### 5) Run Step 2 (Batch)
```bash
$env:IP_ADDRESSES="118.25.6.39,8.8.8.8,invalid-ip,1.1.1.1"
python -m check_ip_batch.main
```

### 6) Testing + Coverage
Run:
```bash
pytest -q --cov=check_ip --cov=check_ip_batch --cov=common --cov-report=term-missing --cov-fail-under=90
```
---
### Quickstart (Windows PowerShell) - Docker
> Prerequisite: Install Docker from the official download page: https://docs.docker.com/get-docker/

### Option A - Pull from Docker Hub
```bash
docker pull hadiserhan/check-ip:latest
docker pull hadiserhan/check-ip-batch:latest
```

### Run Step 1 (Single IP)
```bash
docker run --rm `
  -e ABUSEIPDB_API_KEY="PASTE_YOUR_KEY_HERE" `
  -e IP_ADDRESS="8.8.8.8" `
  -e CONFIDENCE_THRESHOLD="50" `
  hadiserhan/check-ip:latest
```

### Run Step 2 (Batch)
```bash
docker run --rm `
  -e ABUSEIPDB_API_KEY="PASTE_YOUR_KEY_HERE" `
  -e IP_ADDRESSES="118.25.6.39,8.8.8.8,invalid-ip,1.1.1.1" `
  -e CONFIDENCE_THRESHOLD="50" `
  hadiserhan/check-ip-batch:latest
```
---
### Option B - Build the images locally
### 1) Clone the repo
Open a terminal, then run:

```bash
git clone https://github.com/hadiserhan/IPReputationSteps.git
cd IPReputationSteps
```

```bash
docker build --target check-ip -t check-ip .
docker build --target check-ip-batch -t check-ip-batch .
```

### Run Step 1 (Single IP)
```bash
docker run --rm `
  -e ABUSEIPDB_API_KEY="PASTE_YOUR_KEY_HERE" `
  -e IP_ADDRESS="118.25.6.39" `
  -e CONFIDENCE_THRESHOLD="50" `
  check-ip
```

### Run Step 2 (Batch)
```bash
docker run --rm `
  -e ABUSEIPDB_API_KEY="PASTE_YOUR_KEY_HERE" `
  -e IP_ADDRESSES="118.25.6.39,8.8.8.8,invalid-ip,1.1.1.1" `
  -e CONFIDENCE_THRESHOLD="50" `
  check-ip-batch
```
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

- `summary` (counts + risk counts)
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

## Testing + coverage

Tests are written with **pytest** and use Typer’s `CliRunner` to exercise the CLI end-to-end while mocking HTTP calls.

Tests validate the end-to-end CLI output (exit codes + JSON structure) while mocking HTTP requests. A coverage gate (≥90%) helps ensure the main paths—input validation, API failures, and partial-success aggregation—remain tested as the code evolves.

---

## CI (GitHub Actions)

On every push and pull request, the workflow:
- Runs the full pytest suite with a **coverage gate (≥90%)**
- Builds both Docker images (`check-ip` and `check-ip-batch`)
- Runs lightweight **smoke tests** to confirm the containers start and print valid JSON

>The smoke tests run **without an API key** to avoid real network calls, so the containers are expected to exit with code `2`. We use `set +e` / `set -e` so the job can continue while still validating the JSON output.

## CD (Docker image publishing)

We also have a **CD workflow** that publishes Docker images to **Docker Hub** on pushes to `main`.

**What CD does**
- Builds the two Docker targets:
  - **Step 1 image:** `check-ip`
  - **Step 2 image:** `check-ip-batch`
- Pushes them to Docker Hub as:
  - `hadiserhan/check-ip:latest`
  - `hadiserhan/check-ip-batch:latest`

> CD requires GitHub Secrets for Docker Hub auth (e.g., `DOCKERHUB_USERNAME` + `DOCKERHUB_TOKEN`).

---

## Project layout

```
common/            Shared API client + normalization helpers
check_ip/          Step 1 CLI entrypoint (single IP)
check_ip_batch/    Step 2 CLI entrypoint (batch)
tests/             Pytest suite (mocks HTTP calls; checks output JSON)
.github/workflows/ CI (tests + coverage + Docker build + smoke tests) + CD (push images to Docker Hub)
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
