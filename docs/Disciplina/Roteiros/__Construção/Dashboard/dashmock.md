# Roteiro: Criando um Dashboard de Censo Demográfico com Streamlit

Este roteiro explica passo a passo como criar um dashboard interativo para análise de dados demográficos utilizando o Streamlit, uma biblioteca Python para construção rápida de aplicações web de dados.

---

## 1. Instalação das Bibliotecas

Antes de começar, instale as bibliotecas necessárias:

```bash
pip install streamlit pandas numpy matplotlib
```

---

## 2. Estrutura do Projeto

- `dashmock.md` (este roteiro)
- `dashboard.py` (código do dashboard)

---

## 3. Importação das Bibliotecas

No início do seu script, importe as bibliotecas essenciais:

```python
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
```

---

## 4. Configuração da Página

Configure o layout e o título da página do Streamlit:

```python
st.set_page_config(layout="wide", page_title="Dashboard Censo Demográfico")
```

---

## 5. Geração dos Dados Fictícios

Crie uma função para gerar dados simulados do censo, incluindo domicílios e moradores, com características como UF, município, sexo, cor/raça, idade, renda, abastecimento de água, esgoto e lixo.

- Utilize dicionários para mapear códigos para descrições.
- Gere dados aleatórios para cada domicílio e seus moradores.
- Junte os dados em um DataFrame do Pandas.

---

## 6. Carregamento dos Dados

No início da execução, gere ou carregue os dados. Em um cenário real, você pode ler de um CSV ou banco de dados. Aqui, usamos dados fictícios:

```python
if 'df_censo' not in st.session_state:
    st.session_state.df_censo = gerar_dados_ficticios(num_domicilios=5000, num_max_moradores_por_domicilio=6)
df = st.session_state.df_censo
```

---

## 7. Barra Lateral de Filtros

Implemente filtros interativos na barra lateral para permitir ao usuário selecionar:

- UF (Estado)
- Município (dependente da UF)
- Sexo
- Cor/Raça
- Faixa Etária
- Espécie de Domicílio
- Faixa de Rendimento

Cada filtro refina os dados exibidos no painel principal.

---

## 8. Painel Principal

Exiba os principais indicadores e gráficos:

- **Indicadores Chave (KPIs):** Total de moradores e domicílios filtrados.
- **Gráficos de Distribuição:** Por sexo, cor/raça, abastecimento de água, destino do lixo e faixa de rendimento.
- **Alfabetização:** Percentual de pessoas com 5 anos ou mais que sabem ler e escrever.

Utilize `matplotlib` para criar gráficos e `st.pyplot` para exibi-los no Streamlit.

---

## 9. Exibição de Amostras dos Dados

Inclua a opção de mostrar uma amostra dos dados filtrados para inspeção detalhada.

---

## 10. Informações Finais

Adicione mensagens informativas na barra lateral para explicar o propósito do dashboard e lembrar que os dados são fictícios.

---

## 11. Execução do Dashboard

Para rodar o dashboard, execute no terminal:

```bash
streamlit run dashboard.py
```

---

## 12. Dicas Finais

- Adapte os filtros e gráficos conforme as necessidades do seu projeto.
- Para dados reais, substitua a função de geração por leitura de arquivos ou banco de dados.
- Explore outros componentes do Streamlit para enriquecer a experiência do usuário.

---

Com este roteiro, você pode criar dashboards interativos e informativos para análise de dados demográficos ou de outras naturezas usando Python e Streamlit.

