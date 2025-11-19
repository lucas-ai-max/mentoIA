-- Schema SQL para atualizar campo avatar para suportar URLs de imagens
-- Execute este SQL no SQL Editor do Supabase

-- Alterar campo avatar para TEXT (suporta URLs longas do Supabase Storage)
ALTER TABLE agents 
ALTER COLUMN avatar TYPE TEXT;

-- Comentário
COMMENT ON COLUMN agents.avatar IS 'URL da imagem do avatar (Supabase Storage) ou emoji';

