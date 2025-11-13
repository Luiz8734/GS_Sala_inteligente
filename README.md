# 🌡️💡 FiapSense Dashboard + ESP32 IoT

## 👥 Integrantes do Grupo
- **Luiz Moraes Santos**
- **[Adicione aqui o nome completo do segundo integrante]**

---

## 🧠 Descrição Geral

O **FiapSense** é uma solução de **monitoramento inteligente de ambiente** desenvolvida para **empresas e instituições de ensino**, com o objetivo de **melhorar o conforto e a produtividade** de seus usuários.

O sistema integra um **dispositivo físico baseado em ESP32** com sensores e um **dashboard web moderno** (feito em React + TypeScript) que exibe os dados coletados em tempo real, como:

- 🌡️ **Temperatura**
- 💧 **Umidade**
- 💡 **Luminosidade**
- 🔊 **Ruído**
- 👤 **Presença**

---

## ⚙️ Problema Identificado

Ambientes de estudo e trabalho frequentemente apresentam **condições inadequadas** de temperatura, ruído e iluminação, afetando diretamente o **bem-estar e a eficiência** das pessoas.  
Essas variáveis normalmente **não são monitoradas em tempo real**, dificultando ajustes rápidos.

---

## 💡 Solução Proposta

O **FiapSense Dashboard** exibe informações ambientais coletadas por sensores conectados ao **ESP32**.  
Os dados são enviados via **protocolo MQTT** e podem ser exibidos em tempo real no **painel web**.

👉 O dispositivo ainda conta com:
- **Display LCD** para feedback local.
- **LEDs coloridos** que indicam o estado do ambiente.
- **Modo Pausa** ativado por botão, incentivando pausas saudáveis.
- **Alerta sonoro (buzzer)** quando os parâmetros estão fora do ideal.

---

## 🖼️ Imagens do Projeto

### 🔌 Protótipo no Wokwi
> *(Adicione aqui uma captura de tela do circuito montado no Wokwi)*

### 💻 Dashboard Web
> *(Adicione aqui imagens da interface React/TypeScript mostrando os sensores em tempo real)*

### ⚙️ Protótipo Físico
> *(Adicione fotos reais do dispositivo montado com LCD e sensores)*

---

## 🧩 Componentes Utilizados

| Componente | Função |
|-------------|--------|
| **ESP32** | Microcontrolador principal |
| **Sensor DHT22** | Mede temperatura e umidade |
| **LDR (Sensor de Luz)** | Mede intensidade luminosa |
| **Microfone KY-037** | Mede nível de ruído |
| **Sensor Ultrassônico HC-SR04** | Detecta presença |
| **Display LCD 16x2 I2C** | Exibe status do ambiente |
| **LEDs RGB** | Indicam condição (verde = ok, vermelho = alerta, azul = pausa) |
| **Buzzer** | Emite aviso sonoro |
| **Botão** | Ativa modo pausa |

---

## 🧰 Tecnologias Utilizadas

- 🧠 **ESP32** — plataforma IoT com WiFi e Bluetooth integrados  
- ☁️ **MQTT** — protocolo leve para comunicação IoT  
- 🧩 **React + TypeScript** — frontend moderno e modular  
- 🎨 **Tailwind CSS** — design responsivo e estilizado  
- 📟 **Wokwi** — simulação completa do hardware online  

---

## 🧠 Estrutura do Dashboard Web

fiap-sense-dashboard/
│
├── index.html # Template principal
├── metadata.json # Metadados da aplicação
├── README.md # Documentação (este arquivo)
│
└── src/
├── components/
│ ├── Footer.tsx # Rodapé
│ ├── Header.tsx # Cabeçalho
│ ├── SensorCard.tsx # Card de cada sensor
│ └── icons.tsx # Ícones SVG
│
├── App.tsx # Lógica e layout principal
├── index.tsx # Ponto de entrada
└── types.ts # Definições de tipos TypeScript

yaml
Copiar código

---

## 🚀 Instruções de Uso

### 🧩 Executar o Dashboard
1. Baixe o projeto ou clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/fiap-sense-dashboard.git
Acesse a pasta:

bash
Copiar código
cd fiap-sense-dashboard
Instale as dependências:

