---
id: prototipobaixa
title: Protótipo Baixa Fidelidade
---
## Introdução

<p align = "justify">
A construção do protótipo de alta fidelidade auxilia a equipe de desenvolvimento a encontrar um nível de detalhes abrangentes, extrair funcionalidades, testar usabilidade, e também fornece uma base para o gerenciamento do projeto pois com o protótipo é possível realizar estimativas de quanto tempo será necessário desempenhar em cada funcionalidade.
</p>

## Metodologia

<p align = "justify">
Iniciamos o projeto através dos levantamentos iniciais da equipe, após discussões a ferramenta Figma foi selecionada para produzir o protótipo de alta fidelidade com auxílio do Material Design Color Tool.
</p>

## Protótipo de alta fidelidade

### Versão 1.0

### Tela Login

```plantuml
@startsalt
title Página de login - Geral
{
  {+
    **Login com e-mail**
    ==
    E-mail:
    "                     "
    .
    Senha:
    "                     "
    .
    [] Manter Login
    .
    [       Continuar      ]
  
  }
}
@endsalt
```

### Tela Cadastro - Empresa

```plantuml
@startsalt
title Página de Cadastro - Empresa
{
  {+
    **Cadastrar empresa:**
    ==
    CNPJ:
    "                         "
    .
    Razão social:
    "                         "
    .
    Nome fantasia:
    "                         "
    .
    Email:
    "                         "
    .
    Senha:
    "                         "
    .
    Possúi convênio com a faculdade?
    [] Sim 
    [] Não
    .
    [         Continuar      ]
  
  }
}
@endsalt
```

### Página de inscrição de vaga de estágio

```plantuml
@startsalt
title Página de Cadastro - Empresa
{
  {+
    **Cadastrar vaga de estágio:**
    ==
    Nome da vaga:
    "                                       "
    .
    Áreas academicas:
    "                                       "
    .
    Periodo:
    {Min | ^0^^ | Max. | ^0^}
    .
    Ano de formação:
    {| ^2026^}
    .
    Faixa salarial:
    "                                       "
    .
    Local:
    {| ^UF^ | ^Cidade^ }
    {CEP: | "                "}
    {Número: | "             "}
    {| Complemento: | "         "}
    .
    Modalidade e Carga Horária:
    { ^Presencial^ | ^6 horas/dia^ }
    .
    Anexar documento complementar (PDF):
    [ Procurar arquivo...]
    .
    [         Enviar vaga para análise      ]
  
  }
}
@endsalt
```

### Página de detalhes do Processo - Empresa
```plantuml
@startsalt
title Página de detalhes do Processo - Empresa
{
  {+       
    {# **Vagas disponibilizadas:** { "**4**" }}
   --
    {
       "🔎Buscar por nome da vaga:                                     "|^Filtros^
    }
    --
    
    {# 
      **Vaga**| **Curso** | **Status** | **Ações**
      Estágio como analísta de processos juridicos | Direito, Adiministração | Aceito ✅ |{[Visualizar 👁️] | [Remover ❌] | [Editar vaga ✏]}
      Estágio em análize de dados |  Ciência de Dados e IA, Analize de dados | Em análise ⏳ |{[Visualizar 👁️] | [Remover ❌] | [Editar vaga ✏]}
      Estágio em manutenção de bancos de dados |Eng de Software, Eng. se Computação | Negado ❌ |{[Visualizar 👁️] | [Remover ❌] | [Editar vaga ✏]}
      Estágio em controle de midea | Publicidade e Propaganda| Em análise ⏳ |{[Visualizar 👁️] | [Remover ❌] | [Editar vaga ✏]}
    }
}
}
@endsalt
```

### Página de Processos - Coordenador
```plantuml
@startsalt
title Página de Processos - Coordenador
{
  {+       
    {# **Processos Abertos:** { "**15**" }}
   --
    {
       "🔎Buscar por nome do Aluno:                                     "|[ Filtrar ▼]
    }
    --
    
    {# 
      **Nome do Aluno**|**Matrícula**| **Curso** | **Conformidade** | **Ações**
      Breno L. Jordan |202000000000 | Direito | 67% |{[Visualizar 👁️] | [Remover ❌]}
      César Cohen |202000000000 | Engenharia de Software | 69% |{[Visualizar 👁️] | [Remover ❌]}
      Elizabeth Webber |202000000000 | Ciência de Dados e IA | 24% |{[Visualizar 👁️] | [Remover ❌]}
      Arthur Cervero |202000000000 | Publicidade e Propaganda| 22% |{[Visualizar 👁️] | [Remover ❌]}
      Beatrice Portinari |202000000000 | Engenharia de Computação| 71% |{[Visualizar 👁️] | [Remover ❌]}
    }
}
}
@endsalt
```

