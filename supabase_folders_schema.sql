-- Schema SQL para adicionar suporte a pastas no Supabase
-- Execute este SQL no SQL Editor do Supabase

-- Tabela de pastas
CREATE TABLE IF NOT EXISTS folders (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  icon TEXT,
  color TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  user_id TEXT -- Para suporte futuro a múltiplos usuários
);

-- Adicionar coluna folder_id na tabela debates (se ainda não existir)
DO $$ 
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'debates' AND column_name = 'folder_id'
  ) THEN
    ALTER TABLE debates ADD COLUMN folder_id UUID REFERENCES folders(id) ON DELETE SET NULL;
  END IF;
END $$;

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_debates_folder_id ON debates(folder_id);
CREATE INDEX IF NOT EXISTS idx_folders_created_at ON folders(created_at DESC);

-- Comentários
COMMENT ON TABLE folders IS 'Armazena pastas para organização de debates';
COMMENT ON COLUMN debates.folder_id IS 'ID da pasta à qual o debate pertence (NULL = sem pasta)';

