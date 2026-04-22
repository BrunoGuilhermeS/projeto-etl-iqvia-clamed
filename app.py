import streamlit as st
import pandas as pd
import plotly.express as px
from src.queries.queries import get_volume_com_dimensoes as fetch_data

# 1. Configurações da Página
st.set_page_config(page_title="Dashboard Executivo Clamed", layout="wide")

@st.cache_data(ttl=60)
def carregar_dados():
    df = fetch_data()
    
    # Garantimos que o período seja datetime e criamos a string de mês
    df['periodo'] = pd.to_datetime(df['periodo'])
    df['mes_str'] = df['periodo'].dt.strftime('%Y-%m')
    
    # Cálculos de colunas de apoio (Vendas PP vs Concorrência)
    df['vendas_pp'] = df.apply(lambda x: x['volume_venda'] if x['tipo_bandeira'] == 'PP' else 0, axis=1)
    df['vendas_concorrência'] = df.apply(lambda x: x['volume_venda'] if x['tipo_bandeira'] != 'PP' else 0, axis=1)
    
    return df

df = carregar_dados()

# --- SIDEBAR: Filtros Dinâmicos ---
st.sidebar.header("⚙️ Filtros do Dashboard")

# Filtro por Região (Atualizado conforme sua nova query)
lista_regiao = sorted(df['regiao'].unique().tolist())
filtro_regiao = st.sidebar.multiselect("Selecione a Região:", lista_regiao, default=lista_regiao)

# Filtro por Bandeira
lista_bandeira = sorted(df['bandeira'].unique().tolist())
filtro_bandeira = st.sidebar.multiselect("Selecione a Bandeira:", lista_bandeira, default=lista_bandeira)

# Filtro por Mês
lista_mes = sorted(df['mes_str'].unique().tolist(), reverse=True)
filtro_mes = st.sidebar.multiselect("Período (Mês):", lista_mes, default=lista_mes[:6])

# Aplicação dos Filtros
df_filtrado = df[
    (df['regiao'].isin(filtro_regiao)) &
    (df['bandeira'].isin(filtro_bandeira)) &
    (df['mes_str'].isin(filtro_mes))
]

# --- PAINEL PRINCIPAL ---
#st.title("📊 Dashboard de Performance Clamed")

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
else:
    # --- CÁLCULOS DOS KPIs ---
    
    # 1. Market Share PP
    vol_total = df_filtrado['volume_venda'].sum()
    vol_pp = df_filtrado['vendas_pp'].sum()
    share_pp = (vol_pp / vol_total * 100) if vol_total > 0 else 0
    
    # 2. Gap de Volume Médio
    vol_medio_pp = df_filtrado[df_filtrado['tipo_bandeira'] == 'PP']['volume_venda'].mean()
    vol_medio_conv = df_filtrado[df_filtrado['tipo_bandeira'] != 'PP']['volume_venda'].mean()
    gap_vol = (vol_medio_pp or 0) - (vol_medio_conv or 0)

    # 3. Filial Potencial (Busca a filial com maior volume dentro do filtro)
    # Nota: Certifique-se de que 'id_filial' ou similar esteja no seu SELECT da query
    coluna_regiao = 'regiao' # Ajuste para o nome exato que colocou no SQL
    if coluna_regiao in df_filtrado.columns:
        regiao_potencial = df_filtrado.groupby(coluna_regiao)['volume_venda'].sum().idxmax()
    else:
        regiao_potencial = "Coluna não encontrada no SQL"

    cor_barra_verde = "#2D724F"
    cor_texto_branco = "#FFFFFF"

    st.markdown(f"""
    <style>
        /* Estilo para a barra de título customizada */
        .title-bar {{
            background-color: {cor_barra_verde};
            color: {cor_texto_branco};
            padding: 1.5rem;
            margin-top: -3.5rem; /* Puxa para cima para ocupar o topo */
            margin-left: -1rem;  /* Estica para o canto esquerdo */
            margin-right: -1rem; /* Estica para o canto direito */
            border-radius: 0.5rem; /* Bordas levemente arredondadas (opcional) */
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2); /* Sombra suave (opcional) */
            text-align: left; /* Alinhamento do texto */
        }}
        
        /* Ajuste do tamanho da fonte e margens do título interno */
        .title-bar h1 {{
            font-size: 2.2rem;
            margin: 0;
            padding: 0;
            display: inline; /* Mantém o ícone e texto na mesma linha */
            color: {cor_texto_branco} !important; /* Força cor branca */
        }}
        
        /* Ajuste do ícone */
        .title-bar span {{
            font-size: 2rem;
            margin-right: 0.7rem;
            vertical-align: middle;
        }}
    </style>
    
    <div class="title-bar">
        <span>📊</span><h1>Dashboard Executivo Clamed</h1>
    </div>
    <br>
    """,
    unsafe_allow_html=True)
    
    st.markdown("""
    <style>
    [data-testid="stMetric"] {
        background-color: #e6fffa; /* Verde bem clarinho */
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #b2f5ea;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- SEU CÓDIGO DE EXIBIÇÃO ---
st.subheader("Indicadores de Desempenho")

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Market Share (PP)", "15.4%")

with c2:
    st.metric("Gap de Volume Médio", "1.25")

with c3:
    st.metric("Filial Potencial", "São Paulo")

    # --- VISÕES GRÁFICAS ---
    col_v1, col_v2 = st.columns([2, 3])

    with col_v1:
        st.subheader("📍 Performance por Bandeira")
        df_tree = df_filtrado.groupby('bandeira')['volume_venda'].sum().reset_index()
        fig_tree = px.treemap(df_tree, path=['bandeira'], values='volume_venda',
                               color='volume_venda', color_continuous_scale='RdBu')
        st.plotly_chart(fig_tree, use_container_width=True)

    with col_v2:
        st.subheader("📈 Evolução Mensal: PP vs Concorrência")
        df_evolucao = df_filtrado.groupby('mes_str')[['vendas_pp', 'vendas_concorrência']].sum().reset_index()
        df_evolucao = df_evolucao.sort_values('mes_str')
        
        fig_line = px.line(df_evolucao, x='mes_str', 
                           y=['vendas_pp', 'vendas_concorrência'],
                           labels={'value': 'Volume', 'mes_str': 'Mês', 'variable': 'Grupo'},
                           markers=True,
                           color_discrete_map={'vendas_pp': '#00CC96', 'vendas_concorrência': '#EF553B'})
        st.plotly_chart(fig_line, use_container_width=True)