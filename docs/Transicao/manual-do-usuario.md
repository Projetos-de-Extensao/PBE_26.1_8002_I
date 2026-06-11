# Manual do Usuário

Este manual descreve, **passo a passo e por perfil**, como usar o sistema **EstágioIBMEC** (a SPA disponível em `http://localhost:8000/dashboard-ibmec.html` no ambiente de desenvolvimento). Ele se baseia exclusivamente nas telas e fluxos já implementados no front-end (`djangotutorial/dashboard-ibmec.html`) e nos endpoints documentados em [Endpoints da API](../Construcao/api/endpoints.md).

A interface decide automaticamente qual painel mostrar a partir do **tipo do usuário** (campo `tipo` do `Usuario`). Há quatro perfis principais:

| Perfil no sistema | Painel servido pela SPA | Onde está documentado |
| --- | --- | --- |
| `aluno` | `AlunoApp` — sidebar com Início / Meu Processo / Documentos | [Como aluno](#como-aluno) |
| `coordenador` | `CoordApp` — sidebar com Dashboard / Relatórios / Empresas + lista de alunos do curso | [Como coordenador](#como-coordenador) |
| `supervisor_empresa` | `SupervisorApp` — sidebar com Alunos / Documentos da empresa | [Como supervisor de empresa](#como-supervisorempresa) |
| `secretaria`, `casa`, `reitor`, `pro_reitor`, `carreiras` | `CoordApp` em **modo read-only** (visão global) | [Como administrativo / reitoria](#como-administrativo--reitoria) |

> O perfil **administrador técnico** (`is_staff=True` ou `is_superuser=True`) usa o Django Admin em `/admin/`, fora da SPA. Para criar contas em massa em ambiente de demonstração, use `python manage.py seed_completo --force` (cria 70 alunos, 7 cursos, 7 coordenadores, 6 empresas; senha padrão `senha123`).

---

## Antes de começar — acesso, login e senha

### Acessar a aplicação

1. Abra o navegador em `http://localhost:8000/dashboard-ibmec.html` (ambiente local; em produção, troque pelo domínio publicado).
2. A SPA carrega a **tela de login**.

### Entrar com email institucional

1. Em **Email institucional**, digite o seu email (ex.: `ana.lima@al.ibmec.edu.br`).
2. Em **Senha**, digite a senha enviada por email/coordenação. No ambiente de demonstração com `seed_completo`, a senha é `senha123` para todos os usuários.
3. Clique em **Entrar**.
4. Em sucesso, a SPA detecta o seu `tipo` e direciona para o painel correspondente.

> O sistema **não tem mais o botão "Cadastre-se"** na tela de login. Contas comuns são criadas pelo coordenador/admin (ou geradas pelo seed). O fluxo de auto-cadastro de empresa pelo aluno cria automaticamente o usuário do supervisor — descrito em [Iniciar processo de estágio](#3-iniciar-um-processo-de-estágio).

### Esqueci minha senha

1. Na tela de login, clique em **Esqueci minha senha**.
2. Informe seu email institucional e clique em **Enviar link**.
3. Você sempre verá a mensagem genérica "Se o email estiver cadastrado, você receberá instruções." — isso é proposital: o sistema não revela se o email existe.
4. Abra seu email institucional. O link recebido tem o formato `…/redefinir-senha/?uid=…&token=…`.
5. Clique no link: a SPA detecta o `uid` e `token` na URL e abre a tela **Redefinir senha**.
6. Informe a **nova senha** (mínimo 6 caracteres) e confirme.
7. Após o sucesso, clique em **Ir para o login** e entre com a nova senha.

> O token expira em 3 dias e é invalidado assim que você troca a senha — peça um novo link se passou desse prazo.

### Sair

Em qualquer painel, o rodapé da sidebar mostra seu nome e o link **Sair**. Clicar nele invalida o token da sua sessão atual.

---

## Como aluno

Como aluno, você abre e acompanha o seu processo de estágio, envia documentos, preenche o relatório de avaliação e (após aprovação) avalia anonimamente a empresa.

### 1. Visão geral do painel

O painel do aluno tem três áreas na sidebar esquerda:

| Item da sidebar | O que abre |
| --- | --- |
| **Início** | Resumo do processo atual (status, horas, datas, bolsa) e atalhos rápidos |
| **Meu Processo** | Lista dos seus processos (você só tem um "vivo" por vez) com detalhes completos |
| **Documentos** | Geração de PDFs (TCE, Termo), envio de arquivos, preenchimento do relatório e avaliação da empresa |

Na primeira vez, se você ainda **não tem processo aberto**, a tela inicial mostra o card "Nenhum processo de estágio" com o botão **+ Iniciar Processo de Estágio**.

### 2. Acompanhar o status do processo

A SPA exibe o status do processo em um **badge colorido** em todas as telas. Os estados possíveis são definidos pela [máquina de estados](../Construcao/api/state-machine.md):

| Status | O que significa para você |
| --- | --- |
| `RASCUNHO` | Reservado para a feature "salvar para depois" — hoje o processo nasce como `PENDENTE` |
| `PENDENTE` | Esperando análise do coordenador. Você pode cancelar |
| `CORRECAO_SOLICITADA` | O coordenador devolveu para ajuste; corrija e ressubmeta |
| `APROVADO` | Coordenador aprovou; aguarda o início do estágio. **Você não pode mais cancelar diretamente** — peça ao coordenador |
| `ATIVO` | Estágio em execução |
| `ENCERRADO` | Estágio finalizado com sucesso |
| `REJEITADO` | Processo recusado — verifique a justificativa no detalhe |
| `CANCELADO` | Cancelado — você pode abrir um novo processo |

Em **Meu Processo**, clique sobre o cartão de um processo para abrir o modal com todos os campos (horas, bolsa, datas, plano de atividades, justificativa de rejeição se houver) e os documentos anexados.

### 3. Iniciar um processo de estágio

Pré-condição: você precisa estar **matriculado em estágio supervisionado** (campo `matriculado_estagio` do seu cadastro). Caso contrário, o sistema bloqueia a criação com a mensagem da regra RN01.

1. Na sidebar, vá em **Início** (sem processo ainda) ou **Meu Processo**, e clique em **+ Iniciar Processo de Estágio**.
2. O sistema abre um **wizard de 3 etapas** com indicador no topo.

**Etapa 1 — Documento (opcional)**

- Arraste ou clique para selecionar o **PDF da carta da empresa / proposta / contrato**.
- O sistema extrai automaticamente dados como CNPJ, datas, horas/semana e bolsa, e pré-preenche a etapa 2. Os campos detectados aparecem listados em "Campos detectados:".
- Se você não tiver o PDF, pule esta etapa clicando em **Próximo →**.

**Etapa 2 — Formulário**

- Confira o bloco "Dados do aluno" (vem do seu cadastro: nome, curso, CR, período).
- **Empresa** *(obrigatório)*: escolha na lista. Empresas marcadas como *não aprovada* serão **bloqueadas** pela regra RN07 — você verá um aviso.
  - Se a empresa do seu estágio ainda não existe, clique em **+ Cadastrar nova** (veja [Cadastrar uma nova empresa](#3a-cadastrar-uma-nova-empresa-fluxo-do-aluno)).
- **Supervisor** *(opcional)*: escolha um supervisor já cadastrado para a empresa selecionada.
- **Horas semanais** *(obrigatório, máx. 30)*: o limite legal é 30h; o limite do seu curso pode ser menor (RN02/RN03).
- **Valor da bolsa** *(opcional)*.
- **Início** e **Fim** *(obrigatórios)*: a data de fim precisa ser estritamente posterior à de início.
- **Plano de atividades** *(obrigatório)*: descreva as atividades previstas no estágio.

**Etapa 3 — Revisão**

- O wizard mostra um resumo de todos os campos preenchidos.
- Clique em **✓ Criar Processo**.
- Se algum dado violar uma regra de negócio, o sistema mostra o erro com o ID da RN (ex.: `RN01: aluno deve estar com matrícula ativa em estágio supervisionado.`).
- Em sucesso, você recebe a confirmação `Processo #X criado!` e o status inicial fica como `PENDENTE`.

> **Você só tem um processo "vivo" por vez** (RN04). Para abrir outro, é necessário cancelar o anterior (em `RASCUNHO`/`PENDENTE`) ou aguardar o coordenador encerrá-lo.

#### 3.a Cadastrar uma nova empresa (fluxo do aluno)

Disponível dentro do wizard de criação do processo, no campo **Empresa**, botão **+ Cadastrar nova**.

1. Preencha os **8 campos obrigatórios** (RN08) — todos com asterisco no formulário:
   - CNPJ
   - Razão social
   - Áreas de atuação
   - Localização
   - Email do gestor *(será usado para criar o acesso do supervisor)*
   - Descrição da empresa
   - Responsável legal
   - Cargo do responsável
2. Clique em **Salvar**.
3. O sistema:
   - cria a `EmpresaConcedente`;
   - cria automaticamente um `Usuario` + `SupervisorEmpresa` para o gestor;
   - **envia um email para o gestor** com link para definir a senha (`…/redefinir-senha/?uid=…&token=…`).
4. A empresa aparece como opção no campo **Empresa** do wizard, já selecionada.

> A empresa recém-criada começa com `aprovada_ibmec = False`. Para criar o processo, peça à coordenação que aprove a empresa no Django Admin (ou aguarde a homologação). Empresas não aprovadas bloqueiam a criação do processo (RN07).

### 4. Baixar o TCE em PDF (modelo)

Disponível no painel **Documentos**, bloco "Ações disponíveis", quando o processo está em estado ativo de tramitação.

1. Vá em **Documentos** na sidebar.
2. Clique em **📄 Gerar TCE**.
3. O sistema gera o **Termo de Compromisso de Estágio** em PDF (usa o reportlab) e abre/baixa o arquivo `tce_<id>.pdf`.
4. Imprima, colete as assinaturas (aluno, empresa, coordenador) e digitalize.

> O botão **📄 Termo de Realização** funciona da mesma forma, gerando o `termo_<id>.pdf` para uso ao final do estágio.

### 5. Fazer upload do TCE assinado (ou outros documentos)

Disponível em **Documentos → ⬆ Enviar Documento**.

1. Em **Título do documento**, descreva o documento (ex.: `TCE assinado`, `Apólice 2026`, `Carta de apresentação`).
2. Selecione o **arquivo PDF**.
3. Clique em **Enviar**.
4. O sistema:
   - registra o documento como `PENDENTE` (status inicial);
   - calcula um **score de conformidade** do PDF (PyPDF2);
   - se o score ≥ 0.8, **aprova automaticamente** o documento;
   - cria um `LogDocumento` para auditoria.
5. Documentos aparecem listados em "Documentos do processo" com badge de status (`PENDENTE`, `APROVADO`, `REJEITADO`).

> Para a transição `APROVADO → ATIVO` do seu processo, o coordenador exige um documento do tipo **TCE com status APROVADO** (RN05). Garanta que o TCE assinado foi enviado e aprovado antes de pedir a ativação.

### 6. Preencher o relatório de estágio

Disponível em **Documentos → 📝 Preencher Relatório Parcial / Final**.

O coordenador do seu curso configurou um `ModeloFormulario` específico — você só preenche o que o modelo definir.

1. Clique em **📝 Preencher Relatório Parcial** (ou **Final**, quando o parcial já foi enviado).
2. A SPA renderiza as seções dinâmicas conforme o modelo:
   - **Escalas 1–4** (avaliação por nota);
   - **Escala "Suficiente / Insuficiente / Não utilizado"**;
   - **Matrizes de escala** (vários itens × várias colunas);
   - **Checkbox duplo** (marcação múltipla);
   - **Texto livre** (observações).
3. Preencha cada seção. O sistema indica quando uma seção está "completa" no rodapé do passo.
4. Use **Visualizar** se quiser gerar a prévia do PDF sem persistir as respostas.
5. Clique em **Enviar** para finalizar:
   - as respostas são salvas no processo (`respostas_formulario`);
   - o sistema gera o PDF do relatório (`relatorio_parcial_processo_X.pdf` ou `_final_`);
   - cria um `DocumentoProcesso` correspondente, com `tipo=RELATORIO_PARCIAL` ou `RELATORIO_FINAL`.

> Suas respostas no formulário avaliativo são **privadas em relação ao supervisor da empresa**: a API anula `respostas_formulario` no payload que vai para o supervisor. Coordenador e visão global enxergam normalmente.

### 7. Cancelar o processo

1. Em **Meu Processo**, clique sobre o seu processo para abrir o detalhe.
2. Se o status atual permite (apenas `RASCUNHO` e `PENDENTE`), você verá o botão **Cancelar Processo**.
3. Clique nele; o sistema pede **motivo do cancelamento** (justificativa).
4. Confirme: o processo passa para `CANCELADO` e você pode abrir um novo.

> A partir de `APROVADO`, **você não cancela diretamente**. Para encerrar um processo já aprovado/ativo, peça ao coordenador. Isso evita revogar contratos/comunicação com a empresa pelo aluno sozinho.

### 8. Avaliar a empresa (anonimamente)

Disponível em **Documentos** quando o processo está em `APROVADO`, `ATIVO` ou `ENCERRADO`.

1. Procure o card "⭐ Avaliar a empresa do meu estágio" no topo da página de documentos.
2. Clique em **Avaliar empresa**.
3. No modal:
   - escolha uma **nota de 1 a 5 estrelas**;
   - opcionalmente, escreva um **comentário** (recomendado: evite citar nomes para preservar o anonimato).
4. Clique em **Enviar avaliação**.
5. O sistema:
   - registra um `AvaliacaoEmpresa` com `aluno=None` e `processo=None`;
   - identifica você apenas por um **hash SHA-256** (para impedir avaliações duplicadas) — sua identidade não é recuperável a partir desse hash;
   - confirma com a mensagem "Avaliação enviada anonimamente.".
6. O card passa a mostrar "✓ Você já avaliou esta empresa." (limite de uma avaliação por empresa por aluno).

> Nenhum perfil — nem coordenador, nem a empresa, nem o admin — consegue ligar sua avaliação ao seu cadastro. Os agregados (média de estrelas, comentários recentes) aparecem em `/api/dashboard/empresas/` para o coordenador e a visão global.

---

## Como coordenador

Como coordenador, você acompanha os processos dos alunos dos cursos que coordena, valida documentos, conduz as transições de status e configura o formulário de avaliação por curso.

### 1. Visão geral do painel

O painel do coordenador (`CoordApp`) tem **3 abas** no topo da sidebar e uma **lista de alunos** logo abaixo, com filtros:

| Item da sidebar | O que abre |
| --- | --- |
| **Dashboard** | Detalhe individual do aluno selecionado (KPIs, documentos, respostas do formulário) |
| **Relatórios** | Visão agregada dos processos dos seus cursos (consome `GET /api/dashboard/estatisticas/`) |
| **Empresas** | Visão agregada por empresa concedente (consome `GET /api/dashboard/empresas/`) |
| **Filtros (🔍)** | Filtra a lista de alunos por curso, semestre, status, empresa, "com respostas preenchidas" |
| **Formulário** *(botão no rodapé)* | Abre o editor de `ModeloFormulario` do seu curso |

A lista de alunos só mostra processos em estados visíveis (`PENDENTE`, `APROVADO`, `ATIVO`, `CORRECAO_SOLICITADA`, `ENCERRADO`). Processos `REJEITADO`/`CANCELADO` ficam disponíveis apenas dentro da aba **Relatórios**.

### 2. Visualizar um aluno e seu processo

1. Clique em um aluno na sidebar.
2. O Dashboard mostra o detalhe:
   - cabeçalho com nome, matrícula, curso, período, empresa e semestre;
   - KPIs: horas estimadas, remuneração, início, empresa, **score de avaliação**;
   - dados do processo (plano de atividades, fim previsto, auxílio transporte);
   - lista de documentos do processo;
   - se o aluno preencheu o formulário, **renderização visual das respostas** (gráficos radar, barras, etc., conforme o tipo de seção do modelo).
3. Use os filtros (🔍 Filtrar) para encontrar alunos por curso/semestre/status/empresa.

> Coordenadores e administrativo enxergam o campo `respostas_formulario`; supervisores **não** (privacidade do aluno).

### 3. Aprovar / rejeitar / encerrar processos

A transição de status é feita a partir do modal de detalhe do processo. Hoje o coordenador acessa via:

- a **aba Relatórios → cartão do processo → "Abrir aluno"**, ou
- a **lista de alunos → Dashboard → clicar no número do processo** (dependendo do modo da página).

Em qualquer caso, o modal `ProcessoDetailModal` lista as **transições válidas** para o estado atual:

| De → Para | Quando usar |
| --- | --- |
| `PENDENTE → APROVADO` | Documentação e plano OK; aluno pode iniciar |
| `PENDENTE → CORRECAO_SOLICITADA` | Pedir ajuste no plano/dados do processo |
| `PENDENTE → REJEITADO` | Recusar formalmente — **exige justificativa** (RF11/RN11) |
| `APROVADO → ATIVO` | Estágio iniciou — **exige TCE com status APROVADO** (RN05). Senão, o sistema devolve `400` com a mensagem da RN |
| `ATIVO → ENCERRADO` | Estágio concluído |
| qualquer → `CANCELADO` | Atendendo a pedido do aluno após `APROVADO`, ou intervenção institucional |

Passo a passo:

1. Abra o modal de detalhe do processo.
2. Clique no botão da transição desejada (ex.: `→ Aprovado`, `→ Rejeitado`).
3. Em transições que exigem justificativa (`REJEITADO`, `CORRECAO_SOLICITADA`, `CANCELADO`), o sistema abre um campo de texto: descreva o motivo.
4. Clique em **Confirmar**.
5. O sistema:
   - valida a transição no mapa (`state_machine.py`);
   - aplica RN05 quando aplicável;
   - persiste o novo status;
   - registra um `HistoricoStatusProcesso` com `status_anterior`, `status_novo`, `usuario` e `observacao`.

### 4. Validar / reprovar documentos (com comentário)

Dentro do detalhe do aluno (Dashboard), cada documento traz, para coordenadores, **dois botões** quando o status é `PENDENTE`:

1. Localize o documento na lista "Documentos do processo".
2. Clique em **Aprovar** ou **Reprovar**.
3. O sistema abre o `ConfirmModal`:
   - **Aprovar** — observação é **opcional**;
   - **Reprovar** — o motivo da reprovação é **obrigatório**.
4. Digite a justificativa (se aplicável) e clique em **Aprovar** / **Reprovar**.
5. O backend:
   - atualiza `DocumentoProcesso.status`;
   - grava o comentário em `observacoes`;
   - registra um `LogDocumento` com a ação (`APROVADO` ou `REJEITADO`), o usuário e o comentário.

> Documentos rejeitados ficam visíveis para o aluno com o aviso destacado: "Observação: <motivo>". O aluno pode reenviar uma nova versão pelo modal de upload.

### 5. Usar o Dashboard (relatórios agregados)

A aba **Relatórios** consome `GET /api/dashboard/estatisticas/` com os filtros aplicados. O que aparece:

- Total de processos;
- Percentual com respostas preenchidas;
- Média de remuneração e de horas semanais;
- Média geral do score dos documentos;
- Distribuição por status, semestre e empresa;
- Para cada seção do `ModeloFormulario` do seu curso, **agregação dos resultados** (médias, contagens, percentuais).

A aba **Empresas** consome `GET /api/dashboard/empresas/` e mostra, para cada empresa onde seus alunos estagiaram:

- Total de estagiários;
- Média de remuneração e horas semanais;
- Média de avaliação consolidada (formulário) e **avaliação anônima em estrelas** (1–5);
- Comentários anônimos recentes (até 5).

Use o painel de filtros da sidebar (🔍) para recortar os dados por curso, semestre, status, empresa, "com respostas". As três abas obedecem aos mesmos filtros.

### 6. Editar o modelo de formulário (`ModeloFormulario`)

Disponível pelo botão **Formulário** no rodapé da sidebar (visível apenas para coordenadores; perfis administrativos não veem o botão).

1. Clique em **Formulário**.
2. O editor abre com o modelo ativo do seu curso, com:
   - **Título** do formulário;
   - **Curso** vinculado (pré-preenchido);
   - Lista de **seções**, cada uma com:
     - tipo (`escala_1_4`, `escala_1_4_multi`, `escala_3`, `checkbox_duplo`, `texto_livre`, `auto`);
     - título;
     - itens / colunas / opções (conforme o tipo).
3. Edite seções existentes ou adicione novas conforme a necessidade do curso.
4. Clique em **Salvar**.
5. A SPA chama `PUT /api/modelos-formulario/<id>/` e recarrega a lista.
6. O novo modelo passa a valer **para todos os alunos do seu curso** na próxima vez que preencherem o formulário.

> Coordenador só pode editar o modelo **do próprio curso**. Tentativas em outro curso retornam `403 Forbidden`.

### 7. Buscar / filtrar alunos

A sidebar do coordenador combina lista de alunos + filtros. Para encontrar um aluno específico:

1. Clique em **🔍 Filtrar** no cabeçalho de "Alunos".
2. Aplique um ou mais filtros: **curso**, **semestre**, **status**, **empresa**, ou marque **"Com respostas preenchidas"**.
3. A lista é filtrada client-side. O contador no topo mostra "filtrados/total".
4. Clique no aluno para abrir o Dashboard dele.

---

## Como supervisor/empresa

Como supervisor da empresa concedente, você acompanha os estagiários da sua empresa e os documentos vinculados aos processos dela. Seu painel (`SupervisorApp`) é mais enxuto que o do coordenador, com restrições propositais para preservar a privacidade do aluno.

### 1. Como obter acesso

Há dois caminhos para a conta de supervisor existir no sistema:

- **Cadastro automático via aluno**: quando um aluno cadastra a sua empresa pelo wizard, o sistema cria automaticamente o `Usuario` + `SupervisorEmpresa` e envia ao email da empresa um link `…/redefinir-senha/?uid=…&token=…` para você definir a senha;
- **Cadastro por admin**: o administrador do sistema cria a conta no Django Admin.

Em ambos os casos, o primeiro acesso passa pela tela **Redefinir senha** (mesma do fluxo de "esqueci minha senha").

### 2. Visão geral do painel

A sidebar tem dois itens:

| Item | O que abre |
| --- | --- |
| **Alunos** | Lista os estagiários da **sua empresa** com filtros, e abre o Dashboard individual ao clicar |
| **Documentos** | Lista todos os documentos dos processos da sua empresa |

A lista de alunos só mostra processos em estados visíveis no dashboard. Processos `REJEITADO`/`CANCELADO` não aparecem.

### 3. Visualizar processos da empresa

1. Clique no aluno na sidebar para abrir o Dashboard individual.
2. Você vê:
   - dados do aluno (nome, matrícula, curso, período);
   - dados do processo (horas, datas, plano, status);
   - documentos do processo (com link para abrir).
3. O que **não aparece** para o supervisor:
   - **Score de avaliação** do aluno (KPI escondido);
   - **Respostas do formulário** (`respostas_formulario` é anulado na resposta da API);
   - As abas **Relatórios** e **Empresas** do coordenador (dashboards agregados).

Essa restrição é deliberada: o aluno preenche o formulário avaliando a empresa, e expor essas respostas ao supervisor avaliado quebraria a privacidade.

### 4. Fazer upload de documentos

Quando autorizado, o supervisor pode enviar documentos do processo (ex.: avaliação interna, frequência) via `POST /api/documentos/` com o `processo` correspondente.

> A SPA atual não expõe um botão dedicado "Enviar documento" no painel do supervisor; o envio é feito hoje principalmente pelo aluno e por integrações. Para incluir um documento que pertence à empresa, peça ao aluno que faça o upload no painel dele com o título do documento — o sistema registrará `enviado_por = aluno` mesmo assim.

### 5. Acessar / baixar documentos do processo

1. Clique em **Documentos** na sidebar.
2. A SPA lista todos os documentos dos processos da sua empresa, com badge de status.
3. Clique em **Abrir** para visualizar / baixar o arquivo PDF.

### 6. O que você **não** pode fazer

- **Aprovar/rejeitar documentos** — apenas coordenadores;
- **Alterar status do processo** (`alterar_status/`) — apenas coordenadores e admins;
- **Editar `ModeloFormulario`** — apenas coordenadores;
- **Acessar `/api/dashboard/estatisticas/` ou `/api/dashboard/empresas/`** — devolvem `403 Forbidden`.

---

## Como administrativo / reitoria

Os perfis `secretaria`, `casa`, `reitor`, `pro_reitor` e `carreiras` são tratados pelo sistema como **visão global read-only**. O backend reconhece esses tipos pelo helper `is_administrativo` em `permissions.py`, e o conjunto formado por eles + admins compõe `has_global_access`.

### 1. Acesso

Você loga normalmente com email institucional e senha. A SPA detecta seu `tipo` e mostra o **mesmo painel do coordenador** (`CoordApp`), mas com restrições de escrita.

### 2. O que você vê

- **Dashboard / Relatórios / Empresas** com **todos os cursos** (não há filtro implícito por coordenação);
- A lista de alunos da sidebar inclui **todos os alunos** com processos visíveis;
- O detalhe do processo (`ProcessoDetailModal`) mostra **todos os campos** e a indicação "Visualização — sem ações disponíveis para o perfil <seu perfil>" no rodapé.

### 3. O que você **não** pode fazer

- Não há **botão Formulário** no rodapé da sidebar (apenas coordenadores editam o `ModeloFormulario`);
- Os botões de **transição** do processo (`Aprovar`, `Rejeitar`, etc.) não aparecem;
- Os botões de **validar documento** (Aprovar/Reprovar) também não aparecem;
- Qualquer chamada de escrita à API retorna `403 Forbidden`.

A política é clara: **acompanhamento e auditoria, sem interferência operacional**. Para alterar processos ou documentos, é necessário envolver o coordenador do curso correspondente ou um administrador.

### 4. Resumo de permissões

| Recurso | Visão global (`secretaria`, `casa`, `reitor`, `pro_reitor`, `carreiras`) | Admin (`is_staff`) |
| --- | --- | --- |
| Listar/detalhar cursos, alunos, empresas, processos, documentos | ✓ | ✓ |
| Dashboards (`/api/dashboard/processos/`, `/estatisticas/`, `/empresas/`) | ✓ leitura | ✓ leitura |
| Criar/editar/remover qualquer recurso | ✗ (403) | ✓ |
| Disparar transições de status (`alterar_status/`) | ✗ (403) | ✓ qualquer transição |
| Validar documentos (`/documentos/{id}/validar/`) | ✗ (403) | ✓ |
| Editar `ModeloFormulario` | ✗ (403) | ✓ |
| Ver `respostas_formulario` dos alunos | ✓ | ✓ |

Detalhes completos em [Endpoints da API](../Construcao/api/endpoints.md#resumo-de-permissoes-por-papel).

---

## Resolvendo problemas comuns

| Mensagem na SPA | O que significa | O que fazer |
| --- | --- | --- |
| `Credenciais inválidas.` no login | Email ou senha errados | Confirme o email institucional; tente "Esqueci minha senha" |
| `RN01: aluno deve estar com matrícula ativa em estágio supervisionado.` ao criar processo | Sua matrícula em estágio não está marcada | Procure a secretaria/coordenação para regularizar |
| `RN03: excede o limite do curso (Xh/semana).` | Você informou mais horas que o teto do curso | Ajuste `horas_semanais` |
| `Limite legal de 30h semanais (Lei 11.788/08).` | Acima de 30h | Reduza para no máximo 30 |
| `RN05: aluno já possui um processo de estágio em andamento.` | Você tem um processo não-`CANCELADO` aberto | Cancele o anterior em `RASCUNHO`/`PENDENTE`, ou peça ao coordenador para encerrá-lo |
| `RN05: é necessário que o TCE assinado esteja aprovado para ativar o estágio.` | Coordenador tentando ativar sem TCE aprovado | Envie o TCE assinado e peça ao coord. que valide antes de ativar |
| `RN07/RN09: empresa não está aprovada pelo IBMEC.` | Empresa marcada `aprovada_ibmec=False` | Peça à coordenação que aprove a empresa no Django Admin |
| `RN11: justificativa obrigatória ao rejeitar uma solicitação.` | Tentativa de rejeitar sem motivo | Preencha o campo "Justificativa da rejeição" no modal |
| `Todos os campos da empresa são obrigatórios.` ao cadastrar empresa | Faltam um ou mais dos 8 campos do RN08 | Preencha CNPJ, razão social, áreas, localização, email do gestor, descrição, responsável, cargo |
| `Aluno só pode cancelar processos com status RASCUNHO ou PENDENTE.` | Tentativa de cancelar após `APROVADO` | Solicite ao coordenador que cancele em seu nome |
| Botões de transição **não aparecem** no modal | Você está em modo read-only (perfil administrativo) | Esse é o comportamento esperado — peça ao coordenador para agir |
| Documentos do supervisor não mostram **respostas do formulário** | Filtragem de privacidade do aluno | Comportamento intencional |

Para erros de servidor (`5xx`), envie o ID do processo / documento e a hora aproximada ao administrador. Os logs do Django registrarão a stack trace correspondente.

## Referências

- [Visão geral da API](../Construcao/api/index.md)
- [Endpoints completos](../Construcao/api/endpoints.md)
- [Autenticação](../Construcao/api/autenticacao.md)
- [Regras de negócio](../Construcao/api/regras-negocio.md)
- [Máquina de estados de `ProcessoEstagio`](../Construcao/api/state-machine.md)

## Autor(es)

| Data       | Versão | Descrição              | Autor(es)               |
| ---------- | ------ | ---------------------- | ----------------------- |
| 11/06/2026 | 1.0    | Criação do manual baseado no SPA `dashboard-ibmec.html` e nos endpoints publicados | João Gabriel Teodósio |
