import streamlit as st
import pandas as pd
from google.oauth2.service_account import Credentials
import unicodedata

# Configuração da página
st.set_page_config(page_title="Dashboard de Inscrições", layout="wide")

# ======= BANNER CENTRALIZADO =======
st.markdown(
    """
    <div style='text-align:center; margin-bottom:20px;'>
        <img src="https://i.postimg.cc/nhM4cdnw/banner6.png" width="55%">
    </div>
    """,
    unsafe_allow_html=True
)

# Título
st.title("📊 Dashboard de Inscrições - Análise de Dados")

# ID da planilha
SHEET_ID = "1-ffVSPaN9z9hp4wGBYfYjntmY9kToQrQwZEOu9nnEcU"

def remover_acentos(texto):
    """Remove acentos de um texto"""
    if pd.isna(texto):
        return texto
    texto = str(texto)
    nfkd = unicodedata.normalize('NFKD', texto)
    return ''.join([c for c in nfkd if not unicodedata.combining(c)]).upper()

@st.cache_data(ttl=300)
def load_data():
    """Carrega dados da Google Sheet"""
    try:
        from urllib.parse import quote

        # URL pública da planilha com encoding correto
        url_dados = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=DADOS"
        url_municipios = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote('MUNICÍPIOS 2025')}"

        # Carrega os dados
        df_dados = pd.read_csv(url_dados)
        df_municipios = pd.read_csv(url_municipios)

        return df_dados, df_municipios
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None, None

# Carrega os dados
with st.spinner("Carregando dados..."):
    df_dados, df_municipios = load_data()

