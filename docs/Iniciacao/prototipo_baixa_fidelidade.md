## Introdução

<p align = "justify">
A construção do protótipo de baixa fidelidade auxilia a equipe de desenvolvimento a alcançar uma visualização simples do software para que tenham um norte na hora de passar para código.
</p>

## Metodologia

<p align = "justify">
Iniciamos o projeto através dos levantamentos iniciais da equipe, após discussões a ferramenta PlantUML foi a selecionada para a confecção das diferentes páginas desse processo.
</p>

## Protótipo de baixa fidelidade

### Tela Login - Geral

```puml
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

### Página de Cadastro - Empresa

```puml
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

### Página de cadastro de vaga de estágio - Empresa

```puml
@startsalt
title Página de cadastro de vaga de estágio - Empresa
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

### Painel Empresa
```puml
@startsalt
title Painel Empresa
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
### Página de Detalhes do Processo - Empresa
```puml
@startsalt
title Página de Detalhes do Processo - Empresa
{
  {+       
    **Documentos do Estagiário**               **<u>67%</u> de conformidade atual**
  
    --
    {# 
      **Nome** | **Status** | **Ações**
      Documento #1 📄 | Validado ✅| {[Visualizar 👁️]}
      Documento #2 📄| Em análise ⏳| {[Visualizar 👁️]}
      Documento #3 📄 | Negado ❌| {[Visualizar 👁️]}
    }

    --
    **Documentos da Empresa**                 **<u>69%</u> de conformidade atual**
  
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

### Painel do Coordenador
```puml
@startsalt
title Painel do Coordenador
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
```puml
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

### Página de detalhes do Processo - Aluno

```puml
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

### Painel do Aluno
```puml
@startsalt
title Painel Aluno
{
    {+
  **Nome do Aluno**:Julho Souza
  **Matrícula do Aluno**: 202569019487
  **E-mail do Aluno**: JulhoS@gmail.com 
    
    }
  {+
    **Vagas do aluno**
    --
    
    {#
      **Nome da empresa** | **Área*** | **Status** | **Ações**

      Microsoft | Analise de dados |Aceito ✅ | {[Visualizar 👁️]}
      
      Assaí | Suporte técnico | Recusado ❌ | {[Visualizar 👁️]}

      TMG Racing | Sistemas embarcados|  Recusado ❌| {[Visualizar 👁️]}
    }
  }
    -------
    {
  }
}
@endsalt
```

## Conclusão

<p align = "justify">
A partir da elaboração do protótipo foi possível ter uma noção inicial de como é a ideia do software e como deve ser traduzida para código.
</p>

## Autor(es)

| Data     | Versão | Descrição                            | Autor(es)                                                                            |
| -------- | ------- | -------------------------------------- | ------------------------------------------------------------------------------------ |
| 15/04/2026 | 1.0 | Criação do Documento | Roger Pires e Vinicius Machado |

## Dados do Documento
>id: prototipobaixafidelidade-Estágios <br/> title: Protótipo Baixa Fidelidade para Gerenciamento de Estágios para a IBMEC
