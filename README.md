# Chat-Pipefy 🚀
> **Desafio Técnico: Data & AI Software Engineer (Pipefy)**

Um sistema completo de **Retrieval-Augmented Generation (RAG)** de alta performance que permite fazer upload de documentos e interagir com eles por chat com respostas baseadas em contexto e referências às fontes originais.

A aplicação foi projetada focando em **latência extremamente baixa**, **eficiência de custos** e **robustez arquitetural**, utilizando uma estratégia híbrida: embeddings locais combinados com processamento em nuvem ultraveloz via **Groq**.

---

## 🛠️ O que o Projeto Faz (Features de Destaque)

- **Upload Multiformato:** Suporte a arquivos `.pdf`, `.txt` e `.docx`.
- **Busca Semântica Híbrida:** Vetorização automática local e busca rápida por similaridade de cosseno usando Redis Stack.
- **Respostas por Streaming (SSE):** Respostas geradas token a token em tempo real.
- **Histórico Isolado por Sessão:** Mantém o contexto da conversa baseado em sessões ativas do usuário.
- **Rastreabilidade de Fontes:** Exibe exatamente os trechos dos documentos usados pelo modelo para formular cada resposta.
- **Gerenciamento de Documentos:** Lista dinâmica de arquivos indexados e deleção em cascata (remove o registro físico e limpa todos os vetores órfãos do Redis).

---

## 🏗️ Arquitetura do Sistema

O projeto adota uma arquitetura distribuída, 100% containerizada via Docker Compose:

```
                  ┌──────────────────────┐
                  │       Frontend       │
                  │ (React + Vite + TS)  │
                  └──────────┬───────────┘
                             │ (Port 80)
                             ▼ (HTTP / Server-Sent Events)
                  ┌──────────────────────┐
                  │    Backend API       │
                  │      (FastAPI)       │
                  └──────┬────────────┬──┘
             (Port 8000) │            │
                         │            │ (Conexão TCP)
                         ▼            ▼
   ┌───────────────────────┐        ┌───────────────────────┐
   │    Local Embeddings   │        │     Vector Store      │
   │ (SentenceTransformer  │        │   (Redis Stack HNSW)  │
   │    all-MiniLM-L6-v2)  │        └───────────────────────┘
   └───────────────────────┘
                         │
                         ▼ (HTTPS / API)
   ┌───────────────────────┐
   │    Groq LPU Cloud     │
   │      (Llama 3.3)      │
   └───────────────────────┘
```

### Decisões Arquiteturais Relevantes (Diferenciais Técnicos)

1. **Abordagem Groq-Hybrid (Eficiência e Baixo Custo):** 
   Utilizamos a biblioteca open-source `SentenceTransformers` rodando diretamente na CPU do container FastAPI para gerar embeddings locais (vetor de **384 dimensões**). A inferência é terceirizada para os chips LPU da **Groq Cloud** usando o modelo **Llama 3.3**. Isso elimina custos com APIs de embeddings (como OpenAI) e evita limites de cota (*Rate Limits*), mantendo a latência global abaixo de 1 segundo.
2. **Redis como Banco Vetorial:** 
   Optou-se pelo módulo **RedisSearch** com indexação **HNSW (Hierarchical Navigable Small World)** e distância **Cosseno**. Isso garante pesquisas de vizinhos mais próximos em tempo sub-milissegundo, mesmo com o aumento do volume de documentos.
3. **Orquestração LCEL:** 
   O pipeline do RAG é estruturado usando **LangChain Expression Language (LCEL)**, garantindo modularidade para troca fácil de modelos/parâmetros, além de facilitação nativa para streaming.

---

## 🚀 Instalação e Execução (Quick Start)

### Pré-requisitos
- [Docker](https://docs.docker.com/get-docker/) instalado.
- Uma chave de API gratuita da [Groq Cloud](https://console.groq.com/).

### 1. Clonar e Configurar
```bash
git clone https://github.com/seu-usuario/chat-pipefy.git
cd chat-pipefy

# Copiar o arquivo de exemplo de variáveis de ambiente
cp .env.example .env
```

Edite o seu arquivo `.env` recém-criado e adicione sua chave da Groq:
```env
LLM_PROVIDER=groq-hybrid
GROQ_API_KEY=gsk_suachaveaqui...
```

### 2. Inicializar os Containers
Execute o comando abaixo para construir as imagens e subir os serviços:
```bash
docker compose up --build -d
```

Este comando iniciará:
- **`chat-pipefy-redis`** (Porta 6379 / Interface Visual RedisInsight na porta 8001)
- **`chat-pipefy-backend`** (Porta 8000 / Documentação Swagger na porta 8000/docs)
- **`chat-pipefy-frontend`** (Porta 80 / Aplicação Web React)

### 3. Acessar a Aplicação
- **Interface Gráfica (Web):** [http://localhost](http://localhost)
- **Documentação de Rotas (FastAPI):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Explorador do Redis (RedisInsight):** [http://localhost:8001](http://localhost:8001)

---

## 🧪 Rodando os Testes e Cobertura (Coverage)

A suíte de testes unitários cobre integralmente o pipeline de ingestão, as APIs e as mocks de comunicação com Redis e LLM externos.

Para rodar os testes localmente via Docker (garantindo que não haverá incompatibilidade de bibliotecas no seu ambiente local):

```bash
# Executa todos os testes com relatório detalhado de cobertura de linhas
docker compose exec backend pytest --cov=app --cov-report=term-missing
```

### Resumo de Cobertura do Backend
Atualmente os testes alcançam **85% de cobertura global**, ultrapassando com folga o limite mínimo de 60% exigido no edital:

```text
Name                           Stmts   Miss  Cover   Missing
------------------------------------------------------------
app/config.py                     38      5    87%   70-74
app/main.py                       25      2    92%   56-57
app/routers/chat.py               11      0   100%
app/routers/documents.py          13      0   100%
app/routers/upload.py             41      7    83%   40, 92, 101-105
app/services/embeddings.py        34     14    59%   33-43, 57, 65-74, 88-89
app/services/ingestion.py         48      5    90%   37-41
app/services/rag.py               77     16    79%   56-86, 96, 131-132, 150-151
app/services/vector_store.py      84     14    83%   46-72, 176, 221-225
------------------------------------------------------------
TOTAL                            412     63    85%
```

---

## 🔍 Detalhes de Implementação para Avaliadores

### Estrutura de Chunks e Indexação no Redis
Os dados são fragmentados dinamicamente em blocos de texto respeitando os limites de tokens e overlaps configurados no `.env`. A estrutura persistida no Redis é mantida sob chaves do tipo `doc:{file_id}:chunk:{chunk_index}` contendo os seguintes campos em formato Hash:

```json
{
  "content": "Conteúdo extraído em texto plano...",
  "embedding": "Vetor binário Float32 (384 dimensões)",
  "source": "manual_colaborador.pdf",
  "file_id": "8de3229e-937e-42a6-8d63-bb487fe1ab08",
  "chunk_index": 0,
  "uploaded_at": "2026-07-04T00:12:05Z"
}
```

### Fluxo de Limpeza e Persistência
Quando um documento é removido pelo frontend, a rota `DELETE /documents/{id}` executa uma consulta rápida no Redis para encontrar todas as chaves associadas ao prefixo `doc:{id}:*` e efetua a remoção em massa, limpando o armazenamento e o índice vetorial de forma síncrona.

---
Desenvolvido por **Eliezer Queiroz** para o processo seletivo de **Software Engineer Pleno Data & AI da Pipefy**.