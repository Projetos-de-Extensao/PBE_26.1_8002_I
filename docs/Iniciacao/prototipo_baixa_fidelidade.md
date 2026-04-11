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

### Página de Processo - Coordenador
```plantuml
@startsalt
title Página de Processo - Coordenador
{
  {+
    **Detalhes do Processo**
    --
    {
       "🔎Buscar:   "| [Filtrar ⌄]
    }
    --
    {
      {# Documento #1 | [ Abrir ] }
      --
      {# Documento #2 | [ Abrir ] }
    }
    --
    **Documentos Aprovados:** 8
    **Documentos em Aberto:** 3
    **Documentos Faltantes:** 5
  }
}
@endsalt
```

### Tela do Feed

### Tela Feed com configurações

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


### Tela Cadastrar torneio 1


### Tela Cadastrar torneio 2

### Tela Cadastrar torneio 3


### Tela Cadastrar torneio 4


### Tela com meus torneios

### Tela de inscrição em torneio


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

> Material Design Color Tool. Disponível em:  https://material.io/resources/color/#!/?view.left=0&view.right=0

> PMI. Um guia do conhecimento em gerenciamento de projetos. Guia PMBOK® 5a. ed. EUA: Project Management Institute, 2013.

> Ferramenta Figma. Disponível em https://www.figma.com

## Autor(es)

| Data     | Versão | Descrição                            | Autor(es)                                                                            |
| -------- | ------- | -------------------------------------- | ------------------------------------------------------------------------------------ |
| 07/09/20 | 1.0     | Criação do documento                 | Lucas Alexandre e Matheus Estanislau                                                 |
| 07/09/20 | 1.1     | Adicionado as imagens do protótipo    | Lucas Alexandre e Matheus Estanislau                                                 |
| 07/09/20 | 1.2     | Adicionado conclusão e referências   | Lucas Alexandre e Matheus Estanislau                                                 |
| 26/10/20 | 2.0     | Adicionada a versão 2.0 do protótipo | João Pedro, Lucas Alexandre, Matheus Estanislau, Moacir Mascarenha e Renan Cristyan |
