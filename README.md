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

## 🛑 Problema Identificado

Ambientes corporativos e educacionais frequentemente sofrem com condições ambientais inadequadas, como **temperatura elevada, baixa umidade, excesso de ruído e luminosidade inadequada**. Esses fatores afetam diretamente:

- **Conforto dos colaboradores e alunos**
- **Produtividade** e concentração
- **Qualidade das aulas e reuniões**
- **Saúde e bem-estar** no ambiente
- Consumo de energia devido a climatização mal regulada

Além disso, a maioria dos ambientes não possui monitoramento contínuo, o que impede ações rápidas e inteligentes quando algum parâmetro ultrapassa o ideal.

---

## ✅ Solução Proposta

O **FiapSense** surge como uma solução inteligente de monitoramento ambiental baseada em **ESP32 + sensores integrados**. A proposta consiste em:

### 🔍 Monitoramento em Tempo Real
O dispositivo coleta continuamente:
- Temperatura  
- Umidade  
- Luminosidade  
- Níveis de ruído  
- Presença/movimento  

Esses dados são enviados via **MQTT** para um dashboard web moderno e responsivo.

### 🔔 Alertas Automáticos
Quando qualquer parâmetro está fora do ideal, o sistema:
- Gera **alertas visuais** no dashboard  
- Aciona **notificações automáticas**  
- Pode ativar recursos como alarme, LED RGB ou mensagens LCD  

### 📊 Dashboard Interativo
A aplicação web exibe:
- Gráficos individuais e históricos  
- Indicadores instantâneos  
- Status do ambiente  
- Informações sobre tendências e anomalias  

### ⚙️ Tomada de Decisão Inteligente
O sistema pode:
- Recomendar ações (ex.: abrir janelas, ligar ventilação, reduzir barulho)
- Ajustar automaticamente dispositivos conectados
- Ajudar gestores a manter ambientes sempre adequados


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

<img width="777" height="551" alt="image" src="https://github.com/user-attachments/assets/9d764a75-b67c-4bdb-8e98-c58780d8ffbd" />


### Aplicação Web

<img width="878" height="350" alt="image" src="https://github.com/user-attachments/assets/1241963b-8673-4c8c-ad1e-587931354b41" />

<img width="718" height="795" alt="image" src="https://github.com/user-attachments/assets/f25b04a6-7c0c-43c4-bbda-301689046131" />


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
│   └── templates/
│       └── index.html
```

---

## 7. Código do Dispositivo (ESP32)

**Arquivo:** `esp32_fiapsense.ino`

> Abaixo está o código completo que serve como base. Ele reúne leitura de sensores, lógica de alerta, modo pausa, publicação MQTT e exibição LCD — tudo com comentários explicativos.

```cpp
/*
/*
  esp32_fiapsense.ino
  Projeto: FiapSense - ESP32 + Sensores + MQTT + LCD I2C
  Autor: Equipe FIAPSENSE
  Observações: Ajuste os pinos conforme seu hardware.
*/

#include <WiFi.h>              // Biblioteca Wi-Fi para ESP32
#include <PubSubClient.h>      // Biblioteca MQTT
#include <LiquidCrystal_I2C.h> // Tela LCD I2C
#include <DHT.h>               // Sensor DHT22
#include <NewPing.h>           // Sensor Ultrassônico

// ---------------- CONFIG WIFI & MQTT ----------------
const char* ssid = "Wokwi-GUEST";     // Nome da rede WiFi
const char* password = "";            // Senha do WiFi
const char* mqtt_server = "98.92.204.86"; // Endereço do broker MQTT
const int mqtt_port = 1883;           // Porta MQTT
const char* mqtt_user = "";           // Usuário MQTT (opcional)
const char* mqtt_pass = "";           // Senha MQTT (opcional)

WiFiClient espClient;                 // Cliente WiFi
PubSubClient client(espClient);       // Cliente MQTT
unsigned long lastMQTTSend = 0;       // Controle de frequência de envio MQTT

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

// ---------------- OBJETOS DOS SENSORES ----------------
LiquidCrystal_I2C lcd(0x27, 16, 2);   // LCD I2C (endereço 0x27)
DHT dht(DHTPIN, DHTTYPE);             // DHT22
NewPing sonar(ULTRASONIC_TRIG_PIN, ULTRASONIC_ECHO_PIN, MAX_DISTANCE);

