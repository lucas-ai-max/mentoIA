# 🗄️ Configuração do Supabase

## Passo 1: Criar as Tabelas Principais

1. Acesse o [Supabase Dashboard](https://app.supabase.com)
2. Selecione seu projeto: `qkdhwwiohaqacojiijya`
3. Vá em **SQL Editor** (no menu lateral)
4. Clique em **New Query**
5. Copie e cole o conteúdo do arquivo `supabase_schema.sql`
6. Clique em **Run** para executar o SQL

## Passo 1.5: Criar as Tabelas de Administração

1. No mesmo SQL Editor
2. Copie e cole o conteúdo do arquivo `supabase_admin_schema.sql`
3. Clique em **Run** para executar o SQL

## Passo 2: Configurar RLS (Row Level Security)

Após criar as tabelas, execute o arquivo `supabase_rls_setup.sql` para configurar as políticas de segurança:

1. No SQL Editor do Supabase
2. Copie e cole o conteúdo de `supabase_rls_setup.sql`
3. Clique em **Run**

Isso permitirá que a service_role key insira dados nas tabelas.

## Passo 3: Verificar as Tabelas

Após executar os SQLs, você deve ver duas tabelas criadas:

- `debates` - Armazena informações dos debates
- `messages` - Armazena todas as mensagens de cada debate

## Passo 4: Configurar Variáveis de Ambiente (Opcional)

As credenciais já estão configuradas no código, mas você pode adicionar ao `.env`:

```env
SUPABASE_URL=https://qkdhwwiohaqacojiijya.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFrZGh3d2lvaGFxYWNvamlpanlhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MzQ5NzgzOCwiZXhwIjoyMDc5MDczODM4fQ.t1ywCrcYDy6J_GWGOQJr4iEtqwfXF-i-7lIOz9wYvPc
```

## Estrutura das Tabelas

### Tabela `debates`
- `id` (UUID) - ID único do debate
- `pergunta` (TEXT) - Pergunta do debate
- `selected_agents` (TEXT[]) - Array com IDs dos agentes selecionados
- `num_rodadas` (INTEGER) - Número de rodadas do debate
- `sintese` (TEXT) - Síntese final do debate
- `created_at` (TIMESTAMP) - Data de criação
- `updated_at` (TIMESTAMP) - Data de atualização

### Tabela `messages`
- `id` (UUID) - ID único da mensagem
- `debate_id` (UUID) - Referência ao debate
- `type` (TEXT) - Tipo: 'user', 'agent', 'round', 'question', 'sintese', 'sintese_conteudo'
- `content` (TEXT) - Conteúdo da mensagem
- `agent_id` (TEXT) - ID do agente (se aplicável)
- `agent_name` (TEXT) - Nome do agente
- `agent_role` (TEXT) - Papel do agente
- `round_number` (INTEGER) - Número da rodada
- `timestamp` (TIMESTAMP) - Data/hora da mensagem
- `order_index` (INTEGER) - Ordem da mensagem no debate

### Tabela `agents` (Admin)
- `id` (UUID) - ID único do agente
- `name` (VARCHAR) - Nome do agente
- `avatar` (VARCHAR) - Emoji ou URL do avatar
- `color` (VARCHAR) - Cor hexadecimal
- `role` (TEXT) - Papel do agente
- `goal` (TEXT) - Objetivo do agente
- `backstory` (TEXT) - História/personalidade
- `llm_provider` (VARCHAR) - Provedor de LLM
- `llm_model` (VARCHAR) - Modelo de LLM
- `temperature` (DECIMAL) - Temperatura do modelo
- `max_tokens` (INTEGER) - Máximo de tokens
- `verbose` (BOOLEAN) - Modo verbose
- `allow_delegation` (BOOLEAN) - Permitir delegação
- `status` (VARCHAR) - Status (active/inactive)
- `tags` (TEXT[]) - Tags do agente
- `description` (TEXT) - Descrição opcional
- `total_debates` (INTEGER) - Total de debates participados
- `last_used` (TIMESTAMP) - Última vez usado

### Tabela `llm_providers` (Admin)
- `id` (UUID) - ID único
- `provider` (VARCHAR) - Nome do provedor
- `api_key_encrypted` (TEXT) - Chave API criptografada
- `status` (VARCHAR) - Status
- `config` (JSONB) - Configurações específicas
- `usage_stats` (JSONB) - Estatísticas de uso

## Endpoints da API

Após a configuração, os seguintes endpoints estarão disponíveis:

- `POST /api/debate/start` - Inicia um debate e salva no banco
- `GET /api/debate/{debate_id}` - Recupera um debate salvo
- `GET /api/debates` - Lista debates recentes
- `DELETE /api/debate/{debate_id}` - Deleta um debate

## Testando

Após criar as tabelas, inicie o servidor:

```bash
python api_server.py
```

Ao iniciar um debate, ele será automaticamente salvo no Supabase!

## ⚠️ Troubleshooting

Se os dados não estiverem sendo salvos:

1. **Verifique se as tabelas existem**: O servidor mostrará um aviso na inicialização
2. **Verifique RLS**: Execute `supabase_rls_setup.sql` se ainda não executou
3. **Verifique os logs**: O servidor Python mostrará logs detalhados de cada tentativa de salvamento
4. **Verifique as credenciais**: Certifique-se de que a service_role key está correta

Os logs do servidor mostrarão exatamente onde está o problema!

