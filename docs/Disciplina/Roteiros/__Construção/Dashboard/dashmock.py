import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from data import gerar_dados_ficticios

# Configuração da página do Streamlit
st.set_page_config(layout="wide", page_title="Dashboard Censo Demográfico")

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
# Função de ordenação customizada para as faixas de renda
def ordenar_faixas_renda(faixa):
    if faixa == 'Todos':
        return (0, 0, '')  # Coloca 'Todos' no início
    if 'Sem Rendimento' in faixa:
        return (1, 0, faixa)  # Coloca 'Sem Rendimento' depois de 'Todos'
    # Extrai números da faixa e usa-os para ordenação
    import re
    numeros = [int(n) for n in re.findall(r'\d+', faixa)]
    valor = numeros[0] if numeros else 0
    return (2, valor, faixa)
rendas_disponiveis = ['Todos'] + sorted(df_filtrado_sidebar['RENDA_FAIXA_RESPONSAVEL_DESC'].unique().tolist(), key=ordenar_faixas_renda)
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
        renda_counts = df_domicilios_filtrados['RENDA_FAIXA_RESPONSAVEL_DESC'].value_counts().sort_index(key=lambda x: pd.Index(x).map(ordenar_faixas_renda))
        
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