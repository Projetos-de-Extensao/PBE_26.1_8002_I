---
hide:
  - navigation
  - toc
---  

<section class="home-hero" markdown>
<span class="home-badge">PBE 26.1 8002 I | IBMEC</span>

# Gestão e otimização de estágios obrigatórios

<p class="home-lead">
Este projeto propõe uma plataforma web para centralizar a formalização, validação e acompanhamento dos estágios obrigatórios do IBMEC. A solução conecta aluno, empresa concedente, coordenação e professor orientador em um fluxo único, com rastreabilidade documental, regras acadêmicas por curso e menos dependência de processos manuais.
</p>

[Explorar documentação](Iniciacao/index.md){ .md-button .md-button--primary }
[Ver repositório](https://github.com/Projetos-de-Extensao/PBE_26.1_8002_I){ .md-button }

<div class="home-hero__stats">
  <div class="home-stat">
    <strong>Fluxo centralizado</strong>
    <span>Documentos, convênios, aprovações e status do estágio reunidos em um só ambiente.</span>
  </div>
  <div class="home-stat">
    <strong>Validação sistêmica</strong>
    <span>Regras institucionais e acadêmicas aplicadas com mais consistência e menos retrabalho operacional.</span>
  </div>
  <div class="home-stat">
    <strong>Foco no domínio</strong>
    <span>Compatibilidade com o curso, prazos internos, jornada e exigências legais do estágio supervisionado.</span>
  </div>
</div>
</section>

## Visão geral

O sistema está sendo estruturado para resolver um problema recorrente na gestão de estágios: a fragmentação entre documentos, critérios acadêmicos, comunicação entre os envolvidos e acompanhamento do ciclo completo do aluno. A proposta atual concentra a inteligência do produto no back-end, com API, banco relacional e motor de regras de negócio capazes de validar exigências institucionais e operacionais em tempo real.

<div class="grid cards home-cards" markdown>

-   ### :material-alert-circle-outline: O problema

    A secretaria e a coordenação lidam com validações manuais, exigências que variam por curso, análise documental e controle de prazos institucionais.

-   ### :material-cog-outline: A proposta

    Estruturar uma aplicação web que reduza papel, padronize a formalização do estágio e organize o relacionamento entre aluno, faculdade e empresa.

-   ### :material-chart-timeline-variant: O impacto esperado

    Menos erro operacional, mais velocidade na conferência, melhor rastreabilidade e clareza sobre o status de cada processo.

</div>

## O que a solução precisa garantir

<div class="grid cards home-cards" markdown>

-   ### :material-school-outline: Validação acadêmica

    O estágio precisa estar vinculado à formação do aluno, respeitar regras do curso, matrícula regular, frequência e compatibilidade pedagógica.

-   ### :material-file-document-multiple-outline: Gestão documental

    TCE, comprovantes acadêmicos, dados da empresa, relatórios de acompanhamento, avaliação de desempenho e documentos de aditivo ou rescisão precisam ser controlados com clareza.

-   ### :material-office-building-outline: Controle institucional

    Convênios com empresas, cadastro de concedentes, conformidade com normas do IBMEC e aderência às exigências legais não podem ficar fora do fluxo.

-   ### :material-timer-check-outline: Acompanhamento e prazos

    O sistema precisa registrar status, pendências e entregas ao longo do estágio, reduzindo atrasos e pontos cegos para todos os envolvidos.

</div>

## Atores centrais do processo

<div class="grid cards home-cards" markdown>

-   ### :material-account-school-outline: Aluno

    Submete documentos, acompanha status, cumpre prazos, registra informações acadêmicas e entrega relatórios exigidos.

-   ### :material-domain: Empresa concedente

    Informa dados institucionais, jornada, condições do estágio, documentos obrigatórios e participa da formalização do vínculo.

-   ### :material-account-tie-outline: Coordenação e secretaria

    Validam regras institucionais, conferem documentos, acompanham pendências e supervisionam o andamento administrativo do estágio.

-   ### :material-teach: Professor orientador

    Atua na validação e no acompanhamento acadêmico, garantindo aderência entre atividades desenvolvidas e objetivos formativos.

</div>

## Regras de domínio que orientam a solução

<div class="home-callout" markdown>

O projeto foi embasado em três frentes principais: **legislação do estágio**, **diretrizes acadêmicas** e **normas internas do IBMEC**. A partir disso, a solução precisa considerar, entre outros pontos:

- matrícula e frequência regular do aluno;
- compatibilidade entre estágio e formação acadêmica;
- limite de jornada e ausência de conflito com horário de aula;
- exigência de TCE, seguro e documentação da empresa;
- convênio institucional com a concedente;
- relatórios, avaliações e prazos de acompanhamento durante e após o estágio.

</div>

## Fluxo que estamos estruturando

<div class="home-flow" markdown>
<div class="home-flow__item" markdown>
<span class="home-flow__number">1</span>

### Cadastro e regularização

Empresa e aluno informam dados essenciais para o processo, enquanto o sistema verifica pré-condições acadêmicas e institucionais.
</div>
<div class="home-flow__item" markdown>
<span class="home-flow__number">2</span>

### Submissão documental

O fluxo consolida documentos legais, acadêmicos e operacionais exigidos para início, acompanhamento ou encerramento do estágio.
</div>
<div class="home-flow__item" markdown>
<span class="home-flow__number">3</span>

### Validação e aprovação

As regras de negócio apoiam a conferência da coordenação e da orientação acadêmica, destacando pendências e inconsistências.
</div>
<div class="home-flow__item" markdown>
<span class="home-flow__number">4</span>

### Monitoramento do ciclo

Status, prazos, relatórios e eventos do estágio permanecem rastreáveis até a conclusão, aditivo ou rescisão.
</div>
</div>

## Escopo técnico atual

<div class="grid cards home-cards" markdown>

-   ### :material-language-python: Back-end em Django

    A arquitetura atual considera Python com Django para estruturar servidor, autenticação, regras de negócio e API.

-   ### :material-database-outline: Persistência relacional

    O banco MySQL foi definido para sustentar dados acadêmicos, entidades institucionais e rastreabilidade do processo.

-   ### :material-api: API e motor de regras

    A proposta técnica inclui uma API RESTful e uma camada de validação para requisitos específicos de cada curso e estágio.

</div>

## Navegue pela documentação

<div class="grid cards home-cards" markdown>

-   ### :material-rocket-launch-outline: Iniciação

    Entendimento do problema, brainstorming, 5W2H, pesquisa normativa e levantamento inicial do domínio.

    [Acessar seção](Iniciacao/index.md)

-   ### :material-book-search-outline: Pesquisa

    Base legal, diretrizes do MEC, normas acadêmicas do IBMEC e critérios documentais que moldam as regras do sistema.

    [Ver detalhes](Iniciacao/pesquisa-detalhes/index.md)

-   ### :material-draw: Elaboração

    Requisitos, modelos, arquitetura em evolução e artefatos que consolidam a solução proposta.

    [Explorar seção](Elaboracao/index.md)

-   ### :material-hammer-wrench: Construção

    Registro da execução, organização do trabalho, issues, GitHub Projects e andamento técnico do projeto.

    [Acompanhar seção](Construcao/index.md)

</div>
