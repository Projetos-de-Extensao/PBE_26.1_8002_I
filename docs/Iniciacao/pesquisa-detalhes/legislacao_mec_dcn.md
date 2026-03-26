## Legislação do MEC, DCNs e Regras Acadêmicas do Estágio

### Visão geral
A regulamentação do estágio no ensino superior não depende de uma única norma. Para o software, é importante entender que existem **camadas normativas diferentes**:

- a **Lei nº 11.788/2008**, que estabelece as regras gerais do estágio no Brasil;
- a **LDB (Lei nº 9.394/1996)**, que fornece a base legal da educação nacional;
- as **Diretrizes Curriculares Nacionais (DCNs)**, que variam conforme o curso;
- o **Projeto Pedagógico do Curso (PPC)** e os regulamentos internos da instituição, que definem como essas regras são aplicadas localmente.

No contexto acadêmico, o estágio deve ser tratado como **ato educativo escolar supervisionado**, e não apenas como experiência de trabalho. Essa definição é central para o desenvolvimento do sistema, porque significa que o estágio precisa estar vinculado ao curso, ao processo formativo do aluno e ao acompanhamento institucional.

---

### 1. Natureza acadêmica do estágio
A Lei nº 11.788/2008 define o estágio como um ato educativo supervisionado, desenvolvido no ambiente de trabalho e voltado à preparação para o trabalho produtivo do estudante. Em termos de negócio, isso significa que o sistema não deve tratar o estágio apenas como vínculo administrativo entre aluno e empresa, mas como uma atividade com **validade acadêmica** e **finalidade pedagógica**.

#### Impacto no software
O sistema deve garantir que:

- o aluno esteja regularmente vinculado à instituição e ao curso;
- o estágio esteja relacionado à formação acadêmica;
- haja registro institucional da atividade;
- exista acompanhamento por responsáveis acadêmicos e da concedente.

---

### 2. Modalidades de estágio
A legislação distingue duas modalidades:

**Estágio obrigatório**  
É aquele previsto no projeto do curso como requisito para aprovação ou obtenção do diploma.

**Estágio não obrigatório**  
É atividade opcional, acrescida à carga horária regular e obrigatória do curso.

#### Impacto no software
O sistema deve diferenciar claramente as duas modalidades, porque elas afetam:

- exigência de carga horária para integralização;
- regras de aprovação;
- fluxos de validação;
- relatórios acadêmicos;
- critérios de conclusão do curso.

---

### 3. DCNs e PPC: onde entram no processo
As **DCNs não são únicas para todos os cursos**. O MEC publica diretrizes curriculares por área de formação, e cada curso pode ter regras específicas sobre estágio, competências, perfil do egresso e estrutura curricular. Além disso, o **PPC (Projeto Pedagógico de Curso) da instituição** operacionaliza essas diretrizes dentro da realidade do curso ofertado.

Por isso, para o sistema, não é correto assumir uma regra única para todos os alunos. Regras como:

- obrigatoriedade do estágio;
- **carga horária mínima**;
- critérios de aprovação;
- documentação exigida;
- necessidade de relatórios;
- etapas de validação

Devem ser tratadas como **configuráveis por curso e por instituição**. Isso decorre do fato de que a regra acadêmica concreta depende da combinação entre DCN do curso e PPC local. Ou seja, o MEC não diz "todo estágio tem 300 horas". Ele cria um documento para Direito, outro para Engenharia, outro para Medicina. Cada área tem suas regras.


---

### 4. Compatibilidade entre estágio e formação do aluno
Um dos pontos mais importantes para o domínio do problema é que o estágio deve ser **compatível com a área de formação** do estudante e com os objetivos educacionais do curso. A Lei do Estágio exige compatibilidade entre as atividades desenvolvidas e aquelas previstas no termo e no contexto formativo.

O MEC veda que o estudante exerça atividades genéricas ou desviadas do escopo de sua futura profissão (por exemplo, um estudante de engenharia exercendo funções exclusivamente administrativas ou de telemarketing).

Esse ponto é essencial, porque evita que o estágio seja formalizado apenas como relação burocrática, sem aderência ao objetivo pedagógico.

---

### 5. Atores obrigatórios no processo
Para que o estágio tenha validade acadêmica, há pelo menos três atores principais:

**Aluno**  
Participa como estagiário regularmente matriculado.

**Instituição de ensino**  
É responsável pela validação acadêmica do estágio e pela indicação de professor orientador.

**Parte concedente**  
É a organização que recebe o estagiário e indica um supervisor para acompanhá-lo.

A legislação também prevê:

- **professor orientador**, vinculado à instituição e à área desenvolvida no estágio;
- **supervisor da parte concedente**, responsável pelo acompanhamento das atividades no ambiente profissional.

#### Impacto no software
O sistema deve ter entidades, perfis e permissões separados para:

- aluno;
- orientador;
- supervisor;
- coordenação/secretaria;
- empresa concedente.

Também deve haver registro de responsabilidade e histórico de aprovação por ator.

---

### 6. Documentos essenciais do processo
Para a oficialização do estágio, a legislação exige formalização documental. O principal instrumento é o **Termo de Compromisso de Estágio**, celebrado entre estudante, parte concedente e instituição de ensino. A legislação também prevê acompanhamento, relatórios e comprovação das atividades.

#### Impacto no software
O backend deve contemplar:

- geração ou registro do termo de compromisso;
- controle de versão e status documental;
- aprovação institucional;
- armazenamento de relatórios periódicos;
- histórico de alterações;
- rastreabilidade para auditoria.

---

### 7. Carga horária, jornada e integralização
A legislação geral trata do estágio em termos de jornada e formalização, enquanto a exigência de **carga horária mínima obrigatória** para integralização depende do curso e do PPC. Ou seja, como dito anteriormente: a lei define a estrutura geral do instituto do estágio, mas a regra acadêmica concreta de conclusão do curso depende das DCNs e da organização curricular da instituição.

#### Impacto no software
O sistema deve separar:

- **jornada do estágio**: regra operacional do vínculo;
- **carga horária validada**: regra acadêmica de integralização;
- **carga horária mínima exigida**: parâmetro por curso/matriz;
- **horas aproveitadas**: horas efetivamente aceitas pela instituição.

---

### 8. O que é mais importante para a documentação técnica
Para a construção do software, os pontos mais relevantes não são apenas conceituais, mas sim aqueles que viram regra de negócio. Os principais são:

1. **O estágio é ato educativo supervisionado**, então precisa de validação acadêmica.  
2. **Há distinção entre estágio obrigatório e não obrigatório**, com impactos funcionais diferentes.  
3. **As regras específicas variam por curso**, pois dependem das DCNs e do PPC.  
4. **As atividades devem ser compatíveis com a formação do aluno**, e isso deve ser verificável no sistema.  
5. **Há múltiplos atores com papéis distintos**, exigindo controle de permissões e aprovações.  
6. **A oficialização depende de documentos e acompanhamento**, o que exige rastreabilidade e gestão documental.