CASE TÉCNICO DATA & AI

Chat com Documentos via IA

Retrieval-Augmented Generation com busca semântica em Redis

Vaga: Software Engineer Pleno Data & Al (Generalista)
Modalidade: Híbrido Brasil
Prazo de entrega: 5 dias úteis após recebimento
Entrega via: Repositório GitHub com README completo
Contato: Recrutamento Pipefy - Data & Al Team

1. Contexto do Desafio

A Pipefy é uma plataforma de automação de processos usada por mais de 4.000 empresas em 150 países. Nosso time de Data & Al está expandindo suas capacidades de inteligência artificial e busca profissionais capazes de construir produtos que conectam dados, modelos de linguagem e experiências de usuário de ponta a ponta.

Neste case, você irá construir uma solução conversacional completa que permite usuários fazerem upload de documentos e interagirem com eles via chat utilizando busca semântica e geração aumentada por recuperação (RAG - Retrieval-Augmented Generation).

Por que este desafio?
Este projeto simula situações reais do nosso dia a dia: construir pipelines de ingestão de dados, expor APIs confiáveis, integrar LLMs e entregar interfaces funcionais. Queremos avaliar sua capacidade de transitar entre todas essas camadas com autonomia e qualidade de código.

2. Objetivo

Construir uma aplicação full-stack com três componentes principais:

Upload e vetorização de documentos em uma base Redis com busca vetorial.

API conversacional (FastAPI) que responde perguntas usando RAG sobre os documentos indexados.

Interface de chat em React JS para o usuário interagir com a solução de forma intuitiva.

3. Arquitetura da Solução e Tecnologias

A solução deve ser 100% containerizada via Docker.

Frontend: React, Vite ou CRA, Tailwind ou MUI (Chat UI com upload de arquivos e histórico de conversa).

API: Python 3.11+, FastAPI, LangChain (Endpoints de ingestão e chat com RAG).

Vector Store: Redis Stack (RedisSearch) (Armazenamento e busca de embeddings).

LLM: OpenAI GPT-4o ou Claude Sonnet (Anthropic) (Geração de respostas contextualizadas).

Orquestração: LangChain / LangGraph (Pipeline de ingestão + chain de RAG).

Infraestrutura: Docker Compose (Todos os serviços containerizados).

4. Requisitos Técnicos

4.1 Camada de Dados (Ingestão e Vetorização)

O serviço de ingestão deve processar documentos e armazená-los como vetores no Redis:

Formatos suportados: PDF e TXT (mínimo obrigatório).

Chunking: Processar o texto com overlap configurável (ex: chunks de 500 tokens, overlap de 50).

Embeddings: Utilizar a API OpenAI (text-embedding-ada-002 ou text-embedding-3-small) ou via Sentence Transformers (open-source).

Armazenamento: Salvar os vetores no Redis Stack utilizando o módulo RedisSearch com índice vetorial (HNSW ou FLAT).

Metadados: Persistir nome do arquivo, data de upload, número do chunk e texto original do chunk.

Exemplo de estrutura esperada no Redis (doc:{file_id}:chunk:{n}):

{
  "content": "...texto do chunk...",
  "embedding": [...vetor float32...],
  "source": "relatorio_q3.pdf",
  "chunk_index": 3,
  "uploaded_at": "2025-05-08T10:00:00Z"
}


4.2 API (FastAPI com RAG)

A API deve expor os seguintes endpoints:

POST /upload: Recebe arquivo(s) e dispara pipeline de ingestão. Retorna: { file_id, chunks_indexed, status }

GET /documents: Lista documentos indexados na base. Retorna: [{ file_id, name, uploaded_at, chunks }]

DELETE /documents/{id}: Remove documento e seus vetores do Redis. Retorna: { deleted: true }

POST /chat: Recebe pergunta e retorna resposta com RAG. Retorna: { answer, sources: [...] }

GET /health: Health check da API e conectividade Redis. Retorna: { status: 'ok', redis: 'connected' }

Regras de Negócio da API:

O endpoint /chat deve implementar o fluxo RAG completo: embedding da query -> busca vetorial no Redis -> construção do prompt com contexto -> chamada ao LLM -> retorno da resposta com as fontes utilizadas.

