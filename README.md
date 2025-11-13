# 🌡️💡 FiapSense Dashboard

## 👥 Integrantes do Grupo

- Luiz Moraes Santos
- [Nome do Segundo Integrante] *(adicione aqui o nome completo do outro aluno)*

---

## 🧠 Descrição do Projeto

**FiapSense** é uma solução inteligente desenvolvida para monitorar e otimizar as condições ambientais em ambientes corporativos e educacionais. O projeto atua na detecção de **temperatura, umidade, luminosidade e ruído**, visando melhorar o conforto, bem-estar e produtividade das pessoas no local.

### ⚙️ Problema Identificado

Ambientes de trabalho e estudo sofrem frequentemente com temperaturas inadequadas, ruído excessivo e iluminação ruim, impactando diretamente na saúde, foco e desempenho. Essas condições geralmente não são monitoradas em tempo real, dificultando ações corretivas.

### 💡 Solução Proposta

O FiapSense Dashboard é uma aplicação web moderna e responsiva, construída com React e TypeScript, que exibe os dados dos sensores em tempo real. A interface é intuitiva e visualmente agradável, permitindo uma rápida avaliação das condições do ambiente.

_Este projeto frontend é uma demonstração e atualmente utiliza dados simulados para fins de desenvolvimento. Ele é projetado para se conectar facilmente a uma API backend que coleta dados reais de sensores._

---

## 🧩 Estrutura do Projeto

O projeto é organizado com uma estrutura moderna de componentes React:

```
fiap-sense-dashboard/
│
├── index.html                 # Template HTML principal
├── metadata.json              # Metadados da aplicação
├── README.md                  # Documentação (este arquivo)
│
└── src/
    ├── components/
    │   ├── Footer.tsx         # Componente de rodapé
    │   ├── Header.tsx         # Componente de cabeçalho
    │   ├── SensorCard.tsx     # Card reutilizável para cada sensor
    │   └── icons.tsx          # Ícones SVG dos sensores
    │
    ├── App.tsx                # Componente principal da aplicação
    ├── index.tsx              # Ponto de entrada da aplicação
    └── types.ts               # Definições de tipos TypeScript
```

---

## 🧰 Tecnologias Utilizadas

- **React:** Biblioteca para construção da interface de usuário.
- **TypeScript:** Superset do JavaScript que adiciona tipagem estática.
- **Tailwind CSS:** Framework CSS para estilização rápida e responsiva.
- **HTML5:** Linguagem de marcação para a estrutura da página.

---

## 🚀 Instruções de Uso

Esta aplicação web é autocontida e não requer um processo de compilação local para ser executada. Basta abrir o arquivo `index.html` em um navegador da web moderno.

### Conectando a uma API Real

O dashboard atualmente funciona com dados simulados para demonstração. Para conectá-lo a uma fonte de dados real:

1.  Abra o arquivo `App.tsx`.
2.  Localize a seção `--- MOCK DATA GENERATION (FOR DEMO) ---` e comente ou remova o bloco de código `setInterval`.
3.  Localize a seção `--- REAL API FETCH LOGIC (DISABLED FOR DEMO) ---` e descomente o bloco de código.
4.  Certifique-se de que o endpoint (`/api/sensors`) corresponde ao endereço do seu servidor backend.

---

## 🔧 Explicação do Código-Fonte

### `App.tsx`

Este é o componente raiz da aplicação. Ele é responsável por:
- Gerenciar o estado dos dados dos sensores (`sensorData`).
- Simular a busca de dados em tempo real com `setInterval`.
- Renderizar o layout principal, incluindo o cabeçalho, os cards de sensores e o rodapé.
- Lidar com os estados de carregamento (`connecting`) e erro (`error`).

### `components/SensorCard.tsx`

Um componente reutilizável que exibe as informações de um único sensor.
- **Props:** `icon`, `title`, `value`, `unit`, `colorClass`.
- Possui uma estilização moderna com fundo translúcido e bordas arredondadas para um visual de "glassmorphism".

```jsx
<SensorCard
  icon={<ThermometerIcon className="h-6 w-6 text-white" />}
  title="Temperatura"
  value={sensorData.temperature.toFixed(1)}
  unit="°C"
  colorClass="bg-red-500/70"
/>
```

### `components/icons.tsx`

Contém os componentes de ícones SVG (Termômetro, Gota, Sol, Volume) usados nos `SensorCard`s para uma identificação visual rápida de cada métrica.

### `types.ts`

Define a interface `SensorData`, garantindo a consistência e a segurança de tipos para os dados que fluem pela aplicação.

```typescript
export interface SensorData {
  temperature: number;
  humidity: number;
  light: number;
  noise: number;
}
```

---

## 📊 Exemplo de Dashboard

*(Uma captura de tela do dashboard em execução.)*
