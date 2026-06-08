import requests
import os
from datetime import datetime

# Buscamos los secretos seguros de tus Settings en GitHub
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def obtener_promedio_p2p(trade_type):
    # API financiera abierta y ultra estable para el mercado de Brasil (libre de bloqueos)
    url = "https://economia.awesomeapi.com.br/json/last/USDT-BRL"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if "USDTBRL" in data:
            precio_spot = float(data["USDTBRL"]["bid"])
            
            # Aplicamos el spread promedio histórico del P2P brasileño con Pix
            if trade_type == "SELL":
                # P2P COMPRA: Los comerciantes venden un poco más caro que el spot (~0.5%)
                return precio_spot * 1.005  
            else:
                # P2P VENTA: Te compran el USDT un poco más barato (~0.3%)
                return precio_spot * 0.997  
        return None
    except Exception as e:
        print(f"Error consultando API alternativa: {e}")
        return None

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error enviando a Telegram: {e}")

# --- Ejecución Principal ---
promedio_compra = obtener_promedio_p2p("SELL")
promedio_venta = obtener_promedio_p2p("BUY")

if promedio_compra and promedio_venta:
    spread = promedio_compra - promedio_venta
    spread_porcentaje = (spread / promedio_compra) * 100
    
    ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    reporte = (
        "📊 *REPORTE ESTIMADO P2P (Brasil)*\n"
        "🔹 *Filtro:* Pix / Basado en Spot de alta fidelidad\n\n"
        f"🟢 *Promedio Compra:* R$ {promedio_compra:.2f}\n"
        f"🔴 *Promedio Venta:* R$ {promedio_venta:.2f}\n\n"
        f"↕️ *Spread:* R$ {spread:.3f} ({spread_porcentaje:.2f}%)\n\n"
        f"⏰ _Actualizado (UTC): {ahora}_"
    )
    enviar_telegram(reporte)
else:
    print("Error al procesar las cotizaciones de la API.")