bash
Copiar código
npm install
Execute o servidor local:

bash
Copiar código
npm run dev
Abra no navegador o endereço exibido (ex: http://localhost:5173)

🔌 Conectar a uma API Real
Abra o arquivo App.tsx.

Localize a seção --- MOCK DATA GENERATION (FOR DEMO) --- e comente o bloco setInterval.

Localize a seção --- REAL API FETCH LOGIC (DISABLED FOR DEMO) --- e descomente o código.

Certifique-se de que o endpoint (/api/sensors) corresponde ao endereço do servidor backend.

📡 Código ESP32 (com Wi-Fi + MQTT + LCD + Sensores)
O código abaixo deve ser usado no Wokwi ou Arduino IDE.

cpp
Copiar código
#include <WiFi.h>
#include <PubSubClient.h>
#include <LiquidCrystal_I2C.h>
#include <DHT.h>
#include <NewPing.h>

// ---------------- CONFIG WIFI & MQTT ----------------
const char* ssid = "Wokwi-GUEST";
const char* password = "";
const char* mqtt_server = "98.92.204.86";
const int mqtt_port = 1883;
const char* mqtt_user = "";
const char* mqtt_pass = "";

WiFiClient espClient;
PubSubClient client(espClient);
unsigned long lastMQTTSend = 0;

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
LiquidCrystal_I2C lcd(0x27, 16, 2);
DHT dht(DHTPIN, DHTTYPE);
NewPing sonar(ULTRASONIC_TRIG_PIN, ULTRASONIC_ECHO_PIN, MAX_DISTANCE);

// ---------------- VARIÁVEIS ----------------
bool modoPausa = false;
bool ultimoEstadoBotao = HIGH;
unsigned long lastButtonPress = 0;
unsigned long pauseStartTime = 0;
unsigned long lastPauseMessageChange = 0;
unsigned long pauseDuration = 30000;

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

// ---------------- FUNÇÕES ----------------
int lerLuz() {
  int leitura = analogRead(LDR_PIN);
  leitura = 4095 - leitura;
  luzBuffer[luzIndex] = leitura;
  luzIndex = (luzIndex + 1) % NUM_LUZ_LEITURAS;
  int soma = 0;
  for (int i = 0; i < NUM_LUZ_LEITURAS; i++) soma += luzBuffer[i];
  return map(soma / NUM_LUZ_LEITURAS, 0, 4095, 0, 100);
}

int calcularMediaRuido(int val) {
  ruidoBuffer[ruidoIndex] = val;
  ruidoIndex = (ruidoIndex + 1) % 10;
  int soma = 0;
  for (int i = 0; i < 10; i++) soma += ruidoBuffer[i];
  return soma / 10;
}

int lerDistanciaUltrassonica() {
  unsigned int uS = sonar.ping_median(5);
  int dist = uS / US_ROUNDTRIP_CM;
  if (dist == 0) dist = MAX_DISTANCE;
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
    lcd.print("                ");
    lcd.setCursor(0, 1);
    lcd.print(mensagensPausa[pausaMessageIndex]);
    lastPauseMessageChange = millis();
    tone(BUZZER_PIN, 1000, 60);
  }
}

void conectarWiFi() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Conectando WiFi");
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  int tentativas = 0;
  while (WiFi.status() != WL_CONNECTED && tentativas < 30) {
    delay(500);
    tentativas++;
  }
  if (WiFi.status() == WL_CONNECTED) {
    lcd.clear();
    lcd.print("WiFi conectado!");
    lcd.setCursor(0, 1);
    lcd.print(WiFi.localIP());
  } else {
    lcd.clear();
    lcd.print("Falha WiFi!");
  }
}

