🌡️💡 FiapSense Dashboard + ESP32 IoT
👥 Integrantes do Grupo

Luiz Moraes Santos

[Adicione aqui o nome completo do segundo integrante]

🧠 Descrição Geral

O FiapSense é uma solução de monitoramento inteligente de ambiente desenvolvida para empresas e instituições de ensino, com o objetivo de melhorar o conforto e a produtividade de seus usuários.

O sistema integra um dispositivo físico baseado em ESP32 com sensores e um dashboard web moderno (feito em React + TypeScript) que exibe os dados coletados em tempo real, como:

🌡️ Temperatura

💧 Umidade

💡 Luminosidade

🔊 Ruído

👤 Presença

⚙️ Problema Identificado

Ambientes de estudo e trabalho frequentemente apresentam condições inadequadas de temperatura, ruído e iluminação, afetando diretamente o bem-estar e a eficiência das pessoas.
Essas variáveis normalmente não são monitoradas em tempo real, dificultando ajustes rápidos.

💡 Solução Proposta

O FiapSense Dashboard exibe informações ambientais coletadas por sensores conectados ao ESP32.
Os dados são enviados via protocolo MQTT e podem ser exibidos em tempo real no painel web.

👉 O dispositivo ainda conta com:

Display LCD para feedback local.

LEDs coloridos que indicam o estado do ambiente.

Modo Pausa ativado por botão, incentivando pausas saudáveis.

Alerta sonoro (buzzer) quando os parâmetros estão fora do ideal.

🖼️ Imagens do Projeto
🔌 Protótipo no Wokwi

(Adicione aqui uma captura de tela do circuito montado no Wokwi)

💻 Dashboard Web

(Adicione aqui imagens da interface React/TypeScript mostrando os sensores em tempo real)

🧩 Componentes Utilizados
Componente	Função
ESP32	Microcontrolador principal
Sensor DHT22	Mede temperatura e umidade
LDR (Sensor de Luz)	Mede intensidade luminosa
Microfone KY-037	Mede nível de ruído
Sensor Ultrassônico HC-SR04	Detecta presença
Display LCD 16x2 I2C	Exibe status do ambiente
LEDs RGB	Indicam condição (verde = ok, vermelho = alerta, azul = pausa)
Buzzer	Emite aviso sonoro
Botão	Ativa modo pausa
🧰 Tecnologias Utilizadas

🧠 ESP32 — plataforma IoT com WiFi e Bluetooth integrados

☁️ MQTT — protocolo leve para comunicação IoT

🧩 React + TypeScript — frontend moderno e modular

🎨 Tailwind CSS — design responsivo e estilizado

📟 Wokwi — simulação completa do hardware online

🧠 Como o Código Funciona
🔹 Bibliotecas Importadas
#include <WiFi.h>              // Conexão Wi-Fi
#include <PubSubClient.h>      // Comunicação MQTT
#include <LiquidCrystal_I2C.h> // Controle do LCD via I2C
#include <DHT.h>               // Sensor DHT22 (Temperatura e Umidade)
#include <NewPing.h>           // Sensor Ultrassônico (Presença)


Essas bibliotecas permitem ao ESP32:

conectar-se à internet,

enviar dados via MQTT,

exibir informações no LCD,

ler sensores ambientais.

🔹 Configuração de Wi-Fi e MQTT
const char* ssid = "Wokwi-GUEST";
const char* password = "";
const char* mqtt_server = "98.92.204.86";
const int mqtt_port = 1883;


Conecte-se à rede WiFi e ao broker MQTT.
Pode-se usar test.mosquitto.org ou um broker local se desejar testar.

🔹 Mapeamento dos Pinos

Cada sensor e atuador é ligado a uma porta específica:

#define DHTPIN 4
#define LDR_PIN 34
#define MICROFONE_PIN 33
#define BOTAO_PIN 27
#define BUZZER_PIN 26
#define LED_VERMELHO 17
#define LED_VERDE 18
#define LED_AZUL 5
#define ULTRASONIC_TRIG_PIN 32
#define ULTRASONIC_ECHO_PIN 35

