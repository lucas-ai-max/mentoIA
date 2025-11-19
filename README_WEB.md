# Mesa de Debates - Interface Web Moderna 🚀

Interface web moderna criada com Next.js 14+ para substituir a interface Streamlit, mantendo toda a funcionalidade do backend Python com CrewAI.

## 📋 Pré-requisitos

- Node.js 20.9.0 ou superior
- Python 3.11+
- npm ou yarn

## 🚀 Início Rápido

### 1. Backend Python

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar servidor API
python api_server.py
```

O servidor API estará rodando em `http://localhost:8000`

### 2. Frontend Next.js

```bash
# Navegar para a pasta web
cd web

# Instalar dependências
npm install

# Executar em desenvolvimento
npm run dev
```

A interface estará disponível em `http://localhost:3000`

## 🎯 Funcionalidades

### ✅ Implementado

- [x] Interface moderna com dark mode
- [x] Sidebar com navegação e histórico
- [x] Modal de seleção de agentes
- [x] Área de chat com mensagens formatadas
- [x] Indicadores de rodada
- [x] Input de mensagem com validações
- [x] Estados vazios com sugestões
- [x] Persistência de histórico (localStorage)
- [x] Integração com API Python
- [x] Animações e transições suaves

### 🔄 Em Desenvolvimento

- [ ] Melhorar mapeamento de agentes
- [ ] Adicionar exportação de debates
- [ ] Implementar compartilhamento
- [ ] Melhorar responsividade mobile
- [ ] Adicionar testes

## 📁 Estrutura do Projeto

```
mentoIA/
├── web/                    # Frontend Next.js
│   ├── app/               # Páginas e layouts
│   ├── components/        # Componentes React
│   ├── lib/               # Utilitários e stores
│   └── public/            # Arquivos estáticos
├── agents.py              # Definições dos agentes
├── debate_crew.py         # Lógica de debate
├── api_server.py          # Servidor API FastAPI
└── requirements.txt       # Dependências Python
```

## 🔌 API Endpoints

### GET /api/agents
Retorna lista de agentes disponíveis

### POST /api/debate/start
Inicia um novo debate

**Request:**
```json
{
  "agentes": ["elon", "bill"],
  "pergunta": "Qual é o futuro da IA?",
  "num_rodadas": 2
}
```

**Response:**
```json
{
  "historico": [
    {
      "tipo": "pergunta",
      "conteudo": "Qual é o futuro da IA?"
    },
    {
      "tipo": "rodada",
      "conteudo": "--- RODADA 1 ---",
      "rodada": 1
    },
    {
      "tipo": "resposta",
      "conteudo": "...",
      "agente": "CEO da Tesla e SpaceX",
      "rodada": 1
    }
  ]
}
```

## 🎨 Design

A interface foi projetada para ser:
- **Moderna**: Design limpo e profissional
- **Responsiva**: Funciona em desktop, tablet e mobile
- **Acessível**: Segue padrões de acessibilidade
- **Performática**: Otimizada para velocidade

## 🛠️ Tecnologias

### Frontend
- Next.js 14+ (App Router)
- TypeScript
- Tailwind CSS
- Shadcn/ui
- Zustand
- Lucide React

### Backend
- FastAPI
- CrewAI
- LangChain
- OpenAI

## 📝 Notas

- O histórico é salvo automaticamente no localStorage
- A API espera IDs de agentes em minúsculas: `elon`, `bill`, `jeff`, `mark`, `tim`
- O servidor API precisa estar rodando antes de usar a interface web

## 🐛 Troubleshooting

### Erro de CORS
Certifique-se de que o servidor API está configurado para aceitar requisições de `http://localhost:3000`

### Agentes não encontrados
Verifique se os IDs dos agentes correspondem aos nomes em `agents.py`

### API não responde
Verifique se o servidor está rodando na porta 8000 e se a URL está correta em `web/lib/api.ts`

