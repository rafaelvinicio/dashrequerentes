"""Dashboard de matrículas - EJA 2026 (estilo painel Looker/Data Studio).

Rodar:  streamlit run app.py
Fonte:  Google Sheets (precisa estar compartilhada como "qualquer pessoa com o link").
"""
import html

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

SHEET_ID = "1G_b-ZJZiTX-Jb8oJjv_Zd3XtcdcZzJNfIp2ytiBefPM"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
TITULO = "MATRÍCULAS - EJA 2026"

AZUL = "#2196F3"
CORES = ["#E91E8C", "#FFA500", "#F57C00", "#5E35B1", "#2196F3",
         "#00ACC1", "#9C6BB5", "#81D4FA", "#EC407A", "#757575"]

st.set_page_config(page_title=TITULO, layout="wide")

st.markdown(
    f"""
    <style>
      .block-container {{ padding-top: 1.5rem; max-width: 1250px; }}
      h1.titulo {{ text-align:center; font-size:1.7rem; font-weight:700; margin:0 0 1.2rem 0; }}
      .st-key-faixa {{ background:#CCCCCC; padding:1.1rem 1.5rem; border-radius:2px; }}
      .st-key-faixa label p {{ font-weight:700; }}
      .kpi {{ display:flex; align-items:center; justify-content:flex-end; gap:.8rem; height:100%; }}
      .kpi .rot {{ font-weight:800; font-size:1.05rem; color:#111; }}
      .kpi .val {{ font-size:2.2rem; font-weight:300; color:#222; }}
      .tabela-box {{ max-height:430px; overflow:auto; }}
      table.t {{ width:100%; border-collapse:collapse; font-size:.72rem; color:#222; }}
      table.t th {{ background:{AZUL}; color:#fff; text-align:left; padding:.35rem .5rem;
                    position:sticky; top:0; font-weight:700; }}
      table.t td {{ padding:.38rem .5rem; border-bottom:1px solid #e3e3e3; }}
      table.t td.c, table.t th.c {{ text-align:center; }}
      table.t td.n {{ color:#555; width:2rem; }}
      .barra {{ background:#1a73e8; height:9px; border-radius:1px; display:inline-block; }}
      .sub {{ font-size:.8rem; color:#666; margin:.4rem 0 1rem 0; }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------- dados
@st.cache_data(ttl=300, show_spinner="Lendo planilha...")
def carregar():
    bruto = pd.read_csv(SHEET_URL, dtype=str)
    fonte = "Google Sheets (ao vivo)"

    def achar(trecho):
        for c in bruto.columns:
            if trecho.lower() in c.lower():
                return c
        return None

    c_nome = achar("Nome Completo")
    c_curso = achar("Informar o curso")
    c_tipo = achar("Tipo de Matrícula")
    c_cpf = achar("Número do CPF")

    df = pd.DataFrame()
    df["inscrito"] = bruto[c_nome].fillna("").str.strip().str.upper()
    partes = bruto[c_curso].fillna("").str.split("/", expand=True)
    for i in range(4):
        if i not in partes.columns:
            partes[i] = ""
    df["cidade"] = partes[0].str.strip().str.upper()
    df["escola"] = partes[1].str.strip().str.upper()
    df["curso"] = partes[2].str.strip().str.upper()
    df["turno"] = partes[3].str.strip().str.upper()
    df["tipo"] = bruto[c_tipo].fillna("").str.strip().str.upper() if c_tipo else ""
    df["cpf"] = bruto[c_cpf].fillna("").str.replace(r"\D", "", regex=True) if c_cpf else ""
    df = df[df["inscrito"] != ""].reset_index(drop=True)
    return df, fonte


def tabela_html(df, colunas, centradas=(), numerar=True):
    cab = "<th></th>" if numerar else ""
    for nome, _ in colunas:
        cab += f'<th class="{"c" if nome in centradas else ""}">{html.escape(nome)}</th>'
    linhas = ""
    for i, (_, r) in enumerate(df.iterrows(), start=1):
        tds = f'<td class="n">{i}.</td>' if numerar else ""
        for nome, campo in colunas:
            val = r[campo]
            conteudo = val if isinstance(val, str) and val.startswith("<div") else html.escape(str(val))
            tds += f'<td class="{"c" if nome in centradas else ""}">{conteudo}</td>'
        linhas += f"<tr>{tds}</tr>"
    return f'<div class="tabela-box"><table class="t"><thead><tr>{cab}</tr></thead><tbody>{linhas}</tbody></table></div>'


try:
    df, fonte = carregar()
except Exception as e:
    st.error(
        "Não foi possível ler a planilha. Verifique se ela está compartilhada como "
        "'qualquer pessoa com o link pode ver' e se a máquina tem acesso à internet.\n\n"
        f"Detalhe: {e}"
    )
    st.stop()

# ---------------------------------------------------------------- cabeçalho + filtros
st.markdown(f'<h1 class="titulo">{TITULO}</h1>', unsafe_allow_html=True)

with st.container(key="faixa"):
    c0, c1, c2, c3, c4 = st.columns([0.7, 1.5, 1.5, 1.2, 1.6], vertical_alignment="center")
    c0.markdown("**FILTROS**")
    f_cidade = c1.multiselect("Cidade", sorted(df["cidade"].unique()), placeholder="CIDADE", label_visibility="collapsed")
    f_curso = c2.multiselect("Curso", sorted(df["curso"].unique()), placeholder="CURSO", label_visibility="collapsed")
    f_turno = c3.multiselect("Turno", sorted(df["turno"].unique()), placeholder="TURNO", label_visibility="collapsed")
    kpi_slot = c4.empty()

f = df.copy()
if f_cidade:
    f = f[f["cidade"].isin(f_cidade)]
if f_curso:
    f = f[f["curso"].isin(f_curso)]
if f_turno:
    f = f[f["turno"].isin(f_turno)]

kpi_slot.markdown(
    f'<div class="kpi"><span class="rot">TOTAL DE INSCRITOS:</span><span class="val">{len(f):,}</span></div>'.replace(",", "."),
    unsafe_allow_html=True,
)

unicos = f.loc[f["cpf"] != "", "cpf"].nunique()
repetidos = len(f[f["cpf"] != ""]) - unicos
nota = f"{unicos} pessoas únicas (por CPF)"
if repetidos:
    nota += f" · {repetidos} inscrição(ões) repetida(s) em mais de um curso"
st.markdown(f'<div class="sub">{nota} · Fonte: {fonte}</div>', unsafe_allow_html=True)

if f.empty:
    st.info("Nenhum registro para os filtros selecionados.")
    st.stop()

# ---------------------------------------------------------------- corpo
esq, dir_ = st.columns([1, 1], gap="large")

with esq:
    turmas = (
        f.groupby(["cidade", "escola", "curso", "turno"]).size().reset_index(name="inscritos")
        .sort_values(["curso", "cidade", "escola"])
    )
    st.markdown(
        tabela_html(
            turmas,
            [("CIDADE", "cidade"), ("ESCOLA", "escola"), ("TURMA", "curso"), ("TURNO", "turno"), ("INSCRITOS", "inscritos")],
            centradas=("TURNO", "INSCRITOS"),
        ),
        unsafe_allow_html=True,
    )

    st.write("")
    por_curso = f.groupby("curso").size().sort_values(ascending=False)
    top = por_curso.head(9)
    if len(por_curso) > 9:
        top["OUTROS"] = por_curso.iloc[9:].sum()
    fig = go.Figure(
        go.Pie(
            labels=list(top.index), values=list(top.values), hole=0.55,
            marker=dict(colors=CORES[: len(top)]), sort=False,
            textinfo="percent", texttemplate="%{percent:.1%}", textfont=dict(size=11),
            direction="clockwise",
        )
    )
    fig.update_layout(
        height=330, margin=dict(l=0, r=0, t=10, b=10),
        legend=dict(font=dict(size=11), y=0.5), paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, width="stretch")

    maximo = max(por_curso.max(), 1)
    rank = por_curso.reset_index()
    rank.columns = ["curso", "n"]
    rank = rank.sort_values("curso")
    rank["barra"] = rank["n"].apply(
        lambda n: f'<div style="display:flex;align-items:center;gap:.5rem"><span class="barra" style="width:{max(n / maximo * 100, 3):.0f}%"></span><span>{n}</span></div>'
    )
    st.markdown(
        tabela_html(rank, [("CURSO", "curso"), ("INSCRITOS", "barra")]),
        unsafe_allow_html=True,
    )

with dir_:
    lista = f.sort_values(["curso", "inscrito"]).copy()
    lista["qtd"] = 1
    st.markdown(
        tabela_html(
            lista,
            [("INSCRITOS", "inscrito"), ("CURSO", "curso"), ("TURNO", "turno"), ("QTD", "qtd")],
            centradas=("TURNO", "QTD"),
        ).replace("max-height:430px", "max-height:900px"),
        unsafe_allow_html=True,
    )
