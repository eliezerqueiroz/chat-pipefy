# SDD Playbook V3

## Spec-Driven Development Agent Framework

---

# Missão

Este documento define o sistema operacional de desenvolvimento utilizado por agentes de IA e equipes humanas.

Seu objetivo é garantir que todo desenvolvimento seja orientado por especificações, arquitetura, validações e decisões rastreáveis.

A especificação é a fonte da verdade.

O código é apenas a implementação da especificação.

---

# Princípios Fundamentais

## 1. Specification First

Nenhuma implementação deve iniciar sem uma especificação.

---

## 2. Clarify Before Build

Se existir ambiguidade:

* Pare
* Questione
* Aguarde resposta

Nunca assumir requisitos.

---

## 3. Plan Before Code

Nenhuma implementação deve ocorrer sem planejamento.

---

## 4. Architecture Before Tasks

Arquitetura gera tarefas.

Tarefas geram código.

---

## 5. Test Before Completion

Nenhuma tarefa é concluída sem validação.

---

## 6. Review Before Delivery

Nenhuma entrega é considerada concluída sem revisão.

---

## 7. Decisions Must Be Recorded

Toda decisão arquitetural relevante deve ser documentada.

---

# Estados do Projeto

```text
DISCOVERY
    ↓
SPECIFICATION
    ↓
PLANNING
    ↓
ARCHITECTURE
    ↓
DECISION_RECORDS
    ↓
TASK_BREAKDOWN
    ↓
IMPLEMENTATION
    ↓
TESTING
    ↓
REVIEW
    ↓
DELIVERY
```

---

# Framework de Entrevista

## Objetivo

Antes de gerar qualquer artefato, o agente deve conduzir uma entrevista estruturada.

---

## Bloco 1 - Negócio

Perguntas:

* Qual problema estamos resolvendo?
* Qual objetivo principal?
* Quem é o usuário?
* Como o processo funciona hoje?
* Como o sucesso será medido?
* Quais dores atuais existem?

---

## Bloco 2 - Escopo

Perguntas:

* O que deve ser desenvolvido?
* O que não deve ser desenvolvido?
* Existe prazo?
* Existe orçamento?
* Existem restrições?

---

## Bloco 3 - Tecnologia

Perguntas:

* Linguagem principal?
* Framework principal?
* Banco de dados?
* Cloud provider?
* Ferramentas obrigatórias?
* Ferramentas proibidas?

---

## Bloco 4 - Arquitetura

Perguntas:

* Monólito ou microsserviços?
* APIs externas?
* Filas?
* Cache?
* Autenticação?
* Escalabilidade?

---

## Bloco 5 - Qualidade

Perguntas:

* Cobertura mínima de testes?
* Requisitos de performance?
* Requisitos de segurança?
* SLA?
* Compliance?

---

# Regra de Avanço

O agente não pode avançar para Specification enquanto houver perguntas críticas pendentes.

---

# Discovery Mode

## Objetivo

Compreender completamente o problema.

## Artefato

```text
discovery.md
```

## Estrutura

* Problema
* Objetivo
* Stakeholders
* Contexto
* Restrições
* Riscos
* Definição de sucesso

---

# Specification Mode

## Objetivo

Transformar o conhecimento coletado em requisitos formais.

## Artefato

```text
spec.md
```

## Estrutura

### Contexto

### Objetivo

### Requisitos Funcionais

### Requisitos Não Funcionais

### Restrições

### Critérios de Aceitação

### Fora do Escopo

---

# Planning Mode

## Objetivo

Transformar requisitos em estratégia de execução.

## Artefato

```text
planning.md
```

## Estrutura

* Estratégia
* Dependências
* Sequência de Implementação
* Riscos
* Mitigações

---

# Architecture Mode

## Objetivo

Definir a solução técnica.

## Artefato

```text
architecture.md
```

## Estrutura

### Visão Geral

### Componentes

### Módulos

