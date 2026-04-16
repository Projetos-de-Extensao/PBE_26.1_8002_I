# PBE_26.1_8002_I

Projeto da disciplina voltado à gestão e otimização dos estágios obrigatórios do IBMEC. A proposta é centralizar a formalização, validação e acompanhamento do estágio em um único fluxo, conectando aluno, empresa concedente e coordenação com rastreabilidade documental, regras acadêmicas por curso e menos dependência de processos manuais.

## Participantes

- Lucas de Souza Alcantara
- João Gabriel Teodósio de Oliveira Lima
- Roger dos Santos Tavares Pires
- Letícia Rocha Valladão
- Vinícius Dias Lopes Machado Martinez

## Tecnologias usadas

- Python
- Django
- MySQL / banco de dados relacional
- MkDocs
- Material for MkDocs
- PlantUML

## Estrutura de pastas

```text
PBE_26.1_8002_I/
├── .github/workflows/   # automações e publicação
├── docs/                # documentação fonte do projeto
│   ├── Iniciacao/
│   ├── Elaboracao/
│   ├── Construcao/
│   ├── Transicao/
│   ├── assets/          # imagens e arquivos de apoio
│   └── css/             # estilos extras do MkDocs
├── site/                # saída gerada do build do MkDocs
├── mkdocs.yml           # configuração da documentação
├── requirements.txt     # dependências Python
└── README.md
```

## Instalação local

O repositório hoje contém principalmente a documentação do projeto em MkDocs.

```bash
git clone https://github.com/Projetos-de-Extensao/PBE_26.1_8002_I.git
cd PBE_26.1_8002_I
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdocs serve
```

Depois disso, acesse a documentação local em `http://127.0.0.1:8000`.
