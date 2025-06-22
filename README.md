# Python Web3 Event Indexer

This project is a **containerized**, **Python-based** microservice that continuously **indexes ERC‑20 ********`Transfer`******** events** from any EVM-compatible chain into a **Postgres** database, exposes a **health** and **metrics** endpoint, and is fully set up for **VS Code Dev-Containers** and **Poetry** dependency management.

---

## 📦 Features

* **Chain-agnostic indexing**: Configure any EVM chain RPC and ERC‑20 token via `.env`.
* **FastAPI** server exposing:

  * `/healthz` – returns `{ ok: true, events_collected: <number> }`.
  * `/metrics` – Prometheus-formatted metrics for scraping.
* **Postgres persistence** using **SQLModel** (async).
* **Docker Compose** orchestration: Postgres, indexer service.
* **VS Code Dev-Container** config for zero-setup development.
* **Poetry** for dependency and script management.

---

## 🛠️ Getting Started

### Prerequisites

* Docker & Docker Compose (v2) installed
* VS Code with **Remote - Containers** extension (optional)

### 1. Clone the repo

```bash
git clone <your-repo-url> && cd web3_python_indexer_scaffold
```

### 2. Configure environment

Create a file named `.env` in the project root (next to `docker-compose.yml`):

```dotenv
# RPC endpoint (e.g. Base public, Ankr, Alchemy)
RPC_URL=https://mainnet.base.org

# ERC-20 token to index (checksummed address)
TOKEN_ADDRESS=0xd9AEc86B65D86f6A7B5B1b0c42FFA531710b6CA

# Poll interval in seconds (0 = continuous)
POLL_INTERVAL=5
```

### 3. Launch via Docker Compose

```bash
# Clean any old state
docker compose down --volumes

# Build & start services
docker compose up --build
```

Services:

* **db**: Postgres database on port 5432
* **indexer**: FastAPI app + indexing loop on port 8000

### 4. Dev-Container (VS Code)

In VS Code, open the folder and select **Reopen in Container** when prompted. This uses the `.devcontainer/devcontainer.json` to spin up the same Compose services and attach the editor to the `indexer` container.

---

## 🚀 Usage

1. **Health check**

   ```bash
   curl http://localhost:8000/healthz
   # { "ok": true, "events_collected": 42 }
   ```

2. **Metrics**
   Browse to [http://localhost:8000/metrics](http://localhost:8000/metrics) to see Prometheus stats.

3. **Inspect DB**
   Connect to Postgres:

   ```bash
   psql postgresql://postgres:postgres@localhost:5432/postgres
   SELECT count(*) FROM transfer;
   ```

---

## 🧩 Project Structure

```
├── docker-compose.yml    # Orchestrates Postgres & indexer
├── Dockerfile            # Builds the indexer container (Poetry + FastAPI)
├── pyproject.toml        # Poetry project config
├── .env                  # Environment variables for RPC, token, etc.
├── .devcontainer/        # VS Code Dev-Container configuration
└── app/
    ├── main.py           # FastAPI app, startup, health endpoint
    ├── indexer.py        # Async loop: fetch logs → store → repeat
    ├── db.py             # Async SQLModel engine & init
    ├── models.py         # SQLModel `Transfer` table schema
    └── graphql.py        # (week 2) Strawberry GraphQL schema
```

---

## 🛠️ Development Commands

Run these inside the **indexer** container (Poetry env) or prefix with `docker compose exec indexer`:

| Command                                    | Description                     |
| ------------------------------------------ | ------------------------------- |
| `poetry install`                           | Install dependencies            |
| `poetry run black .`                       | Auto-format with Black          |
| `poetry run isort .`                       | Sort imports with isort         |
| `poetry run pytest`                        | Run unit tests                  |
| `poetry run uvicorn app.main:app --reload` | Run FastAPI locally (no Docker) |

---

## 🏗️ Production-Grade Roadmap

Take this PoC all the way to a full platform by layering in these pillars:

1. **Multi-Chain, Plugin Architecture**

   * Drive chain configs from a YAML/JSON file (RPC, token, event definitions).
   * Parallelize indexing across chains via `asyncio.gather` and add a `chain_id` column.
   * Plugin hooks for arbitrary event parsers without touching core code.

2. **High-Performance Store**

   * Swap Postgres for ClickHouse or TimescaleDB for analytical workloads.
   * Batch-insert events (e.g. 1 000 rows per SQL `INSERT`) to maximize throughput.
   * Benchmark end-to-end indexing TPS with k6 + Prometheus → Grafana.

3. **Rich Observability & Alerts**

   * Ship a Grafana dashboard JSON (with error-rate alerts) via Compose.
   * Integrate Loki (or ELK) for centralized logs.
   * Add OpenTelemetry spans in FastAPI for RPC and DB calls.

4. **Full-Featured API**

   * Extend GraphQL with pagination, filtering, and subscriptions (WS).
   * Auto-generate a REST facade with OpenAPI docs (`/transfers?from=&to=`).

5. **UI Dashboard & Demo**

   * Build a Next.js + Tailwind app showing real-time charts and search.
   * Package frontend alongside backend in Compose or Helm.

6. **Security & Quality Gates**

   * CI pipeline: Black, isort, flake8, pytest (>90% cov), Slither/MythX, k6 smoke-tests.
   * Automated dependabot/renovate updates.

7. **Packaging & Distribution**

   * Publish a Docker image (`your-org/web3-indexer:latest`).
   * Release a PyPI package `pip install web3-indexer` with a `BaseIndexer` class.
   * Provide a Helm chart & Terraform module for one-click cloud deploys.

8. **Open-Source Template & Community**

   * Add README badges (build, coverage, Docker Hub, PyPI).
   * Create CONTRIBUTING.md, issue templates, and seed plugin requests.
   * Write a blog post: “Building a Production-Ready Web3 Indexer in Python.”

---

## ❤️ Contributing

Feel free to open issues or PRs for new chains, tokens, or features. Happy hacking! 🚀