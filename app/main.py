from time import perf_counter

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse, Response

app = FastAPI(title="QShield PQC Lab", version="1.0.0")

from .storage import add_asset, get_asset, init_db, latest_scan, list_assets, save_scan, set_asset_status
import json
from urllib.parse import urlparse
import socket
import ssl
import httpx
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

init_db()


class AssetCreate(BaseModel):
    name: str
    url: HttpUrl


@app.get("/api/assets")
def assets():
    return {"assets": list_assets()}


@app.post("/api/assets")
def create_asset(payload: AssetCreate):
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=422, detail="Asset name is required")
    return add_asset(name, str(payload.url))


@app.post("/api/assets/{asset_id}/scan")
def scan_asset(asset_id: int):
    asset = get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    parsed = urlparse(asset["url"])
    if parsed.scheme != "https" or not parsed.hostname:
        raise HTTPException(status_code=422, detail="Only authorized HTTPS assets can be scanned")
    set_asset_status(asset_id, "scanning")
    findings = []
    tls = {}
    try:
        context = ssl.create_default_context()
        with socket.create_connection((parsed.hostname, parsed.port or 443), timeout=8) as raw:
            with context.wrap_socket(raw, server_hostname=parsed.hostname) as conn:
                cert = conn.getpeercert()
                tls = {"version": conn.version(), "cipher": conn.cipher()[0] if conn.cipher() else None, "subject": dict(x[0] for x in cert.get("subject", [])), "issuer": dict(x[0] for x in cert.get("issuer", []))}
                if conn.version() != "TLSv1.3":
                    findings.append({"severity": "high", "title": "TLS version is not TLS 1.3", "recommendation": "Require TLS 1.3 and plan hybrid X25519 + ML-KEM-768."})
                if tls["cipher"] and any(x in tls["cipher"] for x in ("RSA", "ECDHE", "ECDSA")):
                    findings.append({"severity": "medium", "title": "Classical-only cryptographic exchange detected", "recommendation": "Add a hybrid post-quantum policy using ML-KEM-768."})
    except Exception as exc:
        set_asset_status(asset_id, "scan_failed")
        result = {"asset": asset, "status": "scan_failed", "error": str(exc), "findings": [{"severity": "critical", "title": "TLS endpoint could not be assessed", "recommendation": "Verify authorization, DNS, certificate chain, and network access."}]}
        save_scan(asset_id, "scan_failed", 0, json.dumps(result))
        return result
    headers = {}
    try:
        response = httpx.get(asset["url"], timeout=10, follow_redirects=True)
        headers = {k.lower(): v for k, v in response.headers.items()}
        for header, recommendation in (("strict-transport-security", "Enable HSTS."), ("content-security-policy", "Define a Content-Security-Policy."), ("x-content-type-options", "Set X-Content-Type-Options: nosniff.")):
            if header not in headers:
                findings.append({"severity": "low", "title": f"Missing {header}", "recommendation": recommendation})
    except Exception as exc:
        headers = {"error": str(exc)}
    set_asset_status(asset_id, "assessed")
    result = {"asset": asset, "status": "assessed", "tls": tls, "headers": headers, "pqc_readiness": max(0, 100 - len(findings) * 15), "findings": findings}
    save_scan(asset_id, "assessed", result["pqc_readiness"], json.dumps(result))
    return result


@app.get("/api/assets/{asset_id}/latest")
def latest_asset_scan(asset_id: int):
    if not get_asset(asset_id):
        raise HTTPException(status_code=404, detail="Asset not found")
    scan = latest_scan(asset_id)
    if not scan:
        return {"asset_id": asset_id, "status": "not_scanned"}
    scan["result"] = json.loads(scan.pop("result_json"))
    return scan