### Página de detalhes do Processo - Coordenador
```plantuml
@startsalt
title Página de detalhes do Processo - Coordenador
{
    {+
  **Nome do Aluno** | **Matrícula do Aluno**
  **E-mail do Aluno**| [Mais informações]
    
    }
  {+
    **Detalhes do Processo**                                  **<u>67%</u> de conformidade atual**
    --
    {
       "🔎Buscar:                                 "| [ Filtrar ⌄]
    }
    --
    {#
      **Nome** | **Status** | **Ações**

      Documento #1 📄 | Validado ✅| {[Visualizar 👁️] | [Alterar Status✏️]}
      
      Documento #2 📄 | Em análise ⏳| {[Visualizar 👁️] | [Alterar Status✏️]}

      Documento #3 📄 |  Negado ❌| {[Visualizar 👁️] | [Alterar Status✏️]}
    }
  }
    -------
    {
    {#
    **Documentos Aprovados:** 8
    **Documentos em Análise:** 3
    **Documentos Faltantes:** 5
    }
  }
}
@endsalt
```

### Tela de documentos - Aluno

```plantuml
@startsalt
title Página de Documentos - Aluno
{
  {+       
    **Meus Documentos**                             **<u>67%</u> de conformidade atual**
  
    --
    {# 
      **Nome** | **Status** | **Ações**
      Documento #1 📄 | Validado ✅| {[Visualizar 👁️] | [Alterar ✏️]}
      Documento #2 📄| Em análise ⏳| {[Visualizar 👁️] | [Alterar ✏️]}
      Documento #3 📄 | Negado ❌| {[Visualizar 👁️] | [Alterar ✏️]}
    }

    --
    {
                   {[ Anexar novo documento 📎] }
    }
  }
}
@endsalt
```

<p align = "justify">
Na primeira versão do protótipo utilizamos a ferramenta <a href="https://material.io/resources/color/#!/?view.left=0&view.right=0">Material Design Color Tool</a>  para auxiliar na criação da paleta de cores do aplicativo, definimos as cores base do aplicativo mas as cores definidas para as telas 12 e 13 ainda não foram decididas.
</p>

### Versão 2.0

### Versão 1.0

### Tela Login

[![Prototipo 1](../assets/Prototipo/image.png)](../assets/Prototipo/image.png)

### Tela Cadastro 1

[![Prototipo 2](../assets/Prototipo/image.png)](../assets/Prototipo/image.png)

### Tela Cadastro 2

[![Prototipo 3](../assets/Prototipo/image.png)](../assets/Prototipo/image.png)

### Tela Esqueceu Senha

[![Prototipo 4](../assets/Prototipo/image.png)](../assets/Prototipo/image.png)

### Tela do Feed

[![Prototipo 5](../assets/Prototipo/image.png)](../assets/Prototipo/image.png)

### Tela Feed com configurações

[![Prototipo 6](../assets/Prototipo/image.png)](../assets/Prototipo/image.png)

### Tela Perfil

[![Prototipo 7](../assets/Prototipo/image.png)](../assets/Prototipo/image.png)

### Tela Cadastrar torneio 1

[![Prototipo 8](../assets/Prototipo/image.png)](../assets/Prototipo/image.png)

### Tela Cadastrar torneio 2

[![Prototipo 9](../assets/Prototipo/image.png)](../assets/Prototipo/image.png)

### Tela Cadastrar torneio 3

[![Prototipo 10](../assets/Prototipo/image.png)](../assets/Prototipo/image.png)

### Tela Cadastrar torneio 4

[![Prototipo 11](../assets/Prototipo/image.png)](../assets/Prototipo/image.png)

### Tela com meus torneios

[![Prototipo 12](../assets/Prototipo/image.png)](../assets/Prototipo/image.png)

### Tela de inscrição em torneio

[![Prototipo 13](../assets/Prototipo/image.png)](../assets/Prototipo/image.png)

link para o `<a href="https://www.figma.com/">`Protótipo`</a>`

## Conclusão

<p align = "justify">
A partir da elaboração do protótipo foi possível ter uma noção inicial da interface do usuário, definindo fluxo, paleta de cores, botões, app bars e diversas outras funcionalidades
</p>

## Referências

## Autor(es)

| Data     | Versão | Descrição                            | Autor(es)                                                                            |
| -------- | ------- | -------------------------------------- | ------------------------------------------------------------------------------------ |
| | 1.0 | | |
| | 1.1 | | |
| | 1.2 | | |
| | 2.0 | | |
