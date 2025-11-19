# 🛠️ Painel de Administração - BillIA

## 📋 Visão Geral

O painel de administração permite gerenciar completamente os agentes, configurações de LLMs e configurações gerais do sistema.

## 🚀 Acesso

Acesse o painel através de: `http://localhost:3000/admin/dashboard`

## 📁 Estrutura de Rotas

- `/admin/dashboard` - Dashboard com estatísticas
- `/admin/agents` - Lista de agentes
- `/admin/agents/new` - Criar novo agente
- `/admin/agents/:id/edit` - Editar agente existente
- `/admin/llms` - Configuração de LLMs
- `/admin/settings` - Configurações gerais

## 🗄️ Configuração do Banco de Dados

### 1. Criar Tabelas

Execute os seguintes arquivos SQL no Supabase (em ordem):

1. `supabase_schema.sql` - Tabelas principais (debates, messages)
2. `supabase_admin_schema.sql` - Tabelas de administração (agents, llm_providers, agent_usage_logs)
3. `supabase_rls_setup.sql` - Configurar Row Level Security

### 2. Verificar Tabelas

Após executar os SQLs, você deve ter as seguintes tabelas:

- `debates` - Debates realizados
- `messages` - Mensagens dos debates
- `agents` - Agentes configuráveis
- `llm_providers` - Provedores de LLM
- `agent_usage_logs` - Logs de uso dos agentes

## 🔌 APIs Disponíveis

### Agentes

- `GET /api/admin/agents` - Lista agentes (com filtros: search, llm, status)
- `GET /api/admin/agents/{id}` - Busca agente específico
- `POST /api/admin/agents` - Cria novo agente
- `PUT /api/admin/agents/{id}` - Atualiza agente
- `DELETE /api/admin/agents/{id}` - Deleta agente
- `POST /api/admin/agents/{id}/duplicate` - Duplica agente
- `POST /api/admin/agents/{id}/test` - Testa agente

### LLMs

- `GET /api/admin/llms/providers` - Lista provedores
- `POST /api/admin/llms/providers/test` - Testa conexão
- `GET /api/admin/llms/usage` - Estatísticas de uso

## 📝 Funcionalidades

### Dashboard
- Cards de estatísticas (Total de Agentes, Debates, LLMs, Uso de API)
- Atividade recente
- Ações rápidas

### Gerenciamento de Agentes
- Lista de agentes com busca
- Criar/Editar/Deletar agentes
- Duplicar agentes
- Formulário completo com:
  - Informações básicas (nome, avatar, cor, status)
  - Configuração de LLM (provider, modelo, temperature, max_tokens)
  - Prompts (role, goal, backstory)
  - Configurações avançadas (verbose, delegation)
- Preview em tempo real

### Configuração de LLMs
- Gerenciar provedores (OpenAI, Anthropic, Google)
- Configurar API keys
- Habilitar/desabilitar modelos
- Ver estatísticas de uso

### Configurações Gerais
- Configurações de debate
- Limites de API
- Configurações de segurança

## 🎨 Componentes Criados

- `AdminSidebar` - Sidebar de navegação
- `StatsCard` - Card de estatísticas
- `AgentCard` - Card de agente na lista
- `AgentForm` - Formulário completo de agente
- `FormField` - Campo de formulário reutilizável

## 📦 Dependências Adicionadas

- `dropdown-menu` - Menu dropdown
- `tabs` - Tabs para organização
- `select` - Select dropdown
- `switch` - Switch toggle
- `card` - Cards
- `label` - Labels
- `alert` - Alertas
- `textarea` - Textarea
- `progress` - Barra de progresso

## ⚠️ Próximos Passos

1. **Executar SQLs no Supabase** - Criar todas as tabelas
2. **Testar criação de agente** - Criar um agente pelo painel
3. **Integrar agentes dinâmicos** - Fazer os debates usarem agentes do banco
4. **Implementar teste real de agente** - Usar CrewAI para testar
5. **Adicionar autenticação** - Proteger rotas de admin

## 🔒 Segurança

Atualmente o painel não tem autenticação. Para produção, adicione:
- Autenticação de usuário
- Verificação de role (admin)
- Proteção de rotas no frontend e backend

