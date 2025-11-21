-- Schema SQL para criar as tabelas de administração no Supabase
-- Execute este SQL no SQL Editor do Supabase APÓS criar as tabelas principais

-- Tabela de agentes
CREATE TABLE IF NOT EXISTS agents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  avatar VARCHAR(500),
  color VARCHAR(7),
  role TEXT NOT NULL,
  goal TEXT NOT NULL,
  backstory TEXT NOT NULL,
  llm_provider VARCHAR(50) NOT NULL,
  llm_model VARCHAR(100) NOT NULL,
  temperature DECIMAL(3,2) DEFAULT 0.7,
  max_tokens INTEGER DEFAULT 1000,
  "verbose" BOOLEAN DEFAULT TRUE,
  allow_delegation BOOLEAN DEFAULT FALSE,
  status VARCHAR(20) DEFAULT 'active',
  tags TEXT[],
  description TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_by UUID,
  total_debates INTEGER DEFAULT 0,
  last_used TIMESTAMP WITH TIME ZONE
);

-- Tabela de provedores de LLM
CREATE TABLE IF NOT EXISTS llm_providers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  provider VARCHAR(50) UNIQUE NOT NULL,
  api_key_encrypted TEXT,
  status VARCHAR(20) DEFAULT 'active',
  config JSONB,
  usage_stats JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de logs de uso de agentes
CREATE TABLE IF NOT EXISTS agent_usage_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
  debate_id UUID REFERENCES debates(id) ON DELETE SET NULL,
  tokens_used INTEGER,
  cost DECIMAL(10,4),
  response_time_ms INTEGER,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
CREATE INDEX IF NOT EXISTS idx_agents_llm_provider ON agents(llm_provider);
CREATE INDEX IF NOT EXISTS idx_agents_created_at ON agents(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_usage_logs_agent_id ON agent_usage_logs(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_usage_logs_debate_id ON agent_usage_logs(debate_id);
CREATE INDEX IF NOT EXISTS idx_agent_usage_logs_created_at ON agent_usage_logs(created_at DESC);

-- Tabela de configurações gerais do sistema
CREATE TABLE IF NOT EXISTS system_settings (
  key TEXT PRIMARY KEY,
  value JSONB NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_system_settings_key ON system_settings(key);

-- Comentários
COMMENT ON TABLE agents IS 'Armazena configurações dos agentes de debate';
COMMENT ON TABLE llm_providers IS 'Armazena configurações dos provedores de LLM';
COMMENT ON TABLE agent_usage_logs IS 'Logs de uso e performance dos agentes';
COMMENT ON TABLE system_settings IS 'Armazena configurações gerais como limites, segurança e preferências do painel';

