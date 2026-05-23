# OpenSK API

> Transforming Slovak public data into a single, unified API.

OpenSK API is an open-source community project that aggregates Slovak public APIs into one clean, developer-friendly interface. Official government APIs are fragmented, poorly documented, and inconsistent — OpenSK API fixes that.

---

## Available Endpoints

> 🚧 This project is in early development. Endpoints are being added.

| Endpoint | Description | Status |
|---|---|---|
| `GET /v1/holidays/{year}` | Slovak public holidays by year | 🔜 Planned |
| `GET /v1/zip/{code}` | Postal code lookup | 🔜 Planned |
| `GET /v1/banks` | List of Slovak banks and bank codes | 🔜 Planned |
| `GET /v1/companies/{ico}` | Company lookup via ORSR | 🔜 Planned |
| `GET /v1/iban/validate/{iban}` | IBAN validation | 🔜 Planned |

---

## Usage

All endpoints return JSON. No API key required.

```bash
# Get Slovak public holidays for 2026
curl https://opensk-api.fly.dev/v1/holidays/2026

# Look up a postal code
curl https://opensk-api.fly.dev/v1/zip/81101

# Validate an IBAN
curl https://opensk-api.fly.dev/v1/iban/validate/SK3112000000198742637541
```

---

## Motivation

Slovakia publishes valuable public data through various government APIs and portals. The problem: each source has different authentication, response formats, pagination styles, and documentation quality. Developers waste hours integrating what should be simple lookups.

OpenSK API is inspired by [BrasilAPI](https://github.com/BrasilAPI/BrasilAPI) — a community project that unified Brazilian public data into one clean interface.

---

## Tech Stack

- **Python** + **FastAPI**
- **SQLite** for static datasets (postal codes, bank codes)
- **Redis** for caching upstream API responses
- Deployed on **Fly.io**

---

## Contributing

Contributions are welcome. The most valuable contributions are **new endpoints** — if you know of a Slovak public data source that should be included, open an issue or submit a PR.

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding new endpoints.

### Running locally

```bash
git clone https://github.com/matej-fedak/opensk-api
cd opensk-api
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## Roadmap

- [ ] Public holidays
- [ ] Postal codes
- [ ] Bank codes
- [ ] Company registry (ORSR)
- [ ] IBAN validation
- [ ] VAT number validation (VIES)
- [ ] Municipality data
- [ ] MCP server wrapper

---

## License

MIT — see [LICENSE](LICENSE)

---

*Created by [@matej-fedak](https://github.com/matej-fedak). Inspired by [BrasilAPI](https://github.com/BrasilAPI/BrasilAPI).*
