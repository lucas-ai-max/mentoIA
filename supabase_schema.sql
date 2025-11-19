-- Schema SQL para criar as tabelas no Supabase
-- Execute este SQL no SQL Editor do Supabase

-- Tabela de debates
CREATE TABLE IF NOT EXISTS debates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  pergunta TEXT NOT NULL,
  selected_agents TEXT[] NOT NULL,
  num_rodadas INTEGER NOT NULL,
  sintese TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de mensagens
CREATE TABLE IF NOT EXISTS messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  debate_id UUID NOT NULL REFERENCES debates(id) ON DELETE CASCADE,
  type TEXT NOT NULL, -- 'user', 'agent', 'round', 'question', 'sintese', 'sintese_conteudo'
  content TEXT NOT NULL,
  agent_id TEXT,
  agent_name TEXT,
  agent_role TEXT,
  round_number INTEGER,
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  order_index INTEGER NOT NULL
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_messages_debate_id ON messages(debate_id);
CREATE INDEX IF NOT EXISTS idx_messages_order ON messages(debate_id, order_index);
CREATE INDEX IF NOT EXISTS idx_debates_created_at ON debates(created_at DESC);

-- Comentários nas tabelas
COMMENT ON TABLE debates IS 'Armazena informações dos debates realizados';
COMMENT ON TABLE messages IS 'Armazena todas as mensagens de um debate';
COMMENT ON COLUMN messages.type IS 'Tipo da mensagem: user, agent, round, question, sintese, sintese_conteudo';
COMMENT ON COLUMN messages.order_index IS 'Ordem da mensagem no debate';