// ---------------- VARIÁVEIS DO PROJETO ----------------
bool modoPausa = false;               // Controle do modo pausa
bool ultimoEstadoBotao = HIGH;        // Para debounce
unsigned long lastButtonPress = 0;
unsigned long pauseStartTime = 0;
unsigned long lastPauseMessageChange = 0;
unsigned long pauseDuration = 30000;  // Duração da pausa (30s)

// Buffers para suavizar leituras
#define NUM_LUZ_LEITURAS 10
int luzBuffer[NUM_LUZ_LEITURAS] = {0};
int luzIndex = 0;

int ruidoBuffer[10] = {0};
int ruidoIndex = 0;

const char* mensagensPausa[] = {      // Frases exibidas no modo pausa
  "Respire fundo...",
  "Alongue-se...",
  "Olhe longe...",
  "Hidrate-se!"
};
const int numMensagensPausa = sizeof(mensagensPausa) / sizeof(mensagensPausa[0]);
int pausaMessageIndex = 0;

// ---------------- FUNÇÕES DE LEITURA SUAVIZADA ----------------

// Lê a luminosidade com filtro de média
int lerLuz() {
  int leitura = analogRead(LDR_PIN);
  leitura = 4095 - leitura; // Inverte caso tenha divisor
  luzBuffer[luzIndex] = leitura;
  luzIndex = (luzIndex + 1) % NUM_LUZ_LEITURAS;

  long soma = 0;
  for (int i = 0; i < NUM_LUZ_LEITURAS; i++) soma += luzBuffer[i];

  int media = soma / NUM_LUZ_LEITURAS;

  return map(media, 0, 4095, 0, 100); // Retorna % de luz
}

// Média móvel do ruído para suavizar picos
int calcularMediaRuido(int val) {
  ruidoBuffer[ruidoIndex] = val;
  ruidoIndex = (ruidoIndex + 1) % 10;

  int soma = 0;
  for (int i = 0; i < 10; i++) soma += ruidoBuffer[i];

  return soma / 10;
}

// Leitura da distância ultrassônica
int lerDistanciaUltrassonica() {
  unsigned int uS = sonar.ping_median(5);
  int dist = uS / US_ROUNDTRIP_CM;
  if (dist == 0) dist = MAX_DISTANCE; // Sem retorno = longe demais
  return dist;
}

// ---------------- CONTROLE DE LEDS ----------------
void desligarLeds() {
  digitalWrite(LED_VERMELHO, LOW);
  digitalWrite(LED_VERDE, LOW);
  digitalWrite(LED_AZUL, LOW);
}

void acenderLed(int led) {
  desligarLeds();
  digitalWrite(led, HIGH);
}

// ---------------- MODO PAUSA ----------------
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

  tone(BUZZER_PIN, 1200, 100);  // Som de entrada
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

// Atualiza mensagem do modo pausa
void atualizarDisplayPausa() {
  if (millis() - lastPauseMessageChange > 5000) {
    pausaMessageIndex = (pausaMessageIndex + 1) % numMensagensPausa;
    lcd.setCursor(0, 1);
    lcd.print("                ");
    lcd.setCursor(0, 1);
    lcd.print(mensagensPausa[pausaMessageIndex]);
    lastPauseMessageChange = millis();
    tone(BUZZER_PIN, 1000, 60);
  }
}

// ---------------- WIFI ----------------
void conectarWiFi() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Conectando WiFi");

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  int tentativas = 0;

  while (WiFi.status() != WL_CONNECTED && tentativas < 30) {
    delay(500);
    lcd.setCursor(0, 1);
    lcd.print("Tentando...");
    tentativas++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    lcd.clear();
    lcd.print("WiFi Conectado!");
    lcd.setCursor(0, 1);
    lcd.print(WiFi.localIP().toString());
  } else {
    lcd.clear();
    lcd.print("Falha WiFi!");
  }
}

