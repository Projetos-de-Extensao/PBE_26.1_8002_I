# 🌸 Brainstorm para o Site de Gerenciamento de Estágios 🌸
 
## 🎀 Introdução
<p align = "justify">
O brainstorm é uma técnica de elicitação de requisitos que consiste em reunir a equipe e discutir sobre diversos tópicos gerais do projeto apresentados no documento problema de negócio. No brainstorm o diálogo é incentivado e críticas são evitadas para permitir que todos colaborem com suas próprias ideias.
</p>
 
## 🎀 Metodologia
<p align = "justify">
A equipe se reuniu para debater ideias gerais sobre o projeto presencialmente, começou 07/04/2026 e terminou [preencher],onde a equipe decidiu em conjunto as perguntas e as respostas foram transcritas para o documento.
</p>
 
## 🎀 Perguntas
 
### 💕 1. Qual o objetivo principal da aplicação?
 
<p align = "justify">
<b>Letícia</b> - Deve ser uma plataforma onde os coordenadores tenham mais facilidade para gerenciar estágio.
</p>
 
<b>Roger</b> - A plataforma deve fornecer um ambiente de gerenciamento de estágios para os coordenadores e alunos do IBMEC.
 
<b>João Gabriel</b> - O objetivo da aplicação é facilitar  e padronizar a formalização de contratos de estágio referentes aos alunos do IBMEC com empresas externas.
 
<b>Lucas</b> - O principal objetivo da aplicação é simplificar, organizar e facilitar o gerenciamento de estagios do IBMEC em um só lugar.
 
<b>Vinicius</b> - A plataforma deve gerenciar as documentações necessárias para aplicação à vaga de estágio.
</p>
 
---
 
### 💕 2. Como será o processo para cadastrar uma nova empresa?
 
<p align = "justify">
<b>Letícia</b> - Deve ser um processo prático e intuitivo onde a  empresa deve estar de acordo com a legislação e as normas requeridas pela IBMEC.
</p>
 
<b>Roger</b> - Deve ser simples e intuitivo mas que atenda todas a necessidades legais para o cadastro de uma empresa.
 
<b>João Gabriel</b> - Imagino uma tela de login exclusiva para a empresa, com campos específicos e direcionados com o que é importante para o cadastro da empresa e campos de validação de documentos.
 
<b>Lucas</b> - O processo deve validar o CNPJ, verificar se a empresa está de acordo com a legislação trabalhista, normas da IBMEC e normas do MEC e deve requerer aprovação dos coordenadores da IBMEC e conter informações importantes sobre a empresa.
 
<b>Vinicius</b> - Captar a visão geral sobre a empresa, valores da empresa, área de atuação, lugares onde a empresa é sediada.
</p>

--- 

### 💕 3. Como será a forma de adicionar vagas de estágios?(Desconsiderada)
 
<p align = "justify">
<b>Letícia</b> - A empresa deve fornecer todas as informações requeridas pelo sistema com base nas necessidades de cada curso.
</p>
 
<b>Roger</b> - O processo deve ser extenso para que não haja ambiguidade nos objetivos do estágio, tenha todas as informações que convenham para os interessados e ter autenticação não somente automática, como humana.
 
<b>João Gabriel</b> - Deve ser burocrático, com envio de documentações pertinentes à vaga de estágio, alinhada com os padrões do MEC e relacionado com os requerimentos pesquisados. Talvez com uma análise se vai ser aceito ou não em relação à documentação.
 
<b>Lucas</b> - Deverá ser um processo rígido, onde a empresa explicita o objetivo da vaga, a parte de documentos deve ser analisada, os representantes de curso devem autorizar ou não o cadastro de vaga e deverá estar de acordo com os requisitos.
 
<b>Vinicius</b> - Se tiver algum processo seletivo deverá informar como será o processo, a empresa deve informar características da vaga como carga horária, modalidade de trabalho, se é ou não presencial, localização(no caso de ser presencial), valor do salário e informações que seriam úteis para quem vai aplicar para a vaga.
</p>