```python

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Configuração da página do Streamlit
st.set_page_config(layout="wide", page_title="Dashboard Censo Demográfico")

# Função para gerar dados fictícios
def gerar_dados_ficticios(num_domicilios=1000, num_max_moradores_por_domicilio=5):
    """
    Gera um DataFrame do Pandas com dados fictícios do censo.
    """
    ufs = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']
    municipios_por_uf = {uf: [f'Município {i+1}-{uf}' for i in range(np.random.randint(1, 5))] for uf in ufs}

    especie_domicilio_opcoes = {
        1: 'DOMICÍLIO PARTICULAR PERMANENTE OCUPADO',
        5: 'DOMICÍLIO PARTICULAR IMPROVISADO OCUPADO',
        6: 'DOMICÍLIO COLETIVO COM MORADOR'
    }
    
    tipo_domicilio_opcoes = {
        '011': 'CASA', '012': 'CASA DE VILA OU EM CONDOMÍNIO', '013': 'APARTAMENTO',
        '014': 'HABITAÇÃO EM CASA DE CÔMODOS OU CORTIÇO',
        '051': 'TENDA OU BARRACA',
        '061': 'ASILO', '062': 'HOTEL OU PENSÃO'
    }

    sexo_opcoes = {1: 'MASCULINO', 2: 'FEMININO'}
    cor_raca_opcoes = {1: 'BRANCA', 2: 'PRETA', 3: 'AMARELA', 4: 'PARDA', 5: 'INDÍGENA'}
    
    abastecimento_agua_opcoes = {
        1: 'REDE GERAL DE DISTRIBUIÇÃO', 2: 'POÇO PROFUNDO OU ARTESIANO', 3: 'POÇO RASO, FREÁTICO OU CACIMBA',
        4: 'FONTE, NASCENTE OU MINA', 5: 'CARRO-PIPA', 6: 'ÁGUA DA CHUVA ARMAZENADA',
        7: 'RIOS, AÇUDES, CÓRREGOS, LAGOS E IGARAPÉS', 8: 'OUTRA FORMA'
    }
    
    esgoto_opcoes = {
        1: 'REDE GERAL OU PLUVIAL', 2: 'FOSSA SÉPTICA LIGADA À REDE', 3: 'FOSSA SÉPTICA NÃO LIGADA À REDE',
        4: 'FOSSA RUDIMENTAR OU BURACO', 5: 'VALA', 6: 'RIO, LAGO, CÓRREGO OU MAR', 7: 'OUTRA FORMA'
    }
    
    lixo_opcoes = {
        1: 'COLETADO NO DOMICÍLIO POR SERVIÇO DE LIMPEZA', 2: 'DEPOSITADO EM CAÇAMBA DE SERVIÇO DE LIMPEZA',
        3: 'QUEIMADO NA PROPRIEDADE', 4: 'ENTERRADO NA PROPRIEDADE',
        5: 'JOGADO EM TERRENO BALDIO, ENCOSTA OU ÁREA PÚBLICA', 6: 'OUTRO DESTINO'
    }

    renda_faixa_opcoes = {
        1: 'R$ 1,00 A R$ 500,00', 2: 'R$ 501,00 A R$ 1.000,00', 3: 'R$ 1.001,00 A R$ 2.000,00',
        4: 'R$ 2.001,00 A R$ 3.000,00', 5: 'R$ 3.001,00 A R$ 5.000,00', 6: 'R$ 5.001,00 A R$ 10.000,00',
        7: 'R$ 10.001,00 A R$ 20.000,00', 8: 'R$ 20.001,00 A R$ 100.000,00', 9: 'R$ 100.001,00 OU MAIS',
        0: 'SEM RENDIMENTO' # Adicionado para quem não tem rendimento
    }
    
    sabe_ler_escrever_opcoes = {1: 'SIM', 2: 'NÃO'}

    dados_domicilios = []
    dados_moradores = []
    id_morador_global = 0

    for i in range(num_domicilios):
        id_domicilio = f'DOM{i+1:05d}'
        uf_escolhida = np.random.choice(ufs)
        municipio_escolhido = np.random.choice(municipios_por_uf[uf_escolhida])
        especie_dom_cod = np.random.choice(list(especie_domicilio_opcoes.keys()))
        tipo_dom_cod = np.random.choice(list(tipo_domicilio_opcoes.keys()))
        
        abastecimento_cod = np.random.choice(list(abastecimento_agua_opcoes.keys()))
        esgoto_cod = np.random.choice(list(esgoto_opcoes.keys()))
        lixo_cod = np.random.choice(list(lixo_opcoes.keys()))
        
        # Renda é por domicílio (para o responsável)
        renda_responsavel_cod = np.random.choice(list(renda_faixa_opcoes.keys()))

        num_moradores_neste_domicilio = np.random.randint(1, num_max_moradores_por_domicilio + 1)
        
        dados_domicilios.append({
            'ID_DOMICILIO': id_domicilio,
            'UF': uf_escolhida,
            'MUNICIPIO': municipio_escolhido,
            'ESPECIE_DOMICILIO_COD': especie_dom_cod,
            'ESPECIE_DOMICILIO_DESC': especie_domicilio_opcoes[especie_dom_cod],
            'TIPO_DOMICILIO_COD': tipo_dom_cod,
            'TIPO_DOMICILIO_DESC': tipo_domicilio_opcoes[tipo_dom_cod],
            'ABASTECIMENTO_AGUA_COD': abastecimento_cod,
            'ABASTECIMENTO_AGUA_DESC': abastecimento_agua_opcoes[abastecimento_cod],
            'ESGOTO_COD': esgoto_cod,
            'ESGOTO_DESC': esgoto_opcoes[esgoto_cod],
            'LIXO_COD': lixo_cod,
            'LIXO_DESC': lixo_opcoes[lixo_cod],
            'RENDA_FAIXA_RESPONSAVEL_COD': renda_responsavel_cod,
            'RENDA_FAIXA_RESPONSAVEL_DESC': renda_faixa_opcoes[renda_responsavel_cod],
            'NUM_MORADORES': num_moradores_neste_domicilio
        })

        for j in range(num_moradores_neste_domicilio):
            id_morador_global += 1
            sexo_cod = np.random.choice(list(sexo_opcoes.keys()))
            cor_raca_cod = np.random.choice(list(cor_raca_opcoes.keys()))
            idade = np.random.randint(0, 100)
            sabe_ler_escrever_cod = np.random.choice(list(sabe_ler_escrever_opcoes.keys())) if idade >= 5 else 2 # Só para maiores de 5 anos

            dados_moradores.append({
                'ID_MORADOR': f'MOR{id_morador_global:07d}',
                'ID_DOMICILIO': id_domicilio,
                'SEXO_COD': sexo_cod,
                'SEXO_DESC': sexo_opcoes[sexo_cod],
                'IDADE': idade,
                'COR_RACA_COD': cor_raca_cod,
                'COR_RACA_DESC': cor_raca_opcoes[cor_raca_cod],
                'SABE_LER_ESCREVER_COD': sabe_ler_escrever_cod,
                'SABE_LER_ESCREVER_DESC': sabe_ler_escrever_opcoes[sabe_ler_escrever_cod] if idade >=5 else sabe_ler_escrever_opcoes[2]
            })
            
    df_domicilios = pd.DataFrame(dados_domicilios)
    df_moradores = pd.DataFrame(dados_moradores)
    
    # Juntar os dataframes
    df_completo = pd.merge(df_moradores, df_domicilios, on='ID_DOMICILIO', how='left')
    
    return df_completo

# Carregar ou gerar os dados
# Em um aplicativo real, você carregaria os dados de um arquivo CSV, banco de dados, etc.
# Ex: df = pd.read_csv('seus_dados_do_censo.csv')
if 'df_censo' not in st.session_state:
    st.session_state.df_censo = gerar_dados_ficticios(num_domicilios=5000, num_max_moradores_por_domicilio=6)

df = st.session_state.df_censo

# --- BARRA LATERAL DE FILTROS ---
st.sidebar.header('Filtros Demográficos')

# Filtro de UF
ufs_disponiveis = ['Todos'] + sorted(df['UF'].unique().tolist())
uf_selecionada = st.sidebar.selectbox('UF (Estado):', ufs_disponiveis)

# Filtrar dados por UF
if uf_selecionada != 'Todos':
    df_filtrado_sidebar = df[df['UF'] == uf_selecionada].copy() # Usar .copy() para evitar SettingWithCopyWarning
else:
    df_filtrado_sidebar = df.copy()

# Filtro de Município (dependente da UF)
if uf_selecionada != 'Todos':
    municipios_disponiveis = ['Todos'] + sorted(df_filtrado_sidebar['MUNICIPIO'].unique().tolist())
else:
    municipios_disponiveis = ['Todos'] # Se UF for Todos, mostrar todos os municípios seria demais
    
municipio_selecionado = st.sidebar.selectbox('Município:', municipios_disponiveis)

# Filtrar dados por Município
if municipio_selecionado != 'Todos':
    df_filtrado_sidebar = df_filtrado_sidebar[df_filtrado_sidebar['MUNICIPIO'] == municipio_selecionado].copy()


# Filtro de Sexo
sexos_disponiveis = ['Todos'] + df_filtrado_sidebar['SEXO_DESC'].unique().tolist()
sexo_selecionado = st.sidebar.selectbox('Sexo:', sexos_disponiveis)
if sexo_selecionado != 'Todos':
    df_filtrado_sidebar = df_filtrado_sidebar[df_filtrado_sidebar['SEXO_DESC'] == sexo_selecionado].copy()

# Filtro de Cor/Raça
cor_raca_disponiveis = ['Todos'] + df_filtrado_sidebar['COR_RACA_DESC'].unique().tolist()
cor_raca_selecionada = st.sidebar.selectbox('Cor ou Raça:', cor_raca_disponiveis)
if cor_raca_selecionada != 'Todos':
    df_filtrado_sidebar = df_filtrado_sidebar[df_filtrado_sidebar['COR_RACA_DESC'] == cor_raca_selecionada].copy()

# Filtro de Faixa de Idade
st.sidebar.subheader('Faixa Etária (Moradores)')
idade_min, idade_max = int(df_filtrado_sidebar['IDADE'].min()), int(df_filtrado_sidebar['IDADE'].max())
faixa_idade_selecionada = st.sidebar.slider(
    'Selecione a faixa etária:',
    min_value=idade_min,
    max_value=idade_max,
    value=(idade_min, idade_max)
)
df_filtrado_sidebar = df_filtrado_sidebar[
    (df_filtrado_sidebar['IDADE'] >= faixa_idade_selecionada[0]) &
    (df_filtrado_sidebar['IDADE'] <= faixa_idade_selecionada[1])
].copy()


# Filtro de Espécie de Domicílio
especies_dom_disponiveis = ['Todos'] + df_filtrado_sidebar['ESPECIE_DOMICILIO_DESC'].unique().tolist()
especie_dom_selecionada = st.sidebar.selectbox('Espécie de Domicílio:', especies_dom_disponiveis)
if especie_dom_selecionada != 'Todos':
    df_filtrado_sidebar = df_filtrado_sidebar[df_filtrado_sidebar['ESPECIE_DOMICILIO_DESC'] == especie_dom_selecionada].copy()

# Filtro de Faixa de Rendimento do Responsável (por domicílio)
rendas_disponiveis = ['Todos'] + sorted(df_filtrado_sidebar['RENDA_FAIXA_RESPONSAVEL_DESC'].unique().tolist(), key=lambda x: (x.startswith('R$'), x)) # Ordenar corretamente
renda_selecionada = st.sidebar.selectbox('Faixa de Rendimento do Responsável:', rendas_disponiveis)
if renda_selecionada != 'Todos':
    df_filtrado_sidebar = df_filtrado_sidebar[df_filtrado_sidebar['RENDA_FAIXA_RESPONSAVEL_DESC'] == renda_selecionada].copy()


# --- PAINEL PRINCIPAL ---
st.title('Painel Censo Demográfico IBGE 2022 (Dados Fictícios)')

if df_filtrado_sidebar.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
else:
    # Indicadores Chave (KPIs)
    st.header('Indicadores Gerais')
    total_moradores = df_filtrado_sidebar['ID_MORADOR'].nunique()
    total_domicilios = df_filtrado_sidebar['ID_DOMICILIO'].nunique()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Total de Moradores Selecionados", value=f"{total_moradores:,}".replace(",", "."))
    with col2:
        st.metric(label="Total de Domicílios Selecionados", value=f"{total_domicilios:,}".replace(",", "."))

    st.markdown("---")

    # Gráficos
    st.header('Distribuições da População')
    
    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:
        st.subheader('Distribuição por Sexo')
        if total_moradores > 0:
            sexo_counts = df_filtrado_sidebar['SEXO_DESC'].value_counts()
            fig_sexo, ax_sexo = plt.subplots(figsize=(6, 4))
            wedges, texts, autotexts = ax_sexo.pie(
                sexo_counts, 
                labels=sexo_counts.index, 
                autopct='%1.1f%%', 
                startangle=90,
                colors=['#66b3ff','#ff9999','#99ff99','#ffcc99'] # Cores amigáveis
            )
            ax_sexo.axis('equal') # Equal aspect ratio ensures that pie is drawn as a circle.
            plt.setp(autotexts, size=8, weight="bold", color="white")
            plt.setp(texts, size=7)
            st.pyplot(fig_sexo)
        else:
            st.info("Sem dados de sexo para exibir.")

    with col_graf2:
        st.subheader('Distribuição por Cor ou Raça')
        if total_moradores > 0:
            cor_raca_counts = df_filtrado_sidebar['COR_RACA_DESC'].value_counts().sort_index()
            fig_cor, ax_cor = plt.subplots(figsize=(7, 5))
            bars = ax_cor.bar(cor_raca_counts.index, cor_raca_counts.values, color='skyblue')
            ax_cor.set_ylabel('Número de Pessoas')
            ax_cor.set_xlabel('Cor ou Raça')
            plt.xticks(rotation=45, ha="right", fontsize=8)
            plt.yticks(fontsize=8)
            ax_cor.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ','))) # Formatar eixo Y
            # Adicionar rótulos nas barras
            for bar in bars:
                yval = bar.get_height()
                ax_cor.text(bar.get_x() + bar.get_width()/2.0, yval + 0.05 * yval, f'{int(yval):,}', ha='center', va='bottom', fontsize=7)

            st.pyplot(fig_cor)
        else:
            st.info("Sem dados de cor/raça para exibir.")
            
    st.markdown("---")
    st.header('Características dos Domicílios')
    
    # Agrupar por domicílio para características do domicílio
    df_domicilios_filtrados = df_filtrado_sidebar.drop_duplicates(subset=['ID_DOMICILIO']).copy()

    if df_domicilios_filtrados.empty:
        st.info("Sem dados de domicílios para os filtros selecionados.")
    else:
        col_dom1, col_dom2 = st.columns(2)
        with col_dom1:
            st.subheader('Principal Forma de Abastecimento de Água')
            abastecimento_counts = df_domicilios_filtrados['ABASTECIMENTO_AGUA_DESC'].value_counts()
            fig_agua, ax_agua = plt.subplots(figsize=(7, 5))
            bars_agua = ax_agua.barh(abastecimento_counts.index, abastecimento_counts.values, color='lightcoral')
            ax_agua.set_xlabel('Número de Domicílios')
            ax_agua.set_ylabel('Forma de Abastecimento')
            plt.xticks(fontsize=8)
            plt.yticks(fontsize=7)
            ax_agua.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
            # Adicionar rótulos nas barras
            for i, v in enumerate(abastecimento_counts.values):
                 ax_agua.text(v + 0.01 * abastecimento_counts.max() , i , str(f'{v:,}'), color='black', va='center', fontsize=7)
            st.pyplot(fig_agua)

        with col_dom2:
            st.subheader('Destino do Lixo')
            lixo_counts = df_domicilios_filtrados['LIXO_DESC'].value_counts()
            fig_lixo, ax_lixo = plt.subplots(figsize=(7, 5))
            bars_lixo = ax_lixo.barh(lixo_counts.index, lixo_counts.values, color='mediumseagreen')
            ax_lixo.set_xlabel('Número de Domicílios')
            ax_lixo.set_ylabel('Destino do Lixo')
            plt.xticks(fontsize=8)
            plt.yticks(fontsize=7)
            ax_lixo.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
            for i, v in enumerate(lixo_counts.values):
                 ax_lixo.text(v + 0.01 * lixo_counts.max() , i , str(f'{v:,}'), color='black', va='center', fontsize=7)
            st.pyplot(fig_lixo)
            
        st.markdown("---")
        st.subheader('Distribuição de Rendimento Mensal do Responsável pelo Domicílio')
        renda_counts = df_domicilios_filtrados['RENDA_FAIXA_RESPONSAVEL_DESC'].value_counts().sort_index(key=lambda x: (x.str.startswith('R$'), x))
        
        fig_renda, ax_renda = plt.subplots(figsize=(10, 6))
        bars_renda = ax_renda.bar(renda_counts.index, renda_counts.values, color='gold')
        ax_renda.set_ylabel('Número de Domicílios')
        ax_renda.set_xlabel('Faixa de Rendimento')
        plt.xticks(rotation=45, ha="right", fontsize=8)
        plt.yticks(fontsize=8)
        ax_renda.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
        for bar in bars_renda:
            yval = bar.get_height()
            ax_renda.text(bar.get_x() + bar.get_width()/2.0, yval + 0.05 * yval, f'{int(yval):,}', ha='center', va='bottom', fontsize=7)
        st.pyplot(fig_renda)


    st.markdown("---")
    st.header("Alfabetização (Pessoas com 5 anos ou mais)")
    df_alfabetizacao = df_filtrado_sidebar[df_filtrado_sidebar['IDADE'] >= 5].copy()
    if not df_alfabetizacao.empty:
        sabe_ler_counts = df_alfabetizacao['SABE_LER_ESCREVER_DESC'].value_counts()
        fig_ler, ax_ler = plt.subplots(figsize=(6,4))
        wedges_ler, texts_ler, autotexts_ler = ax_ler.pie(
            sabe_ler_counts,
            labels=sabe_ler_counts.index,
            autopct='%1.1f%%',
            startangle=90,
            colors=['#c2c2f0','#ffb3e6']
        )
        ax_ler.axis('equal')
        plt.setp(autotexts_ler, size=8, weight="bold", color="white")
        plt.setp(texts_ler, size=7)
        st.pyplot(fig_ler)
    else:
        st.info("Sem dados de alfabetização para exibir para os filtros selecionados.")


    # Exibir uma amostra dos dados filtrados (opcional)
    st.markdown("---")
    if st.checkbox('Mostrar amostra dos dados filtrados'):
        st.subheader('Amostra dos Dados Filtrados (Moradores)')
        st.dataframe(df_filtrado_sidebar.head(100))
        
        st.subheader('Amostra dos Dados Filtrados (Domicílios - únicos)')
        st.dataframe(df_domicilios_filtrados.head(100))

st.sidebar.markdown("---")
st.sidebar.info("Este é um dashboard com dados fictícios gerados para simular o Censo Demográfico IBGE 2022.")

```
