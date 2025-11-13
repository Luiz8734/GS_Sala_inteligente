🌡️💡 FiapSense Dashboard
👥 Integrantes do Grupo

Luiz Moraes Santos

[Nome do Segundo Integrante] (adicione aqui o nome completo do outro aluno)

🧠 Descrição do Projeto

FiapSense é uma solução inteligente desenvolvida para monitorar e otimizar as condições ambientais em ambientes corporativos e educacionais.
O projeto atua na detecção de temperatura, umidade, luminosidade e ruído, visando melhorar o conforto, bem-estar e produtividade das pessoas no local.

⚙️ Problema Identificado

Ambientes de trabalho e estudo sofrem frequentemente com temperaturas inadequadas, ruído excessivo e iluminação ruim, impactando diretamente na saúde, foco e desempenho.
Essas condições geralmente não são monitoradas em tempo real, dificultando ações corretivas.

💡 Solução Proposta

O FiapSense Dashboard combina sensores físicos (Arduino/ESP32) e uma aplicação web em Flask (Python).
O sistema coleta dados de temperatura, umidade, luminosidade e ruído via sensores e exibe em tempo real um dashboard moderno e intuitivo.
Além disso, alertas automáticos podem ser gerados para indicar condições fora do padrão.

🧩 Estrutura do Projeto
FiapSense/
│
├── src/
│   ├── arduino/
│   │   └── fiap_sense.ino         # Código do ESP32 com sensores
│   ├── server.py                  # Servidor Flask principal
│   ├── mqtt_client.py             # Cliente MQTT (recebe dados)
│   ├── api.py                     # Endpoints HTTP
│
├── templates/
│   └── index.html                 # Interface do dashboard
│
├── static/
│   ├── style.css                  # Estilos do dashboard
│   └── app.js                     # Lógica de atualização via JS
│
├── docs/
│   ├── WOKWI_LINK.txt             # Link da simulação
│   └── VIDEO_LINK.txt             # Link do vídeo explicativo
│
├── requirements.txt               # Dependências do Python
└── README.md                      # Documentação completa

🧰 Tecnologias Utilizadas

ESP32 / Arduino IDE – coleta dos dados via sensores.

Sensores:

DHT22 → Temperatura e Umidade

LDR → Luminosidade

KY-037 → Nível de Ruído

MQTT (Mosquitto) → Comunicação em tempo real entre ESP32 e servidor.

Flask (Python) → Backend e API HTTP.

HTML / CSS / JavaScript → Dashboard interativo.

🚀 Instruções de Uso
🖥️ 1. Clonar o Repositório
git clone https://github.com/seuusuario/fiap-sense-dashboard.git
cd fiap-sense-dashboard

🧩 2. Configurar o Ambiente Python
python -m venv venv
source venv/bin/activate   # No Windows: venv\Scripts\activate
pip install -r requirements.txt

🔌 3. Rodar o Servidor Flask
python src/server.py


Acesse em seu navegador:
👉 http://localhost:5000

🛰️ 4. Subir o Código no ESP32

Abra o arquivo src/arduino/fiap_sense.ino na Arduino IDE, selecione sua placa ESP32 e porta COM e clique em Upload.

🌐 5. Simular no Wokwi

O projeto pode ser simulado online:
📎 Abrir Simulação Wokwi

🎥 6. Vídeo Explicativo

📺 Assista ao Vídeo

⚡ Explicação Técnica
🧠 MQTT

O ESP32 publica os dados dos sensores em tópicos MQTT, por exemplo:

fiapsense/temperature

fiapsense/humidity

fiapsense/light

fiapsense/noise

O cliente MQTT (mqtt_client.py) subscreve nesses tópicos e armazena os dados recebidos em memória, repassando-os à aplicação Flask.

🌍 HTTP Endpoints

A API Flask oferece endpoints REST para o frontend:

GET /api/sensors → retorna os valores atuais de todos os sensores.

GET / → exibe o dashboard principal.

🔧 Código-Fonte Comentado
📟 fiap_sense.ino (Arduino/ESP32)
#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

// ------------------- CONFIGURAÇÕES -------------------
#define DHTPIN 4
#define DHTTYPE DHT22
#define LDRPIN 36
#define MICPIN 34

const char* ssid = "Wokwi-GUEST";
const char* password = "";
const char* mqtt_server = "broker.hivemq.com"; // Broker público
const int mqtt_port = 1883;

WiFiClient espClient;
PubSubClient client(espClient);
DHT dht(DHTPIN, DHTTYPE);

// ------------------- CONEXÃO WIFI -------------------
void setup_wifi() {
  delay(10);
  Serial.println("Conectando ao WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Conectado ao WiFi!");
}

// ------------------- PUBLICAÇÃO MQTT -------------------
void reconnect() {
  while (!client.connected()) {
    Serial.print("Conectando ao MQTT...");
    if (client.connect("FiapSenseClient")) {
      Serial.println("Conectado!");
    } else {
      Serial.print("Erro: ");
      Serial.println(client.state());
      delay(2000);
    }
  }
}

// ------------------- LOOP PRINCIPAL -------------------
void setup() {
  Serial.begin(115200);
  dht.begin();
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();

  float h = dht.readHumidity();
  float t = dht.readTemperature();
  int ldr = analogRead(LDRPIN);
  int noise = analogRead(MICPIN);

  // Envia dados via MQTT
  client.publish("fiapsense/temperature", String(t).c_str());
  client.publish("fiapsense/humidity", String(h).c_str());
  client.publish("fiapsense/light", String(ldr).c_str());
  client.publish("fiapsense/noise", String(noise).c_str());

  delay(2000); // Atualiza a cada 2 segundos
}

🧩 server.py (Flask)
from flask import Flask, render_template, jsonify
from mqtt_client import mqtt_data

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/sensors")
def sensors():
    # Retorna dados mais recentes do MQTT
    return jsonify(mqtt_data)

if __name__ == "__main__":
    app.run(debug=True)

📡 mqtt_client.py
import paho.mqtt.client as mqtt

mqtt_data = {"temperature": 0, "humidity": 0, "light": 0, "noise": 0}

def on_message(client, userdata, msg):
    topic = msg.topic.split("/")[-1]
    mqtt_data[topic] = msg.payload.decode()

client = mqtt.Client()
client.on_message = on_message
client.connect("broker.hivemq.com", 1883)
client.subscribe("fiapsense/#")
client.loop_start()

💻 index.html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>FiapSense Dashboard</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
  <h1>🌡️ FiapSense Dashboard</h1>
  <div id="dados">
    <p>Temperatura: <span id="temp">--</span> °C</p>
    <p>Umidade: <span id="umid">--</span> %</p>
    <p>Luz: <span id="luz">--</span></p>
    <p>Ruído: <span id="ruido">--</span></p>
  </div>
  <script src="{{ url_for('static', filename='app.js') }}"></script>
</body>
</html>

⚙️ app.js
async function atualizar() {
  const resp = await fetch("/api/sensors");
  const data = await resp.json();
  document.getElementById("temp").textContent = data.temperature;
  document.getElementById("umid").textContent = data.humidity;
  document.getElementById("luz").textContent = data.light;
  document.getElementById("ruido").textContent = data.noise;
}
setInterval(atualizar, 2000);

📊 Exemplo de Dashboard

(inserir aqui uma captura de tela do dashboard)