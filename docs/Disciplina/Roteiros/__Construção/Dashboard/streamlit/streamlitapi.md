#  Dashboard com Streamlit + Django REST API

## 1. **Introdução**
- O que é o Streamlit? (ferramenta Python para dashboards interativos)
- O que é uma API REST? (interface para acessar dados remotamente)
- Objetivo: Construir um dashboard que consome dados de um censo via API Django REST e gera relatórios interativos.

---

## 2. **Preparando o Ambiente**
- Instalar dependências:
    ```sh
    pip install streamlit requests pandas matplotlib
    ```
- Ter uma API Django REST rodando (como a do seu projeto).

---

## 3. **Estrutura Sugerida da API**
- Endpoints RESTful para:
    - `/api/domicilios/` (lista de domicílios)
    - `/api/moradores/` (lista de moradores)
    - `/api/responsaveis/` (lista de responsáveis)
- Cada endpoint retorna dados em JSON, por exemplo:
    ```json
    [
      {"id": 1, "uf": "SP", "municipio": "São Paulo", ...}
    ]
    ```

---

## 4. **Consumindo a API no Streamlit**
- Usar a biblioteca `requests` para buscar dados:
    ```python
    import requests
    import pandas as pd

    url = "http://localhost:8000/api/domicilios/"
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data)
    ```

---

## 5. **Montando o Dashboard**
- Estrutura básica do app:
    ```python
    import streamlit as st

    st.title("Relatório do Censo - Dashboard")
    # Carregar dados da API
    # Mostrar filtros (UF, município, faixa etária, etc)
    # Mostrar gráficos (pie, bar, etc)
    # Mostrar tabela de dados filtrados
    ```
- Exemplos de filtros:
    ```python
    uf = st.sidebar.selectbox("UF", df['uf'].unique())
    municipio = st.sidebar.selectbox("Município", df[df['uf'] == uf]['municipio'].unique())
    ```

---

## 6. **Visualizações**
- Gráficos com `matplotlib` ou `plotly`:
    - Distribuição por sexo, faixa etária, cor/raça, renda, etc.
    - Exemplo:
        ```python
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        df['sexo'].value_counts().plot.pie(autopct='%1.1f%%', ax=ax)
        st.pyplot(fig)
        ```

---

## 7. **Gerando Relatórios**
- Permitir download de relatórios filtrados (CSV, PDF, etc):
    ```python
    st.download_button("Baixar CSV", df_filtrado.to_csv(index=False), "relatorio.csv")
    ```

