# Blockchain AI System

<div align="left">

<a href="https://github.com/sjhallo07" title="Repository Owner">
	<img src="https://github.com/sjhallo07.png?size=96" alt="Owner avatar" width="48" height="48" style="border-radius: 50%; vertical-align: middle;" />
</a>

<span style="margin-left:12px; vertical-align: middle;">Author: <strong>Marcos Mora</strong></span>

</div>

Modular AI-driven blockchain operations platform featuring predictive analytics and market telemetry.

## Structure
- `src/api`: FastAPI application exposing market data, AI prediction, and gas optimization endpoints.
- `src/ai/models`: Simple RandomForest-based price predictor utilities.
- `src/data/collectors`: CoinGecko and DeepSeek client shims.
- `src/ai_models`: Advanced LSTM-based experimentation (optional, requires TensorFlow).
- `tests`: Unit test suite.
- `config`: YAML configuration and templates.

## Getting Started
1. Create and activate a virtualenv (recommended) and install deps:
	- `pip install -r requirements.txt`
	- or inside this folder: `pip install -r blockchain-ai-system/requirements.txt`
2. Run the API server (Windows PowerShell example):
	- `python blockchain-ai-system/run_api.py --host 0.0.0.0 --port 8000`
3. Open the docs: http://localhost:8000/docs

### CLI (after editable install)
Optionally install this subproject in editable mode and use the CLI entry point:

```
cd blockchain-ai-system
pip install -e .
blockchain-ai-api --host 0.0.0.0 --port 8000
```

### Optional extras
Install extra capabilities only when you need them:

- PDF generation: `pip install -e .[pdf]` (installs reportlab)
- PostgreSQL client: `pip install -e .[postgres]` (installs psycopg[binary])

Notes on packaging metadata:
- Extras names are normalized (lowercase letters, digits, hyphens), e.g. `pdf`.
- Built distributions will include metadata like `Provides-Extra: pdf` and
	`Requires-Dist: reportlab; extra == "pdf"`.
- Do not declare standard-library modules (e.g., `re`, `sys`, `zlib`,
	`xml.parsers.expat`) as dependencies — packaging tools infer them.

### Endpoints
- `GET /api/market/data?limit=20` — Top market data via CoinGecko
- `GET /api/ai/predict/{coin_id}` — AI + ML prediction for a coin
- `GET /api/gas/optimization` — Heuristic gas optimization tips

Notes:
- The CoinGecko client performs live HTTP requests; ensure outbound internet is available.
- The DeepSeek client here is a simple deterministic mock.

## Testing
Run the unit tests from the repo root, setting PYTHONPATH so `src` can be resolved:
```
python -m unittest discover -s blockchain-ai-system/tests -t blockchain-ai-system
```

## Docker (optional)
Example build/run sequence:
```
docker build -t blockchain-ai-system -f Dockerfile .
docker run -p 8000:8000 --env-file .env blockchain-ai-system
```

## Imports, namespaces, and private modules

- Distribution name: `blockchain-ai-system` (used by pip and on PyPI)
- Import namespaces (under `src/`): `api`, `ai`, `data`, `database`, `utils`, etc.

Examples:
```
from api.server import app
from ai.models.price_predictor import PricePredictor
from data.collectors.coingecko_client import CoinGeckoClient
```

About “Import-Namespace” / “Import-Name”:
- These are not standard Python Core Metadata fields. Tools sometimes document
	the top-level import name(s) for clarity when the distribution name differs
	from the import path (e.g., distribution `zope.interface` provides the
	import namespace `zope`).
- In this project, the distribution name and import namespaces are unrelated;
	install via pip by distribution name, then import by the module/package path
	under `src/`.

Private modules:
- A leading underscore (e.g., `_private_module.py`) signals internal API.
- Use `__all__` in `__init__.py` files to control what the package exports.
- Packaging does not enforce privacy; if a file is included in the wheel, it
	can be imported. To avoid shipping truly internal files, exclude them at
	build time using the build backend’s include/exclude rules.

	## Simple repository API (optional private index)

	This API exposes a minimal Simple Repository API under `/simple/` for local/private
	installation of this package builds.

	How to use:
	1) Build distributions:
	```
	cd blockchain-ai-system
	py -m pip install --upgrade build
	py -m build
	```
	2) Run the API (see above) and visit:
	- HTML index: http://127.0.0.1:8000/simple/
	- JSON index (via Accept negotiation): send `Accept: application/vnd.pypi.simple.v1+json`

	3) Install from this index (example):
	```
	py -m pip install --index-url http://127.0.0.1:8000/simple blockchain-ai-system
	```

	Notes:
	- The server scans `dist/` for files and serves them via `/files/{filename}`.
	- HTML pages include `<meta name="pypi:repository-version" content="1.4">`.
	- JSON responses use `application/vnd.pypi.simple.v1+json` and include `meta.api-version`.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.
