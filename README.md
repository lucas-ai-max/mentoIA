# BillIA 🚀

Uma aplicação interativa usando CrewAI que simula debates entre bilionários da tecnologia.

## 🎯 Funcionalidades

- **Seleção de Agentes**: Escolha quais bilionários participarão do debate
- **Debate Interativo**: Faça perguntas e veja os agentes debaterem entre si
- **Personalidades Únicas**: Cada agente tem sua própria personalidade e estilo de comunicação

## 🛠️ Instalação

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Configure suas variáveis de ambiente:
```bash
cp .env.example .env
```

Edite o arquivo `.env` e adicione sua API key:
```
OPENAI_API_KEY=sua_chave_aqui
```

## 🚀 Como Usar

Execute a aplicação:
```bash
streamlit run app.py
```

Acesse `http://localhost:8501` no seu navegador.

## 👥 Agentes Disponíveis

- **Elon Musk** - Visionário, disruptivo, focado em inovação
- **Bill Gates** - Filantropo, estratégico, focado em impacto social
- **Jeff Bezos** - Focado em longo prazo, orientado ao cliente
- **Mark Zuckerberg** - Focado em conectividade e metaverso
- **Tim Cook** - Focado em qualidade, privacidade e sustentabilidade

## 📝 Notas

Esta aplicação é uma demonstração do poder do CrewAI para criar sistemas multi-agente interativos.