🔹 Funções Importantes
lerLuz()

Calcula a média da luminosidade lida pelo LDR (em %).

calcularMediaRuido()

Filtra o ruído sonoro para evitar leituras falsas.

lerDistanciaUltrassonica()

Usa o sensor HC-SR04 para verificar se há presença humana.

entrarModoPausa() e sairModoPausa()

Controlam o modo descanso, mostrando mensagens motivacionais no LCD e acendendo o LED azul.

conectarWiFi() e reconnectMQTT()

Garantem a conexão constante com a rede e o broker MQTT, reconectando automaticamente se cair.

loop()

Lê todos os sensores, toma decisões (alerta ou normal), envia dados via MQTT e atualiza o LCD.

🧠 Lógica de Decisão
Condição	Ação
Temperatura > 30°C	LED vermelho + alerta sonoro
Ruído > 1900	LED vermelho + alerta sonoro
Luz < 30%	LED azul + alerta sonoro
Nenhum alerta	LED verde + mensagem "Tudo OK"
Sem presença	LED azul + “Sem Presença” no LCD
Botão pressionado	Ativa modo pausa por 30s
📡 Fluxo de Dados (MQTT)

O dispositivo envia mensagens a cada 5 segundos:

{
  "temp": 25.3,
  "umid": 60.1,
  "luz": 75,
  "ruido": 1200,
  "presenca": 1
}


Esses dados podem ser visualizados:

Em um broker MQTT local (como Mosquitto)

Ou no FiapSense Dashboard (versão web)

🧪 Como Replicar o Projeto (Wokwi)

Acesse: 🌐 https://wokwi.com/

Crie um novo projeto ESP32.

Adicione os componentes:

DHT22 → pino 4

LDR → pino 34

Microfone → pino 33

Botão → pino 27

LEDs → pinos 17, 18, 5

Buzzer → pino 26

Sensor Ultrassônico → TRIG = 32, ECHO = 35

LCD I2C (endereço 0x27)

Copie e cole o código completo.

Clique em ▶️ Start Simulation.

Veja os dados aparecendo no Monitor Serial e no LCD virtual.

(💡 Dica: adicione ruído, variações de luz e temperatura simuladas no Wokwi para ver o comportamento realista.)

🧱 Como Replicar o Dashboard Web

Baixe ou clone o repositório do FiapSense Dashboard (React).

Abra a pasta no VS Code.

Instale dependências:

npm install


Execute o servidor local:

npm run dev


O dashboard abrirá em http://localhost:5173.

📘 Explicação Resumida do Funcionamento

ESP32 lê os sensores.

Os dados são mostrados no LCD e enviados via MQTT.

O FiapSense Dashboard recebe esses dados e exibe em gráficos e cards.

Caso algum valor ultrapasse o limite seguro, LEDs e buzzer sinalizam alerta.

Usuário pode ativar modo pausa com o botão.

🧾 Próximos Passos e Melhorias Futuras

Implementar histórico de dados e gráficos no Dashboard.

Adicionar controle automático de climatização via relé.

Integrar com Google Sheets / Firebase para armazenamento em nuvem.

Criar aplicativo mobile para notificações em tempo real.

🖼️ Espaços para Imagens
🧱 Diagrama de Ligações (Wokwi)

(Adicione aqui um print do circuito montado)

💻 Interface Web (React Dashboard)

(Adicione print das telas principais do dashboard)

⚙️ Protótipo Físico (Montagem Real)

(Adicione fotos do dispositivo montado com LCD e sensores)

🧠 Conclusão

O FiapSense Dashboard + ESP32 IoT demonstra como a tecnologia pode melhorar o ambiente físico, promovendo conforto, saúde e eficiência.
Com sua arquitetura modular e escalável, ele está pronto para evoluir e ser aplicado em ambientes reais corporativos e educacionais.