if df_dados is not None and df_municipios is not None:

    # Mantém apenas as colunas principais da aba de municípios
    colunas_desejadas = ['MUNICIPIOS', 'INSCRITOS2025', 'INSCRITOS2024']
    df_municipios = df_municipios[[col for col in colunas_desejadas if col in df_municipios.columns]].copy()

    # Renomeia as colunas
    df_municipios.rename(columns={
        'INSCRITOS2025': 'Inscrito na Adesão 2025',
        'INSCRITOS2024': 'Participou da Adesão 2024'
    }, inplace=True)

    # Corrige possíveis NaN e padroniza maiúsculas
    if 'Inscrito na Adesão 2025' in df_municipios.columns:
        df_municipios['Inscrito na Adesão 2025'] = df_municipios['Inscrito na Adesão 2025'].fillna('NÃO').str.upper()
    if 'Participou da Adesão 2024' in df_municipios.columns:
        df_municipios['Participou da Adesão 2024'] = df_municipios['Participou da Adesão 2024'].fillna('NÃO').str.upper()

    df_municipios_status = df_municipios.copy()
    df_filtrado = df_dados.copy()

    # ======= MÉTRICAS PRINCIPAIS =======
    st.header("📈 Visão Geral")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total de Inscrições", len(df_filtrado))

    with col2:
        inscritos_2025 = (df_municipios_status['Inscrito na Adesão 2025'] == 'SIM').sum() if 'Inscrito na Adesão 2025' in df_municipios_status.columns else 0
        st.metric("Municípios Inscritos 2025", inscritos_2025)

    with col3:
        inscritos_2024 = (df_municipios_status['Participou da Adesão 2024'] == 'SIM').sum() if 'Participou da Adesão 2024' in df_municipios_status.columns else 0
        st.metric("Municípios Inscritos 2024", inscritos_2024)

    with col4:
        if 'Inscrito na Adesão 2025' in df_municipios_status.columns and 'Participou da Adesão 2024' in df_municipios_status.columns:
            reinscritos = ((df_municipios_status['Inscrito na Adesão 2025'] == 'SIM') &
                           (df_municipios_status['Participou da Adesão 2024'] == 'SIM')).sum()
        else:
            reinscritos = 0
        st.metric("Reinscritos (2024→2025)", reinscritos)

    # ======= TABS =======
    tab1, tab2, tab3 = st.tabs(["📍 Por Município", "🎓 Por Curso", "📋 Dados Completos"])

    with tab1:
        st.subheader("Status de Inscrições por Município")

        # ======= GRÁFICOS =======
        col1, col2 = st.columns(2)

        with col1:
            if 'Inscrito na Adesão 2025' in df_municipios_status.columns:
                st.write("**Status Inscrições 2025:**")
                status_2025 = df_municipios_status['Inscrito na Adesão 2025'].value_counts()
                st.bar_chart(status_2025)

        with col2:
            if 'Participou da Adesão 2024' in df_municipios_status.columns:
                st.write("**Status Inscrições 2024:**")
                status_2024 = df_municipios_status['Participou da Adesão 2024'].value_counts()
                st.bar_chart(status_2024)

        # ======= ANÁLISE DE REINSCRIÇÃO =======
        if 'Inscrito na Adesão 2025' in df_municipios_status.columns and 'Participou da Adesão 2024' in df_municipios_status.columns:
            st.write("**Análise de Reinscrição:**")

            col_a, col_b, col_c = st.columns(3)
            with col_a:
                apenas_2024 = ((df_municipios_status['Participou da Adesão 2024'] == 'SIM') &
                               (df_municipios_status['Inscrito na Adesão 2025'] != 'SIM')).sum()
                st.metric("Apenas 2024", apenas_2024)

            with col_b:
                apenas_2025 = ((df_municipios_status['Inscrito na Adesão 2025'] == 'SIM') &
                               (df_municipios_status['Participou da Adesão 2024'] != 'SIM')).sum()
                st.metric("Apenas 2025", apenas_2025)

            with col_c:
                ambos = ((df_municipios_status['Inscrito na Adesão 2025'] == 'SIM') &
                         (df_municipios_status['Participou da Adesão 2024'] == 'SIM')).sum()
                st.metric("Reinscritos", ambos)

        # ======= FILTROS (agora acima da lista de municípios) =======
        st.markdown("---")
        st.subheader("🔍 Filtros de Municípios")

        col_filtro1, col_filtro2 = st.columns(2)
        with col_filtro1:
            status_filtro = st.selectbox(
                "Filtrar por Status:",
                options=['Todos', 'Inscritos 2025', 'Inscritos 2024', 'Reinscritos (ambos)', 'Não Inscritos 2025']
            )
        with col_filtro2:
            buscar_municipio = st.text_input("Buscar município:", "")

        # ======= APLICA FILTROS =======
        df_municipios_exibir = df_municipios_status.copy()

        if status_filtro == 'Inscritos 2025':
            df_municipios_exibir = df_municipios_exibir[df_municipios_exibir['Inscrito na Adesão 2025'] == 'SIM']
        elif status_filtro == 'Inscritos 2024':
            df_municipios_exibir = df_municipios_exibir[df_municipios_exibir['Participou da Adesão 2024'] == 'SIM']
        elif status_filtro == 'Reinscritos (ambos)':
            df_municipios_exibir = df_municipios_exibir[
                (df_municipios_exibir['Inscrito na Adesão 2025'] == 'SIM') &
                (df_municipios_exibir['Participou da Adesão 2024'] == 'SIM')
            ]
        elif status_filtro == 'Não Inscritos 2025':
            df_municipios_exibir = df_municipios_exibir[df_municipios_exibir['Inscrito na Adesão 2025'] != 'SIM']

        if buscar_municipio:
            df_municipios_exibir = df_municipios_exibir[
                df_municipios_exibir['MUNICIPIOS'].str.contains(buscar_municipio, case=False, na=False)
            ]

        # ======= TABELA DE MUNICÍPIOS =======
        st.write(f"**Total de municípios exibidos:** {len(df_municipios_exibir)}")
        st.dataframe(df_municipios_exibir, use_container_width=True, hide_index=True)

        # ======= INSCRIÇÕES POR MUNICÍPIO =======
        if 'MUNICÍPIO' in df_filtrado.columns:
            st.write("**Quantidade de Inscrições por Município (2025):**")
            inscricoes_por_mun = df_filtrado['MUNICÍPIO'].value_counts().head(20)
            st.bar_chart(inscricoes_por_mun, horizontal=True)

    # ======= TAB 2 - CURSOS =======
    with tab2:
        st.subheader("Análise por Curso")
        cursos = []
        for i in range(1, 4):
            col_curso = f'CURSO {i}'
            col_turno = f'TURNO {i}'
            if col_curso in df_filtrado.columns:
                cursos_temp = df_filtrado[[col_curso, col_turno]].dropna()
                if len(cursos_temp) > 0:
                    cursos.append(cursos_temp.rename(columns={col_curso: 'CURSO', col_turno: 'TURNO'}))

        if cursos:
            df_cursos = pd.concat(cursos, ignore_index=True)
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Cursos Mais Procurados:**")
                cursos_count = df_cursos['CURSO'].value_counts().head(15).sort_values(ascending=True)
                st.bar_chart(cursos_count, horizontal=True)

            with col2:
                st.write("**Distribuição por Turno:**")
                turno_count = df_cursos['TURNO'].value_counts().sort_values(ascending=True)
                st.bar_chart(turno_count, horizontal=True)

    # ======= TAB 3 - DADOS COMPLETOS =======
    with tab3:
        st.subheader("Tabela Completa de Dados")
        municipio_filter = []
        status_filter = 'Todos'

        col1, col2 = st.columns(2)
        with col1:
            if 'MUNICÍPIO' in df_filtrado.columns:
                municipio_filter = st.multiselect(
                    "Filtrar por Município:",
                    options=sorted(df_filtrado['MUNICÍPIO'].dropna().unique()),
                    default=[]
                )
        with col2:
            status_filter = st.selectbox(
                "Filtrar por Status:",
                options=['Todos', 'Novos']
            )

        df_exibir = df_filtrado.copy()

        if municipio_filter:
            df_exibir = df_exibir[df_exibir['MUNICÍPIO'].isin(municipio_filter)]

        if 'REINSCRITO' in df_exibir.columns and status_filter != 'Todos':
            if status_filter == 'Reinscritos':
                df_exibir = df_exibir[df_exibir['REINSCRITO'] == True]
            else:
                df_exibir = df_exibir[df_exibir['REINSCRITO'] == False]

        if 'MUNICÍPIO' in df_exibir.columns:
            colunas_ordenadas = ['MUNICÍPIO'] + [col for col in df_exibir.columns if col != 'MUNICÍPIO']
            df_exibir = df_exibir[colunas_ordenadas]

        st.write(f"**Total de registros:** {len(df_exibir)}")
        st.dataframe(df_exibir, use_container_width=True)

        csv = df_exibir.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar dados como CSV",
            data=csv,
            file_name="inscricoes_filtradas.csv",
            mime="text/csv"
        )

else:
    st.error("Não foi possível carregar os dados. Verifique se a planilha está acessível publicamente.")
    st.info("Para tornar a planilha pública: Arquivo → Compartilhar → Qualquer pessoa com o link")

# Rodapé
st.markdown("---")
st.markdown("Dashboard criado com Streamlit | Dados atualizados a cada 5 minutos")
