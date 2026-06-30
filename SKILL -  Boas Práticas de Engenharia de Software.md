---
name: Boas Práticas de Engenharia de Software (Global)
description: Diretrizes obrigatórias e avançadas para a criação e manutenção de projetos, englobando segurança, arquitetura, testes e documentação.
---

# Diretrizes para Projetos de Software

Sempre que atuar em um projeto (criando do zero ou modificando), você DEVE aplicar rigorosamente as seguintes boas práticas de engenharia de software:

## 1. Segurança e Gerenciamento de Segredos (`.env`)
- **NUNCA** faça hardcode de credenciais reais (senhas, chaves de API, tokens) no código-fonte ou em arquivos como `docker-compose.yml`.
- **O arquivo `.env` é o ÚNICO local para dados reais:** Utilize variáveis de ambiente no arquivo `.env` na raiz do projeto para armazenar credenciais válidas. Esse arquivo deve ser IMEDIATAMENTE adicionado ao `.gitignore`.
- **O arquivo `.env_template` DEVE ser sempre FAKE:** Crie e mantenha um `.env_template` (ou `.env.example`). O objetivo dele é **exclusivamente servir de referência** para quem for usar o projeto no futuro. Ele DEVE conter apenas valores ilustrativos, descrições ou placeholders vazios (ex: `GOOGLE_API_KEY=sua_chave_aqui`), e NUNCA dados reais. Este é o arquivo que será comitado no repositório.

## 2. Gerenciamento de Dependências
- Mantenha sempre um arquivo claro com a relação de dependências do projeto.
  - **Python**: Use `requirements.txt`, `pyproject.toml` ou `Pipfile`. Especifique as versões (ex: `requests==2.31.0`) para evitar quebra em atualizações futuras.
  - **Node.js**: Assegure que o `package.json` está atualizado e utilize `npm ci` / `yarn install --frozen-lockfile` em CI/CD.
  - **Outras linguagens**: Siga o padrão do ecossistema (pom.xml, build.gradle, go.mod, etc).

## 3. Arquitetura e Organização de Código
- **Separação de Preocupações (SoC)**: Divida o código em camadas lógicas (ex: Rotas/Controllers, Regras de Negócio/Services, Acesso a Dados/Repositories). 
- **Modularidade**: Funções e classes devem ter uma única responsabilidade (Princípio de Responsabilidade Única - SRP do SOLID).
- **Evite Código Duplicado**: Se um bloco de código se repete em 3 ou mais lugares, extraia-o para uma função ou classe utilitária (DRY - Don't Repeat Yourself).

## 4. Padronização e Formatação
- Utilize formatadores de código e linters configurados no projeto.
  - Ex: `black`/`flake8` para Python, `Prettier`/`ESLint` para JavaScript/TypeScript.
- Mantenha a nomenclatura consistente: use `camelCase`, `snake_case` ou `PascalCase` de acordo com a convenção da linguagem escolhida.
- Escreva nomes de variáveis e funções que deixem claro o que elas fazem, evitando abreviações confusas (`getUserById` ao invés de `getUsr`).
- Todos os comentarios em codigo, logs, descrição de variaveis de ambientes, arquivo README devem ser escritos em ingles

## 5. Testes Automatizados
- Sempre que criar uma nova funcionalidade, considere a criação de testes de unidade e/ou integração para ela.
- Se o projeto já possui testes, garanta que suas alterações não quebrem os testes existentes. Se alterou o comportamento, atualize os testes.
- Tente manter os testes fáceis de ler e independentes uns dos outros.

## 6. Documentação (README)
- Todo projeto DEVE ter um arquivo `README.md` claro.
- O README deve explicar:
  1. O que o projeto faz.
  2. Pré-requisitos (qual versão da linguagem, dependências globais).
  3. Passo a passo para rodar localmente (incluindo a cópia do `.env_template` para `.env`).
  4. Como rodar os testes.