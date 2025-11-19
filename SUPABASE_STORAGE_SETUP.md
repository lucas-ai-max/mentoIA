# 📦 Configuração do Supabase Storage para Avatares

Este guia explica como configurar o Supabase Storage para armazenar as fotos dos mentores.

## 📋 Passo a Passo

### 1. Criar o Bucket no Supabase

1. Acesse o [Supabase Dashboard](https://app.supabase.com)
2. Selecione seu projeto
3. Vá para **Storage** no menu lateral
4. Clique em **New bucket**
5. Configure:
   - **Name**: `agent-avatars`
   - **Public bucket**: ✅ Marque esta opção (permite acesso público às imagens)
6. Clique em **Create bucket**

### 2. Configurar Políticas de Acesso (Opcional)

Execute este SQL no **SQL Editor** do Supabase para configurar políticas de acesso:

```sql
-- Política para permitir leitura pública
CREATE POLICY "Public Access" ON storage.objects
FOR SELECT USING (bucket_id = 'agent-avatars');

-- Política para permitir upload (apenas service_role)
-- Nota: Com service_role key, você já tem acesso total, mas isso é útil para RLS
CREATE POLICY "Service Role Upload" ON storage.objects
FOR INSERT WITH CHECK (bucket_id = 'agent-avatars');
```

**Nota**: Se você estiver usando a `service_role_key`, essas políticas podem não ser necessárias, mas são recomendadas para segurança.

### 3. Atualizar Schema do Banco de Dados

Execute o arquivo `supabase_update_avatar_schema.sql` no SQL Editor do Supabase:

```sql
-- Alterar campo avatar para TEXT (suporta URLs longas do Supabase Storage)
ALTER TABLE agents 
ALTER COLUMN avatar TYPE TEXT;
```

### 4. Verificar Configuração

Após configurar:

1. ✅ Bucket `agent-avatars` criado e público
2. ✅ Campo `avatar` na tabela `agents` alterado para `TEXT`
3. ✅ Políticas de acesso configuradas (opcional)

## 🎯 Como Funciona

1. **Upload**: Quando você faz upload de uma imagem no formulário de agente, ela é enviada para o endpoint `/api/admin/upload-avatar`
2. **Armazenamento**: A imagem é salva no bucket `agent-avatars` do Supabase Storage
3. **URL**: Uma URL pública é gerada e salva no campo `avatar` da tabela `agents`
4. **Exibição**: A URL é usada para exibir a imagem em toda a aplicação

## 📝 Estrutura de Arquivos

As imagens são organizadas assim no Storage:
```
agent-avatars/
  └── avatars/
      ├── uuid-1.jpg
      ├── uuid-2.png
      └── ...
```

## ⚠️ Notas Importantes

- **Tamanho máximo**: 5MB por imagem
- **Formatos aceitos**: Qualquer formato de imagem (jpg, png, gif, webp, etc.)
- **URLs públicas**: As imagens são acessíveis publicamente via URL
- **Backup**: As imagens ficam armazenadas no Supabase Storage, não no banco de dados

## 🔧 Troubleshooting

### Erro: "Bucket not found"
- Verifique se o bucket `agent-avatars` foi criado
- Confirme que o nome está exatamente como `agent-avatars`

### Erro: "Permission denied"
- Verifique se o bucket está marcado como público
- Confirme que a `service_role_key` está configurada corretamente no `.env`

### Erro: "Image too large"
- Reduza o tamanho da imagem (máx 5MB)
- Use ferramentas de compressão de imagem se necessário

## ✅ Pronto!

Após seguir estes passos, você poderá fazer upload de fotos dos mentores e elas serão salvas no Supabase Storage!