> A pergunta foi desconsiderada para a elicitação de requisitos pois percebemos que as vagas não seriam encontradas pelo nosso sistema

---
 
### 💕 4. Como será o processo de aprovação do estágio?

<p align = "justify">
<b>Letícia</b> - O sistema deve validar os documentos requeridos, seguido da aprovação do coordenador e do professor responsável.
</p>
 
<b>Lucas</b> O coordenador e o professor responsável pelo aluno devem aprovar o estágio e supervisionar durante o período de atuação.
 
<b>João Gabriel</b> Deverá conectar os três atores importantes: Estudante, Empresa e Instituição de ensino. Imagino tendo o uso mínimo de papel, com toda a verificação feita pelo próprio site via PDFs junto de assinaturas digitais, junto do uso de `Termos de Compromisso` presentes nos sistma. Além disso, campos de status sobre o estagio (ex: em andamento, concluido, aprovado, pendente).
</p>
 
---
  
## 🎀 1. Objetivo e Escopo
* Qual é o principal problema que a IBMEC quer resolver com esse site? <br/> **Gerenciamento de Requisitos, foco em automatização dos processos burocráticos da aprovação e acompanhamento do estágio.**
* O foco do projeto é somente estágio obrigatório ou incluir estágio não obrigatório no futuro? <br/> **Focar apenas no que foi pedido.**
* O sistema será usado apenas pela IBMEC RJ ou deve nascer preparado para expansão? <br/> **O melhor é focarmos apenas na IBMEC RJ.**
* O cliente espera gestão documental ou também acompanhamento, notificações e relatórios? <br/> **Tudo isso.**
* O sistema deve ajudar no controle acadêmico do cumprimento de horas e aprovação final? <br/> **Tudo isso.**
* Quais resultados fariam o cliente considerar o projeto bem-sucedido? <br/> **Conseguir entregar todo o processo de validação e gerenciamento de estágios automatizado e com acompanhamento em tempo real dos processos de forma clara, além de uma interface e fluxos intuitivos para quem for utilizar.**
* O que ficará claramente dentro do sistema? <br/> **Toda a documentação de estágios ficará dentro do sistema.**
* O sistema vai substituir totalmente o processo físico? <br/> **A ideia é substituir tudo com automatização.**
* Há alguma etapa que precise ser feita manualmente? <br/> **A princípio, não.**
* O site deve permitir cadastrar oportunidades? <br/> **A ideia seria para o futuro talvez integrar com a plataforma de vagas do CASA.**
* A empresa poderá abrir vagas dentro da plataforma? <br/> **Por agora apenas as oportunidades que o aluno apresentar interesse.**
* O sistema deve contemplar renovação, aditivo, encerramento? <br/> **O sistema deve abordar o processo completo do estágio de cada aluno.**
* Se só 3 funcionalidades pudessem existir no MVP, quais seriam? <br/> **Análise de documentos, acompanhamento em tempo real dos processos e logins.**
* Qual tipo de erro o cliente mais quer evitar? <br/> **Recusa ou aceitação do estágio errada pelo sistema.**

## 🎀 2. Perfis de Usuário e Acessos
* Quais perfis de usuário existirão exatamente? <br/> **Empresa, Aluno e Coordenadores.**
* “Professor” e “Coordenador” terão permissões iguais? <br/> **Acredito que tenham as mesmas permissões.**
* A empresa terá vários usuários para atuar pela mesma empresa? <br/> **Não tem necessidade de ter vários logins para uma mesma empresa.**
* A empresa terá login e painel próprios? <br/> **Sim.**
* O aluno poderá acompanhar tudo em tempo real? <br/> **Estritamente necessário o status em tempo real para o aluno.**
* Quem pode aprovar, reprovar, pedir correção de documentos? <br/> **Apenas a coordenação.**
* Quem pode editar dados após o envio? <br/> **Coordenação.**
* O orientador acadêmico terá painel próprio para aprovar planos e horas? <br/> **Necessário.**
* Qual perfil de usuário mais importante para ser simples de usar? <br/> **Todos são importantes, mas para a empresa e para o aluno devem ser os mais fáceis.**
* O sistema terá autenticação institucional para alunos e professores? <br/> **Sim.**
* A empresa fará cadastro manual com validação por e-mail? <br/> **Sim.**

