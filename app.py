from fastapi import FastAPI, HTTPException
import urllib.request
import json
import asyncio

app = FastAPI()

# --- Función para obtener datos de ip-api.com ---
def get_ip_api_data(ip: str):
    # Pedimos TODOS los campos posibles según su documentación
    url = (
        f"http://ip-api.com/json/{ip}?fields="
        "status,message,continent,continentCode,country,countryCode,"
        "region,regionName,city,district,zip,lat,lon,timezone,offset,"
        "currency,isp,org,as,asname,reverse,mobile,proxy,hosting,query"
    )
    try:
        with urllib.request.urlopen(url, timeout=8) as r:
            data = json.loads(r.read().decode())
        if data.get("status") == "success":
            # Limpiamos el campo status para no mostrarlo
            data.pop("status", None)
            return data
        return {"ip-api.com": {"error": data.get("message", "Fallo la consulta")}}
    except Exception as e:
        return {"ip-api.com": {"error": str(e)}}

# --- Función para obtener datos de ipapi.is ---
def get_ipapi_is_data(ip: str):
    url = f"https://api.ipapi.is/?q={ip}"
    try:
        with urllib.request.urlopen(url, timeout=8) as r:
            data = json.loads(r.read().decode())
        return data
    except Exception as e:
        return {"ipapi.is": {"error": str(e)}}

# --- Endpoint principal que combina todo ---
@app.get("/info/{ip}")
async def get_full_info(ip: str):
    # Ejecutamos ambas consultas en paralelo para mayor velocidad
    loop = asyncio.get_event_loop()
    task1 = loop.run_in_executor(None, get_ip_api_data, ip)
    task2 = loop.run_in_executor(None, get_ipapi_is_data, ip)
    
    result1, result2 = await asyncio.gather(task1, task2)
    
    # Combinamos los resultados en un solo objeto
    respuesta_final = {
        "ip_consultada": ip,
        "geolocalizacion_y_red": result1,
        "inteligencia_de_seguridad": result2
    }
    return respuesta_final

@app.get("/")
def inicio():
    return {
        "mensaje": "API de Inteligencia de IP",
        "uso": "Añade /info/{ip} a la URL para consultar. Ej: /info/8.8.8.8"
    }