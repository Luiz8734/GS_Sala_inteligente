from flask import Flask, render_template, jsonify
from flask_cors import CORS
import paho.mqtt.client as mqtt
import threading

app = Flask(__name__)
CORS(app)

# ------------------- VARIÁVEIS GLOBAIS -------------------
dados_sensores = {
    "temp": 0,
    "umid": 0,
    "luz": 0,
    "ruido": 0,
    "presenca": 0
}

# ------------------- CONFIG MQTT -------------------
MQTT_BROKER = "98.92.204.86"
MQTT_PORT = 1883
MQTT_TOPIC = "fiap/sensores"

def on_connect(client, userdata, flags, rc):
    print("✅ Conectado ao MQTT com código:", rc)
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    global dados_sensores
    import json
    try:
        payload = msg.payload.decode()
        dados = json.loads(payload)
        dados_sensores.update(dados)
        print("📡 Dados recebidos:", dados_sensores)
    except Exception as e:
        print("Erro ao processar mensagem MQTT:", e)

def iniciar_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

# Iniciar MQTT em thread separada
threading.Thread(target=iniciar_mqtt, daemon=True).start()

# ------------------- ROTAS WEB -------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dados")
def dados():
    return jsonify(dados_sensores)

if __name__ == "__main__":
    print("🌍 Servidor Flask rodando em http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