void reconnectMQTT() {
  while (!client.connected()) {
    if (client.connect("ESP32-FIAP", mqtt_user, mqtt_pass)) {
      client.publish("fiap/status", "ESP32 conectado com sucesso!");
    } else {
      delay(3000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  lcd.init();
  lcd.backlight();
  lcd.print("PROJETO AMBIENTE");
  lcd.setCursor(0, 1);
  lcd.print("SEGURO - FIAP");
  delay(2500);
  lcd.clear();
  lcd.print("Iniciando...");
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

void loop() {
  if (WiFi.status() != WL_CONNECTED) conectarWiFi();
  if (!client.connected()) reconnectMQTT();
  client.loop();

  bool leituraBotao = digitalRead(BOTAO_PIN);
  if (leituraBotao == LOW && ultimoEstadoBotao == HIGH && millis() - lastButtonPress > 400) {
    lastButtonPress = millis();
    if (!modoPausa) entrarModoPausa();
    else sairModoPausa();
  }
  ultimoEstadoBotao = leituraBotao;

  if (!modoPausa) {
    float temp = dht.readTemperature();
    float umid = dht.readHumidity();
    if (isnan(temp)) temp = 0;
    if (isnan(umid)) umid = 0;

    int luz = lerLuz();
    int ruido = calcularMediaRuido(analogRead(MICROFONE_PIN));
    int dist = lerDistanciaUltrassonica();
    bool presenca = dist < 150;

    bool alertaCalor = temp > 30;
    bool alertaRuido = ruido > 1900;
    bool alertaEscuro = luz < 30;

    int numAlertas = alertaCalor + alertaRuido + alertaEscuro;

    Serial.print("Temp:"); Serial.print(temp, 1);
    Serial.print(" Umid:"); Serial.print(umid, 0);
    Serial.print(" Luz:"); Serial.print(luz);
    Serial.print(" Ruido:"); Serial.print(ruido);
    Serial.print(" Dist:"); Serial.print(dist);
    Serial.print(" Presenca:");
    Serial.println(presenca ? "SIM" : "NAO");

    lcd.clear();
    if (!presenca) {
      lcd.print("Sem Presenca");
      lcd.setCursor(0, 1);
      lcd.print("Dist: "); lcd.print(dist);
      acenderLed(LED_AZUL);
    } else if (numAlertas == 0) {
      lcd.print("Tudo OK :)");
      lcd.setCursor(0, 1);
      lcd.print("T:"); lcd.print(temp, 1);
      lcd.print("C L:"); lcd.print(luz);
      acenderLed(LED_VERDE);
    } else {
      lcd.print("ALERTA!");
      lcd.setCursor(0, 1);
      lcd.print("T:"); lcd.print(temp, 0);
      lcd.print("C L:"); lcd.print(luz);
      tone(BUZZER_PIN, 900, 100);
      acenderLed(LED_VERMELHO);
    }

    if (millis() - lastMQTTSend > 5000) {
      char payload[128];
      snprintf(payload, sizeof(payload),
               "{\"temp\":%.1f,\"umid\":%.1f,\"luz\":%d,\"ruido\":%d,\"presenca\":%d}",
               temp, umid, luz, ruido, presenca);
      client.publish("fiap/sensores", payload);
      lastMQTTSend = millis();
    }

    delay(1200);
  } else {
    atualizarDisplayPausa();
    if (millis() - pauseStartTime > pauseDuration) sairModoPausa();
  }
}
🧪 Como Replicar o Projeto (Wokwi)
Acesse https://wokwi.com/

Crie um novo projeto ESP32

Adicione:

DHT22 → pino 4

LDR → 34

Microfone → 33

Botão → 27

LEDs → 17 (Vermelho), 18 (Verde), 5 (Azul)

Buzzer → 26

Ultrassônico → TRIG 32, ECHO 35

LCD I2C → endereço 0x27

Cole o código acima.

Clique em ▶️ Start Simulation

Veja os dados no Serial Monitor e no LCD virtual

📊 Exemplo de Payload MQTT
json
Copiar código
{
  "temp": 25.3,
  "umid": 60.1,
  "luz": 75,
  "ruido": 1200,
  "presenca": 1
}
🧾 Conclusão
O FiapSense Dashboard + ESP32 IoT mostra como tecnologia e IoT podem melhorar ambientes físicos, promovendo saúde, conforto e produtividade.
Com arquitetura modular e escalável, está pronto para evoluir com novas funções e integrações.

✨ Espaços para Imagens
🧱 Diagrama de Ligações (Wokwi)

💻 Captura do Dashboard React

⚙️ Foto do Protótipo Físico