### Fluxo de Dados

### APIs

### Banco de Dados

### Integrações

### Diagramas

---

# Architecture Decision Records (ADR)

## Objetivo

Registrar decisões arquiteturais importantes.

Toda decisão relevante deve possuir um ADR.

---

## Quando Criar um ADR

Criar ADR quando houver decisão sobre:

* Frameworks
* Linguagens
* Banco de Dados
* Cloud
* Arquitetura
* Integrações
* Segurança
* Observabilidade
* IA / LLMs

---

## Estrutura

Arquivo:

```text
adr/0001-escolha-fastapi.md
```

Template:

```md
# ADR-0001

## Título

Escolha do FastAPI

## Status

Aprovado

## Contexto

Necessidade de API REST performática.

## Opções Consideradas

- Flask
- Django
- FastAPI

## Decisão

Utilizar FastAPI.

## Justificativa

Melhor suporte a tipagem.
Melhor performance.
Documentação OpenAPI nativa.

## Consequências

Necessidade de familiaridade com Pydantic.
```

---

# Task Breakdown Mode

## Objetivo

Transformar arquitetura em tarefas executáveis.

## Artefato

```text
tasks.md
```

## Estrutura

### Task ID

### Objetivo

### Dependências

### Critério de Conclusão

### Critério de Teste

---

# Implementation Mode

## Regras

Implementar apenas uma tarefa por vez.

Não modificar componentes não relacionados.

Gerar testes obrigatoriamente.

Atualizar documentação quando necessário.

---

# Testing Mode

## Objetivo

Validar a implementação.

## Tipos de Teste

* Unitário
* Integração
* Fluxo Principal
* Casos de Erro
* Casos Limite

## Artefato

```text
test-report.md
```

---

# Review Mode

## Objetivo

Garantir aderência ao planejamento.

## Comparar Contra

* discovery.md
* spec.md
* planning.md
* architecture.md
* ADRs
* tasks.md

---

## Checklist

### Requisitos Atendidos

### Critérios de Aceitação Atendidos

### Cobertura de Testes

### Dívida Técnica

### Riscos

### Melhorias Futuras

---

## Artefato

```text
review-report.md
```

---

# Política de Ambiguidade

Sempre que houver:

* Requisitos incompletos
* Requisitos conflitantes
* Falta de contexto
* Dependências desconhecidas

O agente deve:

1. Parar
2. Perguntar
3. Aguardar resposta

---

# Política de Implementação

É proibido:

* Inventar requisitos
* Ignorar critérios de aceitação
* Alterar arquitetura aprovada
* Ignorar ADRs
* Ignorar testes

---

# Estrutura Recomendada do Projeto

```text
.ai/
    sdd-playbook.md

docs/
    discovery.md
    spec.md
    planning.md
    architecture.md
    tasks.md

adr/
    0001.md
    0002.md

tests/

src/
```

---

# Bootstrap de Projeto

Ao iniciar um projeto:

1. Executar Discovery
2. Executar Entrevista Estruturada
3. Gerar discovery.md
4. Gerar spec.md
5. Gerar planning.md
6. Gerar architecture.md
7. Gerar ADRs necessários
8. Gerar tasks.md
9. Iniciar implementação

---

# Prompt de Inicialização

Ao receber um novo projeto:

"Vou iniciar o processo de Discovery.

Primeiro preciso entender completamente o problema antes de criar qualquer artefato.

Farei uma entrevista estruturada para coletar requisitos, restrições, objetivos e critérios de sucesso."

Em seguida iniciar o Framework de Entrevista.

---

# Definição de Pronto

Uma funcionalidade somente é considerada concluída quando:

✓ Discovery concluído

✓ Spec aprovada

✓ Planning concluído

✓ Arquitetura definida

✓ ADRs registrados

✓ Tasks geradas

✓ Implementação concluída

✓ Testes aprovados

✓ Revisão aprovada

✓ Critérios de aceitação atendidos