## 🎀 3. Regras de Negócio e Validações
* Em que momento o aluno pode iniciar um pedido de estágio? <br/> **Quando estiver devidamente matriculado na disciplina Estágio Supervisionado.**
* O aluno precisa comprovar matrícula ativa e vínculo com a disciplina? <br/> **Sim. A ideia é o login dele só ser liberado enquanto ele estiver devidamente matriculado na disciplina.**
* O sistema deve validar automaticamente se o aluno está apto a estagiar? <br/> **Sim.**
* O sistema deve impedir abertura de solicitação se faltarem pré-requisitos? <br/> **Ele não deve nem conseguir abrir uma solicitação se não tiver um login habilitado.**
* Há diferença de fluxo entre cursos diferentes da IBMEC? <br/> **Sim.**
* A carga horária mínima e critérios variam por curso/PPC? <br/> **Sim, terá que ser feita uma análise por curso, mudando requisitos e fluxo.**
* Quais dados da empresa são obrigatórios? <br/> **CNPJ, Nome, Áreas que eles têm vagas disponíveis, Localização.**
* O cliente quer que a faculdade aprove previamente a empresa? <br/> **Sim.**
* A empresa poderá acompanhar mais de um aluno ao mesmo tempo? <br/> **Sim.**
* Quem decide se as atividades propostas são compatíveis com o curso? <br/> **A documentação do curso para uma análise automatizada, mas sempre podendo ter a interferência externa do coordenador se necessário.**
* Validação manual ou regras pré-definidas no sistema? <br/> **A ideia é colocar regras pré-definidas no sistema, com a possibilidade de alterações manuais de acordo com a necessidade.**
* O sistema exige preenchimento de Plano de Atividades? <br/> **Sim.**
* Esse plano deve ser comparado com critérios do curso? <br/> **Sim.**
* Existe lista de atividades proibidas? <br/> **É mais fácil só colocar as que serão aceitas do que as proibidas, mas caso na documentação tenha especificando alguma proibida, podemos colocar também.**
* Sistema bloqueia propostas fora da área? <br/> **Fora da área sim.**
* Como tratar casos com vaga parcialmente compatível? <br/> **Recusa.**
* O sistema precisa guardar justificativa pedagógica da aprovação? <br/> **Sim.**
* Haverá trilha de auditoria de quem aprovou a atividade? <br/> **Sim.**
* O sistema precisa controlar limite diário e semanal de jornada? <br/> **Sim.**
* O sistema deve alertar quando a jornada estiver fora do permitido? <br/> **Sim.**
* O cliente quer controlar duração máxima na mesma concedente? <br/> **Sim.**
* O sistema precisa exigir apólice/seguro antes da aprovação? <br/> **Sim.**
* Calcular automaticamente se a carga horária obrigatória foi integralizada? <br/> **Sim, inclusive o sistema deve analisar antes da aprovação do estágio se a quantidade de horas que a empresa oferece é compatível com a quantidade mínima que o aluno precisa.**

