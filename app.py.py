from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import urllib.request
import json
import asyncio

app = FastAPI()

def get_ip_api_data(ip: str):
    url = (
        f"http://ip-api.com/json/{ip}?fields="
        "status,message,continent,country,countryCode,"
        "regionName,city,zip,lat,lon,timezone,"
        "currency,isp,org,as,asname,reverse,mobile,proxy,hosting,query"
    )
    try:
        with urllib.request.urlopen(url, timeout=8) as r:
            data = json.loads(r.read().decode())
        if data.get("status") == "success":
            data.pop("status", None)
            return data
        return {"error": data.get("message", "Fallo la consulta")}
    except Exception as e:
        return {"error": str(e)}

def get_ipapi_is_data(ip: str):
    url = f"https://api.ipapi.is/?q={ip}"
    try:
        with urllib.request.urlopen(url, timeout=8) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"error": str(e)}

@app.get("/", response_class=HTMLResponse)
async def inicio(request: Request):
    ip_visitante = request.client.host
    return HTMLResponse(f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Info de IP</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{
    font-family: -apple-system, system-ui, sans-serif;
    background: #0f172a;
    color: #e2e8f0;
    margin: 0;
    padding: 20px;
  }}
  .container {{ max-width: 900px; margin: 0 auto; }}
  h1 {{ text-align: center; color: #38bdf8; }}
  .search {{
    display: flex;
    gap: 10px;
    margin: 20px 0;
  }}
  input {{
    flex: 1;
    padding: 14px;
    border-radius: 8px;
    border: 1px solid #334155;
    background: #1e293b;
    color: #e2e8f0;
    font-size: 16px;
  }}
  button {{
    padding: 14px 24px;
    border-radius: 8px;
    border: none;
    background: #38bdf8;
    color: #0f172a;
    font-weight: bold;
    font-size: 16px;
    cursor: pointer;
  }}
  button:hover {{ background: #0ea5e9; }}
  .card {{
    background: #1e293b;
    border-radius: 12px;
    padding: 20px;
    margin-top: 20px;
    border: 1px solid #334155;
  }}
  .card h2 {{
    margin-top: 0;
    color: #38bdf8;
    font-size: 18px;
    border-bottom: 1px solid #334155;
    padding-bottom: 10px;
  }}
  .row {{
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid #1e293b;
  }}
  .row:last-child {{ border-bottom: none; }}
  .label {{ color: #94a3b8; }}
  .value {{ font-weight: 500; text-align: right; max-width: 60%; word-break: break-word; }}
  .badge {{
    display: inline-block;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: bold;
    margin: 4px 4px 0 0;
  }}
  .badge-red {{ background: #7f1d1d; color: #fecaca; }}
  .badge-green {{ background: #14532d; color: #bbf7d0; }}
  .badge-yellow {{ background: #713f12; color: #fef08a; }}
  .loading {{ text-align: center; padding: 20px; color: #94a3b8; }}
  .error {{ color: #f87171; text-align: center; padding: 20px; }}
</style>
</head>
<body>
<div class="container">
  <h1>🌐 Información de IP</h1>
  <div class="search">
    <input id="ipInput" type="text" placeholder="Escribe una IP (ej: 8.8.8.8)" value="{ip_visitante}">
    <button onclick="consultar()">Buscar</button>
  </div>
  <div id="resultado"></div>
</div>

<script>
async function consultar() {{
  const ip = document.getElementById('ipInput').value.trim();
  if (!ip) return;
  const res = document.getElementById('resultado');
  res.innerHTML = '<div class="loading">Cargando...</div>';

  try {{
    const r = await fetch('/info/' + encodeURIComponent(ip));
    const data = await r.json();
    const geo = data.geolocalizacion_y_red || {{}};
    const seg = data.inteligencia_de_seguridad || {{}};

    if (geo.error) {{
      res.innerHTML = '<div class="error">Error: ' + geo.error + '</div>';
      return;
    }}

    let html = '';

    // Ubicación
    html += '<div class="card"><h2>📍 Ubicación</h2>';
    html += row('IP', geo.query || ip);
    html += row('Continente', geo.continent);
    html += row('País', (geo.country || '') + ' (' + (geo.countryCode || '') + ')');
    html += row('Región', geo.regionName);
    html += row('Ciudad', geo.city);
    html += row('Código postal', geo.zip);
    html += row('Coordenadas', geo.lat + ', ' + geo.lon);
    html += row('Zona horaria', geo.timezone);
    html += row('Moneda', geo.currency);
    html += '</div>';

    // Red
    html += '<div class="card"><h2>🛰️ Red</h2>';
    html += row('ISP', geo.isp);
    html += row('Organización', geo.org);
    html += row('ASN', geo.as);
    html += row('Nombre ASN', geo.asname);
    html += row('DNS inverso', geo.reverse || '—');
    html += '</div>';

    // Seguridad
    html += '<div class="card"><h2>🔒 Seguridad</h2><div style="padding:10px 0">';
    html += badge('VPN', seg.is_vpn);
    html += badge('Proxy', seg.is_proxy);
    html += badge('Tor', seg.is_tor);
    html += badge('Datacenter', seg.is_datacenter);
    html += badge('Móvil', seg.is_mobile);
    html += badge('Crawler', seg.is_crawler);
    html += badge('Abuser', seg.is_abuser);
    html += '</div></div>';

    // Datos extra
    if (seg.asn) {{
      html += '<div class="card"><h2>📊 Datos ASN</h2>';
      if (seg.asn.asn) html += row('ASN', seg.asn.asn);
      if (seg.asn.org) html += row('Organización', seg.asn.org);
      if (seg.asn.country) html += row('País', seg.asn.country);
      if (seg.asn.type) html += row('Tipo', seg.asn.type);
      html += '</div>';
    }}

    if (seg.company) {{
      html += '<div class="card"><h2>🏢 Compañía</h2>';
      if (seg.company.name) html += row('Nombre', seg.company.name);
      if (seg.company.type) html += row('Tipo', seg.company.type);
      if (seg.company.domain) html += row('Dominio', seg.company.domain);
      html += '</div>';
    }}

    res.innerHTML = html;
  }} catch (e) {{
    res.innerHTML = '<div class="error">Error al consultar: ' + e.message + '</div>';
  }}
}}

function row(label, value) {{
  if (value === undefined || value === null || value === '') return '';
  return '<div class="row"><span class="label">' + label + '</span><span class="value">' + value + '</span></div>';
}}

function badge(nombre, valor) {{
  const clase = valor ? 'badge-red' : 'badge-green';
  const texto = valor ? 'SÍ' : 'NO';
  return '<span class="badge ' + clase + '">' + nombre + ': ' + texto + '</span>';
}}

// Consultar automáticamente la IP del visitante al cargar
window.addEventListener('load', consultar);
</script>
</body>
</html>
    """)

@app.get("/info/{ip}")
async def get_full_info(ip: str):
    loop = asyncio.get_event_loop()
    task1 = loop.run_in_executor(None, get_ip_api_data, ip)
    task2 = loop.run_in_executor(None, get_ipapi_is_data, ip)
    r1, r2 = await asyncio.gather(task1, task2)
    return {
        "ip_consultada": ip,
        "geolocalizacion_y_red": r1,
        "inteligencia_de_seguridad": r2
    }