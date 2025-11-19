-- Script para configurar RLS (Row Level Security) no Supabase
-- Execute este SQL APÓS criar as tabelas com supabase_schema.sql

-- IMPORTANTE: Se você está usando service_role key, pode desabilitar RLS
-- OU criar políticas que permitam inserções

-- Opção 1: Desabilitar RLS (mais simples para desenvolvimento)
-- Descomente as linhas abaixo se quiser desabilitar RLS:
-- ALTER TABLE debates DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE messages DISABLE ROW LEVEL SECURITY;

-- Opção 2: Habilitar RLS mas permitir todas as operações para service_role
-- (Recomendado para produção com service_role)

-- Habilitar RLS
ALTER TABLE debates ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE llm_providers ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_usage_logs ENABLE ROW LEVEL SECURITY;

-- Criar políticas que permitem todas as operações
-- (Isso permite que a service_role key funcione)

-- Políticas para debates
CREATE POLICY "Allow all operations on debates" ON debates
  FOR ALL
  USING (true)
  WITH CHECK (true);

-- Políticas para messages
CREATE POLICY "Allow all operations on messages" ON messages
  FOR ALL
  USING (true)
  WITH CHECK (true);

-- Políticas para agents
CREATE POLICY "Allow all operations on agents" ON agents
  FOR ALL
  USING (true)
  WITH CHECK (true);

-- Políticas para llm_providers
CREATE POLICY "Allow all operations on llm_providers" ON llm_providers
  FOR ALL
  USING (true)
  WITH CHECK (true);

-- Políticas para agent_usage_logs
CREATE POLICY "Allow all operations on agent_usage_logs" ON agent_usage_logs
  FOR ALL
  USING (true)
  WITH CHECK (true);

-- Verificar se as políticas foram criadas
SELECT * FROM pg_policies WHERE tablename IN ('debates', 'messages', 'agents', 'llm_providers', 'agent_usage_logs');

