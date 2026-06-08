import requests
import os
from datetime import datetime

# Buscamos correctamente los secretos por el nombre de la etiqueta guardada en Settings
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def obtener_promedio_p2p(trade_type):
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/p2p/search"
    payload = {
        "asset": "USDT",
        "fiat": "BRL",
        "merchantCheck": True,
        "page": 1,
        "rows": 5,
        "payTypes": ["Pix"],
        "publisherType": None,
        "tradeType": trade_type
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        if data.get("code") == "000000" and data.get("data"):
            precios = [float(anuncio["adv"]["price"]) for anuncio in data["data"]]
            return sum(precios) / len(precios)
        return None
    except Exception as e:
        print(f"Error consultando Binance: {e}")
        return None

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error enviando a Telegram: {e}")

# Ejecución principal
promedio_compra = obtener_promedio_p2p("SELL")
promedio_venta = obtener_promedio_p2p("BUY")

if promedio_compra and promedio_venta:
    spread = promedio_compra - promedio_venta
    spread_porcentaje = (spread / promedio_compra) * 100
    
    ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    reporte = (
        "📊 *REPORTE REAL BINANCE P2P*\n"
        "🔹 *Filtro:* Pix / Verificados\n\n"
        f"🟢 *Promedio Compra:* R$ {promedio_compra:.2f}\n"
        f"🔴 *Promedio Venta:* R$ {promedio_venta:.2f}\n\n"
        f"↕️ *Spread:* R$ {spread:.3f} ({spread_porcentaje:.2f}%)\n\n"
        f"⏰ _Actualizado (UTC): {ahora}_"
    )
    enviar_telegram(reporte)
else:
    print("No se pudieron obtener precios reales.")
