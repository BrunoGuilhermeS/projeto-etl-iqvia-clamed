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

# Filtro por Região
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

    # 3. Filial Potencial
    coluna_regiao = 'regiao'
    if coluna_regiao in df_filtrado.columns:
        regiao_potencial = df_filtrado.groupby(coluna_regiao)['volume_venda'].sum().idxmax()
    else:
        regiao_potencial = "N/A"

    # --- ESTILIZAÇÃO CSS ---
    cor_barra_verde = "#2D724F"
    cor_texto_branco = "#FFFFFF"

    st.markdown(f"""
    <style>
        /* Estilo para a barra de título customizada */
        .title-bar {{
            background-color: {cor_barra_verde};
            color: {cor_texto_branco};
            padding: 1.5rem;
            margin-top: -3.5rem;
            margin-left: -1rem; 
            margin-right: -1rem;
            border-radius: 0.5rem;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
            text-align: left;
        }}
        
        .title-bar h1 {{
            font-size: 2.2rem;
            margin: 0;
            padding: 0;
            display: inline;
            color: {cor_texto_branco} !important;
        }}
        
        .title-bar span {{
            font-size: 2rem;
            margin-right: 0.7rem;
            vertical-align: middle;
        }}
        
        /* Estilo para as caixinhas de métricas verdes */
        [data-testid="stMetric"] {{
            background-color: #e6fffa;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #b2f5ea;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        }}
    </style>
    
    <div class="title-bar">
        <span>📊</span><h1>Dashboard Executivo Clamed</h1>
    </div>
    <br>
    """, unsafe_allow_html=True)
    
    # --- EXIBIÇÃO DOS KPIs ---
    st.subheader("Indicadores de Desempenho")
    
    c1, c2, c3 = st.columns(3)

    # Usei as variáveis matemáticas para ficar dinâmico de verdade
    with c1:
        st.metric("Market Share (PP)", f"{share_pp:.1f}%")

    with c2:
        st.metric("Gap de Volume Médio", f"{gap_vol:.2f}")

    with c3:
        st.metric("Filial Potencial", regiao_potencial)

    st.divider() # Uma linha sutil para separar as métricas dos gráficos

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
        
        # Aqui o fig_line é criado ANTES de ser chamado
        fig_line = px.line(df_evolucao, x='mes_str', 
                           y=['vendas_pp', 'vendas_concorrência'],
                           labels={'value': 'Volume', 'mes_str': 'Mês', 'variable': 'Grupo'},
                           markers=True,
                           color_discrete_map={'vendas_pp': '#00CC96', 'vendas_concorrência': '#EF553B'})
        
        # Agora o Streamlit sabe quem é o fig_line para desenhar
        st.plotly_chart(fig_line, use_container_width=True)