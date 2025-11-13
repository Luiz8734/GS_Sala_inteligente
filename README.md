# 🌡️💡 FiapSense — Dashboard & Dispositivo ESP32 (README completo)

> Projeto: **FiapSense** — monitor ambiental com ESP32, MQTT e dashboard web.
> Desenvolvido por alunos da FIAP como exemplo completo de IoT: dispositivo embarcado + nuvem (MQTT) + dashboard web.

---

## 🧭 Sumário

1. Visão Geral
2. Integrantes
3. Objetivos
4. Componentes de Hardware
5. Diagrama de Conexões / Mapeamento de Pinos
6. Estrutura do Projeto
7. Código do Dispositivo (ESP32) — arquivo: `esp32_fiapsense.ino` (completo e comentado)
8. Aplicação Web (Flask) — arquivos: `app.py`, `requirements.txt`, `templates/index.html`
9. Como rodar (simulação Wokwi e físico)
10. Tópicos MQTT e Payloads
11. Testes e Debug
12. Melhorias Futuras
13. Créditos e Licença

---

## 1. Visão Geral

FiapSense é um sistema de monitoramento ambiental que lê sensores (temperatura/umidade, luminosidade, ruído, distância/presença) com um ESP32, publica os dados via MQTT e exibe tudo em um dashboard web em tempo real. O dispositivo possui modos de alerta com LEDs e buzzer, e um modo "pausa" para exibir mensagens educativas.

> Este README contém: código completo do ESP32 com comentários detalhados, instruções para a aplicação Flask que consome MQTT, e passo a passo para executar no Wokwi ou em hardware real.

---

## 2. Integrantes

|     RM | Nome                |
| -----: | ------------------- |
| 562142 | Luiz Antonio Morais |
| 561997 | Nicolas Barnabe     |


# FIAPSENSE Dashboard

## 🔗 Links Importantes

