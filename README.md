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
from flask import Flask, render_template, jsonify, send_file
import paho.mqtt.client as mqtt
import threading
import time
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = Flask(__name__)

# dados globais (thread-safe simples para demo)
dados = {"temp":0.0, "umid":0.0, "luz":0, "ruido":0, "presenca":0, "last":None}

MQTT_BROKER = '98.92.204.86'
MQTT_PORT = 1883
TOPICO = 'fiap/sensores'

# Callback MQTT
def on_connect(client, userdata, flags, rc):
    print('Conectado MQTT', rc)
    client.subscribe(TOPICO)

def on_message(client, userdata, msg):
    try:
        import json
        payload = json.loads(msg.payload.decode())
        dados.update(payload)
        dados['last'] = time.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print('Erro parse MQTT:', e)

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

# roda MQTT em thread separada
def mqtt_loop():
    mqtt_client.loop_forever()

threading.Thread(target=mqtt_loop, daemon=True).start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dados')
def get_dados():
    return jsonify(dados)

@app.route('/grafico')
def grafico():
    # gera gráfico simples (exemplo)
    fig, ax = plt.subplots()
    labels = ['Temp','Umid','Luz','Ruido']
    vals = [dados['temp'], dados['umid'], dados['luz'], dados['ruido']]
    ax.barh(labels, vals)
    buf = io.BytesIO()
    plt.tight_layout()
    fig.savefig(buf, format='png')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
```

### `templates/index.html` (esqueleto)

```html
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>FiapSense Dashboard</title>
  <style>
    body { background:#0f1724; color:#e6eef8; font-family:Arial, sans-serif; padding:16px }
    .card{ background:#111827; padding:12px; border-radius:8px; margin-bottom:12px }
  </style>
</head>
<body>
  <h1>FiapSense</h1>
  <div id="placar" class="card">
    <p>Temp: <span id="temp">-</span> °C</p>
    <p>Umid: <span id="umid">-</span> %</p>
    <p>Luz: <span id="luz">-</span> %</p>
    <p>Ruido: <span id="ruido">-</span></p>
    <p>Presença: <span id="pres">-</span></p>
    <p>Última: <span id="last">-</span></p>
  </div>
  <img id="graf" src="/grafico" alt="graf" style="width:100%; max-width:600px">

<script>
  async function atualizar(){
    const r = await fetch('/dados');
    const j = await r.json();
    document.getElementById('temp').innerText = j.temp;
    document.getElementById('umid').innerText = j.umid;
    document.getElementById('luz').innerText = j.luz;
    document.getElementById('ruido').innerText = j.ruido;
    document.getElementById('pres').innerText = j.presenca ? 'SIM' : 'NAO';
    document.getElementById('last').innerText = j.last || '-';
    document.getElementById('graf').src = '/grafico?ts=' + new Date().getTime();
  }
  setInterval(atualizar, 2000);
  atualizar();
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
