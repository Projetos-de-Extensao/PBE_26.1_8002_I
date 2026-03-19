import streamlit as st
import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns

# --- Configurações da Página ---
st.set_page_config(layout="wide", page_title="Dashboard Estatístico")

# --- Funções Auxiliares ---

@st.cache_data # Cache para otimizar o carregamento de dados
def carregar_dados_json(caminho_arquivo_json):
    """Carrega dados de um arquivo JSON."""
    try:
        with open(caminho_arquivo_json, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        return pd.DataFrame(dados)
    except FileNotFoundError:
        st.error(f"Erro: Arquivo JSON não encontrado em '{caminho_arquivo_json}'.")
        return pd.DataFrame()
    except json.JSONDecodeError:
        st.error(f"Erro: O arquivo JSON em '{caminho_arquivo_json}' não é válido.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar os dados: {e}")
        return pd.DataFrame()

def plotar_histograma(df, coluna, titulo, xlabel, ylabel="Frequência"):
    """Cria e exibe um histograma no Streamlit."""
    if coluna not in df.columns or df[coluna].empty:
        st.warning(f"Coluna '{coluna}' não encontrada ou vazia para o gráfico '{titulo}'.")
        return

    fig, ax = plt.subplots()
    sns.histplot(df[coluna].dropna(), kde=True, ax=ax)
    ax.set_title(titulo, fontsize=15)
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    plt.tight_layout()
    st.pyplot(fig)
    plt.clf() # Limpa a figura para o próximo gráfico

def plotar_barras(df, coluna, titulo, xlabel, ylabel="Contagem"):
    """Cria e exibe um gráfico de barras no Streamlit."""
    if coluna not in df.columns or df[coluna].empty:
        st.warning(f"Coluna '{coluna}' não encontrada ou vazia para o gráfico '{titulo}'.")
        return

    contagem = df[coluna].value_counts()
    fig, ax = plt.subplots()
    sns.barplot(x=contagem.index, y=contagem.values, ax=ax, palette="viridis")
    ax.set_title(titulo, fontsize=15)
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    st.pyplot(fig)
    plt.clf()

# --- Título Principal do Dashboard ---
st.title("📊 Dashboard Estatístico a partir de JSON")
st.markdown("Visualização de dados estatísticos carregados de um arquivo JSON local.")

# --- Carregamento dos Dados ---
# Substitua pelo caminho correto do seu arquivo JSON
caminho_json = "data/dados_censo.json" 
df_dados = carregar_dados_json(caminho_json)

if df_dados.empty:
    st.warning("Não foi possível carregar os dados. Verifique o arquivo JSON e o caminho.")
    st.stop() # Interrompe a execução se os dados não puderem ser carregados

# --- Exibição de Estatísticas Descritivas ---
st.header("Estatísticas Descritivas Gerais")

# Mostrar um resumo dos dados
if st.checkbox("Mostrar resumo dos dados (DataFrame.describe())"):
    st.dataframe(df_dados.describe(include='all'))

# Indicadores Chave (KPIs)
total_registros = len(df_dados)
media_idade_responsavel = df_dados['idade_responsavel'].mean() if 'idade_responsavel' in df_dados.columns else "N/A"
media_renda_domiciliar = df_dados['renda_domiciliar'].mean() if 'renda_domiciliar' in df_dados.columns else "N/A"

col1, col2, col3 = st.columns(3)
col1.metric("Total de Domicílios", f"{total_registros:,}".replace(",", "."))
if isinstance(media_idade_responsavel, (int, float)):
    col2.metric("Idade Média do Responsável", f"{media_idade_responsavel:.1f} anos")
else:
    col2.metric("Idade Média do Responsável", media_idade_responsavel)

if isinstance(media_renda_domiciliar, (int, float)):
    col3.metric("Renda Média Domiciliar", f"R$ {media_renda_domiciliar:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
else:
    col3.metric("Renda Média Domiciliar", media_renda_domiciliar)


st.markdown("---")

# --- Visualizações Estatísticas ---
st.header("Visualizações dos Dados")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if 'idade_responsavel' in df_dados.columns:
        plotar_histograma(df_dados, 'idade_responsavel', 
                          'Distribuição da Idade dos Responsáveis', 
                          'Idade do Responsável')
    else:
        st.info("Coluna 'idade_responsavel' não encontrada para plotar histograma.")

with col_graf2:
    if 'uf' in df_dados.columns:
        plotar_barras(df_dados, 'uf', 
                      'Distribuição de Domicílios por UF', 
                      'UF')
    else:
        st.info("Coluna 'uf' não encontrada para plotar gráfico de barras.")

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if 'renda_domiciliar' in df_dados.columns:
        plotar_histograma(df_dados, 'renda_domiciliar', 
                          'Distribuição da Renda Domiciliar', 
                          'Renda Domiciliar (R$)')
    else:
        st.info("Coluna 'renda_domiciliar' não encontrada para plotar histograma.")
        
with col_graf4:
    if 'tipo_domicilio' in df_dados.columns:
        plotar_barras(df_dados, 'tipo_domicilio', 
                      'Distribuição por Tipo de Domicílio', 
                      'Tipo de Domicílio')
    else:
        st.info("Coluna 'tipo_domicilio' não encontrada para plotar gráfico de barras.")

# --- Exibir Dados Brutos (Opcional) ---
st.markdown("---")
if st.checkbox("Mostrar dados brutos carregados do JSON"):
    st.subheader("Dados Brutos")
    st.dataframe(df_dados)

st.sidebar.info("Dashboard para visualização de dados de um arquivo JSON.")
