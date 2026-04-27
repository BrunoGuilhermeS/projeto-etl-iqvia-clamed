import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from src.queries.queries import get_volume_com_dimensoes as fetch_data

st.set_page_config(page_title="Dashboard Executivo Clamed", layout="wide")

def carregar_css():
    css_path = Path(__file__).parent / "assets" / "style.css"
    try:
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Arquivo style.css não encontrado. Verifique a pasta 'assets'.")

carregar_css()

@st.cache_data(ttl=60)
def carregar_dados():
    df = fetch_data()
    
    df['periodo'] = pd.to_datetime(df['periodo'])
    df['mes_str'] = df['periodo'].dt.strftime('%Y-%m')
    
    nome_limpo = df['nome_produto'].fillna("PRODUTO SEM NOME").astype(str)
    ean_limpo = df['ean_produto'].fillna("S/ EAN").astype(str)

    df['produto_label'] = nome_limpo + " (" + ean_limpo + ")"

    df['vendas_pp'] = df.apply(
        lambda x: x['volume_venda'] if str(x['tipo_bandeira']).upper() == 'PP' else 0, 
        axis=1
    )
    df['vendas_concorrência'] = df.apply(
        lambda x: x['volume_venda'] if str(x['tipo_bandeira']).upper() != 'PP' else 0, 
        axis=1
    )
    
    return df

df = carregar_dados()

# --- SIDEBAR ---
st.sidebar.header("⚙️ Filtros do Dashboard")

lista_regiao = sorted(df['regiao'].unique().tolist())
filtro_regiao = st.sidebar.multiselect("Selecione a Região:", lista_regiao, default=lista_regiao)

lista_bandeira = sorted(df['bandeira'].unique().tolist())
filtro_bandeira = st.sidebar.multiselect("Selecione a Bandeira:", lista_bandeira, default=lista_bandeira)

lista_produto = sorted(df['produto_label'].unique().tolist())
filtro_produto = st.sidebar.multiselect("Produto (EAN):", lista_produto)

lista_mes = sorted(df['mes_str'].unique().tolist(), reverse=True)
filtro_mes = st.sidebar.multiselect("Período (Mês):", lista_mes, default=lista_mes[:6])

# --- APLICAÇÃO DOS FILTROS ---
mascara = (
    (df['regiao'].isin(filtro_regiao)) &
    (df['bandeira'].isin(filtro_bandeira)) &
    (df['mes_str'].isin(filtro_mes))
)

if filtro_produto:
    mascara = mascara & (df['produto_label'].isin(filtro_produto))

df_filtrado = df[mascara]

st.markdown("""
<div class="title-bar">
    <h1>Dashboard Executivo Clamed</h1>
</div>
<br>
""", unsafe_allow_html=True)

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
else:
    # --- KPIs ---
    st.subheader("Indicadores de Desempenho")
    c1, c2, c3 = st.columns(3)
    
    vol_total = df_filtrado['volume_venda'].sum()
    vol_pp = df_filtrado['vendas_pp'].sum()
    share_pp = (vol_pp / vol_total * 100) if vol_total > 0 else 0
    
    df_filtrado['tipo_bandeira_clean'] = df_filtrado['tipo_bandeira'].astype(str).str.upper().str.strip()
    
    vol_pp_serie = df_filtrado[df_filtrado['tipo_bandeira_clean'] == 'PP']['volume_venda']
    vol_conv_serie = df_filtrado[df_filtrado['tipo_bandeira_clean'] != 'PP']['volume_venda']
    
    vol_medio_pp = vol_pp_serie.median() if not vol_pp_serie.empty else 0
    vol_medio_conv = vol_conv_serie.median() if not vol_conv_serie.empty else 0
    
    if vol_medio_conv > 0:
        gap_percentual = ((vol_medio_pp - vol_medio_conv) / vol_medio_conv) * 100
        texto_gap = f"{gap_percentual:+.1f}%"
    else:
        texto_gap = "N/A"
    
    regiao_potencial = df_filtrado.groupby('regiao')['volume_venda'].sum().idxmax()

    c1.metric("Market Share (PP)", f"{share_pp:.1f}%")
    c2.metric("Gap de Volume (Relativo)", texto_gap)
    c3.metric("Filial Potencial", regiao_potencial)

    st.divider()

    # --- GRID DE GRÁFICOS ---
    col_v1, col_v2 = st.columns([2, 3])

    with col_v1:
        st.subheader("📍 Performance por Bandeira")
        df_tree = df_filtrado.groupby('bandeira')['volume_venda'].sum().reset_index()
        fig_tree = px.treemap(df_tree, path=['bandeira'], values='volume_venda',
                               color='volume_venda', color_continuous_scale='Greens')
        st.plotly_chart(fig_tree, use_container_width=True)

    with col_v2:
        st.subheader("📈 Evolução: PP vs Mercado")
        df_evolucao = df_filtrado.groupby('mes_str')[['vendas_pp', 'vendas_concorrência']].sum().reset_index().sort_values('mes_str')
        fig_line = px.line(df_evolucao, x='mes_str', y=['vendas_pp', 'vendas_concorrência'],
                           markers=True, color_discrete_map={'vendas_pp': '#2D724F', 'vendas_concorrência': '#EF553B'})
        st.plotly_chart(fig_line, use_container_width=True)

    # --- GRID DE GRÁFICOS ---
    col_v3, col_v4 = st.columns(2)

    with col_v3:
        st.subheader("🗺️ Market Share por Região")
        df_share = df_filtrado.groupby(['regiao', 'tipo_bandeira_clean'])['volume_venda'].sum().reset_index()
        
        fig_share = px.bar(df_share, 
                           y='regiao', 
                           x='volume_venda', 
                           color='tipo_bandeira_clean', 
                           orientation='h', 
                           barmode='relative',
                           color_discrete_map={'PP': '#2D724F', 'CONCORRENTE': '#EF553B'},
                           labels={'volume_venda': 'Market Share (%)', 'regiao': 'Região'})
        
        fig_share.update_layout(barnorm='percent')
        st.plotly_chart(fig_share, use_container_width=True)

with col_v4:
        st.subheader("📦 Volume por Produto (Top 10)")
        
        top_10_nomes = df_filtrado.groupby('produto_label')['volume_venda'].sum().nlargest(10).index
        
        df_top_10 = df_filtrado[df_filtrado['produto_label'].isin(top_10_nomes)]
              
        df_top_grouped = df_top_10.groupby(['produto_label', 'tipo_bandeira_clean'])['volume_venda'].sum().reset_index()
        
        ordem_y = df_top_10.groupby('produto_label')['volume_venda'].sum().sort_values(ascending=True).index
        
        fig_top = px.bar(
            df_top_grouped, 
            x='volume_venda', 
            y='produto_label', 
            color='tipo_bandeira_clean',
            orientation='h',
            category_orders={'produto_label': ordem_y}, 
            color_discrete_map={'PP': '#2D724F', 'CONCORRENTE': '#EF553B'}, 
            labels={'volume_venda': 'Volume', 'produto_label': '', 'tipo_bandeira_clean': 'Tipo'}
        )
        
        st.plotly_chart(fig_top, use_container_width=True)