// ---------------- MQTT ----------------
void reconnectMQTT() {
  while (!client.connected()) {
    if (client.connect("ESP32-FIAP", mqtt_user, mqtt_pass)) {
      client.publish("fiap/status", "ESP32 conectado!");
    } else {
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

  dht.begin();

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

// ---------------- LOOP PRINCIPAL ----------------
void loop() {
  // Reconeção automática WiFi
  if (WiFi.status() != WL_CONNECTED)
    conectarWiFi();

  // Conexão MQTT
  if (!client.connected())
    reconnectMQTT();

  client.loop();

  // BOTÃO COM DEBOUNCE
  bool leituraBotao = digitalRead(BOTAO_PIN);
  if (leituraBotao == LOW && ultimoEstadoBotao == HIGH && millis() - lastButtonPress > 400) {
    lastButtonPress = millis();
    if (!modoPausa) entrarModoPausa();
    else sairModoPausa();
  }
  ultimoEstadoBotao = leituraBotao;

  // ---------- MODO NORMAL ----------
  if (!modoPausa) {
    // Sensores
    float temp = dht.readTemperature();
    float umid = dht.readHumidity();
    if (isnan(temp)) temp = 0;
    if (isnan(umid)) umid = 0;

    int luz = lerLuz();
    int ruidoRaw = analogRead(MICROFONE_PIN);
    int ruido = calcularMediaRuido(ruidoRaw);
    int dist = lerDistanciaUltrassonica();
    bool presenca = dist < 150;

    bool alertaCalor = temp > 30;
    bool alertaRuido = ruido > 1900;
    bool alertaEscuro = luz < 30;

    int numAlertas = alertaCalor + alertaRuido + alertaEscuro;

    // LCD e LEDs
    lcd.clear();

    if (!presenca) {
      lcd.setCursor(0, 0);
      lcd.print("Sem Presenca");
      lcd.setCursor(0, 1);
      lcd.print("Dist: ");
      lcd.print(dist);
      acenderLed(LED_AZUL);

    } else if (numAlertas == 0) {
      lcd.setCursor(0, 0);
      lcd.print("Tudo OK :)");
      lcd.setCursor(0, 1);
      lcd.print("T:");
      lcd.print(temp);
      lcd.print(" L:");
      lcd.print(luz);
      acenderLed(LED_VERDE);

    } else {
      lcd.setCursor(0, 0);
      if (alertaCalor) lcd.print("Calor ");
      if (alertaRuido) lcd.print("Ruido ");
      if (alertaEscuro) lcd.print("Escuro");

      lcd.setCursor(0, 1);
      lcd.print("T:");
      lcd.print(temp);
      lcd.print(" L:");
      lcd.print(luz);

      if (alertaCalor) tone(BUZZER_PIN, 900, 100);
      if (alertaRuido) tone(BUZZER_PIN, 1000, 100);
      if (alertaEscuro) tone(BUZZER_PIN, 800, 100);

      acenderLed(numAlertas == 1 ? LED_AZUL : LED_VERMELHO);
    }

    // ENVIO MQTT A CADA 5s
    if (millis() - lastMQTTSend > 5000) {
      char payload[256];
      snprintf(payload, sizeof(payload),
        "{\"temp\":%.1f,\"umid\":%.1f,\"luz\":%d,\"ruido\":%d,\"presenca\":%d}",
        temp, umid, luz, ruido, presenca);

      client.publish("fiap/sensores", payload);
      lastMQTTSend = millis();
    }

    delay(1200);

  } else {
    // ---------- MODO PAUSA ----------
    atualizarDisplayPausa();
    if (millis() - pauseStartTime > pauseDuration)
      sairModoPausa();
  }
}

```

**Observações e ajustes**

* Ajuste `alertaRuido` dependendo do microfone (valor analógico pode variar muito). Use `Serial.println(ruidoRaw)` para calibrar.
* `lerLuz()` assume divisor do LDR com referência 3.3V e leitura invertida; adapte se necessário.
* `map(..., 0, 4095, 0, 100)` transforma leitura ADC para porcentagem.
---

## 8. Aplicação Web (Flask)

**Estrutura mínima:**

`backend/app.py` — servidor Flask que se conecta ao broker MQTT e exibe dados em tempo real.

`backend/templates/index.html` — interface simples (tema escuro) que mostra valores atuais e gráfico.

### `app.py` (exemplo mínimo)

```python
# app.py
from flask import Flask, render_template, jsonify
from flask_cors import CORS
import paho.mqtt.client as mqtt
import threading

# Cria a aplicação Flask
app = Flask(__name__)
CORS(app)  # Libera acesso para o front-end (evita erro de CORS)

# ------------------- VARIÁVEIS GLOBAIS -------------------
# Dicionário que armazena os dados recebidos pelo MQTT
dados_sensores = {
    "temp": 0,
    "umid": 0,
    "luz": 0,
    "ruido": 0,
    "presenca": 0
}

# ------------------- CONFIG MQTT -------------------
MQTT_BROKER = "98.92.204.86"   # IP do servidor MQTT
MQTT_PORT = 1883               # Porta padrão
MQTT_TOPIC = "fiap/sensores"   # Tópico a ser recebido

# Função executada quando o cliente MQTT conecta ao broker
def on_connect(client, userdata, flags, rc):
    print(" Conectado ao MQTT com código:", rc)
    client.subscribe(MQTT_TOPIC)  # Inscreve no tópico

# Função executada quando chega uma mensagem no tópico inscrito
def on_message(client, userdata, msg):
    global dados_sensores
    import json
    try:
        payload = msg.payload.decode()  # Converte bytes → texto
        dados = json.loads(payload)     # Converte JSON → dict
        dados_sensores.update(dados)    # Atualiza dados globais
        print(" Dados recebidos:", dados_sensores)
    except Exception as e:
        print("Erro ao processar mensagem MQTT:", e)

# Função que inicia o cliente MQTT
def iniciar_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect   # Callback de conexão
    client.on_message = on_message   # Callback de mensagem
    client.connect(MQTT_BROKER, MQTT_PORT, 60)  # Conecta ao broker
    client.loop_forever()  # Mantém o MQTT rodando para sempre

# Inicia o MQTT em uma thread separada do Flask
threading.Thread(target=iniciar_mqtt, daemon=True).start()

# ------------------- ROTAS WEB -------------------
# Página principal (renderiza index.html)
@app.route("/")
def index():
    return render_template("index.html")

# Rota que retorna os dados dos sensores em JSON
@app.route("/dados")
def dados():
    return jsonify(dados_sensores)

# Inicia o servidor Flask
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
  <title>FiapSense | LNK-TECH</title>

  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/static/style.css">
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>

<body>
  <header class="header">
    <h1>🌿 FiapSense</h1>
    <p>Monitoramento inteligente do ambiente</p>
  </header>

  <main class="container">

    <!-- CARDS DE SENSORES -->
    <section class="sensor-data">
      <div class="card"><h3>Temperatura</h3><p id="temp">-- °C</p></div>
      <div class="card"><h3>Umidade</h3><p id="umid">-- %</p></div>
      <div class="card"><h3>Luminosidade</h3><p id="luz">-- lux</p></div>
      <div class="card"><h3>Ruído</h3><p id="ruido">-- dB</p></div>
      <div class="card"><h3>Presença</h3><p id="presenca">--</p></div>
    </section>

    <!-- GRÁFICOS -->
    <section class="chart-container">
      <h2>Monitoramento em Tempo Real</h2>
      <canvas id="graficoTempUmid"></canvas>
      <canvas id="graficoRuido" style="margin-top: 20px;"></canvas>
      <div id="alertas" class="alertas"></div>
    </section>

  </main>

  <footer class="footer">
    <p>© 2025 LNK-TECH | Projeto FiapSense</p>
  </footer>

  <!-- SCRIPT -->
  <script>
    // GRÁFICO TEMPERATURA / UMIDADE
    const graficoTempUmid = new Chart(document.getElementById("graficoTempUmid"), {
      type: "line",
      data: { labels: [], datasets: [
        { label: "Temperatura", data: [], borderColor: "#00aaff", tension: 0.4 },
        { label: "Umidade", data: [], borderColor: "#00ffaa", tension: 0.4 }
      ]},
      options: { responsive: true }
    });

    // GRÁFICO RUÍDO
    const graficoRuido = new Chart(document.getElementById("graficoRuido"), {
      type: "line",
      data: { labels: [], datasets: [
        { label: "Ruído (dB)", data: [], borderColor: "#ff6b6b", tension: 0.4 }
      ]},
      options: { responsive: true }
    });

    // FUNÇÃO QUE PEGA OS DADOS DO BACKEND
    async function atualizar() {
      const res = await fetch("/dados");
      const d = await res.json();

      document.getElementById("temp").innerText = `${d.temp} °C`;
      document.getElementById("umid").innerText = `${d.umid} %`;
      document.getElementById("luz").innerText = `${d.luz} lux`;
      document.getElementById("ruido").innerText = `${d.ruido} dB`;
      document.getElementById("presenca").innerText = d.presenca ? "Sim" : "Não";

      const hora = new Date().toLocaleTimeString();

      graficoTempUmid.data.labels.push(hora);
      graficoTempUmid.data.datasets[0].data.push(d.temp);
      graficoTempUmid.data.datasets[1].data.push(d.umid);
      graficoTempUmid.update();

      graficoRuido.data.labels.push(hora);
      graficoRuido.data.datasets[0].data.push(d.ruido);
      graficoRuido.update();
    }

    setInterval(atualizar, 2000);
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
6. Rode o backend Flask: `pip install Flask
pip install Flask-Cors
pip install paho-mqtt` → `python app.py`.
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

**Autores:** Equipe FiapSense

---
