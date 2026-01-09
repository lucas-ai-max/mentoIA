# 🚀 Guia de Deploy no Google Cloud Run

Este guia explica como fazer deploy do backend Python no Google Cloud Run e conectar ao frontend na Vercel.

## 📋 Pré-requisitos

1. Conta no Google Cloud Platform (GCP)
2. **Billing habilitado no projeto GCP** ⚠️ **OBRIGATÓRIO**
3. Projeto no GitHub
4. Conta na Vercel (para o frontend)
5. Google Cloud SDK instalado (opcional, para deploy manual)

> **⚠️ IMPORTANTE:** O Google Cloud requer billing habilitado para usar Artifact Registry e Cloud Run. 
> - Cloud Run oferece um tier gratuito generoso (2 milhões de requisições/mês)
> - Artifact Registry também tem tier gratuito (0.5 GB de armazenamento)
> - [Habilitar billing](https://console.developers.google.com/billing/enable)

## 🔧 Passo 1: Configurar Google Cloud

### 1.1 Criar/Selecionar Projeto

1. Acesse: https://console.cloud.google.com/
2. Crie um novo projeto ou selecione um existente
3. Anote o **Project ID** (você vai precisar dele)

### 1.2 Habilitar Billing ⚠️ OBRIGATÓRIO

1. Acesse: https://console.developers.google.com/billing/enable
2. Selecione seu projeto
3. Escolha uma conta de billing ou crie uma nova
4. **Nota:** Cloud Run tem tier gratuito generoso, então você não será cobrado a menos que exceda os limites gratuitos

### 1.3 Ativar APIs Necessárias

1. Vá em **APIs e Serviços > Biblioteca**
2. Ative as seguintes APIs:
   - **Cloud Run API**
   - **Cloud Build API**
   - **Artifact Registry API** (substitui Container Registry)

### 1.4 Criar Conta de Serviço (para CI/CD)

1. Vá em **IAM e Administração > Contas de Serviço**
2. Clique em **Criar Conta de Serviço**
3. Nome: `cloud-run-deployer`
4. Função: **Cloud Run Admin** e **Storage Admin**
5. Crie e baixe a chave JSON (salve como `gcp-key.json`)

## 🐳 Passo 2: Deploy Manual (Primeira Vez)

### 2.1 Instalar Google Cloud SDK

**Windows:**
```powershell
# Baixe e instale de: https://cloud.google.com/sdk/docs/install
# Ou use Chocolatey:
choco install gcloudsdk
```

**Mac/Linux:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### 2.2 Autenticar

```bash
gcloud init
gcloud auth login
gcloud config set project SEU-PROJECT-ID
```

### 2.3 Fazer Build e Deploy

```bash
# Definir variáveis
export PROJECT_ID="seu-projeto-id"
export SERVICE_NAME="mentoia-api"
export REGION="us-central1"

# Build da imagem
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy no Cloud Run
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 600 \
  --max-instances 10 \
  --set-env-vars "ALLOWED_ORIGINS=https://web-rust-pi-54.vercel.app,http://localhost:3000" \
  --set-env-vars "SUPABASE_URL=sua-url-supabase" \
  --set-env-vars "SUPABASE_SERVICE_ROLE_KEY=sua-key-supabase"
```

### 2.4 Obter URL do Serviço

Após o deploy, você receberá uma URL como:
```
https://mentoia-api-xxxxx-uc.a.run.app
```

**Anote esta URL!** Você vai precisar dela para configurar o frontend.

## ⚙️ Passo 3: Configurar Variáveis de Ambiente

### 3.1 No Console do Google Cloud

1. Vá em **Cloud Run > mentoia-api > Editar e reimplantar**
2. Clique em **Variáveis e segredos**
3. Adicione as seguintes variáveis:

| Variável | Valor | Descrição |
|----------|-------|-----------|
| `ALLOWED_ORIGINS` | `https://web-rust-pi-54.vercel.app,http://localhost:3000` | URLs permitidas para CORS |
| `SUPABASE_URL` | Sua URL do Supabase | URL do projeto Supabase |
| `SUPABASE_SERVICE_ROLE_KEY` | Sua chave de serviço | Service role key do Supabase |
| `OPENAI_API_KEY` | Sua chave OpenAI | (Opcional) Se usar OpenAI |
| `ANTHROPIC_API_KEY` | Sua chave Anthropic | (Opcional) Se usar Claude |

### 3.2 Ou via linha de comando

```bash
# IMPORTANTE: Substitua 'southamerica-east1' pela região onde seu serviço está deployado
# Para verificar a região: gcloud run services list
gcloud run services update mentoia-api \
  --region southamerica-east1 \
  --update-env-vars "ALLOWED_ORIGINS=https://web-rust-pi-54.vercel.app,http://localhost:3000,SUPABASE_URL=sua-url,SUPABASE_SERVICE_ROLE_KEY=sua-key"
```

**Nota:** O código agora inclui `https://web-rust-pi-54.vercel.app` por padrão, mas você ainda precisa atualizar a variável de ambiente no Cloud Run se já estiver deployado.

## 🔄 Passo 4: Configurar CI/CD Automático (GitHub Actions)

### 4.1 Configurar Secrets no GitHub

1. Vá no seu repositório GitHub
2. **Settings > Secrets and variables > Actions**
3. Adicione os seguintes secrets:

| Secret | Valor |
|--------|-------|
| `GCP_PROJECT_ID` | ID do seu projeto GCP |
| `GCP_SA_KEY` | Conteúdo completo do arquivo JSON da conta de serviço |
| `SUPABASE_URL` | URL do Supabase |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key do Supabase |
| `ALLOWED_ORIGINS` | `https://web-rust-pi-54.vercel.app,http://localhost:3000` |

### 4.2 Como obter o conteúdo do GCP_SA_KEY

Abra o arquivo JSON da conta de serviço e copie TODO o conteúdo (incluindo chaves `{}`).

### 4.3 Deploy Automático

Agora, sempre que você fizer push para `main`, o deploy será automático!

## 🌐 Passo 5: Configurar Frontend na Vercel

### 5.1 Adicionar Variável de Ambiente

1. No projeto Vercel, vá em **Settings > Environment Variables**
2. Adicione:
   - **Name:** `NEXT_PUBLIC_API_URL`
   - **Value:** `https://mentoia-api-xxxxx-uc.a.run.app` (URL do Cloud Run)
   - **Environment:** Production, Preview, Development

### 5.2 Ou criar `.env.production` no projeto

```env
NEXT_PUBLIC_API_URL=https://mentoia-api-xxxxx-uc.a.run.app
```

### 5.3 Fazer Deploy

```bash
# Se ainda não fez deploy
vercel

# Ou fazer push para o GitHub (se configurou integração)
git push origin main
```

## ✅ Passo 6: Testar

### 6.1 Testar Backend

```bash
# Health check
curl https://mentoia-api-xxxxx-uc.a.run.app/api/health

# Deve retornar: {"status":"ok"}
```

### 6.2 Testar Frontend

1. Acesse seu app na Vercel
2. Tente fazer uma requisição (ex: listar agentes)
3. Verifique o console do navegador para erros de CORS

## 🔍 Troubleshooting

### Erro: "This API method requires billing to be enabled"

**Causa:** O projeto GCP não tem billing habilitado.

**Solução:**
1. Acesse: https://console.developers.google.com/billing/enable?project=SEU-PROJECT-ID
2. Substitua `SEU-PROJECT-ID` pelo ID do seu projeto (ex: `1047931843367`)
3. Escolha uma conta de billing ou crie uma nova
4. Aguarde alguns minutos para a propagação
5. Tente o deploy novamente

**Nota:** Cloud Run oferece tier gratuito generoso:
- 2 milhões de requisições/mês
- 360.000 GB-segundos de memória
- 180.000 vCPU-segundos
- Você só será cobrado se exceder esses limites

### Erro: "CORS policy blocked"

**Solução:** Verifique se `ALLOWED_ORIGINS` inclui a URL exata do seu frontend (com `https://`)

### Erro: "Service unavailable"

**Solução:** 
- Verifique se todas as variáveis de ambiente estão configuradas
- Verifique os logs no Cloud Run: **Cloud Run > mentoia-api > Logs**

### Erro: "Build failed"

**Solução:**
- Verifique se o `Dockerfile` está na raiz do projeto
- Verifique se `requirements.txt` está correto
- Veja os logs do build: **Cloud Build > Histórico**

### Erro: "Database connection failed"

**Solução:**
- Verifique se `SUPABASE_URL` e `SUPABASE_SERVICE_ROLE_KEY` estão corretos
- Verifique se o Supabase permite conexões do Cloud Run

## 💰 Custos Estimados

- **Cloud Run:** 
  - Primeiros 2 milhões de requisições/mês: **GRÁTIS**
  - Após: ~$0.40 por milhão de requisições
  - CPU/Memória: cobrado apenas quando em uso

- **Container Registry:**
  - Primeiros 0.5 GB: **GRÁTIS**
  - Após: ~$0.026/GB/mês

**Estimativa para uso baixo/médio: $0-5/mês**

## 📚 Recursos Úteis

- [Documentação Cloud Run](https://cloud.google.com/run/docs)
- [Preços Cloud Run](https://cloud.google.com/run/pricing)
- [GitHub Actions para GCP](https://github.com/google-github-actions)

## 🎉 Pronto!

Seu backend está rodando no Cloud Run e conectado ao frontend na Vercel!

