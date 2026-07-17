# QShield PQC Lab

Minimal V1.0 web app demonstrating real ML-KEM-768 and ML-DSA-65 operations through a FastAPI interface.

## Run

```bash
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000.

The app reports `crypto_unavailable` instead of fabricating results when the liboqs runtime is not installed.