Utilizar LangChain para orquestrar o pipeline de RAG (RetrievalQA ou LCEL).

Dar suporte a histórico de conversa por sessão (armazenar últimas N mensagens para contexto).

Respostas do chat devem incluir o campo sources com os trechos e documentos utilizados.

Utilizar variáveis de ambiente para configuração (chaves de API, URL do Redis, modelo LLM).

4.3 Frontend (React JS)

A interface deve ser funcional e clara (não é exigido design sofisticado, mas usabilidade e organização). Uma SPA simples é suficiente (sem necessidade de SSR como Next.js).

Features:

Tela de upload de arquivos (drag-and-drop ou seletor) com indicador de progresso.

Lista de documentos indexados com opção de remoção.

Interface de chat com histórico de mensagens, campo de input (suporte a Enter) e indicador de carregamento.

Exibição das fontes utilizadas em cada resposta (via collapse ou tooltip).

Stack Sugerida: Vite/CRA, Context API/Zustand/Redux, Tailwind/MUI/CSS Modules, Axios/Fetch.

4.4 Infraestrutura e Docker

Todos os serviços devem ser orchestrados via Docker Compose. O projeto deve rodar localmente com um único comando: docker-compose up --build.

Necessário Dockerfile para API e para o Frontend (build estático servido via Nginx ou node).

Variáveis de ambiente via .env (não commitar chaves).

Volumes configurados para persistência do Redis e health checks com depends_on.

4.5 Testes Unitários

Utilize pytest como framework principal de testes. Cobertura mínima esperada: 60% do código de backend.

Testar os serviços de processamento (chunking, embeddings com mock, indexação no Redis).

Testar endpoints da FastAPI utilizando httpx e TestClient.

Testar pipeline RAG com mocks para Redis e LLM (evitar chamadas reais na API de testes).

Incluir um Makefile ou script (ex: make test ou ./run_tests.sh).

5. Estrutura Esperada do Repositório

my-rag-app/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routers/
│   │   ├── services/
│   │   ├── models/
│   │   └── config.py
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── .env.example
├── Makefile
└── README.md


6. Dicas de Implementação do Redis Vector Search

A imagem Docker redis/redis-stack:latest já inclui o RedisSearch. Defina o índice com a métrica COSINE.

from redis import Redis
from redis.commands.search.field import VectorField, TextField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType

r = Redis(host='redis', port=6379)
schema = (
    TextField('content'),
    TextField('source'),
    VectorField('embedding', 'HNSW', {
        'TYPE': 'FLOAT32',
        'DIM': 1536,
        'DISTANCE_METRIC': 'COSINE'
    })
)
r.ft('docs').create_index(schema, definition=IndexDefinition(prefix=['doc:'], index_type=IndexType.HASH))


9.4 Soluções Open-Source aceitas

Caso não tenha créditos em APIs pagas, a solução pode ser 100% open-source:

Embeddings: sentence-transformers (all-MiniLM-L6-v2) - roda localmente, sem custo.

LLM: Ollama com modelos locais (llama3:8b, mistral:7b).

O importante é que a arquitetura RAG funcione corretamente.

10. Implementações de Diferencial

Não obrigatórias, mas valorizadas na avaliação:

Streaming de respostas (Server-Sent Events ou WebSocket) para o frontend exibir a resposta em tempo real.

Suporte a múltiplos arquivos simultâneos no mesmo contexto de chat.

Remoção de documentos com limpeza dos vetores correspondentes no Redis.

Deploy em nuvem (GCP Cloud Run, Railway, Render ou similar) com link funcional.

Pipeline de Cl com GitHub Actions executando os testes a cada push.

Uso de LangGraph para o pipeline de RAG ao invés de chains simples.

Suporte a arquivos DOCX além de PDF e TXT.

Interface com suporte a múltiplas sessões de chat com nomes customizáveis.

11. Dúvidas

Caso tenha dúvidas sobre o escopo ou requisitos do case, entre em contato com o time de recrutamento antes de iniciar a implementação. Perguntas técnicas sobre decisões de arquitetura são bem-vindas e também fazem parte da avaliação - demonstram raciocínio e capacidade de comunicação.

Boa sorte estamos ansiosos para ver o que você vai construir.