* **Vídeo no YouTube:** *(adicione aqui o link do vídeo)*
* **Simulação no Wokwi:** *([link da simulação](https://wokwi.com/projects/447278705835346945))*

## 🖼️ Imagens do Projeto

### Wokwi

*(<img width="777" height="551" alt="image" src="https://github.com/user-attachments/assets/9d764a75-b67c-4bdb-8e98-c58780d8ffbd" />
)*

### Aplicação Web

*(adicione aqui imagens das telas da aplicação / dashboard)*

---

## 3. Objetivos

* Coletar dados ambientais e de presença (DHT22, LDR, microfone, sensor ultrassônico).
* Publicar leituras periodicamente via MQTT.
* Exibir estado em LCD I2C e fornecer feedback com LEDs/buzzer.
* Dashboard Flask para visualização em tempo real e endpoints REST.
* Suportar simulação no Wokwi para desenvolvimento sem hardware.

---

## 4. Componentes de Hardware

* ESP32 (Dev Module)
* Sensor DHT22 (temperatura e umidade)
* LDR (sensor de luminosidade) + resistor pull-down / divisor de tensão
* Microfone (por exemplo KY-037) — entrada analógica
* Sensor ultrassônico (HC-SR04) — TRIG / ECHO (ou usar biblioteca NewPing)
* Display LCD I2C 16x2 (endereço geralmente 0x27)
* Buzzer (piezo)
* LEDs (3 cores ou 3 LEDs separados)
* Botão (INPUT_PULLUP) para entrar/sair do modo pausa
* Potenciômetro (opcional) — p.ex. para ajustar brilho / threshold
* Fios, protoboard

**Observação sobre tensão:** ESP32 usa 3.3V. Certifique-se de adaptar divisores/resistores para entradas analógicas e de não alimentar sensores de 5V diretamente nos pinos do ESP32.

---

## 5. Diagrama de Conexões / Mapeamento de Pinos

| Componente         |    Pino ESP32 | Função                     |
| ------------------ | ------------: | -------------------------- |
| DHT22              |        GPIO 4 | Data (1-wire)              |
| LDR (divisor)      | GPIO 34 (ADC) | Leitura luminosidade       |
| Microfone (analog) | GPIO 33 (ADC) | Leitura ruído              |
| Botão              |       GPIO 27 | Entrada com `INPUT_PULLUP` |
| Buzzer             |       GPIO 26 | Saída PWM / tone           |
| LED Vermelho       |       GPIO 17 | Saída digital              |
| LED Verde          |       GPIO 18 | Saída digital              |
| LED Azul           |        GPIO 5 | Saída digital              |
| Ultrassônico TRIG  |       GPIO 32 | Trigger                    |
| Ultrassônico ECHO  |       GPIO 35 | Echo (entrada)             |
| LCD I2C SDA        |       GPIO 21 | I2C SDA                    |
| LCD I2C SCL        |       GPIO 22 | I2C SCL                    |

---

## 6. Estrutura do Projeto

```
FiapSense/
├── README.md  (este arquivo)
├── esp32/                     # Firmware do ESP32
│   └── esp32_fiapsense.ino   # Código comentado completo
├── backend/                   # Dashboard Flask
│   ├── app.py
│   ├── requirements.txt
│   └── templates/
│       └── index.html
└── docs/                      # Imagens, esquemas, capturas
    └── wokwi_screenshot.png
```

---

## 7. Código do Dispositivo (ESP32)

**Arquivo:** `esp32_fiapsense.ino`

> Abaixo está o código completo que serve como base. Ele reúne leitura de sensores, lógica de alerta, modo pausa, publicação MQTT e exibição LCD — tudo com comentários explicativos.

```cpp
/*
  esp32_fiapsense.ino
  Projeto: FiapSense - ESP32 + Sensores + MQTT + LCD I2C
  Autor: Equipe FIAP (adaptado)
  Observações: Ajuste os pinos conforme seu hardware.
*/

#include <WiFi.h>
#include <PubSubClient.h>
#include <LiquidCrystal_I2C.h>
#include <DHT.h>
#include <NewPing.h>

// ---------------- CONFIG WIFI & MQTT ----------------
const char* ssid = "Wokwi-GUEST";   // troque pela sua rede
const char* password = "";          // senha da rede
const char* mqtt_server = "98.92.204.86"; // broker MQTT
const int mqtt_port = 1883;
const char* mqtt_user = "";         // se houver, coloque
const char* mqtt_pass = "";

WiFiClient espClient;
PubSubClient client(espClient);
unsigned long lastMQTTSend = 0;      // controle de envio MQTT

// ---------------- PINOS ----------------
#define DHTPIN 4
#define DHTTYPE DHT22
#define LDR_PIN 34
#define MICROFONE_PIN 33
#define BOTAO_PIN 27
#define BUZZER_PIN 26
#define LED_VERMELHO 17
#define LED_VERDE 18
#define LED_AZUL 5
#define ULTRASONIC_TRIG_PIN 32
#define ULTRASONIC_ECHO_PIN 35
#define MAX_DISTANCE 400
#define US_ROUNDTRIP_CM 58

// ---------------- OBJETOS ----------------
LiquidCrystal_I2C lcd(0x27, 16, 2); // endereço I2C comum 0x27
DHT dht(DHTPIN, DHTTYPE);
NewPing sonar(ULTRASONIC_TRIG_PIN, ULTRASONIC_ECHO_PIN, MAX_DISTANCE);

// ---------------- VARIÁVEIS ----------------
bool modoPausa = false;               // flag modo pausa
bool ultimoEstadoBotao = HIGH;        // para debounce do botão
unsigned long lastButtonPress = 0;    // timestamp do último press
unsigned long pauseStartTime = 0;
unsigned long lastPauseMessageChange = 0;
unsigned long pauseDuration = 30000;  // duração automática do modo pausa (30s)

#define NUM_LUZ_LEITURAS 10
int luzBuffer[NUM_LUZ_LEITURAS] = {0};
int luzIndex = 0;

int ruidoBuffer[10] = {0};
int ruidoIndex = 0;

const char* mensagensPausa[] = {
  "Respire fundo...",
  "Alongue-se...",
  "Olhe longe...",
  "Hidrate-se!"
};
const int numMensagensPausa = sizeof(mensagensPausa) / sizeof(mensagensPausa[0]);
int pausaMessageIndex = 0;

// ---------------- FUNÇÕES AUXILIARES ----------------

// Leitura média suave do LDR
int lerLuz() {
  int leitura = analogRead(LDR_PIN);
  // No ESP32, ADC é 0..4095 por padrão (12-bit)
  leitura = 4095 - leitura; // inverter se seu divisor for assim
  luzBuffer[luzIndex] = leitura;
  luzIndex = (luzIndex + 1) % NUM_LUZ_LEITURAS;
  long soma = 0;
  for (int i = 0; i < NUM_LUZ_LEITURAS; i++) soma += luzBuffer[i];
  int media = soma / NUM_LUZ_LEITURAS;
  return map(media, 0, 4095, 0, 100); // retorna 0..100 (%)
}

// Media simples para evitar picos no ruído
int calcularMediaRuido(int val) {
  ruidoBuffer[ruidoIndex] = val;
  ruidoIndex = (ruidoIndex + 1) % 10;
  int soma = 0;
  for (int i = 0; i < 10; i++) soma += ruidoBuffer[i];
  return soma / 10;
}

// Leitura de distância com NewPing
int lerDistanciaUltrassonica() {
  unsigned int uS = sonar.ping_median(5); // usa median para suavizar leituras
  int dist = uS / US_ROUNDTRIP_CM;
  if (dist == 0) dist = MAX_DISTANCE; // se sem retorno
  return dist;
}

void desligarLeds() {
  digitalWrite(LED_VERMELHO, LOW);
  digitalWrite(LED_VERDE, LOW);
  digitalWrite(LED_AZUL, LOW);
}

void acenderLed(int led) {
  desligarLeds();
  digitalWrite(led, HIGH);
}

// ---- Funções de pausa ----
void entrarModoPausa() {
  modoPausa = true;
  pauseStartTime = millis();
  pausaMessageIndex = 0;
  lastPauseMessageChange = millis();
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("PAUSA ATIVA");
  lcd.setCursor(0, 1);
  lcd.print(mensagensPausa[pausaMessageIndex]);
  tone(BUZZER_PIN, 1200, 100);
  acenderLed(LED_AZUL);
}

void sairModoPausa() {
  modoPausa = false;
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Pausa Encerrada");
  tone(BUZZER_PIN, 1300, 100);
  desligarLeds();
  delay(800);
  lcd.clear();
}

void atualizarDisplayPausa() {
  if (millis() - lastPauseMessageChange > 5000) {
    pausaMessageIndex = (pausaMessageIndex + 1) % numMensagensPausa;
    lcd.setCursor(0, 1);
    lcd.print("                "); // limpa linha
    lcd.setCursor(0, 1);
    lcd.print(mensagensPausa[pausaMessageIndex]);
    lastPauseMessageChange = millis();
    tone(BUZZER_PIN, 1000, 60);
  }
}

// ---------------- WIFI + MQTT ----------------
void conectarWiFi() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Conectando WiFi");
  Serial.println("🔌 Conectando ao Wi-Fi...");

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  int tentativas = 0;
  while (WiFi.status() != WL_CONNECTED && tentativas < 30) {
    delay(500);
    Serial.print(".");
    lcd.setCursor(0, 1);
    lcd.print("Tentando...");
    tentativas++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    lcd.clear();
    lcd.print("WiFi conectado!");
    lcd.setCursor(0, 1);
    lcd.print(WiFi.localIP().toString());
    Serial.println("\n✅ Wi-Fi conectado!");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
  } else {
    lcd.clear();
    lcd.print("Falha WiFi!");
    Serial.println("\n❌ Falha ao conectar ao Wi-Fi!");
  }
}

void reconnectMQTT() {
  while (!client.connected()) {
    Serial.print("Conectando MQTT...");
    // client.connect( ID, user, pass );
    if (client.connect("ESP32-FIAP", mqtt_user, mqtt_pass)) {
      Serial.println("✅ Conectado ao servidor MQTT!");
      client.publish("fiap/status", "ESP32 conectado com sucesso!");
      // se desejar receber comandos, usa: client.subscribe("fiap/cmd");
    } else {
      Serial.print("Falha, rc=");
      Serial.print(client.state());
      Serial.println(" tentando em 3s...");
      delay(3000);
    }
  }
}

// ---------------- SETUP ----------------
void setup() {
  Serial.begin(115200);
  lcd.init();
  lcd.backlight();
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("PROJETO AMBIENTE");
  lcd.setCursor(0, 1);
  lcd.print("SEGURO - FIAP");
  delay(2500);
  lcd.clear();
  lcd.print("Iniciando...");
  dht.begin();

  // Configuração de pinos
  pinMode(LDR_PIN, INPUT);
  pinMode(MICROFONE_PIN, INPUT);
  pinMode(BOTAO_PIN, INPUT_PULLUP);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_VERMELHO, OUTPUT);
  pinMode(LED_VERDE, OUTPUT);
  pinMode(LED_AZUL, OUTPUT);

  desligarLeds();

  conectarWiFi();
  client.setServer(mqtt_server, mqtt_port);

  lcd.clear();
}

// ---------------- LOOP ----------------
void loop() {
  // Garante conexão WiFi
  if (WiFi.status() != WL_CONNECTED) {
    conectarWiFi();
  }

  // Garante conexão MQTT
  if (!client.connected()) reconnectMQTT();
  client.loop();

  // Leitura do botão com debounce simples
  bool leituraBotao = digitalRead(BOTAO_PIN);
  if (leituraBotao == LOW && ultimoEstadoBotao == HIGH && millis() - lastButtonPress > 400) {
    lastButtonPress = millis();
    if (!modoPausa) entrarModoPausa();
    else sairModoPausa();
  }
  ultimoEstadoBotao = leituraBotao;

  if (!modoPausa) {
    // Leitura sensores
    float temp = dht.readTemperature();
    float umid = dht.readHumidity();
    if (isnan(temp)) temp = 0; // tratamento simples
    if (isnan(umid)) umid = 0;

    int luz = lerLuz();
    int ruidoRaw = analogRead(MICROFONE_PIN);
    int ruido = calcularMediaRuido(ruidoRaw);
    int dist = lerDistanciaUltrassonica();
    bool presenca = dist < 150; // threshold de presença

    bool alertaCalor = temp > 30;
    bool alertaRuido = ruido > 1900; // ajuste conforme seu sensor
    bool alertaEscuro = luz < 30;

    int numAlertas = alertaCalor + alertaRuido + alertaEscuro;

    // Log serial em uma linha compacta
    Serial.print("Temp:"); Serial.print(temp, 1); Serial.print("C ");
    Serial.print("Umid:"); Serial.print(umid, 0); Serial.print("% ");
    Serial.print("Luz:"); Serial.print(luz); Serial.print("% ");
    Serial.print("Ruido:"); Serial.print(ruido); Serial.print(" ");
    Serial.print("Dist:"); Serial.print(dist); Serial.print("cm ");
    Serial.print("Presenca:"); Serial.println(presenca ? "SIM" : "NAO");

    // Atualiza LCD com lógica simples de prioridades
    lcd.clear();
    if (!presenca) {
      lcd.setCursor(0, 0);
      lcd.print("Sem Presenca");
      lcd.setCursor(0, 1);
      lcd.print("Dist: "); lcd.print(dist); lcd.print("cm");
      acenderLed(LED_AZUL);
    } else if (numAlertas == 0) {
      lcd.setCursor(0, 0);
      lcd.print("Tudo OK :)");
      lcd.setCursor(0, 1);
      lcd.print("T:"); lcd.print(temp, 1); lcd.print("C L:"); lcd.print(luz);
      acenderLed(LED_VERDE);
    } else {
      lcd.setCursor(0, 0);
      if (alertaCalor) lcd.print("Calor ");
      if (alertaRuido) lcd.print("Ruido ");
      if (alertaEscuro) lcd.print("Escuro");
      lcd.setCursor(0, 1);
      lcd.print("T:"); lcd.print(temp, 0); lcd.print("C L:"); lcd.print(luz); lcd.print("%");
      // sons diferenciados para alertas
      if (alertaCalor) tone(BUZZER_PIN, 900, 100);
      if (alertaRuido) tone(BUZZER_PIN, 1000, 100);
      if (alertaEscuro) tone(BUZZER_PIN, 800, 100);
      acenderLed(numAlertas == 1 ? LED_AZUL : LED_VERMELHO);
    }

    // --- Publicação MQTT a cada 5 segundos ---
    if (millis() - lastMQTTSend > 5000) {
      char payload[256];
      snprintf(payload, sizeof(payload),
               "{\"temp\":%.1f,\"umid\":%.1f,\"luz\":%d,\"ruido\":%d,\"presenca\":%d}",
               temp, umid, luz, ruido, presenca);
      client.publish("fiap/sensores", payload);
      lastMQTTSend = millis();
    }

    delay(1200); // ajuste de taxa de amostragem
  } else {
    // Modo pausa — exibe mensagens tranquilizadoras
    atualizarDisplayPausa();
    if (millis() - pauseStartTime > pauseDuration) sairModoPausa();
  }
}
```

**Observações e ajustes**

* Ajuste `alertaRuido` dependendo do microfone (valor analógico pode variar muito). Use `Serial.println(ruidoRaw)` para calibrar.
* `lerLuz()` assume divisor do LDR com referência 3.3V e leitura invertida; adapte se necessário.
* `map(..., 0, 4095, 0, 100)` transforma leitura ADC para porcentagem.
* `tone()` é usado para o buzzer; em alguns firmwares/tars, pode haver limitações no PWM.

---

## 8. Aplicação Web (Flask)

**Estrutura mínima:**

`backend/app.py` — servidor Flask que se conecta ao broker MQTT e exibe dados em tempo real.

`backend/requirements.txt` — dependências Python.

`backend/templates/index.html` — interface simples (tema escuro) que mostra valores atuais e gráfico.

### `requirements.txt`

```
flask
paho-mqtt
matplotlib

# opcional
flask_socketio
```

### `app.py` (exemplo mínimo)

```python
# app.py
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
    print(" Conectado ao MQTT com código:", rc)
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    global dados_sensores
    import json
    try:
        payload = msg.payload.decode()
        dados = json.loads(payload)
        dados_sensores.update(dados)
        print(" Dados recebidos:", dados_sensores)
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
    print(" Servidor Flask rodando em http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)

```

### `templates/index.html` (esqueleto)

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>LNK-TECH | FiapSense Dashboard</title>
  <!-- Google Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
  <!-- CSS Externo -->
  <link rel="stylesheet" href="/static/style.css">
  <!-- Chart.js -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
  <header class="header">
    <div class="container">
      <h1>🌿 FiapSense by LNK-TECH</h1>
      <p>Monitoramento inteligente para ambientes corporativos e educacionais mais saudáveis e produtivos.</p>
    </div>
  </header>
  <main class="container">
    <!-- SEÇÃO DE SENSORES -->
    <section class="sensor-data">
      <div class="card">
        <div class="card-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 4v10.54a4 4 0 1 1-4 0V4a2 2 0 0 1 4 0Z"/></svg>
        </div>
        <h3>Temperatura</h3>
        <p id="temp">-- °C</p>
      </div>
      <div class="card">
        <div class="card-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22a7 7 0 0 0 7-7c0-2-1-3.9-3-5.5s-3.5-4-4-6.5c-.5 2.5-2 4.9-4 6.5C6 11.1 5 13 5 15a7 7 0 0 0 7 7z"/></svg>
        </div>
        <h3>Umidade</h3>
        <p id="umid">-- %</p>
      </div>
      <div class="card">
        <div class="card-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>
        </div>
        <h3>Luminosidade</h3>
        <p id="luz">-- lux</p>
      </div>
      <div class="card">
        <div class="card-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/></svg>
        </div>
        <h3>Ruído</h3>
        <p id="ruido">-- dB</p>
      </div>
      <div class="card">
        <div class="card-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-2.17A2 2 0 0 1 14.24 5l-2.48-2.48A2 2 0 0 0 10.17 2H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2Z"/><circle cx="12" cy="12" r="3"/></svg>
        </div>
        <h3>Presença</h3>
        <p id="presenca">--</p>
      </div>
    </section>

    <!-- GRÁFICO COM TEMPERATURA E RUÍDO (substituído por 2 gráficos separados abaixo, mantendo estrutura original) -->
    <section class="chart-container">
      <h2>Monitoramento em Tempo Real</h2>
      <!-- Gráfico 1: Temperatura + Umidade -->
      <canvas id="graficoTempUmid"></canvas>
      <!-- Gráfico 2: Ruído (separado) -->
      <canvas id="graficoRuido" style="margin-top:20px;"></canvas>
      <div id="alertas" class="alertas"></div>
    </section>

    <!-- SEÇÃO: O PROBLEMA -->
    <section class="info-section">
      <h2>🚨 O Desafio do Conforto Ambiental</h2>
      <p>
        Fatores como temperatura inadequada, iluminação deficiente e ruído excessivo impactam diretamente o bem-estar, a produtividade e a capacidade de concentração em ambientes de trabalho e estudo.
      </p>
    </section>

    <!-- SEÇÃO: A SOLUÇÃO -->
    <section class="info-section">
      <h2>💡 Nossa Solução: FiapSense</h2>
      <p>
        O FiapSense promove ambientes mais confortáveis e saudáveis. Ao equilibrar temperatura, umidade e luminosidade, criamos as condições ideais para o aprendizado e a colaboração, aumentando a satisfação e o desempenho.
      </p>
    </section>

    <!-- SEÇÃO: AMBIENTE CORPORATIVO -->
    <section class="info-section">
      <h2>🏢 Ambiente Corporativo</h2>
      <div class="benefits-grid">
        <div class="benefit-card">
          <div class="benefit-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
          </div>
          <h3>Produtividade</h3>
          <p>Ambientes otimizados aumentam a produtividade dos colaboradores em até 15%, reduzindo fadiga e melhorando o foco.</p>
        </div>
        <div class="benefit-card">
          <div class="benefit-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
            </svg>
          </div>
          <h3>Eficiência Energética</h3>
          <p>Controle inteligente de climatização e iluminação reduz custos operacionais e o impacto ambiental.</p>
        </div>
        <div class="benefit-card">
          <div class="benefit-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M9 12l2 2 4-4"/><path d="M21 12c-1 0-3-1-3-3s2-3 3-3 3 1 3 3-2 3-3 3"/><path d="M3 12c1 0 3-1 3-3s-2-3-3-3-3 1-3 3 2 3 3 3"/><path d="M12 3c0 1-1 3-3 3s-3-2-3-3 1-3 3-3 3 2 3 3"/><path d="M12 21c0-1-1-3-3-3s-3 2-3 3 1 3 3 3 3-2 3-3"/>
            </svg>
          </div>
          <h3>Bem-estar</h3>
          <p>Monitoramento contínuo garante condições ideais de trabalho, reduzindo afastamentos e melhorando a satisfação.</p>
        </div>
      </div>
    </section>

    <!-- SEÇÃO: AMBIENTE ESCOLAR -->
    <section class="info-section">
      <h2>🎓 Ambiente Escolar</h2>
      <div class="benefits-grid">
        <div class="benefit-card">
          <div class="benefit-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/><path d="M9 10h6"/><path d="M9 14h6"/>
            </svg>
          </div>
          <h3>Aprendizado Otimizado</h3>
          <p>Condições ambientais ideais melhoram a concentração e o desempenho acadêmico dos estudantes.</p>
        </div>
        <div class="benefit-card">
          <div class="benefit-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
          </div>
          <h3>Segurança</h3>
          <p>Sensores de presença e monitoramento garantem segurança e controle de acesso em áreas escolares.</p>
        </div>
        <div class="benefit-card">
          <div class="benefit-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
          </div>
          <h3>Conforto Térmico</h3>
          <p>Temperatura e umidade controladas criam ambientes mais agradáveis, facilitando o aprendizado.</p>
        </div>
      </div>
    </section>

    <!-- SEÇÃO: APLICAÇÕES E BENEFÍCIOS -->
    <section class="info-section">
      <h2>🚀 Aplicações e Benefícios</h2>
      <div class="applications-grid">
        <div class="application-item">
          <div class="application-image">
            <svg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><path d="M9 9h6v6H9z"/>
            </svg>
          </div>
          <h3>Salas de Reunião</h3>
          <p>Otimização automática de temperatura e iluminação para reuniões mais produtivas e confortáveis.</p>
        </div>
        <div class="application-item">
          <div class="application-image">
            <svg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/>
            </svg>
          </div>
          <h3>Bibliotecas</h3>
          <p>Ambientes silenciosos e bem iluminados que favorecem a leitura e o estudo concentrado.</p>
        </div>
        <div class="application-item">
          <div class="application-image">
            <svg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/>
            </svg>
          </div>
          <h3>Laboratórios</h3>
          <p>Monitoramento preciso de condições ambientais críticas para experimentos e pesquisas.</p>
        </div>
        <div class="application-item">
          <div class="application-image">
            <svg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
            </svg>
          </div>
          <h3>Escritórios</h3>
          <p>Controle inteligente que adapta o ambiente às necessidades dos colaboradores ao longo do dia.</p>
        </div>
      </div>
    </section>
  </main>
  <footer class="footer">
    <p>© 2025 LNK-TECH | Projeto FiapSense - Inovando ambientes inteligentes.</p>
  </footer>
  <script>
    // inicializa gráficos separados: Temperatura+Umidade e Ruído
    const ctxTempUmid = document.getElementById("graficoTempUmid").getContext("2d");
    const graficoTempUmid = new Chart(ctxTempUmid, {
      type: "line",
      data: {
        labels: [],
        datasets: [
          {
            label: "Temperatura (°C)",
            data: [],
            borderColor: "#00aaff",
            backgroundColor: "rgba(0, 170, 255, 0.1)",
            borderWidth: 2,
            fill: true,
            tension: 0.4,
            yAxisID: 'y'
          },
          {
            label: "Umidade (%)",
            data: [],
            borderColor: "#00ffaa",
            backgroundColor: "rgba(0, 255, 170, 0.08)",
            borderWidth: 2,
            fill: true,
            tension: 0.4,
            yAxisID: 'y'
          }
        ]
      },
      options: {
        responsive: true,
        interaction: {
          mode: 'index',
          intersect: false,
        },
        scales: {
          y: { 
            type: 'linear',
            display: true,
            position: 'left',
            beginAtZero: false,
            title: {
              display: true,
              text: 'Temperatura / Umidade',
              color: '#00aaff'
            },
            grid: {
              color: 'rgba(255, 255, 255, 0.1)'
            },
            ticks: {
              color: '#00aaff'
            }
          },
          x: {
            grid: {
              color: 'rgba(255, 255, 255, 0.1)'
            },
            ticks: {
              color: '#8b949e'
            }
          }
        },
        plugins: {
          legend: {
            display: true,
            labels: {
              color: '#e6edf3'
            }
          },
          tooltip: {
            backgroundColor: 'rgba(13, 17, 23, 0.9)',
            titleColor: '#e6edf3',
            bodyColor: '#e6edf3',
            borderColor: '#00aaff',
            borderWidth: 1
          }
        }
      }
    });

    const ctxRuido = document.getElementById("graficoRuido").getContext("2d");
    const graficoRuido = new Chart(ctxRuido, {
      type: "line",
      data: {
        labels: [],
        datasets: [
          {
            label: "Ruído (dB)",
            data: [],
            borderColor: "#ff6b6b",
            backgroundColor: "rgba(255, 107, 107, 0.1)",
            borderWidth: 2,
            fill: true,
            tension: 0.4,
            yAxisID: 'y1'
          }
        ]
      },
      options: {
        responsive: true,
        interaction: {
          mode: 'index',
          intersect: false,
        },
        scales: {
          y1: {
            type: 'linear',
            display: true,
            position: 'left',
            beginAtZero: false,
            title: {
              display: true,
              text: 'Ruído (dB)',
              color: '#ff6b6b'
            },
            grid: {
              color: 'rgba(255, 255, 255, 0.1)'
            },
            ticks: {
              color: '#ff6b6b'
            }
          },
          x: {
            grid: {
              color: 'rgba(255, 255, 255, 0.1)'
            },
            ticks: {
              color: '#8b949e'
            }
          }
        },
        plugins: {
          legend: {
            display: true,
            labels: {
              color: '#e6edf3'
            }
          },
          tooltip: {
            backgroundColor: 'rgba(13, 17, 23, 0.9)',
            titleColor: '#e6edf3',
            bodyColor: '#e6edf3',
            borderColor: '#ff6b6b',
            borderWidth: 1
          }
        }
      }
    });

    async function atualizar() {
      try {
        const res = await fetch("/dados");
        const dados = await res.json();

        document.getElementById("temp").innerText = `${dados.temp.toFixed(1)} °C`;
        document.getElementById("umid").innerText = `${dados.umid.toFixed(1)} %`;
        document.getElementById("luz").innerText = `${dados.luz.toFixed(0)} lux`;
        document.getElementById("ruido").innerText = `${dados.ruido.toFixed(1)} dB`;
        document.getElementById("presenca").innerText = dados.presenca ? "Detectada" : "Ausente";

        const now = new Date();
        const timeLabel = `${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
        
        // Atualiza Temperatura + Umidade
        graficoTempUmid.data.labels.push(timeLabel);
        graficoTempUmid.data.datasets[0].data.push(dados.temp);
        graficoTempUmid.data.datasets[1].data.push(dados.umid);

        if (graficoTempUmid.data.labels.length > 20) {
          graficoTempUmid.data.labels.shift();
          graficoTempUmid.data.datasets[0].data.shift();
          graficoTempUmid.data.datasets[1].data.shift();
        }
        graficoTempUmid.update();

        // Atualiza Ruído
        graficoRuido.data.labels.push(timeLabel);
        graficoRuido.data.datasets[0].data.push(dados.ruido);

        if (graficoRuido.data.labels.length > 20) {
          graficoRuido.data.labels.shift();
          graficoRuido.data.datasets[0].data.shift();
        }
        graficoRuido.update();

        const alertas = [];
        if (dados.temp > 28) alertas.push("Alerta: Ambiente muito quente!");
        if (dados.temp < 18) alertas.push("Alerta: Ambiente muito frio!");
        if (dados.luz < 35) alertas.push("Alerta: Iluminação fraca!");
        if (dados.ruido > 1900) alertas.push("Alerta: Ruído excessivo detectado!");
        document.getElementById("alertas").innerText = alertas.join(" | ");

      } catch (error) {
        console.error("Erro ao buscar dados:", error);
        document.getElementById("alertas").innerText = "Erro de conexão com o servidor.";
      } finally {
        setTimeout(atualizar, 2000);
      }
    }
    
    document.addEventListener("DOMContentLoaded", atualizar);
  </script>
</body>
</html>

```

---

## 9. Como rodar

### 9.1. Simulação no Wokwi

1. Acesse: **Wokwi** e crie um projeto ESP32.
2. Cole o código `esp32_fiapsense.ino` no sketch.
3. Conecte os componentes virtuais (DHT22, LDR, microfone, LCD I2C, HC-SR04) nos pinos indicados.
4. Start Simulation. Abra o Serial Monitor para depurar.

> **Dica:** No Wokwi você pode alimentar sensores virtuais via sliders e ver os logs no terminal.

### 9.2. Em hardware real (ESP32)

1. Conecte os sensores conforme tabela de pinos.
2. Abra o Arduino IDE / PlatformIO, selecione placa ESP32.
3. Instale bibliotecas: `DHT sensor library`, `LiquidCrystal_I2C`, `PubSubClient`, `NewPing`.
4. Ajuste `ssid`, `password` e `mqtt_server` no código.
5. Compile e faça upload.
6. Rode o backend Flask: `pip install -r requirements.txt` → `python app.py`.
7. Acesse `http://localhost:5000`.

---

## 10. Tópicos MQTT e Payloads

* **Broker:** `98.92.204.86:1883` (ajuste se necessário)
* **Tópico de publicação:** `fiap/sensores`
* **Exemplo de payload publicado (JSON):**

```json
{"temp":23.4,"umid":45.0,"luz":78,"ruido":1200,"presenca":1}
```

* **Tópico de status:** `fiap/status`

---

## 11. Testes e Debug

* Use o Serial Monitor para verificar leituras brutas (`Serial.println(ruidoRaw)`, `Serial.println(analogRead(LDR_PIN))`).
* Para calibrar ruído, observe valores máximos/mínimos em silêncio/ruído.
* Se o LCD não inicializar, verifique endereço I2C (tente 0x27 e 0x3F).
* Em caso de problemas com o broker, teste com um broker público (p.ex. `test.mosquitto.org`) antes de apontar para um broker privado.

---

## 12. Melhorias Futuras

* Autenticação TLS no MQTT (MQTT sobre TLS / port 8883) para segurança
* Histórico persistente (BD SQLite ou InfluxDB)
* Visualizações mais ricas com Chart.js e WebSocket (em vez de polling)
* Mobile-first layout e notificações push
* Múltiplos dispositivos e registro por ID de dispositivo

---

## 13. Créditos e Licença

Projeto educacional — FIAP

**Autores:** Equipe FiapSense (nomes na seção Integrantes)

Licença: MIT (sinta-se livre para adaptar para seu repositório acadêmico)

---

<!-- Espaço para imagens: adicione prints do Wokwi, fotos do dispositivo e capturas do dashboard abaixo -->

![Wokwi screenshot](docs/wokwi_screenshot.png)

<!-- Fim do README -->