## 🎀 4. Documentos e Formalizações
* O sistema trabalhará com modelos prontos de documentos? <br/> **Sim.**
* O Termo de Compromisso (TCE) será gerado automaticamente? <br/> **Sim.**
* O Plano de Atividades será documento separado ou parte do TCE? <br/> **Estará dentro do TCE.**
* Haverá assinatura digital? <br/> **De quem for necessário assinatura.**
* O sistema deve versionar documentos em correções? <br/> **Sim.**
* Como será tratado documento vencido ou com divergência? <br/> **Necessária intervenção externa (Coordenador/Empresa).**
* Impedir início das atividades sem toda documentação obrigatória? <br/> **Sim, só será feita aprovação do estágio após todos os requisitos cumpridos.**
* Quem dá a aprovação final para o estágio começar? <br/> **Coordenação.**
* O sistema deve trabalhar com status de análise? <br/> **Sim, com status variados indicando o andamento.**
* Quando etapa é rejeitada, o processo volta para quem? <br/> **Depende do motivo da rejeição.**
* O professor aprova no início ou acompanha todo o estágio? <br/> **Acompanha durante todo o processo.**
* O coordenador participa sempre ou em exceções? <br/> **Apenas em exceções para requisitar a participação dele, mas ele sempre terá acesso se quiser.**
* O aluno anexa relatório final? <br/> **Sim.**
* A empresa emite avaliação final pelo sistema? <br/> **Sim.**
* Professor/coordenador lança parecer final na plataforma? <br/> **Sim.**
* Se o aluno trocar de empresa antes do início? <br/> **Reinicia todo o processo, ou separa quais documentações são independentes da vaga para não ter que fazer tudo do início.**
* Sistema deve permitir reaproveitamento parcial de documentos? <br/> **Muito interessante, se conseguirmos incluir essa funcionalidade seria muito bom.**
* Sistema deve permitir salvar rascunho? <br/> **Sim.**
* O cliente precisa de logs de auditoria? <br/> **Sim.**
* Quem poderá excluir documentos ou processos? <br/> **Coordenador.**
* O sistema deve manter o processo arquivado após encerramento para auditoria futura? <br/> **Sim.**

## 🎀 5. Notificações e Acompanhamento
* O aluno precisará lançar frequência, horas ou atividades periodicamente? <br/> **Sim.**
* O sistema deve registrar data e hora de cada aprovação? <br/> **Sim.**
* Há prazos máximos para cada ator responder? <br/> **Sim.**
* O sistema deve avisar automaticamente sobre atrasos de entrega? <br/> **Sim.**
* Quais eventos devem gerar notificação? <br/> **Documentação pendente, atraso, necessidade de alteração, recusa.**
* As notificações serão por e-mail, na plataforma ou ambos? <br/> **Ambos, interessante colocar SMS ou WhatsApp também.**
* Aluno deve ser avisado sobre mudança de status? <br/> **Sim.**
* Empresa recebe lembretes de pendências? <br/> **Sim.**
* Professor/coordenador recebe fila de aprovações pendentes? <br/> **Sim.**
* Notificações automáticas para prazos próximos do vencimento? <br/> **Sim.**
* Deve existir histórico completo de mensagens e ocorrências? <br/> **Sim.**
* O que acontece quando um documento é rejeitado? <br/> **Pode enviar uma notificação pedindo alteração tanto para o coordenador quanto para o aluno, e enquanto isso o processo fica como pendente.**
* Haverá dashboard gerencial? <br/> **Sim.**
* Quais indicadores importam mais no Dashboard? <br/> **Número de processos e pendências principalmente.**

 
## 🎀 Autor(es)
| Data | Versão | Descrição | Autor(es) |
| -- | -- | -- | -- |
| 07/04/2026 | 1.0 | Criação do documento | Letícia Valladão, Roger Pires, Lucas Alcântara, João Gabriel de Oliveira |
| 11/04/2026 | 2.0 | Adicionado os requisitos | Letícia Valladão |
| 16/04/2026 | 3.0 | Migrei os requisitos para um documento só para requisitos e adicionei as perguntas que respondi para elicitar os requisitos | Letícia Valladão |


## 🎀 Dados do Documento
> id: Brainstorm-Estagios <br/> title: Brainstorm do Site para Gerenciamento de Estágios para a IBMEC
