import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import requests

# 1. Conectar à API Django
def fetch_data():
    try:
        response = requests.get('http://localhost:8000/api/domicilios/?format=json')
        domicilios = response.json()
        
        moradores = []
        for dom in domicilios:
            moradores_response = requests.get(f'http://localhost:8000/api/moradores/?domicilio={dom["id"]}')
            moradores.extend(moradores_response.json())
        
        return pd.DataFrame(moradores)
    except Exception as e:
        print(f"Erro ao buscar dados: {e}")
        return pd.DataFrame()

# 2. Inicializar o app Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# 3. Layout do Dashboard
app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("Painel do Censo 2022 - IBGE", className="text-center my-4"))),
    
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='uf-filter',
                options=[{'label': uf, 'value': uf} for uf in ['SP', 'RJ', 'MG', 'RS']],  # Exemplo
                multi=True,
                placeholder="Selecione UF(s)..."
            )
        ], width=6),
        
        dbc.Col([
            dcc.Slider(
                id='age-slider',
                min=0,
                max=100,
                step=5,
                value=30,
                marks={i: str(i) for i in range(0, 101, 10)}
            )
        ], width=6)
    ]),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id='pirâmide-etária'), width=6),
        dbc.Col(dcc.Graph(id='distribuição-uf'), width=6)
    ]),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id='infraestrutura'), width=12)
    ]),
    
    dcc.Interval(id='update-interval', interval=60*1000)  # Atualizar a cada 1 minuto
], fluid=True)

# 4. Callbacks (Interatividade)
@app.callback(
    [Output('pirâmide-etária', 'figure'),
     Output('distribuição-uf', 'figure'),
     Output('infraestrutura', 'figure')],
    [Input('uf-filter', 'value'),
     Input('age-slider', 'value'),
     Input('update-interval', 'n_intervals')]
)
def update_charts(selected_ufs, max_age, _):
    df = fetch_data()
    if df.empty:
        return px.bar(), px.bar(), px.bar()
    
    # Filtros
    if selected_ufs:
        df = df[df['uf'].isin(selected_ufs)]
    df = df[df['idade'] <= max_age]
    
    # Gráfico 1: Pirâmide Etária
    bins = [0, 5, 12, 18, 30, 60, 100]
    labels = ['0-4', '5-11', '12-17', '18-29', '30-59', '60+']
    df['faixa_etaria'] = pd.cut(df['idade'], bins=bins, labels=labels)
    
    pyramid = px.bar(
        df.groupby(['faixa_etaria', 'sexo']).size().unstack(),
        barmode='group',
        title="Pirâmide Etária"
    )
    
    # Gráfico 2: Distribuição por UF
    uf_dist = px.bar(
        df.groupby('uf').size().reset_index(name='count'),
        x='uf',
        y='count',
        title="Moradores por UF"
    )
    
    # Gráfico 3: Infraestrutura (exemplo)
    infra = px.pie(
        df.groupby('abastecimento_agua').size().reset_index(name='count'),
        names='abastecimento_agua',
        values='count',
        title="Tipo de Abastecimento de Água"
    )
    
    return pyramid, uf_dist, infra

# 5. Executar o app
if __name__ == '__main__':
    app.run(debug=True, port=8050)