@app.get("/api/assets/{asset_id}/report.pdf")
def asset_report(asset_id: int):
    asset = get_asset(asset_id)
    scan = latest_scan(asset_id)
    if not asset or not scan:
        raise HTTPException(status_code=404, detail="Asset must be scanned before a report can be generated")
    result = json.loads(scan["result_json"])
    from io import BytesIO
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=42, leftMargin=42, topMargin=42, bottomMargin=42)
    styles = getSampleStyleSheet()
    story = [Paragraph("QSHIELD SECURITY ASSESSMENT", styles["Title"]), Paragraph("Post-Quantum Readiness Report", styles["Heading2"]), Spacer(1, 14), Paragraph(f"Asset: {asset['name']} ({asset['url']})", styles["BodyText"]), Paragraph(f"Generated: {scan['created_at']}", styles["BodyText"]), Spacer(1, 18), Paragraph(f"PQC readiness score: {result.get('pqc_readiness', 0)}/100", styles["Heading2"]), Spacer(1, 10)]
    rows = [["Severity", "Finding", "Recommendation"]]
    rows += [[f.get("severity", "info").upper(), f.get("title", ""), f.get("recommendation", "")] for f in result.get("findings", [])]
    table = Table(rows, colWidths=[70, 190, 240], repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#102b42")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), .4, colors.HexColor("#9fb6c8")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("FONTSIZE", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 7)]))
    story += [table, Spacer(1, 18), Paragraph("Recommended direction: adopt hybrid X25519 + ML-KEM-768 for key establishment and hybrid Ed25519 + ML-DSA-65 for signatures. Validate all recommendations against the organization’s approved change process.", styles["BodyText"])]
    doc.build(story)
    return Response(buffer.getvalue(), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=qshield-{asset_id}-report.pdf"})


def oqs_module():
    try:
        import oqs
        if not hasattr(oqs, "KeyEncapsulation") or not hasattr(oqs, "Signature"):
            return None, "The installed oqs package is not liboqs-python. Install liboqs-python and its native liboqs runtime."
        return oqs, None
    except Exception as exc:
        return None, str(exc)


@app.get("/api/health")
def health():
    oqs, error = oqs_module()
    return {"status": "ready" if oqs else "crypto_unavailable", "oqs": bool(oqs), "error": error}


@app.post("/api/kem")
def kem_demo():
    oqs, error = oqs_module()
    if not oqs:
        return {"ok": False, "error": error}
    started = perf_counter()
    with oqs.KeyEncapsulation("ML-KEM-768") as kem:
        public_key = kem.generate_keypair()
        ciphertext, sender_secret = kem.encap_secret(public_key)
        receiver_secret = kem.decap_secret(ciphertext)
    return {
        "ok": sender_secret == receiver_secret,
        "algorithm": "ML-KEM-768",
        "public_key_bytes": len(public_key),
        "ciphertext_bytes": len(ciphertext),
        "shared_secret_match": sender_secret == receiver_secret,
        "duration_ms": round((perf_counter() - started) * 1000, 2),
    }


@app.post("/api/signature")
def signature_demo():
    oqs, error = oqs_module()
    if not oqs:
        return {"ok": False, "error": error}
    message = b"QShield PQC Lab v1.0"
    started = perf_counter()
    with oqs.Signature("ML-DSA-65") as signer:
        public_key = signer.generate_keypair()
        signature = signer.sign(message)
        valid = signer.verify(message, signature, public_key)
        tampered = signer.verify(message + b"!", signature, public_key)
    return {
        "ok": valid and not tampered,
        "algorithm": "ML-DSA-65",
        "public_key_bytes": len(public_key),
        "signature_bytes": len(signature),
        "valid_signature": valid,
        "tampered_message_rejected": not tampered,
        "duration_ms": round((perf_counter() - started) * 1000, 2),
    }


@app.get("/api/assessment")
def assessment():
    return {
        "organization": "Demo Organization",
        "readiness_score": 38,
        "services_scanned": 4,
        "quantum_safe": 1,
        "at_risk": 3,
        "findings": [
            {"service": "Public API", "current": "TLS 1.3 / ECDHE", "risk": "Harvest-now, decrypt-later", "recommendation": "Enable X25519 + ML-KEM-768"},
            {"service": "Release signing", "current": "Ed25519", "risk": "Classical-only signatures", "recommendation": "Add ML-DSA-65"},
            {"service": "Firmware portal", "current": "RSA-2048", "risk": "Quantum vulnerable", "recommendation": "Migrate to ML-DSA-65"},
        ],
    }


@app.get("/api/report")
def report():
    return JSONResponse(content={"title": "QShield PQC Readiness Report", "generated": "V1.5 demo", "assessment": assessment()})


@app.get("/", response_class=HTMLResponse)
def home():
    return HTMLResponse("""<!doctype html>
<html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>QShield PQC Lab</title>
<style>@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Space+Grotesk:wght@400;500;600;700&display=swap');:root{--bg:#050912;--panel:rgba(11,22,38,.82);--line:#1b3a52;--cyan:#5ee7ff;--green:#50f2a2;--amber:#ffd166;--red:#ff6b85}*{box-sizing:border-box}body{font-family:'Space Grotesk',system-ui;background:var(--bg);color:#e8f3ff;margin:0;min-height:100vh;background-image:linear-gradient(rgba(94,231,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(94,231,255,.035) 1px,transparent 1px),radial-gradient(circle at 80% 0%,#12314a 0,transparent 35%);background-size:42px 42px,42px 42px,100% 100%}.wrap{max-width:1180px;margin:auto;padding:34px 24px 60px}.top{display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--line);padding-bottom:22px}.brand{display:flex;gap:12px;align-items:center}.shield{width:38px;height:38px;border:1px solid var(--cyan);border-radius:10px;display:grid;place-items:center;color:var(--cyan);box-shadow:0 0 22px #1b8da255}.badge{font:600 12px 'IBM Plex Mono',monospace;color:var(--green);letter-spacing:2px}.status{font:12px 'IBM Plex Mono',monospace;color:#89a9c2}.status i{display:inline-block;width:8px;height:8px;background:var(--green);border-radius:50%;box-shadow:0 0 12px var(--green);margin-right:8px}h1{font-size:42px;letter-spacing:-1px;margin:34px 0 6px}.sub{color:#8da9c0;max-width:680px}.nav{display:flex;gap:8px;flex-wrap:wrap;margin:28px 0}.nav button{background:#0d1a2c;color:#9fc1d7;border:1px solid #1e4057}.nav button.on{background:var(--cyan);color:#04121c;border-color:var(--cyan);box-shadow:0 0 20px #5ee7ff44}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.card{background:var(--panel);backdrop-filter:blur(16px);border:1px solid var(--line);border-radius:14px;padding:22px;box-shadow:0 12px 40px #0005}.card h2{margin-top:0}.metric{font:600 38px 'IBM Plex Mono',monospace}.green{color:var(--green)}.amber{color:var(--amber)}.red{color:var(--red)}button{border:0;border-radius:7px;padding:11px 16px;font-weight:700;cursor:pointer;margin-top:8px;transition:.2s}button:hover{transform:translateY(-1px);filter:brightness(1.12)}pre{font:12px 'IBM Plex Mono',monospace;white-space:pre-wrap;color:#aaf7cb;min-height:80px;overflow:auto;background:#02070d;border-radius:8px;padding:12px}.page{display:none}.page.active{display:block}table{width:100%;border-collapse:collapse;font-size:14px}td,th{text-align:left;border-bottom:1px solid var(--line);padding:13px 8px}th{font:500 11px 'IBM Plex Mono',monospace;color:#78a4bc;text-transform:uppercase}@media(max-width:700px){.grid{grid-template-columns:1fr}.top{align-items:flex-start;gap:15px;flex-direction:column}h1{font-size:32px}}</style></head>
<body><main class='wrap'><div class='top'><div class='brand'><div class='shield'>◈</div><div><div class='badge'>QSHIELD // SECURITY COMMAND</div><div class='status'><i></i>CONTROL PLANE ONLINE · PQC ENGINE READY</div></div></div><div class='status'>V1.5.0 / SECURE MODE</div></div><h1>Post-Quantum Security Platform</h1><p class='sub'>Discover cryptographic risk, prove PQC protection, and plan migration across your digital estate.</p>
<nav class='nav'><button class='on' onclick="show('overview',this)">Overview</button><button onclick="show('assessment',this)">Assessment</button><button onclick="show('lab',this)">PQC Lab</button><button onclick="show('migration',this)">Migration</button><button onclick="downloadReport()">Export report</button></nav>
<section id='overview' class='page active'><div class='card' style='margin-bottom:16px'><h2>Assess an authorized website</h2><p class='sub'>Enter a website your organization owns or is authorized to assess. QShield will register it, inspect its public TLS posture, and generate evidence-backed findings.</p><div style='display:flex;gap:10px;flex-wrap:wrap'><input id='assetName' placeholder='Asset name' style='flex:1;min-width:180px;padding:12px;border-radius:7px;border:1px solid #1b3a52;background:#07111d;color:#e8f3ff'><input id='assetUrl' placeholder='https://your-company.com' style='flex:2;min-width:240px;padding:12px;border-radius:7px;border:1px solid #1b3a52;background:#07111d;color:#e8f3ff'><button onclick='onboard()' style='background:var(--cyan);color:#04121c'>Register & assess</button></div><pre id='onboardResult'>Waiting for an asset…</pre></div><div class='grid'><div class='card'><div class='sub'>Readiness score</div><div class='metric green'>38%</div><p>Migration started</p></div><div class='card'><div class='sub'>Services scanned</div><div class='metric'>4</div><p>1 protected · 3 at risk</p></div><div class='card'><div class='sub'>Recommended policy</div><div class='metric'>PQC</div><p>X25519 + ML-KEM-768</p></div></div><div class='card' style='margin-top:16px'><h2>Investor / client view</h2><p>QShield turns an unknown cryptographic estate into an actionable, measurable post-quantum migration plan.</p></div></section>
<section id='assessment' class='page'><div class='card'><h2>Cryptographic assessment</h2><p class='sub'>Demo inventory with actionable findings.</p><div id='findings'>Loading…</div></div></section>
<section id='lab' class='page'><div class='grid'><section class='card'><h2>ML-KEM-768</h2><p>Real key encapsulation and shared-secret agreement.</p><button onclick="run('/api/kem','kem')">Run demonstration</button><pre id='kem'>Waiting…</pre></section><section class='card'><h2>ML-DSA-65</h2><p>Real signing, verification, and tamper rejection.</p><button onclick="run('/api/signature','sig')">Run demonstration</button><pre id='sig'>Waiting…</pre></section><section class='card'><h2>Trust status</h2><div class='metric green'>LIVE</div><p>Results come from the container PQC runtime.</p></section></div></section>
<section id='migration' class='page'><div class='card'><h2>Migration simulator</h2><p>Apply the recommended policy to the demo estate.</p><button onclick="document.getElementById('migrationResult').textContent='Migration plan ready: 4 services mapped to hybrid PQC policies.'">Generate migration plan</button><pre id='migrationResult'>Waiting…</pre></div></section></main>
<script>function show(id,btn){document.querySelectorAll('.page').forEach(x=>x.classList.remove('active'));document.getElementById(id).classList.add('active');document.querySelectorAll('.nav button').forEach(x=>x.classList.remove('on'));btn.classList.add('on');if(id==='assessment')loadAssessment()}async function onboard(){const out=document.getElementById('onboardResult');const name=document.getElementById('assetName').value.trim();const url=document.getElementById('assetUrl').value.trim();if(!name||!url){out.textContent='Enter an asset name and HTTPS URL.';return}out.textContent='Registering asset…';try{const created=await fetch('/api/assets',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name,url})}).then(async r=>{const d=await r.json();if(!r.ok)throw Error(JSON.stringify(d));return d});out.textContent='Asset registered. Running passive assessment…';const scan=await fetch('/api/assets/'+created.id+'/scan',{method:'POST'}).then(r=>r.json());out.textContent=JSON.stringify(scan,null,2)}catch(e){out.textContent='Assessment failed: '+e.message}}async function loadAssessment(){const d=await fetch('/api/assessment').then(r=>r.json());document.getElementById('findings').innerHTML='<table><tr><th>Service</th><th>Current</th><th>Risk</th><th>Recommendation</th></tr>'+d.findings.map(f=>`<tr><td>${f.service}</td><td>${f.current}</td><td class='red'>${f.risk}</td><td>${f.recommendation}</td></tr>`).join('')+'</table>'}async function run(path,id){const el=document.getElementById(id);el.textContent='Running…';try{const r=await fetch(new URL(path,location.href),{method:'POST'});el.textContent=JSON.stringify(await r.json(),null,2)}catch(e){el.textContent='Request failed: '+e.message}}function downloadReport(){window.open('/api/report','_blank')}</script></body></html>""")
