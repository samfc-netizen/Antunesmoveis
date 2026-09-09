import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import unicodedata
from pathlib import Path
from io import BytesIO
import base64

st.set_page_config(page_title="Antunes Móveis Planejados | Indicadores", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

LOGO_ANTUNES_BASE64 = "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"

def aplicar_layout_software():
    st.markdown(
        """
        <style>
            :root {
                --app-bg: #F4F6F8;
                --surface: #FFFFFF;
                --surface-soft: #F8FAFC;
                --text: #111827;
                --muted: #667085;
                --line: #E4E7EC;
                --brand: #171717;
                --brand-soft: #2D2D2D;
                --accent: #4B5563;
                --radius: 16px;
            }

            html, body, [class*="css"] {
                font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            }
            .stApp { background: var(--app-bg); }
            .block-container {
                max-width: 1540px;
                padding-top: 1.35rem;
                padding-bottom: 3rem;
            }
            [data-testid="stSidebar"] {
                background: #111214;
                border-right: 1px solid #24262A;
            }
            [data-testid="stSidebar"] * { color: #F8FAFC; }
            [data-testid="stSidebar"] .stCaption,
            [data-testid="stSidebar"] small { color: #A7ADB7 !important; }
            [data-testid="stSidebar"] hr { border-color: #2C2F34; }

            .sidebar-brand {
                display:flex; align-items:center; gap:12px;
                margin: 4px 0 20px 0; padding: 10px 8px 16px 8px;
                border-bottom:1px solid #2A2D31;
            }
            .sidebar-logo {
                width:52px; height:52px; border-radius:50%; object-fit:cover;
                background:#fff; border:2px solid #34373C; padding:2px;
            }
            .sidebar-brand-title { font-size:15px; font-weight:800; line-height:1.2; }
            .sidebar-brand-sub { font-size:11px; color:#A7ADB7; margin-top:4px; }

            .software-header {
                background: var(--surface);
                border:1px solid var(--line);
                border-radius:20px;
                box-shadow: 0 6px 24px rgba(16,24,40,.05);
                padding:18px 22px; margin-bottom:18px;
                display:flex; align-items:center; justify-content:space-between; gap:18px;
            }
            .software-brand { display:flex; align-items:center; gap:14px; min-width:0; }
            .software-logo {
                width:58px; height:58px; border-radius:50%; object-fit:cover;
                background:#fff; border:1px solid var(--line); padding:3px;
                box-shadow: 0 4px 12px rgba(16,24,40,.08); flex:0 0 auto;
            }
            .software-title { font-size:20px; font-weight:800; color:var(--text); letter-spacing:-.02em; }
            .software-subtitle { font-size:13px; color:var(--muted); margin-top:3px; }
            .software-badge {
                display:inline-flex; align-items:center; gap:7px; white-space:nowrap;
                background:#F2F4F7; color:#344054; border:1px solid #EAECF0;
                border-radius:999px; padding:8px 12px; font-size:12px; font-weight:700;
            }
            .software-dot { width:8px; height:8px; border-radius:50%; background:#12B76A; }

            h1, h2, h3 { color:var(--text); letter-spacing:-.025em; }
            h1 { font-size:1.85rem !important; }
            h2 { font-size:1.42rem !important; }
            h3 { font-size:1.12rem !important; }
            [data-testid="stMetric"] {
                background:var(--surface); border:1px solid var(--line); border-radius:var(--radius);
                padding:16px 18px; box-shadow:0 3px 14px rgba(16,24,40,.035); min-height:112px;
            }
            [data-testid="stMetricLabel"] { color:#667085; font-weight:600; }
            [data-testid="stMetricValue"] { color:#101828; font-weight:800; letter-spacing:-.025em; }
            [data-testid="stDataFrame"] {
                background:#fff; border:1px solid var(--line); border-radius:14px; overflow:hidden;
            }
            [data-testid="stPlotlyChart"] {
                background:#fff; border:1px solid var(--line); border-radius:16px;
                padding:8px; box-shadow:0 3px 14px rgba(16,24,40,.03);
            }
            [data-testid="stExpander"] {
                background:#fff; border:1px solid var(--line); border-radius:14px; overflow:hidden;
            }
            .stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] button {
                border-radius:10px !important; font-weight:700 !important;
                min-height:42px; transition:all .15s ease;
            }
            .stButton > button:hover, .stDownloadButton > button:hover, [data-testid="stFormSubmitButton"] button:hover {
                transform:translateY(-1px);
            }
            [data-testid="stSidebar"] [data-testid="stForm"] {
                border:1px solid #2D3035; border-radius:14px; padding:14px 12px; background:#17191C;
            }
            [data-testid="stSidebar"] [data-testid="stFormSubmitButton"] button {
                width:100%; background:#F8FAFC !important; color:#111214 !important; border:none !important;
            }
            /* Controles claros da sidebar: texto escuro para manter contraste */
            [data-testid="stSidebar"] [data-baseweb="select"] > div {
                background:#FFFFFF !important;
                color:#111827 !important;
                border-color:#D0D5DD !important;
            }
            [data-testid="stSidebar"] [data-baseweb="select"] span,
            [data-testid="stSidebar"] [data-baseweb="select"] input,
            [data-testid="stSidebar"] [data-baseweb="select"] svg {
                color:#111827 !important;
                fill:#667085 !important;
                -webkit-text-fill-color:#111827 !important;
            }
            [data-testid="stSidebar"] [data-testid="stFormSubmitButton"] button *,
            [data-testid="stSidebar"] [data-testid="stFormSubmitButton"] button p {
                color:#111214 !important;
                -webkit-text-fill-color:#111214 !important;
            }
            [data-testid="stSidebar"] [role="radiogroup"] label {
                padding:7px 8px; border-radius:8px;
            }
            [data-testid="stSidebar"] [role="radiogroup"] label:hover { background:#202328; }
            .filter-caption { font-size:11px; color:#A7ADB7; line-height:1.4; margin:-4px 0 8px 0; }
            .period-chip {
                display:inline-block; background:#EEF2F6; color:#344054; border:1px solid #E4E7EC;
                border-radius:999px; padding:6px 10px; margin:0 6px 8px 0; font-size:12px; font-weight:700;
            }
            .data-status {
                display:inline-flex; align-items:center; gap:8px; color:#475467; background:#FFFFFF;
                border:1px solid #EAECF0; border-radius:10px; padding:8px 11px; margin:0 0 14px 0; font-size:12px;
            }
            @media (max-width: 800px) {
                .software-header { align-items:flex-start; flex-direction:column; }
                .software-badge { align-self:flex-start; }
                .software-title { font-size:18px; }
            }
        </style>
        """, unsafe_allow_html=True
    )

def renderizar_branding():
    st.sidebar.markdown(
        f"""
        <div class="sidebar-brand">
            <img class="sidebar-logo" src="data:image/png;base64,{LOGO_ANTUNES_BASE64}">
            <div>
                <div class="sidebar-brand-title">Antunes</div>
                <div class="sidebar-brand-sub">Gestão & Indicadores</div>
            </div>
        </div>
        """, unsafe_allow_html=True
    )
    st.markdown(
        f"""
        <div class="software-header">
            <div class="software-brand">
                <img class="software-logo" src="data:image/png;base64,{LOGO_ANTUNES_BASE64}">
                <div>
                    <div class="software-title">Antunes Móveis Planejados</div>
                    <div class="software-subtitle">Central gerencial de resultados, caixa e performance</div>
                </div>
            </div>
            <div class="software-badge"><span class="software-dot"></span> Base conectada</div>
        </div>
        """, unsafe_allow_html=True
    )

aplicar_layout_software()

MESES_ORDEM = {
    "JANEIRO": 1, "FEVEREIRO": 2, "MARÇO": 3, "MARCO": 3, "ABRIL": 4,
    "MAIO": 5, "JUNHO": 6, "JULHO": 7, "AGOSTO": 8,
    "SETEMBRO": 9, "OUTUBRO": 10, "NOVEMBRO": 11, "DEZEMBRO": 12,
}
MESES_ABREV = {1:"JAN",2:"FEV",3:"MAR",4:"ABR",5:"MAI",6:"JUN",7:"JUL",8:"AGO",9:"SET",10:"OUT",11:"NOV",12:"DEZ"}


def normalizar_texto(txt):
    if pd.isna(txt):
        return ""
    txt = str(txt).strip()
    txt = unicodedata.normalize("NFKD", txt).encode("ASCII", "ignore").decode("ASCII")
    return " ".join(txt.upper().split())


def consolidar_descricao_parcelada(descricao):
    """Remove apenas o indicador de parcela final, como (1/5), (2/5) etc.

    Assim, lançamentos da mesma origem ficam consolidados em uma única linha,
    sem alterar descrições que não tenham esse padrão no final.
    """
    if pd.isna(descricao):
        return ""
    import re
    texto = str(descricao).strip()
    texto = re.sub(r"\s*\(\s*\d+\s*/\s*\d+\s*\)\s*$", "", texto)
    return " ".join(texto.split()).strip()


def moeda(v):
    try:
        v = float(v)
        return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return v


def perc(v):
    try:
        return f"{float(v):.2f}%".replace(".", ",")
    except Exception:
        return v


def numero(v):
    try:
        return f"{float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return v


def converter_numero_br(serie):
    if pd.api.types.is_numeric_dtype(serie):
        return pd.to_numeric(serie, errors="coerce").fillna(0)
    return (
        serie.astype(str)
        .str.replace("R$", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.strip()
        .replace(["", "nan", "None"], np.nan)
        .pipe(pd.to_numeric, errors="coerce")
        .fillna(0)
    )


def achar_coluna(df, candidatos):
    mapa = {normalizar_texto(c): c for c in df.columns}
    candidatos_norm = [normalizar_texto(c) for c in candidatos]
    for cand in candidatos_norm:
        if cand in mapa:
            return mapa[cand]
    for cand in candidatos_norm:
        for col_norm, col_original in mapa.items():
            if cand in col_norm or col_norm in cand:
                return col_original
    return None


def preparar_base(base_raw):
    base = base_raw.copy().dropna(how="all").dropna(axis=1, how="all")
    if base.shape[1] < 2:
        return pd.DataFrame(columns=["PLANO", "CONTA_RESULTADO", "PLANO_NORM"])
    base = base.iloc[:, :2].copy()
    base.columns = ["PLANO", "CONTA_RESULTADO"]
    base = base.dropna(subset=["PLANO"])
    base["PLANO"] = base["PLANO"].astype(str).str.strip()
    base["CONTA_RESULTADO"] = base["CONTA_RESULTADO"].astype(str).str.strip()
    base["PLANO_NORM"] = base["PLANO"].apply(normalizar_texto)
    return base


def mes_ano_label(mes, ano):
    mes_num = MESES_ORDEM.get(normalizar_texto(mes))
    if mes_num is None:
        return f"{str(mes).strip()} / {ano}"
    return f"{MESES_ABREV[mes_num]}/{str(int(ano))[-2:]}"


def ordenar_periodos(labels):
    inv = {v: k for k, v in MESES_ABREV.items()}
    def chave(label):
        try:
            mes_abrev, ano2 = str(label).split("/")
            return (2000 + int(ano2), inv.get(mes_abrev, 99))
        except Exception:
            return (9999, 99)
    return sorted(labels, key=chave)


def tabela_mes_percentual(linhas, periodos):
    cols = ["CONTA"]
    for p in periodos:
        cols.extend([p, f"{p}%"])
    return pd.DataFrame(linhas, columns=cols)


def formatar_tabela_valor_percentual(df):
    out = df.copy()
    for c in out.columns:
        if c == "CONTA":
            continue
        if str(c).endswith("%"):
            out[c] = out[c].apply(perc)
        else:
            out[c] = out[c].apply(moeda)
    return out


def estilizar_tabela_principal(df, linhas_azuis=None, linhas_resultado=None):
    linhas_azuis = [x.upper() for x in (linhas_azuis or [])]
    linhas_resultado = [x.upper() for x in (linhas_resultado or [])]
    def estilo_linha(row):
        conta = str(row.iloc[0]).upper()
        estilos = []
        for col, val in row.items():
            estilo = ""
            if conta in linhas_azuis:
                estilo += "color:#0B5ED7;font-weight:700;"
            if conta in linhas_resultado:
                if col == row.index[0]:
                    estilo += "font-weight:700;"
                else:
                    bruto = str(val).replace("R$", "").replace(".", "").replace(",", ".").replace("%", "").strip()
                    try:
                        num = float(bruto)
                        estilo += "color:#198754;font-weight:700;" if num >= 0 else "color:#DC3545;font-weight:700;"
                    except Exception:
                        estilo += "font-weight:700;"
            if "%" in str(col):
                estilo += "background-color:#F7F7F7;"
            estilos.append(estilo)
        return estilos
    return df.style.apply(estilo_linha, axis=1)


def base_referencia_total(tipo, receita_cmv, recebimentos):
    if tipo == "DRE":
        return receita_cmv["RECEITA"].sum()
    return recebimentos["RECEBIMENTO"].sum()


def treemap_despesas(df, contas_validas, titulo, base_total, label_base):
    dados = df[df["CONTA_RESULTADO_NORM"].isin([normalizar_texto(x) for x in contas_validas])].copy()
    if dados.empty:
        st.info("Sem dados para gerar o treemap.")
        return

    agrup = dados.groupby(["CONTA_RESULTADO", "Plano de contas"], as_index=False)["Valor total"].sum()
    agrup["% sobre base"] = np.where(base_total != 0, agrup["Valor total"] / base_total * 100, 0)
    agrup["Label"] = agrup["% sobre base"].apply(lambda x: f"{x:.2f}%".replace(".", ","))

    fig = px.treemap(
        agrup,
        path=["CONTA_RESULTADO", "Plano de contas"],
        values="Valor total",
        custom_data=["% sobre base", "Valor total"],
        title=titulo,
    )
    fig.update_traces(
        texttemplate="%{label}<br>%{customdata[0]:.2f}%",
        hovertemplate="<b>%{label}</b><br>Valor: R$ %{customdata[1]:,.2f}<br>% sobre " + label_base + ": %{customdata[0]:.2f}%<extra></extra>",
    )
    fig.update_layout(margin=dict(t=50, l=10, r=10, b=10))
    st.plotly_chart(fig, use_container_width=True)


def mostrar_kpi_conta(df, conta_resultado, base_total, label_base):
    dados = df[df["CONTA_RESULTADO_NORM"] == normalizar_texto(conta_resultado)].copy()
    total = dados["Valor total"].sum()
    qtd = len(dados)
    representatividade = total / base_total * 100 if base_total else 0
    c1, c2, c3 = st.columns(3)
    c1.metric("Valor da conta selecionada", moeda(total))
    c2.metric(f"% sobre {label_base}", perc(representatividade))
    c3.metric("Qtd. de lançamentos", f"{qtd:,}".replace(",", "."))


def montar_pivot(df, index_cols, periodos):
    if df.empty:
        return pd.DataFrame()
    pivot = pd.pivot_table(df, values="Valor total", index=index_cols, columns="PERIODO", aggfunc="sum", fill_value=0)
    for p in periodos:
        if p not in pivot.columns:
            pivot[p] = 0
    pivot = pivot[periodos].reset_index()
    pivot["TOTAL"] = pivot[periodos].sum(axis=1)
    pivot = pivot.sort_values("TOTAL", ascending=False)
    return pivot


def formatar_pivot_valores(pivot, periodos):
    out = pivot.copy()
    for c in periodos + ["TOTAL"]:
        if c in out.columns:
            out[c] = out[c].apply(moeda)
    return out


def adicionar_painel_variacao(pivot, periodos):
    """Adiciona alertas por linha quando algum mês supera a média dos meses com movimento."""
    if pivot.empty:
        return pivot.copy()

    out = pivot.copy()
    status_lista = []
    desvio_lista = []
    meses_alerta_lista = []

    for _, linha in out.iterrows():
        valores = pd.to_numeric(linha[periodos], errors="coerce").fillna(0)
        valores_com_movimento = valores[valores != 0]

        if valores_com_movimento.empty:
            status_lista.append("🟢 Normal")
            desvio_lista.append(0.0)
            meses_alerta_lista.append("")
            continue

        media = valores_com_movimento.mean()
        if media == 0:
            status_lista.append("🟢 Normal")
            desvio_lista.append(0.0)
            meses_alerta_lista.append("")
            continue

        variacoes = ((valores - media) / abs(media)) * 100
        meses_acima_20 = [p for p in periodos if valores[p] != 0 and variacoes[p] > 20]
        maior_desvio = max([variacoes[p] for p in periodos if valores[p] != 0], default=0.0)

        if maior_desvio > 35:
            status = "🚨 Verificar"
        elif maior_desvio > 20:
            status = "🟡 Oscilação"
        else:
            status = "🟢 Normal"

        status_lista.append(status)
        desvio_lista.append(float(max(maior_desvio, 0)))
        meses_alerta_lista.append(", ".join(meses_acima_20))

    out.insert(0, "Status", status_lista)
    out["Maior aumento vs. média"] = desvio_lista
    out["Meses acima de 20%"] = meses_alerta_lista
    return out


def formatar_painel_variacao(pivot, periodos):
    out = pivot.copy()
    for c in periodos + ["TOTAL"]:
        if c in out.columns:
            out[c] = out[c].apply(moeda)
    if "Maior aumento vs. média" in out.columns:
        out["Maior aumento vs. média"] = out["Maior aumento vs. média"].apply(perc)
    return out


def mostrar_drill_conta(df, conta_resultado, periodos, chave_unica=""):
    dados = df[df["CONTA_RESULTADO_NORM"] == normalizar_texto(conta_resultado)].copy()
    if dados.empty:
        st.info("Não há lançamentos para esta conta de resultado.")
        return

    st.markdown("**Consolidado por Plano de Contas**")
    consolidado = montar_pivot(dados, ["Plano de contas"], periodos)
    painel_consolidado = adicionar_painel_variacao(consolidado, periodos)
    st.caption("🟢 Normal: até 20% | 🟡 Oscilação: acima de 20% até 35% | 🚨 Verificar: acima de 35% da média dos meses com movimento")
    st.dataframe(formatar_painel_variacao(painel_consolidado, periodos), use_container_width=True, hide_index=True)

    st.markdown("**Detalhamento por descrição dentro do Plano de Contas**")
    planos = consolidado["Plano de contas"].tolist() if not consolidado.empty else sorted(dados["Plano de contas"].dropna().unique())
    plano_sel = st.selectbox("Selecione o Plano de Contas para detalhar", planos, key=f"plano_{chave_unica}_{normalizar_texto(conta_resultado)}")
    dados_plano = dados[dados["Plano de contas"] == plano_sel].copy()
    dados_plano["Descrição consolidada"] = dados_plano["Descrição"].apply(consolidar_descricao_parcelada)
    detalhado = montar_pivot(dados_plano, ["Plano de contas", "Descrição consolidada"], periodos)
    detalhado = detalhado.rename(columns={"Descrição consolidada": "Descrição"})
    st.dataframe(formatar_pivot_valores(detalhado, periodos), use_container_width=True, hide_index=True)


def mostrar_drill_atrasados(atrasadas):
    st.subheader("Drill de Títulos Atrasados")
    if atrasadas.empty:
        st.info("Não há títulos em aberto no período selecionado.")
        return

    agrup = atrasadas.groupby(["CONTA_RESULTADO", "Plano de contas"], dropna=False, as_index=False).agg(
        QTD=("Valor total", "count"), VALOR=("Valor total", "sum")
    ).sort_values("VALOR", ascending=False)
    agrup_fmt = agrup.copy()
    agrup_fmt["CONTA_RESULTADO"] = agrup_fmt["CONTA_RESULTADO"].replace("", "Sem classificação")
    agrup_fmt["VALOR"] = agrup_fmt["VALOR"].apply(moeda)
    st.markdown("**Resumo por Conta de Resultado e Plano de Contas**")
    st.dataframe(agrup_fmt, use_container_width=True, hide_index=True)

    colunas_base = ["Data de vencimento", "Data de confirmação", "PERIODO", "CONTA_RESULTADO", "Plano de contas", "Descrição", "Valor total", "Situação"]
    colunas_existentes = [c for c in colunas_base if c in atrasadas.columns]
    detalhe = atrasadas[colunas_existentes].copy()
    for col_data in ["Data de vencimento", "Data de confirmação"]:
        if col_data in detalhe.columns:
            detalhe[col_data] = pd.to_datetime(detalhe[col_data], errors="coerce").dt.strftime("%d/%m/%Y")
    if "CONTA_RESULTADO" in detalhe.columns:
        detalhe["CONTA_RESULTADO"] = detalhe["CONTA_RESULTADO"].replace("", "Sem classificação")
    if "Valor total" in detalhe.columns:
        detalhe["Valor total"] = detalhe["Valor total"].apply(moeda)
    st.markdown("**Detalhamento dos títulos em aberto**")
    st.dataframe(detalhe, use_container_width=True, hide_index=True)


def mostrar_planos_sem_classificacao(sem_classificacao_df):
    st.subheader("Planos de Contas sem Classificação")
    if sem_classificacao_df.empty:
        st.success("Não há planos de contas sem classificação no período selecionado.")
        return

    st.warning("Existem planos de contas sem Conta de Resultado na aba BASE. Classifique esses planos para que entrem corretamente no DRE, DFC e Ponto de Equilíbrio.")
    resumo = sem_classificacao_df.groupby("Plano de contas", as_index=False).agg(
        QTD=("Valor total", "count"),
        VALOR=("Valor total", "sum"),
    ).sort_values("VALOR", ascending=False)
    resumo_fmt = resumo.copy()
    resumo_fmt["VALOR"] = resumo_fmt["VALOR"].apply(moeda)
    st.markdown("**Resumo dos planos sem classificação**")
    st.dataframe(resumo_fmt, use_container_width=True, hide_index=True)

    colunas = ["Data de vencimento", "Data de confirmação", "PERIODO", "Plano de contas", "Descrição", "Valor total", "Situação"]
    colunas = [c for c in colunas if c in sem_classificacao_df.columns]
    detalhe = sem_classificacao_df[colunas].copy()
    for col_data in ["Data de vencimento", "Data de confirmação"]:
        if col_data in detalhe.columns:
            detalhe[col_data] = pd.to_datetime(detalhe[col_data], errors="coerce").dt.strftime("%d/%m/%Y")
    if "Valor total" in detalhe.columns:
        detalhe["Valor total"] = detalhe["Valor total"].apply(moeda)
    st.markdown("**Lançamentos vinculados a planos sem classificação**")
    st.dataframe(detalhe, use_container_width=True, hide_index=True)

def mostrar_drill_ajustes_aplicacoes(confirmadas, periodos):
    st.subheader("Drill de Ajustes e Aplicações")
    dados = confirmadas[confirmadas["CONTA_RESULTADO_NORM"].isin([normalizar_texto("AJUSTE"), normalizar_texto("APLICAÇÃO")])].copy()
    if dados.empty:
        st.info("Não há lançamentos classificados como Ajuste ou Aplicação.")
        return

    resumo = dados.groupby("CONTA_RESULTADO", as_index=False).agg(QTD=("Valor total", "count"), VALOR=("Valor total", "sum"))
    resumo_fmt = resumo.copy()
    resumo_fmt["VALOR"] = resumo_fmt["VALOR"].apply(moeda)
    st.markdown("**Resumo agrupado**")
    st.dataframe(resumo_fmt, use_container_width=True, hide_index=True)

    conta_opcoes = resumo["CONTA_RESULTADO"].tolist()
    conta_sel = st.selectbox("Selecione para detalhar Ajuste/Aplicação", conta_opcoes, key="ajustes_aplicacoes_sel")
    mostrar_drill_conta(dados, conta_sel, periodos, chave_unica="ajustes")

    with st.expander("Ver lançamentos analíticos de Ajustes e Aplicações"):
        det = dados[["Data de confirmação", "PERIODO", "CONTA_RESULTADO", "Plano de contas", "Descrição", "Valor total"]].copy()
        det["Data de confirmação"] = det["Data de confirmação"].dt.strftime("%d/%m/%Y")
        det["Valor total"] = det["Valor total"].apply(moeda)
        st.dataframe(det, use_container_width=True, hide_index=True)




@st.cache_data(show_spinner=False)
def gerar_pdf_dashboard(titulo, subtitulo, kpis, tabela_df):
    """Gera um PDF simples com KPIs e a tabela principal do dashboard."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import cm
    except Exception as e:
        st.error("Para exportar PDF, inclua reportlab no requirements.txt e faça o redeploy do app.")
        return None

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=0.7*cm,
        leftMargin=0.7*cm,
        topMargin=0.7*cm,
        bottomMargin=0.7*cm,
    )
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph(f"<b>{titulo}</b>", styles["Title"]))
    story.append(Paragraph(subtitulo, styles["Normal"]))
    story.append(Spacer(1, 0.25*cm))

    if kpis:
        kpi_data = [[str(k), str(v)] for k, v in kpis.items()]
        kpi_table = Table(kpi_data, colWidths=[6*cm, 5*cm])
        kpi_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EAF2FF")),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(kpi_table)
        story.append(Spacer(1, 0.35*cm))

    tabela_pdf = tabela_df.copy().astype(str)
    max_cols = 10
    if len(tabela_pdf.columns) > max_cols:
        tabela_pdf = tabela_pdf.iloc[:, :max_cols]
        story.append(Paragraph("Tabela reduzida no PDF para manter legibilidade. Use o dashboard para ver todos os meses.", styles["Italic"]))
        story.append(Spacer(1, 0.15*cm))

    data = [list(tabela_pdf.columns)] + tabela_pdf.values.tolist()
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B5ED7")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(table)
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def botao_pdf_dashboard(nome_arquivo, titulo, subtitulo, kpis, tabela_df, key):
    pdf_bytes = gerar_pdf_dashboard(titulo, subtitulo, kpis, tabela_df)
    if pdf_bytes:
        st.download_button(
            label="Exportar PDF do Dashboard",
            data=pdf_bytes,
            file_name=nome_arquivo,
            mime="application/pdf",
            key=key,
            use_container_width=False,
        )

# ============================================================
# INTERFACE / CAPA / LEITURA
# ============================================================

def mostrar_capa():
    st.markdown(
        """
        <style>
            .block-container {padding-top: 2rem;}
            .capa-container {
                background: linear-gradient(135deg, #0F172A 0%, #1E293B 48%, #334155 100%);
                border-radius: 28px;
                padding: 54px 48px;
                color: white;
                box-shadow: 0 18px 45px rgba(15, 23, 42, 0.22);
                margin-bottom: 26px;
            }
            .capa-tag {
                display: inline-block;
                background: rgba(255,255,255,0.12);
                border: 1px solid rgba(255,255,255,0.22);
                border-radius: 999px;
                padding: 8px 14px;
                font-size: 13px;
                letter-spacing: .08em;
                text-transform: uppercase;
                margin-bottom: 18px;
            }
            .capa-titulo {
                font-size: 44px;
                line-height: 1.05;
                font-weight: 800;
                margin: 0 0 18px 0;
            }
            .capa-texto {
                font-size: 18px;
                line-height: 1.55;
                max-width: 820px;
                color: #E2E8F0;
                margin-bottom: 28px;
            }
            .capa-card {
                background: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 18px;
                padding: 22px;
                box-shadow: 0 8px 28px rgba(15, 23, 42, 0.08);
                height: 100%;
            }
            .capa-card h3 {margin-top: 0; color:#0F172A;}
            .capa-card p {color:#475569;}
            div.stButton > button {
                background: #0F172A;
                color: white;
                border-radius: 12px;
                padding: 0.85rem 1.4rem;
                border: none;
                font-weight: 700;
            }
            div.stButton > button:hover {
                background: #334155;
                color: white;
                border: none;
            }
        </style>

        <div class="capa-container">
            <div class="capa-tag">Dashboard Gerencial</div>
            <div class="capa-titulo">ANTUNES MÓVEIS PLANEJADOS<br>INDICADORES DE RESULTADO</div>
            <div class="capa-texto">
                Painel para acompanhamento financeiro, leitura de DRE, DFC, projetos, ponto de equilíbrio,
                títulos em aberto e planos de contas pendentes de classificação.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="capa-card"><h3>DRE Gerencial</h3><p>Receita, CMV, margem bruta, despesas e resultado econômico.</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="capa-card"><h3>DFC e Caixa</h3><p>Recebimentos, saídas, fornecedores, resultado de caixa e títulos em aberto.</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="capa-card"><h3>Gestão de Base</h3><p>Identificação dos planos de contas sem classificação para correção da aba BASE.</p></div>', unsafe_allow_html=True)

    st.write("")
    if st.button("Iniciar análise", use_container_width=True):
        st.session_state["app_iniciado"] = True
        st.rerun()


if not st.session_state.get("app_iniciado", False):
    mostrar_capa()
    st.stop()

renderizar_branding()

# ============================================================
# LEITURA AUTOMÁTICA DA PLANILHA
# Para Streamlit Cloud, coloque a planilha no mesmo repositório
# com este nome exato ou ajuste a variável NOME_PLANILHA abaixo.
# ============================================================

NOME_PLANILHA = "CONTAS A PAGAR SAMUEL ANTUNES.xlsx"
PLANILHAS_POSSIVEIS = [
    NOME_PLANILHA,
    "CONTAS A PAGAR SAMUEL ANTUNES(2).xlsx",
    "CONTAS A PAGAR SAMUEL ANTUNES (2).xlsx",
    "CONTAS A PAGAR SAMUEL ANTUNES(3).xlsx",
    "CONTAS A PAGAR SAMUEL ANTUNES (3).xlsx",
]
CAMINHO_PLANILHA = None
for nome_arquivo in PLANILHAS_POSSIVEIS:
    caminho_teste = Path(__file__).parent / nome_arquivo
    if caminho_teste.exists():
        CAMINHO_PLANILHA = caminho_teste
        NOME_PLANILHA = nome_arquivo
        break

if CAMINHO_PLANILHA is None:
    st.error(
        "Planilha não encontrada. Coloque o arquivo Excel na mesma pasta/repositório deste app.py "
        "com o nome CONTAS A PAGAR SAMUEL ANTUNES.xlsx."
    )
    st.stop()

st.markdown(f'<div class="data-status">● Base carregada automaticamente &nbsp;•&nbsp; {NOME_PLANILHA}</div>', unsafe_allow_html=True)

# Cache da leitura do Excel: trocar filtros não deve reler o arquivo inteiro.
# O mtime entra na chave para o cache ser invalidado automaticamente quando a planilha for atualizada.
@st.cache_data(show_spinner=False)
def carregar_planilha_cache(caminho_str, modificado_em):
    with pd.ExcelFile(caminho_str) as xls:
        contas_df = pd.read_excel(xls, "relatorio_contas_pagar")
        base_df = pd.read_excel(xls, "BASE", header=None)
        receita_cmv_df = pd.read_excel(xls, "RECEITA E CMV")
        recebimentos_df = pd.read_excel(xls, "RECEBIMENTO")
        projetos_df = pd.read_excel(xls, "PROJETOS")
    return contas_df, base_df, receita_cmv_df, recebimentos_df, projetos_df

_mtime_planilha = CAMINHO_PLANILHA.stat().st_mtime
contas, base_raw, receita_cmv, recebimentos, projetos = carregar_planilha_cache(
    str(CAMINHO_PLANILHA), _mtime_planilha
)

contas.columns = [str(c).strip() for c in contas.columns]
receita_cmv.columns = [str(c).strip() for c in receita_cmv.columns]
recebimentos.columns = [str(c).strip() for c in recebimentos.columns]
projetos.columns = [str(c).strip() for c in projetos.columns]
base = preparar_base(base_raw)

# Contas a pagar
col_plano = achar_coluna(contas, ["Plano de contas"])
col_data_conf = achar_coluna(contas, ["Data de confirmação"])
col_data_venc = achar_coluna(contas, ["Data de vencimento"])
col_situacao = achar_coluna(contas, ["Situação", "Situacao"])
col_valor_total = achar_coluna(contas, ["Valor total"])
col_descricao = achar_coluna(contas, ["Descrição", "Descricao"])
if not all([col_plano, col_data_conf, col_situacao, col_valor_total, col_descricao]):
    st.error("Não consegui localizar todas as colunas necessárias na aba relatorio_contas_pagar.")
    st.write("Colunas encontradas:", list(contas.columns))
    st.stop()

contas["Plano de contas"] = contas[col_plano].astype(str).str.strip()
contas["Descrição"] = contas[col_descricao].astype(str).str.strip()
contas["Descrição consolidada"] = contas["Descrição"].apply(consolidar_descricao_parcelada)
contas["Situação"] = contas[col_situacao].astype(str).str.strip()
contas["Valor total"] = converter_numero_br(contas[col_valor_total])
contas["Data de confirmação"] = pd.to_datetime(contas[col_data_conf], dayfirst=True, errors="coerce")
if col_data_venc:
    contas["Data de vencimento"] = pd.to_datetime(contas[col_data_venc], dayfirst=True, errors="coerce")
else:
    contas["Data de vencimento"] = pd.NaT
def periodo_por_data(data):
    if pd.isna(data):
        return ""
    try:
        return f"{MESES_ABREV.get(int(data.month), '')}/{str(int(data.year))[-2:]}"
    except Exception:
        return ""

# Período financeiro padrão: confirmados seguem pela Data de confirmação.
contas["ANO"] = contas["Data de confirmação"].dt.year
contas["MES_NUM"] = contas["Data de confirmação"].dt.month
contas["PERIODO_CONFIRMACAO"] = contas["Data de confirmação"].apply(periodo_por_data)

# Período de vencimento: usado para títulos em aberto/atrasados.
contas["PERIODO_VENCIMENTO"] = contas["Data de vencimento"].apply(periodo_por_data)

# PERIODO geral começa pela confirmação; nos títulos em aberto será trocado para vencimento abaixo.
contas["PERIODO"] = contas["PERIODO_CONFIRMACAO"]
contas["PLANO_NORM"] = contas["Plano de contas"].apply(normalizar_texto)
contas = contas.merge(base[["PLANO_NORM", "CONTA_RESULTADO"]], on="PLANO_NORM", how="left")
contas["CONTA_RESULTADO"] = contas["CONTA_RESULTADO"].fillna("").astype(str).str.strip()
contas["CONTA_RESULTADO_NORM"] = contas["CONTA_RESULTADO"].apply(normalizar_texto)

# ============================================================
# LANÇAMENTOS MANUAIS FIXOS NO CÓDIGO
# Solicitação: adicionar fornecedor Leo Madeiras em OUT/25 e NOV/25,
# plano de contas Matéria prima, conta de resultado FORNECEDORES.
# Esses lançamentos entram como CONFIRMADO e compõem DFC/Ponto de Equilíbrio.
# ============================================================

lancamentos_manuais = pd.DataFrame([
    {
        "Plano de contas": "Matéria prima",
        "Descrição": "Leo Madeiras",
        "Situação": "Confirmado",
        "Valor total": 37247.26,
        "Data de confirmação": pd.Timestamp(2025, 10, 31),
        "Data de vencimento": pd.Timestamp(2025, 10, 31),
        "ANO": 2025,
        "MES_NUM": 10,
        "PERIODO": "OUT/25",
        "PLANO_NORM": normalizar_texto("Matéria prima"),
        "CONTA_RESULTADO": "FORNECEDORES",
        "CONTA_RESULTADO_NORM": normalizar_texto("FORNECEDORES"),
    },
    {
        "Plano de contas": "Matéria prima",
        "Descrição": "Leo Madeiras",
        "Situação": "Confirmado",
        "Valor total": 15609.85,
        "Data de confirmação": pd.Timestamp(2025, 11, 30),
        "Data de vencimento": pd.Timestamp(2025, 11, 30),
        "ANO": 2025,
        "MES_NUM": 11,
        "PERIODO": "NOV/25",
        "PLANO_NORM": normalizar_texto("Matéria prima"),
        "CONTA_RESULTADO": "FORNECEDORES",
        "CONTA_RESULTADO_NORM": normalizar_texto("FORNECEDORES"),
    },
])

contas = pd.concat([contas, lancamentos_manuais], ignore_index=True)
contas["Descrição consolidada"] = contas["Descrição"].apply(consolidar_descricao_parcelada)

confirmadas = contas[contas["Situação"].apply(normalizar_texto).eq("CONFIRMADO")].copy()

# Regra operacional: na base da Antunes, todo título com Situação = EM ABERTO deve entrar
# no drill de títulos em aberto/atrasados, usando a Data de vencimento como referência do período.
atrasadas = contas[contas["Situação"].apply(normalizar_texto).eq("EM ABERTO")].copy()
if not atrasadas.empty:
    atrasadas["ANO"] = atrasadas["Data de vencimento"].dt.year
    atrasadas["MES_NUM"] = atrasadas["Data de vencimento"].dt.month
    atrasadas["PERIODO"] = atrasadas["PERIODO_VENCIMENTO"]
    # Se por algum motivo não houver vencimento, usa a confirmação apenas como contingência.
    atrasadas.loc[atrasadas["PERIODO"].eq(""), "PERIODO"] = atrasadas.loc[atrasadas["PERIODO"].eq(""), "PERIODO_CONFIRMACAO"]

# Mostra todos os planos sem Conta de Resultado, inclusive títulos em aberto, para facilitar correção da aba BASE.
sem_classificacao = contas[contas["CONTA_RESULTADO"].eq("")].copy()
if not sem_classificacao.empty:
    mask_aberto_sem_class = sem_classificacao["Situação"].apply(normalizar_texto).eq("EM ABERTO")
    sem_classificacao.loc[mask_aberto_sem_class, "PERIODO"] = sem_classificacao.loc[mask_aberto_sem_class, "PERIODO_VENCIMENTO"]
    sem_classificacao.loc[sem_classificacao["PERIODO"].eq(""), "PERIODO"] = sem_classificacao.loc[sem_classificacao["PERIODO"].eq(""), "PERIODO_CONFIRMACAO"]

# Receita / CMV
col_mes_rc = achar_coluna(receita_cmv, ["MÊS", "MES"])
col_ano_rc = achar_coluna(receita_cmv, ["ANO"])
col_receita = achar_coluna(receita_cmv, ["RECEITA"])
col_cmv = achar_coluna(receita_cmv, ["CMV"])
if not all([col_mes_rc, col_ano_rc, col_receita, col_cmv]):
    st.error("Não consegui localizar MÊS, ANO, RECEITA e CMV na aba RECEITA E CMV.")
    st.write(list(receita_cmv.columns))
    st.stop()
receita_cmv["PERIODO"] = receita_cmv.apply(lambda r: mes_ano_label(r[col_mes_rc], r[col_ano_rc]), axis=1)
receita_cmv["RECEITA"] = converter_numero_br(receita_cmv[col_receita])
receita_cmv["CMV"] = converter_numero_br(receita_cmv[col_cmv])

# Recebimento
col_mes_rec = achar_coluna(recebimentos, ["MÊS", "MES"])
col_ano_rec = achar_coluna(recebimentos, ["ANO"])
col_recebimento = achar_coluna(recebimentos, ["RECEBIMENTO"])
if not all([col_mes_rec, col_ano_rec, col_recebimento]):
    st.error("Não consegui localizar MÊS, ANO e RECEBIMENTO na aba RECEBIMENTO.")
    st.write(list(recebimentos.columns))
    st.stop()
recebimentos["PERIODO"] = recebimentos.apply(lambda r: mes_ano_label(r[col_mes_rec], r[col_ano_rec]), axis=1)
recebimentos["RECEBIMENTO"] = converter_numero_br(recebimentos[col_recebimento])


# ============================================================
# PREPARAÇÃO E MOTOR DE PERGUNTAS E RESPOSTAS
# ============================================================

def periodo_para_texto_opcoes():
    return ", ".join(ordenar_periodos(sorted(set(receita_cmv["PERIODO"].dropna()) | set(recebimentos["PERIODO"].dropna()) | set(confirmadas["PERIODO"].dropna()) | set(projetos_chat["PERIODO"].dropna() if "projetos_chat" in globals() and not projetos_chat.empty else []))))


def extrair_periodo_da_pergunta(pergunta, periodos_disponiveis):
    """Tenta identificar mês/ano na pergunta. Aceita JAN/25, JANEIRO 2025, 01/2025 etc."""
    txt = normalizar_texto(pergunta)
    inv_abrev = {normalizar_texto(v): k for k, v in MESES_ABREV.items()}

    # Formato JAN/25, JAN-25, JAN 25
    import re
    m = re.search(r"\b(JAN|FEV|MAR|ABR|MAI|JUN|JUL|AGO|SET|OUT|NOV|DEZ)[\s\-/]*(\d{2,4})\b", txt)
    if m:
        mes = inv_abrev.get(m.group(1))
        ano = int(m.group(2))
        ano2 = str(ano)[-2:]
        candidato = f"{MESES_ABREV[mes]}/{ano2}"
        if candidato in periodos_disponiveis:
            return candidato

    # Formato 01/2025 ou 1/25
    m = re.search(r"\b(0?[1-9]|1[0-2])[\-/](\d{2,4})\b", txt)
    if m:
        mes = int(m.group(1))
        ano2 = str(int(m.group(2)))[-2:]
        candidato = f"{MESES_ABREV[mes]}/{ano2}"
        if candidato in periodos_disponiveis:
            return candidato

    # Formato JANEIRO 2025, JANEIRO/25, etc.
    for nome_mes, mes_num in MESES_ORDEM.items():
        nome_norm = normalizar_texto(nome_mes)
        if nome_norm in txt:
            anos = re.findall(r"\b(20\d{2}|\d{2})\b", txt)
            if anos:
                ano2 = str(int(anos[-1]))[-2:]
                candidato = f"{MESES_ABREV[mes_num]}/{ano2}"
                if candidato in periodos_disponiveis:
                    return candidato
            # Se não veio ano, tenta único período com esse mês
            candidatos = [p for p in periodos_disponiveis if p.startswith(f"{MESES_ABREV[mes_num]}/")]
            if len(candidatos) == 1:
                return candidatos[0]

    return None


def preparar_projetos_para_chat(projetos_df):
    """Normaliza a aba PROJETOS para ser usada no chat gerencial."""
    pr = projetos_df.copy()
    col_mes_pr = achar_coluna(pr, ["MÊS", "MES"])
    col_ano_pr = achar_coluna(pr, ["ANO"])
    col_projeto = achar_coluna(pr, ["PROJETO", "CLIENTE"])
    col_receita_pr = achar_coluna(pr, ["RECEITA"])
    col_cmv_pr = achar_coluna(pr, ["CMV"])
    col_markup = achar_coluna(pr, ["MARKUP"])
    col_margem_rs = achar_coluna(pr, ["MARGEM B R$", "MARGEM BRUTA R$", "MARGEM"])
    col_margem_pct = achar_coluna(pr, ["MARGEM B %", "MARGEM BRUTA %"])

    if not all([col_mes_pr, col_ano_pr, col_projeto, col_receita_pr, col_cmv_pr]):
        return pd.DataFrame()

    pr["PERIODO"] = pr.apply(lambda r: mes_ano_label(r[col_mes_pr], r[col_ano_pr]), axis=1)
    pr["PROJETO_NOME"] = pr[col_projeto].astype(str).str.strip()
    pr["RECEITA_NUM"] = converter_numero_br(pr[col_receita_pr])
    pr["CMV_NUM"] = converter_numero_br(pr[col_cmv_pr])
    pr["MARKUP_NUM"] = pd.to_numeric(pr[col_markup], errors="coerce").fillna(0) if col_markup else np.where(pr["CMV_NUM"] != 0, pr["RECEITA_NUM"] / pr["CMV_NUM"], 0)
    pr["MARGEM_RS_NUM"] = converter_numero_br(pr[col_margem_rs]) if col_margem_rs else pr["RECEITA_NUM"] - pr["CMV_NUM"]
    if col_margem_pct:
        pr["MARGEM_PCT_NUM"] = pd.to_numeric(pr[col_margem_pct], errors="coerce").fillna(0)
        pr["MARGEM_PCT_NUM"] = np.where(pr["MARGEM_PCT_NUM"].abs() <= 1, pr["MARGEM_PCT_NUM"] * 100, pr["MARGEM_PCT_NUM"])
    else:
        pr["MARGEM_PCT_NUM"] = np.where(pr["RECEITA_NUM"] != 0, pr["MARGEM_RS_NUM"] / pr["RECEITA_NUM"] * 100, 0)
    return pr


projetos_chat = preparar_projetos_para_chat(projetos)


def calcular_dre_periodo(periodo):
    ordem_dre = [
        "IMPOSTOS/deduções", "DESPESA COM PESSOAL", "DESPESAS OPERACIONAIS",
        "DESPESAS FINANCEIRAS", "DESPESAS ADMINISTRATIVAS", "DESPESAS COMERCIAIS",
    ]
    receita = receita_cmv.loc[receita_cmv["PERIODO"] == periodo, "RECEITA"].sum()
    cmv = receita_cmv.loc[receita_cmv["PERIODO"] == periodo, "CMV"].sum()
    despesas = {}
    for conta in ordem_dre:
        despesas[conta] = confirmadas[(confirmadas["CONTA_RESULTADO_NORM"] == normalizar_texto(conta)) & (confirmadas["PERIODO"] == periodo)]["Valor total"].sum()
    resultado = receita - cmv - sum(despesas.values())
    return {"periodo": periodo, "receita": receita, "cmv": cmv, "margem_bruta": receita - cmv, "despesas": despesas, "resultado_dre": resultado}


def calcular_dfc_periodo(periodo):
    ordem_dfc = [
        "DESPESA COM PESSOAL", "DESPESAS OPERACIONAIS", "DESPESAS FINANCEIRAS",
        "DESPESAS ADMINISTRATIVAS", "DESPESAS COMERCIAIS", "IMPOSTOS/deduções", "FORNECEDORES",
    ]
    recebimento = recebimentos.loc[recebimentos["PERIODO"] == periodo, "RECEBIMENTO"].sum()
    saidas = {}
    for conta in ordem_dfc:
        saidas[conta] = confirmadas[(confirmadas["CONTA_RESULTADO_NORM"] == normalizar_texto(conta)) & (confirmadas["PERIODO"] == periodo)]["Valor total"].sum()
    resultado = recebimento - sum(saidas.values())
    return {"periodo": periodo, "recebimento": recebimento, "saidas": saidas, "resultado_caixa": resultado}



CONTAS_RESULTADO_PADRAO = [
    "IMPOSTOS/deduções", "DESPESA COM PESSOAL", "DESPESAS OPERACIONAIS",
    "DESPESAS FINANCEIRAS", "DESPESAS ADMINISTRATIVAS", "DESPESAS COMERCIAIS",
    "FORNECEDORES", "AJUSTE", "APLICAÇÃO"
]

ALIAS_CONTAS_RESULTADO = {
    "PESSOAL": "DESPESA COM PESSOAL",
    "FOLHA": "DESPESA COM PESSOAL",
    "SALARIO": "DESPESA COM PESSOAL",
    "SALARIOS": "DESPESA COM PESSOAL",
    "OPERACIONAL": "DESPESAS OPERACIONAIS",
    "OPERACIONAIS": "DESPESAS OPERACIONAIS",
    "FINANCEIRA": "DESPESAS FINANCEIRAS",
    "FINANCEIRAS": "DESPESAS FINANCEIRAS",
    "ADMINISTRATIVA": "DESPESAS ADMINISTRATIVAS",
    "ADMINISTRATIVAS": "DESPESAS ADMINISTRATIVAS",
    "COMERCIAL": "DESPESAS COMERCIAIS",
    "COMERCIAIS": "DESPESAS COMERCIAIS",
    "IMPOSTO": "IMPOSTOS/deduções",
    "IMPOSTOS": "IMPOSTOS/deduções",
    "DEDUCAO": "IMPOSTOS/deduções",
    "DEDUCOES": "IMPOSTOS/deduções",
    "FORNECEDOR": "FORNECEDORES",
    "FORNECEDORES": "FORNECEDORES",
    "AJUSTE": "AJUSTE",
    "AJUSTES": "AJUSTE",
    "APLICACAO": "APLICAÇÃO",
    "APLICACOES": "APLICAÇÃO",
}


def localizar_conta_resultado_na_pergunta(pergunta):
    txt = normalizar_texto(pergunta)
    for alias, conta in ALIAS_CONTAS_RESULTADO.items():
        if alias in txt:
            return conta
    contas_base = sorted([c for c in confirmadas["CONTA_RESULTADO"].dropna().unique() if str(c).strip()])
    for conta in contas_base:
        conta_norm = normalizar_texto(conta)
        if conta_norm and conta_norm in txt:
            return conta
    return None


def periodos_da_pergunta(pergunta, periodos_disponiveis):
    """Extrai um ou mais períodos da pergunta. Se encontrar intervalo, retorna os meses do intervalo."""
    txt = normalizar_texto(pergunta)
    achados = []
    for p in periodos_disponiveis:
        mes, ano = p.split("/")
        padroes = [p, p.replace("/", " "), p.replace("/", "-"), f"{mes}/{ano}"]
        if any(normalizar_texto(x) in txt for x in padroes):
            achados.append(p)
    primeiro = extrair_periodo_da_pergunta(pergunta, periodos_disponiveis)
    if primeiro and primeiro not in achados:
        achados.append(primeiro)
    achados = ordenar_periodos(achados)
    if len(achados) >= 2 and any(x in txt for x in [" A ", "ATE", "ATÉ", "ENTRE", "COMPAR", "VERSUS", "VS"]):
        todos = ordenar_periodos(periodos_disponiveis)
        i1, i2 = todos.index(achados[0]), todos.index(achados[-1])
        if i1 <= i2:
            return todos[i1:i2+1]
    return achados


def df_para_markdown_tabela(df, max_linhas=20):
    """Gera tabela em texto sem depender da biblioteca tabulate.
    Evita erro no Streamlit Cloud quando o pandas tenta usar df.to_markdown().
    """
    if df is None or df.empty:
        return "Sem dados para exibir."
    texto = df.head(max_linhas).astype(str).to_string(index=False)
    return f"```text\n{texto}\n```"


def calcular_variacao_mensal(resumo, coluna_valor="Valor total"):
    out = resumo.copy()
    if out.empty or coluna_valor not in out.columns:
        return out
    out["Variação R$"] = out[coluna_valor].diff().fillna(0)
    out["Variação %"] = np.where(out[coluna_valor].shift(1).fillna(0) != 0, out["Variação R$"] / out[coluna_valor].shift(1) * 100, 0)
    out["Tendência"] = np.select(
        [out["Variação R$"] > 0, out["Variação R$"] < 0],
        ["Evolução", "Queda"],
        default="Estável"
    )
    return out


def localizar_planos_contas_na_pergunta(pergunta, limite=12):
    """Busca dinâmica por Plano de Contas.
    Ex.: pergunta com 'energia' encontra 'Energia elétrica + água'.
    """
    import difflib
    txt = normalizar_texto(pergunta)
    stop = {
        "DETALHE", "DETALHAR", "DETALHAMENTO", "COMPARE", "COMPARAR", "COMPARATIVO",
        "EVOLUCAO", "EVOLUÇÃO", "VARIACAO", "VARIAÇÃO", "DESPESA", "DESPESAS",
        "CONTA", "PLANO", "PLANOS", "CONTAS", "RESULTADO", "VALOR", "VALORES",
        "MES", "MESES", "MES A MES", "MENSAL", "DE", "DA", "DAS", "DO", "DOS",
        "EM", "NO", "NA", "NOS", "NAS", "A", "ATE", "ATÉ", "ENTRE", "POR", "PARA",
        "QUAL", "QUAIS", "FOI", "FORAM", "MOSTRE", "MOSTRAR", "ABRA", "ABRIR"
    }
    # remove períodos e nomes de meses da busca
    for p in sorted(set(confirmadas["PERIODO"].dropna().astype(str))):
        txt = txt.replace(normalizar_texto(p), " ")
        txt = txt.replace(normalizar_texto(p.replace("/", " ")), " ")
    for mes in list(MESES_ORDEM.keys()) + list(MESES_ABREV.values()):
        txt = txt.replace(normalizar_texto(mes), " ")
    for alias in ALIAS_CONTAS_RESULTADO.keys():
        txt = txt.replace(alias, " ")

    termos = [t for t in txt.split() if len(t) >= 4 and t not in stop and not t.isdigit()]
    planos = confirmadas[["Plano de contas", "PLANO_NORM"]].dropna().drop_duplicates()
    if planos.empty:
        return []

    matches = []
    for _, row in planos.iterrows():
        plano = str(row["Plano de contas"]).strip()
        plano_norm = str(row["PLANO_NORM"]).strip()
        score = 0
        for termo in termos:
            if termo and termo in plano_norm:
                score += 10 + len(termo)
        if txt.strip() and txt.strip() in plano_norm:
            score += 20
        if score > 0:
            matches.append((score, plano, plano_norm))

    if not matches and termos:
        plano_norms = planos["PLANO_NORM"].astype(str).tolist()
        for termo in termos:
            for prox in difflib.get_close_matches(termo, plano_norms, n=limite, cutoff=0.68):
                plano = planos.loc[planos["PLANO_NORM"].astype(str).eq(prox), "Plano de contas"].iloc[0]
                matches.append((5, str(plano), prox))

    unicos = {}
    for score, plano, plano_norm in matches:
        if plano_norm not in unicos or score > unicos[plano_norm][0]:
            unicos[plano_norm] = (score, plano)
    ordenados = sorted(unicos.values(), key=lambda x: x[0], reverse=True)[:limite]
    return [plano for _, plano in ordenados]


def resumo_plano_por_periodo(planos, periodos_ref=None):
    periodos_ref = periodos_ref or ordenar_periodos(confirmadas["PERIODO"].dropna().unique())
    planos_norm = [normalizar_texto(p) for p in planos]
    dados = confirmadas[
        (confirmadas["PLANO_NORM"].isin(planos_norm)) &
        (confirmadas["PERIODO"].isin(periodos_ref))
    ].copy()
    resumo = dados.groupby("PERIODO", as_index=False)["Valor total"].sum()
    todos = pd.DataFrame({"PERIODO": periodos_ref})
    resumo = todos.merge(resumo, on="PERIODO", how="left").fillna({"Valor total": 0})
    resumo["ORDEM"] = resumo["PERIODO"].apply(lambda p: periodos_ref.index(p) if p in periodos_ref else 999)
    resumo = resumo.sort_values("ORDEM").drop(columns=["ORDEM"])
    return resumo, dados


def resumo_conta_por_periodo(conta, periodos_ref=None):
    periodos_ref = periodos_ref or ordenar_periodos(confirmadas["PERIODO"].dropna().unique())
    dados = confirmadas[
        (confirmadas["CONTA_RESULTADO_NORM"] == normalizar_texto(conta)) &
        (confirmadas["PERIODO"].isin(periodos_ref))
    ].copy()
    resumo = dados.groupby("PERIODO", as_index=False)["Valor total"].sum()
    todos = pd.DataFrame({"PERIODO": periodos_ref})
    resumo = todos.merge(resumo, on="PERIODO", how="left").fillna({"Valor total": 0})
    resumo["ORDEM"] = resumo["PERIODO"].apply(lambda p: periodos_ref.index(p) if p in periodos_ref else 999)
    resumo = resumo.sort_values("ORDEM").drop(columns=["ORDEM"])
    return resumo


def responder_comparativo_despesa(pergunta, periodos_disponiveis):
    conta = localizar_conta_resultado_na_pergunta(pergunta)
    planos = [] if conta else localizar_planos_contas_na_pergunta(pergunta)

    if not conta and not planos:
        return (
            "Identifiquei que você quer um comparativo, mas não consegui localizar a despesa/conta. "
            "Exemplos: 'Compare despesas com pessoal de JAN/25 a MAR/25' ou 'Compare energia de outubro a abril'."
        )

    ps = periodos_da_pergunta(pergunta, periodos_disponiveis)
    if not ps:
        ps = periodos_disponiveis

    if conta:
        titulo = conta
        resumo = resumo_conta_por_periodo(conta, ps)
        base_dados = confirmadas[
            (confirmadas["CONTA_RESULTADO_NORM"] == normalizar_texto(conta)) &
            (confirmadas["PERIODO"].isin(ps))
        ].copy()
    else:
        titulo = " + ".join(planos[:3]) + ("..." if len(planos) > 3 else "")
        resumo, base_dados = resumo_plano_por_periodo(planos, ps)

    resumo = calcular_variacao_mensal(resumo, "Valor total")
    total = resumo["Valor total"].sum()
    media = resumo["Valor total"].mean() if len(resumo) else 0
    maior = resumo.sort_values("Valor total", ascending=False).iloc[0] if not resumo.empty else None
    menor = resumo.sort_values("Valor total", ascending=True).iloc[0] if not resumo.empty else None

    resumo_fmt = resumo.copy()
    resumo_fmt["Valor"] = resumo_fmt["Valor total"].apply(moeda)
    resumo_fmt["Variação R$"] = resumo_fmt["Variação R$"].apply(moeda)
    resumo_fmt["Variação %"] = resumo_fmt["Variação %"].apply(perc)
    resumo_fmt = resumo_fmt[["PERIODO", "Valor", "Variação R$", "Variação %", "Tendência"]]

    variacao_txt = ""
    leitura = ""
    if len(resumo) >= 2:
        ini = resumo.iloc[0]["Valor total"]
        fim = resumo.iloc[-1]["Valor total"]
        var = fim - ini
        var_pct = (var / ini * 100) if ini else 0
        sentido = "evolução" if var > 0 else "queda" if var < 0 else "estabilidade"
        variacao_txt = f"\n\nDo primeiro para o último período houve **{sentido}** de **{moeda(abs(var))}** ({perc(var_pct)})."
        leitura = "Atenção: a despesa aumentou no período, vale verificar os lançamentos que puxaram essa alta." if var > 0 else "Boa leitura: houve redução no período, vale entender se foi ganho de eficiência ou apenas postergação de pagamento." if var < 0 else "A conta ficou praticamente estável no período."

    detalhe_planos = ""
    if not base_dados.empty:
        por_plano = base_dados.groupby("Plano de contas", as_index=False)["Valor total"].sum().sort_values("Valor total", ascending=False).head(10)
        por_plano["Valor"] = por_plano["Valor total"].apply(moeda)
        detalhe_planos = "\n\n#### Principais planos de contas encontrados\n" + df_para_markdown_tabela(por_plano[["Plano de contas", "Valor"]], 10)

    return (
        f"### Comparativo mensal — {titulo}\n\n"
        f"Período analisado: **{', '.join(ps)}**.\n\n"
        f"Total: **{moeda(total)}**.\n"
        f"Média mensal: **{moeda(media)}**.\n"
        f"Maior mês: **{maior['PERIODO']}**, com **{moeda(maior['Valor total'])}**.\n"
        f"Menor mês: **{menor['PERIODO']}**, com **{moeda(menor['Valor total'])}**."
        f"{variacao_txt}\n\n"
        f"**Leitura gerencial:** {leitura}\n\n"
        f"#### Mês a mês\n"
        f"{df_para_markdown_tabela(resumo_fmt, 48)}"
        f"{detalhe_planos}"
    )

def responder_detalhamento_conta(pergunta, periodos_disponiveis):
    conta = localizar_conta_resultado_na_pergunta(pergunta)
    planos = [] if conta else localizar_planos_contas_na_pergunta(pergunta)

    if not conta and not planos:
        return (
            "Identifiquei que você quer um detalhamento, mas não consegui localizar a conta. "
            "Exemplos: 'Detalhe despesas com pessoal', 'Detalhe energia', 'Detalhe aluguel' ou 'Detalhe impostos de JAN/25'."
        )

    ps = periodos_da_pergunta(pergunta, periodos_disponiveis)
    if not ps:
        ps = periodos_disponiveis

    if conta:
        titulo = conta
        dados = confirmadas[
            (confirmadas["CONTA_RESULTADO_NORM"] == normalizar_texto(conta)) &
            (confirmadas["PERIODO"].isin(ps))
        ].copy()
    else:
        titulo = "Plano de contas: " + " + ".join(planos[:5]) + ("..." if len(planos) > 5 else "")
        dados = confirmadas[
            (confirmadas["PLANO_NORM"].isin([normalizar_texto(p) for p in planos])) &
            (confirmadas["PERIODO"].isin(ps))
        ].copy()

    if dados.empty:
        return f"Não encontrei lançamentos para **{titulo}** no período solicitado."

    resumo = dados.groupby("Plano de contas", as_index=False).agg(
        Qtd=("Valor total", "count"),
        Valor=("Valor total", "sum")
    ).sort_values("Valor", ascending=False)
    total = resumo["Valor"].sum()
    resumo["% sobre total"] = np.where(total != 0, resumo["Valor"] / total * 100, 0)

    resumo_fmt = resumo.copy()
    resumo_fmt["Valor"] = resumo_fmt["Valor"].apply(moeda)
    resumo_fmt["% sobre total"] = resumo_fmt["% sobre total"].apply(perc)
    top = resumo.iloc[0]

    mensal = dados.groupby("PERIODO", as_index=False)["Valor total"].sum()
    todos = pd.DataFrame({"PERIODO": ps})
    mensal = todos.merge(mensal, on="PERIODO", how="left").fillna({"Valor total": 0})
    mensal["ORDEM"] = mensal["PERIODO"].apply(lambda p: ps.index(p) if p in ps else 999)
    mensal = calcular_variacao_mensal(mensal.sort_values("ORDEM").drop(columns=["ORDEM"]), "Valor total")
    mensal_fmt = mensal.copy()
    mensal_fmt["Valor"] = mensal_fmt["Valor total"].apply(moeda)
    mensal_fmt["Variação R$"] = mensal_fmt["Variação R$"].apply(moeda)
    mensal_fmt["Variação %"] = mensal_fmt["Variação %"].apply(perc)
    mensal_fmt = mensal_fmt[["PERIODO", "Valor", "Variação R$", "Variação %", "Tendência"]]

    dados["Descrição consolidada"] = dados["Descrição"].apply(consolidar_descricao_parcelada)
    descricoes = dados.groupby(["Plano de contas", "Descrição consolidada"], as_index=False).agg(
        Qtd=("Valor total", "count"),
        Valor=("Valor total", "sum")
    ).sort_values("Valor", ascending=False).head(30)
    descricoes = descricoes.rename(columns={"Descrição consolidada": "Descrição"})
    descricoes_fmt = descricoes.copy()
    descricoes_fmt["Valor"] = descricoes_fmt["Valor"].apply(moeda)

    return (
        f"### Detalhamento — {titulo}\n\n"
        f"Período analisado: **{', '.join(ps)}**.\n\n"
        f"Total encontrado: **{moeda(total)}**.\n"
        f"Quantidade de lançamentos: **{len(dados)}**.\n"
        f"Principal plano de contas: **{top['Plano de contas']}**, com **{moeda(top['Valor'])}**.\n\n"
        f"#### Resumo por plano de contas\n"
        f"{df_para_markdown_tabela(resumo_fmt, 30)}\n\n"
        f"#### Evolução mensal\n"
        f"{df_para_markdown_tabela(mensal_fmt, 48)}\n\n"
        f"#### Detalhamento por descrição\n"
        f"{df_para_markdown_tabela(descricoes_fmt, 30)}"
    )

def responder_analise_projetos(pergunta, periodos_disponiveis):
    if projetos_chat.empty:
        return "Não consegui preparar a aba PROJETOS. Verifique se existem as colunas MÊS, ANO, PROJETO/CLIENTE, RECEITA e CMV."
    ps = periodos_da_pergunta(pergunta, sorted(projetos_chat["PERIODO"].dropna().unique()))
    base = projetos_chat.copy()
    contexto = "base completa de projetos"
    if ps:
        base = base[base["PERIODO"].isin(ps)].copy()
        contexto = ", ".join(ps)
    if base.empty:
        return f"Não encontrei projetos para {contexto}."
    receita = base["RECEITA_NUM"].sum()
    cmv = base["CMV_NUM"].sum()
    margem = base["MARGEM_RS_NUM"].sum()
    markup = receita / cmv if cmv else 0
    margem_pct = margem / receita * 100 if receita else 0
    cmv_pct = cmv / receita * 100 if receita else 0
    ranking = base.groupby("PROJETO_NOME", as_index=False).agg(
        Receita=("RECEITA_NUM", "sum"),
        CMV=("CMV_NUM", "sum"),
        Margem=("MARGEM_RS_NUM", "sum"),
    )
    ranking["Markup"] = np.where(ranking["CMV"] != 0, ranking["Receita"] / ranking["CMV"], 0)
    ranking["Margem %"] = np.where(ranking["Receita"] != 0, ranking["Margem"] / ranking["Receita"] * 100, 0)
    ranking = ranking.sort_values("Margem", ascending=False)
    top_margem = ranking.iloc[0]
    top_receita = ranking.sort_values("Receita", ascending=False).iloc[0]
    ranking_fmt = ranking.head(10).copy()
    for c in ["Receita", "CMV", "Margem"]:
        ranking_fmt[c] = ranking_fmt[c].apply(moeda)
    ranking_fmt["Markup"] = ranking_fmt["Markup"].apply(numero)
    ranking_fmt["Margem %"] = ranking_fmt["Margem %"].apply(perc)
    diagnostico = ""
    if margem_pct < 20:
        diagnostico = "A margem percentual está baixa. Vale revisar precificação, composição de custo e descontos concedidos nos projetos."
    elif margem_pct < 35:
        diagnostico = "A margem está em faixa intermediária. Há espaço para melhorar markup em projetos de maior volume."
    else:
        diagnostico = "A margem geral dos projetos está saudável, desde que os custos estejam corretamente alocados."
    return (
        f"### Análise de Projetos — {contexto}\n\n"
        f"Receita total: **{moeda(receita)}**.\n"
        f"Custo/CMV total: **{moeda(cmv)}** ({perc(cmv_pct)} da receita).\n"
        f"Margem bruta: **{moeda(margem)}** ({perc(margem_pct)}).\n"
        f"Markup médio: **{numero(markup)}**.\n\n"
        f"Projeto/cliente com maior receita: **{top_receita['PROJETO_NOME']}**, com **{moeda(top_receita['Receita'])}**.\n"
        f"Projeto/cliente com maior margem: **{top_margem['PROJETO_NOME']}**, com **{moeda(top_margem['Margem'])}**.\n\n"
        f"**Leitura gerencial:** {diagnostico}\n\n"
        f"#### Top 10 projetos por margem\n"
        f"{df_para_markdown_tabela(ranking_fmt, 10)}"
    )


def gerar_100_exemplos_perguntas():
    meses_ex = ["JAN/25", "FEV/25", "MAR/25", "ABR/25", "MAI/25", "JUN/25"]
    contas_ex = ["despesas com pessoal", "despesas operacionais", "despesas financeiras", "despesas administrativas", "despesas comerciais", "impostos", "fornecedores", "ajustes", "aplicações"]
    perguntas = []
    perguntas += [
        "Qual foi a receita de JAN/25?",
        "Qual foi o faturamento de FEV/25?",
        "Qual foi o CMV de MAR/25?",
        "Qual foi a margem bruta de ABR/25?",
        "Qual foi a margem bruta de 2025?",
        "Qual foi a margem bruta de janeiro de 2025?",
        "Compare a margem bruta de 2025 com 2026.",
        "Qual foi o faturamento de 2025?",
        "Qual foi o percentual de CMV em MAI/25?",
        "Qual foi o lucro no DRE de JAN/25?",
        "Qual foi o resultado no DRE de FEV/25?",
        "Qual foi o lucro no DFC de MAR/25?",
        "Qual foi o resultado de caixa de ABR/25?",
        "Qual foi o recebimento de MAI/25?",
    ]
    for conta in contas_ex:
        perguntas.append(f"Qual foi o valor de {conta} em JAN/25?")
        perguntas.append(f"Detalhe {conta} em FEV/25.")
        perguntas.append(f"Compare {conta} de JAN/25 a MAR/25.")
        perguntas.append(f"Qual foi a média de {conta} no período selecionado?")
        perguntas.append(f"Qual mês teve maior valor de {conta}?")
    perguntas += [
        "Faça uma análise dos projetos.",
        "Faça uma análise dos projetos de JAN/25.",
        "Qual projeto teve maior receita?",
        "Qual projeto teve maior margem?",
        "Qual projeto teve menor margem percentual?",
        "Qual foi o markup dos projetos em JAN/25?",
        "Qual foi o markup médio dos projetos?",
        "Liste os 10 maiores projetos por receita.",
        "Liste os 10 maiores projetos por margem.",
        "Qual cliente/projeto mais consumiu CMV?",
        "Qual cliente/projeto teve melhor markup?",
        "Qual cliente/projeto teve pior markup?",
        "Analise receita, custo, margem e markup dos projetos de MAR/25.",
        "Qual foi a margem percentual dos projetos de ABR/25?",
        "Compare os projetos de JAN/25 a MAR/25.",
        "Qual foi a participação do CMV nos projetos?",
        "Qual projeto merece atenção por margem baixa?",
        "Qual foi o cliente que mais deu margem?",
        "Qual foi o cliente que mais deu margem em JAN/25?",
        "Qual foi a representatividade do maior projeto na receita total?",
    ]
    perguntas += [
        "Compare receita de JAN/25 a MAR/25.",
        "Compare resultado DRE de JAN/25 a MAR/25.",
        "Compare resultado DFC de JAN/25 a MAR/25.",
        "Quais foram os meses com resultado DRE negativo?",
        "Quais foram os meses com resultado de caixa negativo?",
        "Qual mês teve maior receita?",
        "Qual mês teve menor receita?",
        "Qual mês teve maior margem bruta?",
        "Qual mês teve pior resultado DRE?",
        "Qual mês teve pior resultado DFC?",
        "Faça uma análise geral do DRE.",
        "Faça uma análise geral do DFC.",
        "Faça uma análise geral do período selecionado.",
        "Quais contas mais pesaram no DRE?",
        "Quais contas mais pesaram no DFC?",
        "Qual despesa representa mais sobre a receita?",
        "Qual saída representa mais sobre o recebimento?",
        "Qual foi o ponto de atenção do mês JAN/25?",
        "Qual despesa cresceu mais no período?",
        "Qual despesa reduziu mais no período?",
    ]
    perguntas += [
        "Detalhe despesas com pessoal por plano de contas.",
        "Detalhe despesas operacionais por plano de contas.",
        "Detalhe despesas financeiras por plano de contas.",
        "Detalhe despesas administrativas por plano de contas.",
        "Detalhe despesas comerciais por plano de contas.",
        "Detalhe impostos por plano de contas.",
        "Detalhe fornecedores por plano de contas.",
        "Quais são os principais planos dentro de despesas com pessoal?",
        "Quais são os principais planos dentro de despesas operacionais?",
        "Quais são os principais planos dentro de despesas financeiras?",
    ]
    perguntas += [
        "Qual foi a necessidade média de caixa?",
        "Qual foi a média mensal de despesas com pessoal?",
        "Qual foi a média mensal de fornecedores?",
        "Qual foi a média mensal de impostos?",
        "Qual conta pesa mais no ponto de equilíbrio?",
        "Qual seria a necessidade semanal de caixa?",
        "Qual seria a necessidade diária de caixa?",
        "Quais contas devo acompanhar com mais atenção?",
        "Onde posso reduzir despesas?",
        "O resultado está saudável?",
        "A margem bruta está boa?",
        "O CMV está alto?",
        "As despesas com pessoal estão pesando muito?",
        "As despesas operacionais estão fora do padrão?",
        "As despesas financeiras estão altas?",
        "Os impostos estão representando quanto da receita?",
        "Fornecedores estão pesando quanto no caixa?",
        "Faça um resumo executivo do mês JAN/25.",
        "Faça um resumo executivo do período selecionado.",
        "Quais são os principais riscos financeiros do período?",
        "Quais são as principais oportunidades de melhoria?",
        "Me dê uma análise para reunião de diretoria.",
        "Me dê uma análise curta para WhatsApp.",
        "O que mais impactou o resultado?",
        "O que mais impactou o caixa?",
    ]
    # Garante pelo menos 100 e remove duplicidades preservando ordem.
    unicas = []
    for p in perguntas:
        if p not in unicas:
            unicas.append(p)
    return unicas[:100]


def responder_pergunta_gerencial(pergunta):
    txt = normalizar_texto(pergunta)
    periodos_disponiveis = ordenar_periodos(sorted(set(receita_cmv["PERIODO"].dropna()) | set(recebimentos["PERIODO"].dropna()) | set(confirmadas["PERIODO"].dropna()) | set(projetos_chat["PERIODO"].dropna() if not projetos_chat.empty else [])))
    periodo = extrair_periodo_da_pergunta(pergunta, periodos_disponiveis)

    # Detalhamento por Conta de Resultado
    if any(x in txt for x in ["DETALH", "ABRA", "ABRIR", "PLANOS DE CONTAS", "POR PLANO", "PRINCIPAIS PLANOS"]):
        return responder_detalhamento_conta(pergunta, periodos_disponiveis)

    # Comparativos de qualquer despesa/conta
    if any(x in txt for x in ["COMPAR", "EVOLUCAO", "EVOLUÇÃO", "VARIACAO", "VARIAÇÃO", "MES A MES", "MÊS A MÊS"]):
        if any(x in txt for x in ["PROJETO", "CLIENTE"]):
            return responder_analise_projetos(pergunta, periodos_disponiveis)
        return responder_comparativo_despesa(pergunta, periodos_disponiveis)

    # Análise textual de projetos
    if "PROJETO" in txt or ("CLIENTE" in txt and any(x in txt for x in ["MARGEM", "MARKUP", "RECEITA", "CMV"])):
        if "MARKUP" not in txt and any(x in txt for x in ["ANALISE", "ANALISAR", "RESUMO", "DETALH", "RECEITA", "CUSTO", "CMV", "MARGEM"]):
            return responder_analise_projetos(pergunta, periodos_disponiveis)

    if any(palavra in txt for palavra in ["RECEITA", "FATURAMENTO"]):
        if not periodo:
            return "Não identifiquei o mês/ano na pergunta. Exemplo: 'Qual foi a receita de JAN/25?'"
        valor = receita_cmv.loc[receita_cmv["PERIODO"] == periodo, "RECEITA"].sum()
        cmv = receita_cmv.loc[receita_cmv["PERIODO"] == periodo, "CMV"].sum()
        margem = valor - cmv
        margem_pct = margem / valor * 100 if valor else 0
        return f"A receita de {periodo} foi de **{moeda(valor)}**.\n\nCMV: **{moeda(cmv)}**.\nMargem bruta: **{moeda(margem)}** ({perc(margem_pct)})."

    if "CMV" in txt or "CUSTO" in txt:
        if not periodo:
            return "Não identifiquei o mês/ano na pergunta. Exemplo: 'Qual foi o CMV de JAN/25?'"
        receita = receita_cmv.loc[receita_cmv["PERIODO"] == periodo, "RECEITA"].sum()
        cmv = receita_cmv.loc[receita_cmv["PERIODO"] == periodo, "CMV"].sum()
        pct = cmv / receita * 100 if receita else 0
        return f"O CMV/custo de {periodo} foi de **{moeda(cmv)}**, representando **{perc(pct)}** da receita."

    # Valor simples de qualquer conta de resultado
    conta = localizar_conta_resultado_na_pergunta(pergunta)
    if conta:
        if not periodo:
            return responder_detalhamento_conta(pergunta, periodos_disponiveis)
        valor = confirmadas[(confirmadas["CONTA_RESULTADO_NORM"] == normalizar_texto(conta)) & (confirmadas["PERIODO"] == periodo)]["Valor total"].sum()
        receita = receita_cmv.loc[receita_cmv["PERIODO"] == periodo, "RECEITA"].sum()
        recebimento = recebimentos.loc[recebimentos["PERIODO"] == periodo, "RECEBIMENTO"].sum()
        pct_receita = valor / receita * 100 if receita else 0
        pct_receb = valor / recebimento * 100 if recebimento else 0
        return f"A conta **{conta}** em {periodo} foi de **{moeda(valor)}**.\n\nRepresenta **{perc(pct_receita)}** da receita e **{perc(pct_receb)}** do recebimento do mês."

    # Busca dinâmica por plano de contas quando o usuário cita uma despesa específica, como energia, aluguel, internet etc.
    planos_encontrados = localizar_planos_contas_na_pergunta(pergunta)
    if planos_encontrados and any(x in txt for x in ["DETALH", "PLANO", "CONTA", "DESPESA", "VALOR", "ENERGIA", "ALUGUEL", "AGUA", "ÁGUA", "INTERNET", "TELEFONE"]):
        if any(x in txt for x in ["COMPAR", "EVOLUCAO", "EVOLUÇÃO", "VARIACAO", "VARIAÇÃO", "MES A MES", "MÊS A MÊS"]):
            return responder_comparativo_despesa(pergunta, periodos_disponiveis)
        return responder_detalhamento_conta(pergunta, periodos_disponiveis)

    if ("LUCRO" in txt or "RESULTADO" in txt) and "DFC" in txt:
        if not periodo:
            return "Não identifiquei o mês/ano na pergunta. Exemplo: 'Qual foi o lucro no DFC de ABR/25?'"
        d = calcular_dfc_periodo(periodo)
        pct = d["resultado_caixa"] / d["recebimento"] * 100 if d["recebimento"] else 0
        return f"O resultado de caixa/DFC em {periodo} foi de **{moeda(d['resultado_caixa'])}**.\n\nRecebimento: **{moeda(d['recebimento'])}**.\nSaídas: **{moeda(sum(d['saidas'].values()))}**.\nResultado sobre recebimento: **{perc(pct)}**."

    if ("LUCRO" in txt or "RESULTADO" in txt) and "DRE" in txt:
        if not periodo:
            return "Não identifiquei o mês/ano na pergunta. Exemplo: 'Qual foi o lucro no DRE de ABR/25?'"
        d = calcular_dre_periodo(periodo)
        pct = d["resultado_dre"] / d["receita"] * 100 if d["receita"] else 0
        return f"O resultado/lucro no DRE em {periodo} foi de **{moeda(d['resultado_dre'])}**.\n\nReceita: **{moeda(d['receita'])}**.\nCMV: **{moeda(d['cmv'])}**.\nDespesas DRE: **{moeda(sum(d['despesas'].values()))}**.\nResultado sobre receita: **{perc(pct)}**."

    if "RECEBIMENTO" in txt or "RECEBIMENTOS" in txt:
        if not periodo:
            return "Não identifiquei o mês/ano na pergunta. Exemplo: 'Qual foi o recebimento de JAN/25?'"
        valor = recebimentos.loc[recebimentos["PERIODO"] == periodo, "RECEBIMENTO"].sum()
        return f"O recebimento de {periodo} foi de **{moeda(valor)}**."

    if "MARKUP" in txt:
        if projetos_chat.empty:
            return "Não consegui preparar a aba PROJETOS para analisar markup. Verifique as colunas MÊS, ANO, PROJETO/CLIENTE, RECEITA e CMV."
        if not periodo:
            return responder_analise_projetos(pergunta, periodos_disponiveis)
        base = projetos_chat[projetos_chat["PERIODO"] == periodo].copy()
        receita = base["RECEITA_NUM"].sum()
        cmv = base["CMV_NUM"].sum()
        margem = receita - cmv
        markup = receita / cmv if cmv else 0
        margem_pct = margem / receita * 100 if receita else 0
        return f"O markup dos projetos em {periodo} foi de **{numero(markup)}**.\n\nReceita de projetos: **{moeda(receita)}**.\nCMV de projetos: **{moeda(cmv)}**.\nMargem: **{moeda(margem)}** ({perc(margem_pct)})."

    if any(x in txt for x in ["ANALISE GERAL", "RESUMO EXECUTIVO", "DIRETORIA", "SAUDAVEL", "RISCO", "OPORTUNIDADE"]):
        ps = periodos_da_pergunta(pergunta, periodos_disponiveis) or periodos
        receita = receita_cmv[receita_cmv["PERIODO"].isin(ps)]["RECEITA"].sum()
        cmv = receita_cmv[receita_cmv["PERIODO"].isin(ps)]["CMV"].sum()
        receb = recebimentos[recebimentos["PERIODO"].isin(ps)]["RECEBIMENTO"].sum()
        saidas = confirmadas[confirmadas["PERIODO"].isin(ps) & confirmadas["CONTA_RESULTADO_NORM"].isin([normalizar_texto(c) for c in CONTAS_RESULTADO_PADRAO])]["Valor total"].sum()
        margem = receita - cmv
        resultado_dre = receita - cmv - confirmadas[confirmadas["PERIODO"].isin(ps) & confirmadas["CONTA_RESULTADO_NORM"].isin([normalizar_texto(c) for c in CONTAS_RESULTADO_PADRAO if c != "FORNECEDORES"])] ["Valor total"].sum()
        resultado_caixa = receb - saidas
        return (
            f"### Resumo executivo — {', '.join(ps)}\n\n"
            f"Receita: **{moeda(receita)}**.\n"
            f"CMV: **{moeda(cmv)}**.\n"
            f"Margem bruta: **{moeda(margem)}** ({perc(margem/receita*100 if receita else 0)}).\n"
            f"Resultado DRE estimado: **{moeda(resultado_dre)}**.\n"
            f"Recebimento: **{moeda(receb)}**.\n"
            f"Saídas DFC: **{moeda(saidas)}**.\n"
            f"Resultado de caixa estimado: **{moeda(resultado_caixa)}**.\n\n"
            f"**Leitura gerencial:** acompanhe principalmente as contas com maior peso sobre receita/recebimento e valide se o resultado de caixa acompanha o resultado econômico."
        )

    return "Ainda não tenho uma rota pronta para essa pergunta. Abra a lista de exemplos e teste perguntas sobre receita, CMV, despesas, comparativos, detalhamento de contas, DRE, DFC ou projetos."



# ============================================================
# AGENTE DE BI CONVERSACIONAL - ROTEADOR + PANDAS
# ============================================================

def periodo_chave(periodo):
    """Converte JAN/25 em chave numérica (2025, 1)."""
    try:
        mes_abrev, ano2 = str(periodo).split("/")
        inv = {v: k for k, v in MESES_ABREV.items()}
        return (2000 + int(ano2), inv.get(mes_abrev.upper(), 99))
    except Exception:
        return (9999, 99)


def periodo_label_por_chave(ano, mes):
    return f"{MESES_ABREV[int(mes)]}/{str(int(ano))[-2:]}"


def anos_mencionados_na_pergunta(pergunta):
    """Extrai anos escritos como 2025/2026 ou 25/26 quando aparecem na pergunta."""
    import re
    txt = normalizar_texto(pergunta)
    anos = []

    for m in re.finditer(r"\b(20\d{2})\b", txt):
        ano = int(m.group(1))
        if 2000 <= ano <= 2099 and ano not in anos:
            anos.append(ano)

    # Aceita ano curto apenas quando houver pistas financeiras/temporais, para evitar confundir valores.
    if not anos and any(x in txt for x in ["ANO", "ANOS", "MES", "MESES", "MARGEM", "RECEITA", "FATURAMENTO", "CMV", "DRE", "DFC", "RESULTADO", "COMPAR"]):
        for m in re.finditer(r"\b(\d{2})\b", txt):
            ano2 = int(m.group(1))
            if 20 <= ano2 <= 99:
                ano = 2000 + ano2
                if ano not in anos:
                    anos.append(ano)
    return anos


def periodo_pertence_a_ano(periodo, ano):
    try:
        ano_p, _ = periodo_chave(periodo)
        return int(ano_p) == int(ano)
    except Exception:
        return False


def meses_mencionados_com_posicao(pergunta):
    """Identifica meses escritos por extenso ou abreviados, preservando ordem na frase."""
    import re
    txt = normalizar_texto(pergunta)
    mapa = {}
    for nome, num in MESES_ORDEM.items():
        mapa[normalizar_texto(nome)] = num
    for num, abrev in MESES_ABREV.items():
        mapa[normalizar_texto(abrev)] = num

    achados = []
    for token, mes_num in mapa.items():
        for m in re.finditer(rf"\b{re.escape(token)}\b", txt):
            achados.append((m.start(), mes_num, token))
    achados = sorted(achados, key=lambda x: x[0])

    # Evita duplicidade MAR/MARCO no mesmo ponto quando ocorrer
    limpos = []
    pos_usadas = set()
    for pos, mes, token in achados:
        if pos not in pos_usadas:
            limpos.append((pos, mes, token))
            pos_usadas.add(pos)
    return limpos


def intervalo_periodos_por_meses(pergunta, periodos_disponiveis):
    """Monta os períodos citados na pergunta.
    Aceita ano inteiro (2025), mês + ano (janeiro de 2025), período curto (JAN/25)
    e intervalos que cruzam ano, como OUT/25 a ABR/26.
    """
    txt = normalizar_texto(pergunta)
    todos = ordenar_periodos([p for p in periodos_disponiveis if p and "/" in str(p)])
    if not todos:
        return []

    anos = anos_mencionados_na_pergunta(pergunta)
    meses = meses_mencionados_com_posicao(pergunta)

    # 0) Mês + ano explícito por extenso/abreviado: "margem de janeiro 2025" ou "margem jan 25".
    # Antes o código pegava o mês mais recente e ignorava o ano.
    if len(meses) == 1 and anos:
        mes = meses[0][1]
        candidatos = [p for p in todos if periodo_chave(p) == (anos[-1], mes)]
        if candidatos:
            return candidatos

    # 0.1) Ano inteiro sem mês: "margem de 2025", "faturamento 2026".
    # Retorna todos os meses daquele(s) ano(s) existentes na base.
    if anos and not meses:
        selecionados = [p for p in todos if any(periodo_pertence_a_ano(p, ano) for ano in anos)]
        if selecionados:
            return ordenar_periodos(selecionados)

    # 1) Se o usuário escreveu períodos explícitos, como OUT/25 a ABR/26
    explicitos = []
    for p in todos:
        formas = [p, p.replace("/", " "), p.replace("/", "-")]
        if any(normalizar_texto(f) in txt for f in formas):
            explicitos.append(p)
    explicitos = ordenar_periodos(explicitos)
    if len(explicitos) >= 2:
        i1, i2 = todos.index(explicitos[0]), todos.index(explicitos[-1])
        if i1 <= i2:
            return todos[i1:i2 + 1]
        return todos[i2:i1 + 1]
    if len(explicitos) == 1:
        return explicitos

    # 2) Se escreveu mês por extenso, como outubro a abril
    meses = meses_mencionados_com_posicao(pergunta)
    if len(meses) >= 2 and any(x in txt for x in [" A ", "ATE", "ATÉ", "ENTRE", "COMPAR", "EVOLU", "VARIAC"]):
        mes_ini = meses[0][1]
        mes_fim = meses[-1][1]
        chaves = [periodo_chave(p) for p in todos]
        candidatos = []

        for i, (ano_i, mes_i) in enumerate(chaves):
            if mes_i != mes_ini:
                continue
            for j in range(i, len(chaves)):
                ano_j, mes_j = chaves[j]
                if mes_j == mes_fim:
                    seq = todos[i:j + 1]
                    # Evita intervalos gigantes por engano
                    if 1 <= len(seq) <= 18:
                        candidatos.append(seq)

        if candidatos:
            # Preferir o intervalo mais curto; em empate, o mais recente
            candidatos = sorted(candidatos, key=lambda s: (len(s), periodo_chave(s[0])), reverse=False)
            menor_tamanho = len(candidatos[0])
            menores = [c for c in candidatos if len(c) == menor_tamanho]
            return sorted(menores, key=lambda s: periodo_chave(s[0]), reverse=True)[0]

    # 3) Um único mês sem ano: tenta o período filtrado; se tiver mais de um, usa o mais recente
    if len(meses) == 1:
        mes = meses[0][1]
        candidatos = [p for p in todos if periodo_chave(p)[1] == mes]
        if candidatos:
            return [ordenar_periodos(candidatos)[-1]]

    # 4) Fallback para a função antiga
    ps = periodos_da_pergunta(pergunta, todos)
    return ps or []


def detectar_intencao_bi(pergunta):
    """Roteador de intenção do Agente de BI.
    A ideia é cadastrar operações de negócio, não frases exatas.
    """
    txt = normalizar_texto(pergunta)

    if any(x in txt for x in ["E SE", "SIMULE", "SIMULAR", "CENARIO", "CENÁRIO", "PROJETAR IMPACTO", "IMPACTO SE"]):
        return "cenario"

    if any(x in txt for x in ["SAUDE FINANCEIRA", "SAÚDE FINANCEIRA", "DIAGNOSTICO", "DIAGNÓSTICO", "NOTA FINANCEIRA", "COMO ESTA A EMPRESA", "COMO ESTÁ A EMPRESA"]):
        return "saude_financeira"

    if any(x in txt for x in ["O QUE IMPACTOU", "MAIOR IMPACTO", "TOP IMPACTOS", "IMPACTOU O RESULTADO", "IMPACTOU O CAIXA", "POR QUE O LUCRO", "PORQUE O LUCRO", "O QUE MUDOU"]):
        return "top_impactos"

    if any(x in txt for x in ["EFICIENCIA", "EFICIÊNCIA", "PROPORCIONAL", "SOBRE A RECEITA", "% DA RECEITA", "PESA NA RECEITA", "CONSUME DA RECEITA"]):
        return "eficiencia"

    if any(x in txt for x in ["MAIORES DESPESAS", "TOP DESPESAS", "RANKING DE DESPESAS", "CONTAS QUE MAIS PESAM", "MAIORES CONTAS", "MAIORES SAIDAS", "MAIORES SAÍDAS"]):
        return "ranking_contas"

    if any(x in txt for x in ["ONDE POSSO ECONOMIZAR", "ECONOMIZAR", "REDUZIR DESPESAS", "DESPESAS CRESCERAM ACIMA", "CRESCEU ACIMA DA RECEITA"]):
        return "inteligencia_despesas"

    if any(x in txt for x in ["PROJECAO", "PROJEÇÃO", "PREVISAO", "PREVISÃO", "FECHAMENTO DO MES", "FECHAMENTO DO MÊS"]):
        return "projecao"

    if "PONTO DE EQUILIBRIO" in txt or "PONTO DE EQUILÍBRIO" in txt or "NECESSIDADE DE CAIXA" in txt:
        return "ponto_equilibrio"

    if "PROJETO" in txt or ("CLIENTE" in txt and any(x in txt for x in ["MARGEM", "MARKUP", "RECEITA", "CMV", "CUSTO", "RENTAVEL", "RENTÁVEL"])):
        return "analise_projetos"

    if any(x in txt for x in ["MARGEM BRUTA", "LUCRO BRUTO", "MARGEM %", "MARGEM PERCENTUAL"]):
        if any(x in txt for x in ["COMPAR", "EVOLU", "VARIAC", "MES A MES", "MÊS A MÊS", "HISTORICO", "HISTÓRICO", "MELHOR", "PIOR"]):
            return "comparativo_indicador"
        return "margem_bruta"

    if any(x in txt for x in ["COMPAR", "EVOLUCAO", "EVOLUÇÃO", "VARIACAO", "VARIAÇÃO", "MES A MES", "MÊS A MÊS", "HISTORICO", "HISTÓRICO", "CONTRA"]):
        if any(x in txt for x in ["RECEITA", "FATURAMENTO", "CMV", "CUSTO", "MARGEM", "RESULTADO", "DRE", "DFC", "CAIXA", "RECEBIMENTO"]):
            return "comparativo_indicador"
        return "comparativo_mensal"

    if any(x in txt for x in ["DETALH", "ABRA", "ABRIR", "PLANOS DE CONTAS", "POR PLANO", "LANÇAMENT", "LANCAMENT"]):
        return "detalhamento"

    if any(x in txt for x in ["RESUMO EXECUTIVO", "ANALISE GERAL", "ANÁLISE GERAL", "DIRETORIA", "RISCO", "OPORTUNIDADE", "EMPRESARIO", "EMPRESÁRIO"]):
        return "resumo_executivo"
    if ("RESULTADO" in txt or "LUCRO" in txt) and "DFC" in txt:
        return "resultado_dfc"
    if ("RESULTADO" in txt or "LUCRO" in txt) and "DRE" in txt:
        return "resultado_dre"
    if any(x in txt for x in ["RECEITA", "FATURAMENTO"]):
        return "receita"
    if any(x in txt for x in ["RECEBIMENTO", "RECEBIMENTOS"]):
        return "recebimento"
    if any(x in txt for x in ["CMV", "CUSTO"]):
        return "cmv"
    if "MARKUP" in txt:
        return "markup_projetos"
    return "consulta_livre"


def localizar_entidade_bi(pergunta):
    """Localiza primeiro Conta de Resultado; se não achar, busca Plano de Contas por aproximação."""
    conta = localizar_conta_resultado_na_pergunta(pergunta)
    if conta:
        return {
            "tipo": "conta_resultado",
            "titulo": conta,
            "conta": conta,
            "planos": [],
        }
    planos = localizar_planos_contas_na_pergunta(pergunta, limite=20)
    if planos:
        return {
            "tipo": "plano_contas",
            "titulo": " + ".join(planos[:3]) + ("..." if len(planos) > 3 else ""),
            "conta": None,
            "planos": planos,
        }
    return {"tipo": None, "titulo": None, "conta": None, "planos": []}


def formatar_df_financeiro(df, colunas_moeda=None, colunas_perc=None):
    out = df.copy()
    colunas_moeda = colunas_moeda or []
    colunas_perc = colunas_perc or []
    for c in colunas_moeda:
        if c in out.columns:
            out[c] = out[c].apply(moeda)
    for c in colunas_perc:
        if c in out.columns:
            out[c] = out[c].apply(perc)
    return out


def montar_comparativo_entidade(entidade, ps):
    if entidade["tipo"] == "conta_resultado":
        resumo = resumo_conta_por_periodo(entidade["conta"], ps)
        dados = confirmadas[
            (confirmadas["CONTA_RESULTADO_NORM"] == normalizar_texto(entidade["conta"])) &
            (confirmadas["PERIODO"].isin(ps))
        ].copy()
    else:
        resumo, dados = resumo_plano_por_periodo(entidade["planos"], ps)

    resumo = calcular_variacao_mensal(resumo, "Valor total")
    resumo = resumo.rename(columns={"Valor total": "Valor"})
    return resumo, dados


def tabela_indicadores_periodos(ps):
    """Monta base financeira por período para o Agente de BI."""
    linhas = []
    ordem_dre = [
        "IMPOSTOS/deduções", "DESPESA COM PESSOAL", "DESPESAS OPERACIONAIS",
        "DESPESAS FINANCEIRAS", "DESPESAS ADMINISTRATIVAS", "DESPESAS COMERCIAIS",
    ]
    ordem_dfc = ordem_dre + ["FORNECEDORES"]
    for p in ps:
        receita = receita_cmv.loc[receita_cmv["PERIODO"] == p, "RECEITA"].sum()
        cmv = receita_cmv.loc[receita_cmv["PERIODO"] == p, "CMV"].sum()
        recebimento = recebimentos.loc[recebimentos["PERIODO"] == p, "RECEBIMENTO"].sum()
        despesas_dre = confirmadas[
            (confirmadas["PERIODO"] == p) &
            (confirmadas["CONTA_RESULTADO_NORM"].isin([normalizar_texto(c) for c in ordem_dre]))
        ]["Valor total"].sum()
        saidas_dfc = confirmadas[
            (confirmadas["PERIODO"] == p) &
            (confirmadas["CONTA_RESULTADO_NORM"].isin([normalizar_texto(c) for c in ordem_dfc]))
        ]["Valor total"].sum()
        margem = receita - cmv
        resultado_dre = margem - despesas_dre
        resultado_dfc = recebimento - saidas_dfc
        linhas.append({
            "PERIODO": p,
            "Receita": receita,
            "CMV": cmv,
            "CMV %": (cmv / receita * 100) if receita else 0,
            "Margem Bruta": margem,
            "Margem Bruta %": (margem / receita * 100) if receita else 0,
            "Despesas DRE": despesas_dre,
            "Resultado DRE": resultado_dre,
            "Resultado DRE %": (resultado_dre / receita * 100) if receita else 0,
            "Recebimento": recebimento,
            "Saídas DFC": saidas_dfc,
            "Resultado DFC": resultado_dfc,
            "Resultado DFC %": (resultado_dfc / recebimento * 100) if recebimento else 0,
        })
    df = pd.DataFrame(linhas)
    if not df.empty:
        df["ORDEM"] = df["PERIODO"].apply(lambda p: ps.index(p) if p in ps else 999)
        df = df.sort_values("ORDEM").drop(columns=["ORDEM"])
    return df


def detectar_indicador_financeiro(pergunta):
    txt = normalizar_texto(pergunta)
    if "MARGEM BRUTA" in txt or "LUCRO BRUTO" in txt or "MARGEM" in txt:
        return "Margem Bruta"
    if "RESULTADO" in txt and "DFC" in txt or "CAIXA" in txt and "RESULTADO" in txt:
        return "Resultado DFC"
    if "RESULTADO" in txt and "DRE" in txt or "LUCRO" in txt and "DRE" in txt:
        return "Resultado DRE"
    if "RECEBIMENTO" in txt:
        return "Recebimento"
    if "CMV" in txt or "CUSTO" in txt:
        return "CMV"
    if "RECEITA" in txt or "FATURAMENTO" in txt:
        return "Receita"
    return "Margem Bruta"


def resposta_comparativo_indicador(pergunta, ps):
    indicador = detectar_indicador_financeiro(pergunta)
    base = tabela_indicadores_periodos(ps)
    resultado = {
        "tipo": "bi", "intencao": "comparativo_indicador", "titulo": f"Comparativo — {indicador}",
        "texto": "", "metricas": [], "tabelas": [], "graficos": []
    }
    if base.empty or indicador not in base.columns:
        resultado["texto"] = "Não encontrei dados para montar esse comparativo."
        return resultado

    tabela = base[["PERIODO", indicador]].rename(columns={indicador: "Valor"}).copy()
    tabela = calcular_variacao_mensal(tabela, "Valor")
    total = tabela["Valor"].sum()
    media = tabela["Valor"].mean() if len(tabela) else 0
    maior = tabela.sort_values("Valor", ascending=False).iloc[0]
    menor = tabela.sort_values("Valor", ascending=True).iloc[0]
    var_total = tabela.iloc[-1]["Valor"] - tabela.iloc[0]["Valor"] if len(tabela) >= 2 else 0
    var_pct = var_total / tabela.iloc[0]["Valor"] * 100 if len(tabela) >= 2 and tabela.iloc[0]["Valor"] else 0
    sentido = "evolução" if var_total > 0 else "queda" if var_total < 0 else "estabilidade"

    tabela_fmt = formatar_df_financeiro(
        tabela[["PERIODO", "Valor", "Variação R$", "Variação %", "Tendência"]],
        colunas_moeda=["Valor", "Variação R$"], colunas_perc=["Variação %"]
    )

    extra = ""
    if indicador == "Margem Bruta":
        extra_df = base[["PERIODO", "Receita", "CMV", "CMV %", "Margem Bruta", "Margem Bruta %"]].copy()
        extra_fmt = formatar_df_financeiro(extra_df, colunas_moeda=["Receita", "CMV", "Margem Bruta"], colunas_perc=["CMV %", "Margem Bruta %"])
        resultado["tabelas"].append(("Margem Bruta aberta por Receita e CMV", extra_fmt))
        extra = " A margem bruta deve ser avaliada junto com o CMV %, pois aumento de receita sem ganho de margem pode indicar desconto, custo elevado ou mix menos rentável."

    resultado["metricas"] = [
        ("Total", moeda(total)),
        ("Média mensal", moeda(media)),
        ("Maior mês", f"{maior['PERIODO']} | {moeda(maior['Valor'])}"),
        ("Menor mês", f"{menor['PERIODO']} | {moeda(menor['Valor'])}"),
    ]
    resultado["texto"] = (
        f"Período analisado: **{', '.join(ps)}**. Do primeiro para o último mês houve **{sentido}** "
        f"de **{moeda(abs(var_total))}** ({perc(var_pct)}).{extra}"
    )
    resultado["tabelas"].insert(0, ("Evolução mês a mês", tabela_fmt))
    resultado["graficos"].append((f"Evolução — {indicador}", tabela[["PERIODO", "Valor"]], "linha"))
    return resultado


def resposta_margem_bruta(pergunta, ps):
    base = tabela_indicadores_periodos(ps)
    resultado = {"tipo": "bi", "intencao": "margem_bruta", "titulo": "Margem Bruta", "texto": "", "metricas": [], "tabelas": [], "graficos": []}
    if base.empty:
        resultado["texto"] = "Não encontrei dados de receita e CMV para calcular margem bruta."
        return resultado
    receita = base["Receita"].sum()
    cmv = base["CMV"].sum()
    margem = receita - cmv
    margem_pct = margem / receita * 100 if receita else 0
    cmv_pct = cmv / receita * 100 if receita else 0
    resultado["metricas"] = [
        ("Receita", moeda(receita)), ("CMV", moeda(cmv)), ("Margem Bruta", moeda(margem)), ("Margem Bruta %", perc(margem_pct))
    ]
    leitura = "Margem saudável." if margem_pct >= 35 else "Margem intermediária; vale revisar mix, custo e descontos." if margem_pct >= 20 else "Margem baixa; atenção para precificação, custo e composição de vendas."
    resultado["texto"] = f"No período **{', '.join(ps)}**, o CMV representou **{perc(cmv_pct)}** da receita. **Leitura:** {leitura}"
    tabela = base[["PERIODO", "Receita", "CMV", "CMV %", "Margem Bruta", "Margem Bruta %"]].copy()
    tabela_fmt = formatar_df_financeiro(tabela, colunas_moeda=["Receita", "CMV", "Margem Bruta"], colunas_perc=["CMV %", "Margem Bruta %"])
    resultado["tabelas"].append(("Margem por período", tabela_fmt))
    resultado["graficos"].append(("Margem Bruta mensal", base[["PERIODO", "Margem Bruta"]].rename(columns={"Margem Bruta": "Valor"}), "linha"))
    return resultado


def resposta_top_impactos(pergunta, ps):
    resultado = {"tipo":"bi", "intencao":"top_impactos", "titulo":"Top impactos no resultado", "texto":"", "metricas":[], "tabelas":[], "graficos":[]}
    if len(ps) < 2:
        resultado["texto"] = "Para analisar impacto, informe dois meses ou um intervalo. Exemplo: **O que impactou o resultado de março para abril?**"
        return resultado
    p1, p2 = ps[-2], ps[-1]
    contas_dre = ["IMPOSTOS/deduções", "DESPESA COM PESSOAL", "DESPESAS OPERACIONAIS", "DESPESAS FINANCEIRAS", "DESPESAS ADMINISTRATIVAS", "DESPESAS COMERCIAIS"]
    d1, d2 = calcular_dre_periodo(p1), calcular_dre_periodo(p2)
    linhas = []
    linhas.append({"Item":"Receita", p1:d1["receita"], p2:d2["receita"], "Variação":d2["receita"]-d1["receita"], "Impacto no resultado":d2["receita"]-d1["receita"]})
    linhas.append({"Item":"CMV", p1:d1["cmv"], p2:d2["cmv"], "Variação":d2["cmv"]-d1["cmv"], "Impacto no resultado":-(d2["cmv"]-d1["cmv"])})
    for c in contas_dre:
        v1, v2 = d1["despesas"].get(c,0), d2["despesas"].get(c,0)
        linhas.append({"Item":c, p1:v1, p2:v2, "Variação":v2-v1, "Impacto no resultado":-(v2-v1)})
    df = pd.DataFrame(linhas)
    df["Impacto absoluto"] = df["Impacto no resultado"].abs()
    df = df.sort_values("Impacto absoluto", ascending=False).drop(columns=["Impacto absoluto"])
    resultado_dif = d2["resultado_dre"] - d1["resultado_dre"]
    resultado["metricas"] = [("Resultado DRE anterior", moeda(d1["resultado_dre"])), ("Resultado DRE atual", moeda(d2["resultado_dre"])), ("Variação do resultado", moeda(resultado_dif)), ("Período", f"{p1} → {p2}")]
    sentido = "melhorou" if resultado_dif > 0 else "piorou" if resultado_dif < 0 else "ficou estável"
    resultado["texto"] = f"De **{p1}** para **{p2}**, o resultado DRE **{sentido}** em **{moeda(abs(resultado_dif))}**. A tabela mostra o impacto de cada linha no resultado."
    df_fmt = formatar_df_financeiro(df, colunas_moeda=[p1, p2, "Variação", "Impacto no resultado"])
    resultado["tabelas"].append(("Impactos no resultado", df_fmt))
    graf = df[["Item", "Impacto no resultado"]].rename(columns={"Item":"PERIODO", "Impacto no resultado":"Valor"}).head(10)
    resultado["graficos"].append(("Principais impactos", graf, "barra"))
    return resultado


def resposta_eficiencia(pergunta, ps):
    resultado = {"tipo":"bi", "intencao":"eficiencia", "titulo":"Análise de eficiência", "texto":"", "metricas":[], "tabelas":[], "graficos":[]}
    entidade = localizar_entidade_bi(pergunta)
    base = tabela_indicadores_periodos(ps)
    if base.empty:
        resultado["texto"] = "Não encontrei dados para análise de eficiência."
        return resultado
    if entidade["tipo"]:
        resumo, _ = montar_comparativo_entidade(entidade, ps)
        df = base[["PERIODO", "Receita", "Recebimento"]].merge(resumo[["PERIODO", "Valor"]], on="PERIODO", how="left").fillna({"Valor":0})
        df["% Receita"] = np.where(df["Receita"] != 0, df["Valor"] / df["Receita"] * 100, 0)
        df["% Recebimento"] = np.where(df["Recebimento"] != 0, df["Valor"] / df["Recebimento"] * 100, 0)
        titulo = entidade["titulo"]
    else:
        df = base[["PERIODO", "Receita", "CMV", "CMV %", "Margem Bruta %", "Despesas DRE", "Resultado DRE %"]].copy()
        titulo = "Indicadores principais"
    resultado["titulo"] = f"Eficiência — {titulo}"
    if entidade["tipo"]:
        media = df["% Receita"].mean()
        resultado["metricas"] = [("Média sobre receita", perc(media)), ("Maior peso", perc(df["% Receita"].max())), ("Menor peso", perc(df["% Receita"].min())), ("Período", ", ".join(ps))]
        resultado["texto"] = "Quanto menor o percentual sobre receita, maior tende a ser a eficiência operacional dessa conta, desde que não haja perda de qualidade ou capacidade produtiva."
        df_fmt = formatar_df_financeiro(df, colunas_moeda=["Receita", "Recebimento", "Valor"], colunas_perc=["% Receita", "% Recebimento"])
        resultado["tabelas"].append(("Peso mensal da conta", df_fmt))
        resultado["graficos"].append(("% da Receita", df[["PERIODO", "% Receita"]].rename(columns={"% Receita":"Valor"}), "linha"))
    else:
        df_fmt = formatar_df_financeiro(df, colunas_moeda=["Receita", "CMV", "Despesas DRE"], colunas_perc=["CMV %", "Margem Bruta %", "Resultado DRE %"])
        resultado["texto"] = "A eficiência deve ser lida pela combinação de CMV %, Margem Bruta %, Despesas sobre receita e Resultado DRE %."
        resultado["tabelas"].append(("Eficiência por mês", df_fmt))
        resultado["graficos"].append(("Margem Bruta %", df[["PERIODO", "Margem Bruta %"]].rename(columns={"Margem Bruta %":"Valor"}), "linha"))
    return resultado


def resposta_ranking_contas(pergunta, ps):
    resultado = {"tipo":"bi", "intencao":"ranking_contas", "titulo":"Ranking de despesas/contas", "texto":"", "metricas":[], "tabelas":[], "graficos":[]}
    txt = normalizar_texto(pergunta)
    dados = confirmadas[confirmadas["PERIODO"].isin(ps)].copy()
    if dados.empty:
        resultado["texto"] = "Não encontrei lançamentos no período selecionado."
        return resultado
    if "PLANO" in txt or "PLANOS" in txt or "DESPESA" in txt:
        agrup = dados.groupby("Plano de contas", as_index=False)["Valor total"].sum().sort_values("Valor total", ascending=False).head(20)
        agrup = agrup.rename(columns={"Plano de contas":"Conta", "Valor total":"Valor"})
    else:
        agrup = dados.groupby("CONTA_RESULTADO", as_index=False)["Valor total"].sum().sort_values("Valor total", ascending=False).head(20)
        agrup = agrup.rename(columns={"CONTA_RESULTADO":"Conta", "Valor total":"Valor"})
    total = agrup["Valor"].sum()
    agrup["% sobre ranking"] = np.where(total != 0, agrup["Valor"] / total * 100, 0)
    resultado["metricas"] = [("Total top contas", moeda(total)), ("Maior conta", str(agrup.iloc[0]["Conta"])), ("Valor maior conta", moeda(agrup.iloc[0]["Valor"])), ("Período", ", ".join(ps))]
    resultado["texto"] = "Esse ranking ajuda a identificar onde estão os maiores blocos de gasto e onde a gestão deve olhar primeiro."
    agrup_fmt = formatar_df_financeiro(agrup, colunas_moeda=["Valor"], colunas_perc=["% sobre ranking"])
    resultado["tabelas"].append(("Top contas", agrup_fmt))
    resultado["graficos"].append(("Top contas", agrup.head(10).rename(columns={"Conta":"PERIODO"})[["PERIODO", "Valor"]], "barra"))
    return resultado


def resposta_inteligencia_despesas(pergunta, ps):
    resultado = {"tipo":"bi", "intencao":"inteligencia_despesas", "titulo":"Inteligência de despesas", "texto":"", "metricas":[], "tabelas":[], "graficos":[]}
    if len(ps) < 2:
        resultado["texto"] = "Para analisar economia, selecione ou informe pelo menos dois meses. Exemplo: **Onde posso economizar de janeiro a abril?**"
        return resultado
    dados = confirmadas[confirmadas["PERIODO"].isin(ps)].copy()
    if dados.empty:
        resultado["texto"] = "Não encontrei despesas no período."
        return resultado
    pivot = pd.pivot_table(dados, values="Valor total", index="Plano de contas", columns="PERIODO", aggfunc="sum", fill_value=0)
    for p in ps:
        if p not in pivot.columns:
            pivot[p] = 0
    pivot = pivot[ps]
    pivot["Total"] = pivot[ps].sum(axis=1)
    pivot["Variação início/fim"] = pivot[ps[-1]] - pivot[ps[0]]
    pivot["Variação %"] = np.where(pivot[ps[0]] != 0, pivot["Variação início/fim"] / pivot[ps[0]] * 100, 0)
    df = pivot.reset_index().sort_values(["Variação início/fim", "Total"], ascending=False).head(20)
    potencial = df[df["Variação início/fim"] > 0]["Variação início/fim"].sum()
    resultado["metricas"] = [("Aumento mapeado", moeda(potencial)), ("Contas analisadas", dados["Plano de contas"].nunique()), ("Maior alta", str(df.iloc[0]["Plano de contas"])), ("Período", f"{ps[0]} → {ps[-1]}")]
    resultado["texto"] = "Priorize contas com alta recorrente e crescimento acima da receita. Nem toda alta é problema, mas toda alta relevante merece explicação."
    df_fmt = formatar_df_financeiro(df, colunas_moeda=ps+["Total", "Variação início/fim"], colunas_perc=["Variação %"])
    resultado["tabelas"].append(("Contas com maior aumento", df_fmt))
    resultado["graficos"].append(("Maiores altas", df[["Plano de contas", "Variação início/fim"]].rename(columns={"Plano de contas":"PERIODO", "Variação início/fim":"Valor"}).head(10), "barra"))
    return resultado


def resposta_saude_financeira(pergunta, ps):
    resultado = {"tipo":"bi", "intencao":"saude_financeira", "titulo":"Diagnóstico de saúde financeira", "texto":"", "metricas":[], "tabelas":[], "graficos":[]}
    base = tabela_indicadores_periodos(ps)
    if base.empty:
        resultado["texto"] = "Não encontrei dados para diagnóstico."
        return resultado
    receita = base["Receita"].sum(); cmv = base["CMV"].sum(); margem = receita-cmv
    receb = base["Recebimento"].sum(); saidas = base["Saídas DFC"].sum(); resultado_dfc = receb-saidas
    despesas_dre = base["Despesas DRE"].sum(); resultado_dre = margem-despesas_dre
    margem_pct = margem/receita*100 if receita else 0
    cmv_pct = cmv/receita*100 if receita else 0
    dre_pct = resultado_dre/receita*100 if receita else 0
    caixa_pct = resultado_dfc/receb*100 if receb else 0
    score = 0
    score += 2.5 if margem_pct >= 35 else 1.5 if margem_pct >= 20 else 0.5
    score += 2.0 if dre_pct >= 10 else 1.0 if dre_pct >= 0 else 0
    score += 2.0 if caixa_pct >= 10 else 1.0 if caixa_pct >= 0 else 0
    score += 1.5 if cmv_pct <= 65 else 0.8 if cmv_pct <= 80 else 0.2
    score += 2.0 if receita > 0 and receb > 0 else 0.5
    pontos = []
    if margem_pct < 25: pontos.append("Margem bruta baixa")
    if dre_pct < 0: pontos.append("Resultado DRE negativo")
    if caixa_pct < 0: pontos.append("Resultado de caixa negativo")
    if cmv_pct > 75: pontos.append("CMV alto sobre receita")
    if not pontos: pontos.append("Sem alerta crítico pelos indicadores principais")
    resultado["metricas"] = [("Nota financeira", f"{score:.1f}/10"), ("Margem Bruta %", perc(margem_pct)), ("Resultado DRE %", perc(dre_pct)), ("Resultado Caixa %", perc(caixa_pct))]
    resultado["texto"] = "**Pontos de atenção:** " + "; ".join(pontos) + ". Use esse diagnóstico como triagem executiva; a decisão final deve considerar sazonalidade e lançamentos extraordinários."
    df = pd.DataFrame([
        {"Indicador":"Receita", "Valor":receita}, {"Indicador":"CMV", "Valor":cmv}, {"Indicador":"Margem Bruta", "Valor":margem},
        {"Indicador":"Despesas DRE", "Valor":despesas_dre}, {"Indicador":"Resultado DRE", "Valor":resultado_dre},
        {"Indicador":"Recebimento", "Valor":receb}, {"Indicador":"Saídas DFC", "Valor":saidas}, {"Indicador":"Resultado DFC", "Valor":resultado_dfc},
    ])
    df_fmt = formatar_df_financeiro(df, colunas_moeda=["Valor"])
    resultado["tabelas"].append(("Resumo financeiro", df_fmt))
    return resultado


def resposta_cenario(pergunta, ps):
    import re
    resultado = {"tipo":"bi", "intencao":"cenario", "titulo":"Simulação de cenário", "texto":"", "metricas":[], "tabelas":[], "graficos":[]}
    base = tabela_indicadores_periodos(ps[-1:])
    if base.empty:
        resultado["texto"] = "Não encontrei um mês-base para simular. Informe um mês, por exemplo: **E se reduzir pessoal em 10% em ABR/25?**"
        return resultado
    p = base.iloc[0]["PERIODO"]
    pct_match = re.search(r"(\d+(?:[\.,]\d+)?)\s*%", pergunta)
    pct = float(pct_match.group(1).replace(",", ".")) if pct_match else 10.0
    txt = normalizar_texto(pergunta)
    direcao = -1 if any(x in txt for x in ["REDUZ", "CAIR", "DIMINUI", "CORT"] ) else 1
    d = calcular_dre_periodo(p)
    receita = d["receita"]; cmv = d["cmv"]; despesas = sum(d["despesas"].values()); resultado_atual = d["resultado_dre"]
    conta = localizar_conta_resultado_na_pergunta(pergunta)
    receita_n, cmv_n, despesas_n = receita, cmv, despesas
    alvo = ""
    impacto = 0
    if "RECEITA" in txt or "FATURAMENTO" in txt:
        alvo = "Receita"; receita_n = receita * (1 + direcao * pct/100); impacto = receita_n - receita
    elif "CMV" in txt or "CUSTO" in txt:
        alvo = "CMV"; cmv_n = cmv * (1 + direcao * pct/100); impacto = -(cmv_n - cmv)
    elif conta:
        alvo = conta; valor_conta = d["despesas"].get(conta, 0); novo_valor = valor_conta * (1 + direcao * pct/100); despesas_n = despesas - valor_conta + novo_valor; impacto = -(novo_valor - valor_conta)
    else:
        alvo = "Despesas DRE"; despesas_n = despesas * (1 + direcao * pct/100); impacto = -(despesas_n - despesas)
    resultado_novo = receita_n - cmv_n - despesas_n
    df = pd.DataFrame([
        {"Cenário":"Atual", "Receita":receita, "CMV":cmv, "Despesas DRE":despesas, "Resultado DRE":resultado_atual},
        {"Cenário":"Simulado", "Receita":receita_n, "CMV":cmv_n, "Despesas DRE":despesas_n, "Resultado DRE":resultado_novo},
    ])
    df["Margem Resultado %"] = np.where(df["Receita"] != 0, df["Resultado DRE"] / df["Receita"] * 100, 0)
    resultado["metricas"] = [("Mês-base", p), ("Alvo", alvo), ("Variação simulada", perc(direcao*pct)), ("Impacto estimado", moeda(impacto))]
    resultado["texto"] = f"Simulação sobre **{p}**. Resultado DRE sairia de **{moeda(resultado_atual)}** para **{moeda(resultado_novo)}**."
    df_fmt = formatar_df_financeiro(df, colunas_moeda=["Receita", "CMV", "Despesas DRE", "Resultado DRE"], colunas_perc=["Margem Resultado %"])
    resultado["tabelas"].append(("Cenário atual x simulado", df_fmt))
    return resultado


def resposta_ponto_equilibrio_bi(pergunta, ps):
    resultado = {"tipo":"bi", "intencao":"ponto_equilibrio", "titulo":"Ponto de Equilíbrio / Necessidade de Caixa", "texto":"", "metricas":[], "tabelas":[], "graficos":[]}
    ordem_pe = ["DESPESA COM PESSOAL", "AJUSTE", "DESPESAS OPERACIONAIS", "APLICAÇÃO", "DESPESAS FINANCEIRAS", "DESPESAS ADMINISTRATIVAS", "DESPESAS COMERCIAIS", "IMPOSTOS/deduções", "FORNECEDORES"]
    qtd = len(ps) if ps else 1
    linhas = []
    for conta in ordem_pe:
        total = confirmadas[(confirmadas["CONTA_RESULTADO_NORM"] == normalizar_texto(conta)) & (confirmadas["PERIODO"].isin(ps))]["Valor total"].sum()
        linhas.append({"Conta":conta, "Total no período":total, "Média mensal":total/qtd if qtd else 0})
    df = pd.DataFrame(linhas).sort_values("Média mensal", ascending=False)
    necessidade_mes = df["Média mensal"].sum(); necessidade_semana = necessidade_mes/4; necessidade_dia = necessidade_semana/7
    df["% sobre necessidade"] = np.where(necessidade_mes != 0, df["Média mensal"] / necessidade_mes * 100, 0)
    resultado["metricas"] = [("Necessidade mês", moeda(necessidade_mes)), ("Necessidade semana", moeda(necessidade_semana)), ("Necessidade dia", moeda(necessidade_dia)), ("Meses", qtd)]
    resultado["texto"] = "Essa é a média mensal de saídas usada como referência de necessidade de caixa/ponto de equilíbrio operacional."
    df_fmt = formatar_df_financeiro(df, colunas_moeda=["Total no período", "Média mensal"], colunas_perc=["% sobre necessidade"])
    resultado["tabelas"].append(("Composição da necessidade", df_fmt))
    resultado["graficos"].append(("Composição", df.rename(columns={"Conta":"PERIODO", "Média mensal":"Valor"})[["PERIODO", "Valor"]].head(10), "barra"))
    return resultado


def resposta_projecao(pergunta, ps):
    resultado = {"tipo":"bi", "intencao":"projecao", "titulo":"Projeção de fechamento", "texto":"", "metricas":[], "tabelas":[], "graficos":[]}
    # Como a base está agregada por mês, sem dia realizado, usamos média dos meses selecionados como referência simples.
    base = tabela_indicadores_periodos(ps)
    if base.empty:
        resultado["texto"] = "Não encontrei dados para projeção."
        return resultado
    medias = base[["Receita", "CMV", "Margem Bruta", "Resultado DRE", "Recebimento", "Resultado DFC"]].mean(numeric_only=True)
    df = pd.DataFrame([{"Indicador":k, "Projeção simples pela média mensal":v} for k, v in medias.items()])
    resultado["metricas"] = [("Base", ", ".join(ps)), ("Receita média", moeda(medias.get("Receita",0))), ("Resultado DRE médio", moeda(medias.get("Resultado DRE",0))), ("Resultado DFC médio", moeda(medias.get("Resultado DFC",0)))]
    resultado["texto"] = "Projeção simples baseada na média mensal dos períodos selecionados. Para previsão diária real, a base precisa ter dados por dia útil realizado."
    df_fmt = formatar_df_financeiro(df, colunas_moeda=["Projeção simples pela média mensal"])
    resultado["tabelas"].append(("Projeção pela média", df_fmt))
    return resultado


def executar_agente_bi(pergunta, periodos_contexto):
    """Agente de BI sem IA externa: interpreta intenção, extrai parâmetros e calcula com Pandas."""
    periodos_disponiveis = ordenar_periodos(sorted(
        set(receita_cmv["PERIODO"].dropna()) |
        set(recebimentos["PERIODO"].dropna()) |
        set(confirmadas["PERIODO"].dropna()) |
        set(projetos_chat["PERIODO"].dropna() if not projetos_chat.empty else [])
    ))
    intencao = detectar_intencao_bi(pergunta)
    ps = intervalo_periodos_por_meses(pergunta, periodos_disponiveis)
    if not ps:
        ps = periodos_contexto if periodos_contexto else periodos_disponiveis
    ps = ordenar_periodos([p for p in ps if p in periodos_disponiveis])

    resultado = {
        "tipo": "bi",
        "intencao": intencao,
        "titulo": "Consulta Gerencial",
        "texto": "",
        "metricas": [],
        "tabelas": [],
        "graficos": [],
    }

    if intencao == "comparativo_indicador":
        return resposta_comparativo_indicador(pergunta, ps)

    if intencao == "margem_bruta":
        return resposta_margem_bruta(pergunta, ps)

    if intencao == "top_impactos":
        return resposta_top_impactos(pergunta, ps)

    if intencao == "eficiencia":
        return resposta_eficiencia(pergunta, ps)

    if intencao == "ranking_contas":
        return resposta_ranking_contas(pergunta, ps)

    if intencao == "inteligencia_despesas":
        return resposta_inteligencia_despesas(pergunta, ps)

    if intencao == "saude_financeira":
        return resposta_saude_financeira(pergunta, ps)

    if intencao == "cenario":
        return resposta_cenario(pergunta, ps)

    if intencao == "ponto_equilibrio":
        return resposta_ponto_equilibrio_bi(pergunta, ps)

    if intencao == "projecao":
        return resposta_projecao(pergunta, ps)

    if intencao == "comparativo_mensal":
        entidade = localizar_entidade_bi(pergunta)
        if not entidade["tipo"]:
            resultado["titulo"] = "Não localizei a despesa ou plano de contas"
            resultado["texto"] = "Tente perguntar, por exemplo: **Compare despesas com pessoal de outubro até abril** ou **Compare energia de OUT/25 a ABR/26**."
            return resultado

        resumo, dados = montar_comparativo_entidade(entidade, ps)
        total = resumo["Valor"].sum()
        media = resumo["Valor"].mean() if len(resumo) else 0
        maior = resumo.sort_values("Valor", ascending=False).iloc[0] if not resumo.empty else None
        menor = resumo.sort_values("Valor", ascending=True).iloc[0] if not resumo.empty else None

        variacao_total = 0
        variacao_pct = 0
        sentido = "estabilidade"
        if len(resumo) >= 2:
            ini = resumo.iloc[0]["Valor"]
            fim = resumo.iloc[-1]["Valor"]
            variacao_total = fim - ini
            variacao_pct = variacao_total / ini * 100 if ini else 0
            sentido = "evolução" if variacao_total > 0 else "queda" if variacao_total < 0 else "estabilidade"

        tabela = resumo.copy()
        tabela["Variação R$"] = tabela["Variação R$"]
        tabela["Variação %"] = tabela["Variação %"]
        tabela_fmt = formatar_df_financeiro(
            tabela[["PERIODO", "Valor", "Variação R$", "Variação %", "Tendência"]],
            colunas_moeda=["Valor", "Variação R$"],
            colunas_perc=["Variação %"]
        )

        resultado["titulo"] = f"Comparativo mensal — {entidade['titulo']}"
        resultado["metricas"] = [
            ("Total no período", moeda(total)),
            ("Média mensal", moeda(media)),
            ("Maior mês", f"{maior['PERIODO']} | {moeda(maior['Valor'])}" if maior is not None else "-"),
            ("Menor mês", f"{menor['PERIODO']} | {moeda(menor['Valor'])}" if menor is not None else "-"),
        ]
        resultado["texto"] = (
            f"Período analisado: **{', '.join(ps)}**. "
            f"Do primeiro para o último mês houve **{sentido}** de **{moeda(abs(variacao_total))}** ({perc(variacao_pct)}). "
            f"A leitura deve considerar se a variação representa ganho de eficiência, sazonalidade ou postergação/acúmulo de lançamentos."
        )
        resultado["tabelas"].append(("Evolução mês a mês", tabela_fmt))
        resultado["graficos"].append(("Evolução mensal", resumo[["PERIODO", "Valor"]].copy(), "linha"))

        if not dados.empty:
            por_plano = dados.groupby("Plano de contas", as_index=False)["Valor total"].sum().sort_values("Valor total", ascending=False).head(15)
            por_plano = por_plano.rename(columns={"Valor total": "Valor"})
            por_plano_fmt = formatar_df_financeiro(por_plano, colunas_moeda=["Valor"])
            resultado["tabelas"].append(("Principais planos de contas dentro da consulta", por_plano_fmt))
        return resultado

    if intencao == "detalhamento":
        entidade = localizar_entidade_bi(pergunta)
        if not entidade["tipo"]:
            resultado["titulo"] = "Não localizei a conta para detalhar"
            resultado["texto"] = "Tente perguntar: **Detalhe despesas com pessoal**, **Detalhe energia** ou **Detalhe aluguel de janeiro a março**."
            return resultado

        if entidade["tipo"] == "conta_resultado":
            dados = confirmadas[
                (confirmadas["CONTA_RESULTADO_NORM"] == normalizar_texto(entidade["conta"])) &
                (confirmadas["PERIODO"].isin(ps))
            ].copy()
        else:
            dados = confirmadas[
                (confirmadas["PLANO_NORM"].isin([normalizar_texto(p) for p in entidade["planos"]])) &
                (confirmadas["PERIODO"].isin(ps))
            ].copy()

        if dados.empty:
            resultado["titulo"] = f"Sem lançamentos — {entidade['titulo']}"
            resultado["texto"] = f"Não encontrei lançamentos para **{entidade['titulo']}** em **{', '.join(ps)}**."
            return resultado

        resumo = dados.groupby("Plano de contas", as_index=False).agg(Qtd=("Valor total", "count"), Valor=("Valor total", "sum")).sort_values("Valor", ascending=False)
        total = resumo["Valor"].sum()
        resumo["% sobre total"] = np.where(total != 0, resumo["Valor"] / total * 100, 0)
        resumo_fmt = formatar_df_financeiro(resumo, colunas_moeda=["Valor"], colunas_perc=["% sobre total"])

        mensal = dados.groupby("PERIODO", as_index=False)["Valor total"].sum()
        todos = pd.DataFrame({"PERIODO": ps})
        mensal = todos.merge(mensal, on="PERIODO", how="left").fillna({"Valor total": 0})
        mensal = calcular_variacao_mensal(mensal.rename(columns={"Valor total": "Valor"}), "Valor")
        mensal_fmt = formatar_df_financeiro(mensal[["PERIODO", "Valor", "Variação R$", "Variação %", "Tendência"]], colunas_moeda=["Valor", "Variação R$"], colunas_perc=["Variação %"])

        desc = dados.groupby(["Plano de contas", "Descrição"], as_index=False).agg(Qtd=("Valor total", "count"), Valor=("Valor total", "sum")).sort_values("Valor", ascending=False).head(50)
        desc_fmt = formatar_df_financeiro(desc, colunas_moeda=["Valor"])

        resultado["titulo"] = f"Detalhamento — {entidade['titulo']}"
        resultado["metricas"] = [
            ("Total encontrado", moeda(total)),
            ("Qtd. lançamentos", f"{len(dados):,}".replace(",", ".")),
            ("Planos encontrados", resumo["Plano de contas"].nunique()),
            ("Período", ", ".join(ps)),
        ]
        resultado["texto"] = "Abaixo está a abertura por plano de contas, a evolução mensal e os principais lançamentos/descrições encontrados."
        resultado["tabelas"].append(("Resumo por plano de contas", resumo_fmt))
        resultado["tabelas"].append(("Evolução mensal", mensal_fmt))
        resultado["tabelas"].append(("Detalhamento por descrição", desc_fmt))
        resultado["graficos"].append(("Evolução mensal", mensal[["PERIODO", "Valor"]].copy(), "barra"))
        return resultado

    if intencao == "analise_projetos":
        texto = responder_analise_projetos(pergunta, periodos_disponiveis)
        resultado["titulo"] = "Análise de Projetos"
        resultado["texto"] = texto
        return resultado

    # Para demais intenções, usa as rotas objetivas já existentes.
    resultado["titulo"] = "Resposta gerencial"
    resultado["texto"] = responder_pergunta_gerencial(pergunta)
    return resultado


def renderizar_resposta_bi(resultado, chave_base="resposta"):
    if isinstance(resultado, str):
        st.markdown(resultado)
        return

    st.markdown(f"### {resultado.get('titulo', 'Resposta')}")

    metricas = resultado.get("metricas", [])
    if metricas:
        cols = st.columns(min(4, len(metricas)))
        for i, (nome, valor) in enumerate(metricas):
            cols[i % len(cols)].metric(str(nome), str(valor))

    texto = resultado.get("texto", "")
    if texto:
        st.markdown(texto)

    for idx_grafico, (titulo, dados, tipo) in enumerate(resultado.get("graficos", [])):
        if isinstance(dados, pd.DataFrame) and not dados.empty and "PERIODO" in dados.columns:
            st.markdown(f"**{titulo}**")
            if tipo == "linha":
                fig = px.line(dados, x="PERIODO", y=dados.columns[-1], markers=True, title=titulo)
            else:
                fig = px.bar(dados, x="PERIODO", y=dados.columns[-1], title=titulo)
            fig.update_layout(xaxis_title="Mês", yaxis_title="Valor")
            st.plotly_chart(fig, use_container_width=True, key=f"plotly_bi_{chave_base}_{idx_grafico}")

    for idx_tabela, (titulo, tabela) in enumerate(resultado.get("tabelas", [])):
        st.markdown(f"**{titulo}**")
        st.dataframe(tabela, use_container_width=True, hide_index=True, key=f"df_bi_{chave_base}_{idx_tabela}")


periodos = ordenar_periodos(sorted(set(receita_cmv["PERIODO"].dropna()) | set(recebimentos["PERIODO"].dropna()) | set(confirmadas["PERIODO"].dropna()) | set(atrasadas["PERIODO"].dropna())))
periodos = [p for p in periodos if p and p != "/"]

# ============================================================
# FILTRO GLOBAL DE PERÍODO
# Esse filtro conversa com DRE, DFC, Observações e Ponto de Equilíbrio.
# ============================================================

# Filtro em formulário: alterações só são aplicadas ao clicar em Atualizar filtros.
# Isso reduz reruns desnecessários no Streamlit durante a seleção.
periodos_disponiveis = periodos.copy()

def _ano_do_periodo(p):
    try:
        return 2000 + int(str(p).split("/")[-1])
    except Exception:
        return None

anos_disponiveis = sorted({a for a in (_ano_do_periodo(p) for p in periodos_disponiveis) if a is not None})
if not anos_disponiveis:
    st.error("Não encontrei anos válidos na base para montar o filtro.")
    st.stop()

if "filtro_ano_aplicado" not in st.session_state:
    st.session_state["filtro_ano_aplicado"] = max(anos_disponiveis)
if st.session_state["filtro_ano_aplicado"] not in anos_disponiveis:
    st.session_state["filtro_ano_aplicado"] = max(anos_disponiveis)
if "filtro_meses_aplicados" not in st.session_state:
    st.session_state["filtro_meses_aplicados"] = list(range(1, 13))

st.sidebar.markdown("### Período")
st.sidebar.markdown('<div class="filter-caption">Escolha o ano e marque os meses. O dashboard só recalcula quando você confirmar.</div>', unsafe_allow_html=True)

with st.sidebar.form("form_filtro_periodo", clear_on_submit=False):
    ano_atual = st.session_state["filtro_ano_aplicado"]
    ano_sel = st.selectbox(
        "Ano",
        options=anos_disponiveis,
        index=anos_disponiveis.index(ano_atual),
        key="filtro_ano_input",
    )
    st.markdown("**Meses**")
    meses_input = []
    col_a, col_b = st.columns(2)
    meses_nomes = [(1,"JAN"),(2,"FEV"),(3,"MAR"),(4,"ABR"),(5,"MAI"),(6,"JUN"),
                   (7,"JUL"),(8,"AGO"),(9,"SET"),(10,"OUT"),(11,"NOV"),(12,"DEZ")]
    for idx, (mes_num, mes_nome) in enumerate(meses_nomes):
        coluna = col_a if idx % 2 == 0 else col_b
        with coluna:
            marcado = st.checkbox(
                mes_nome,
                value=mes_num in st.session_state["filtro_meses_aplicados"],
                key=f"filtro_mes_{mes_num}"
            )
            if marcado:
                meses_input.append(mes_num)

    atualizar = st.form_submit_button("Atualizar filtros", use_container_width=True)

if atualizar:
    if not meses_input:
        st.sidebar.error("Marque pelo menos um mês.")
    else:
        # O clique no submit já provoca um único rerun do Streamlit.
        # Não chamamos st.rerun() novamente: os novos filtros são aplicados nesta mesma execução.
        st.session_state["filtro_ano_aplicado"] = int(ano_sel)
        st.session_state["filtro_meses_aplicados"] = list(meses_input)

ano_aplicado = int(st.session_state["filtro_ano_aplicado"])
meses_aplicados = list(st.session_state["filtro_meses_aplicados"])
# Mapeia JAN/FEV/... diretamente para o número do mês.
_abrev_para_num = {v: k for k, v in MESES_ABREV.items()}
periodos_filtrados = [
    p for p in periodos_disponiveis
    if _ano_do_periodo(p) == ano_aplicado
    and _abrev_para_num.get(str(p).split("/")[0]) in meses_aplicados
]

if not periodos_filtrados:
    st.warning("Não há dados para o ano e os meses selecionados. Ajuste o filtro lateral e clique em Atualizar filtros.")
    st.stop()

periodos = ordenar_periodos(periodos_filtrados)

chips = "".join(f'<span class="period-chip">{p}</span>' for p in periodos)
st.markdown(f'<div style="margin:0 0 8px 0">{chips}</div>', unsafe_allow_html=True)

confirmadas_periodo = confirmadas[confirmadas["PERIODO"].isin(periodos)].copy()
atrasadas_periodo = atrasadas[atrasadas["PERIODO"].isin(periodos)].copy()
sem_classificacao_periodo = sem_classificacao[sem_classificacao["PERIODO"].isin(periodos)].copy()
receita_cmv_periodo = receita_cmv[receita_cmv["PERIODO"].isin(periodos)].copy()
recebimentos_periodo_df = recebimentos[recebimentos["PERIODO"].isin(periodos)].copy()

pagina = st.sidebar.radio("Menu", ["DRE", "DFC", "Projetos", "Ponto de Equilíbrio", "Perguntas e Respostas"])

# ============================================================
# DRE
# ============================================================
if pagina == "DRE":
    st.header("DRE Gerencial")
    ordem_dre = [
        "IMPOSTOS/deduções", "DESPESA COM PESSOAL", "DESPESAS OPERACIONAIS",
        "DESPESAS FINANCEIRAS", "DESPESAS ADMINISTRATIVAS", "DESPESAS COMERCIAIS",
    ]

    linhas = []
    linha_receita, linha_cmv, linha_margem = ["RECEITA"], ["CMV"], ["MARGEM BRUTA"]
    receita_por_periodo, cmv_por_periodo, despesas_por_conta = {}, {}, {}

    for p in periodos:
        r = receita_cmv_periodo.loc[receita_cmv_periodo["PERIODO"] == p, "RECEITA"].sum()
        c = receita_cmv_periodo.loc[receita_cmv_periodo["PERIODO"] == p, "CMV"].sum()
        receita_por_periodo[p], cmv_por_periodo[p] = r, c
        linha_receita += [r, 100 if r else 0]
        linha_cmv += [c, (c / r * 100) if r else 0]
        linha_margem += [r - c, ((r - c) / r * 100) if r else 0]
    linhas += [linha_receita, linha_cmv, linha_margem]

    for conta in ordem_dre:
        linha, total_conta_periodos = [conta], {}
        for p in periodos:
            valor = confirmadas_periodo[(confirmadas_periodo["CONTA_RESULTADO_NORM"] == normalizar_texto(conta)) & (confirmadas_periodo["PERIODO"] == p)]["Valor total"].sum()
            total_conta_periodos[p] = valor
            r = receita_por_periodo.get(p, 0)
            linha += [valor, (valor / r * 100) if r else 0]
        despesas_por_conta[conta] = total_conta_periodos
        linhas.append(linha)

    linha_resultado = ["RESULTADO"]
    for p in periodos:
        receita_val = receita_por_periodo.get(p, 0)
        resultado = receita_val - cmv_por_periodo.get(p, 0) - sum(despesas_por_conta[c].get(p, 0) for c in ordem_dre)
        linha_resultado += [resultado, (resultado / receita_val * 100) if receita_val else 0]
    linhas.append(linha_resultado)

    receita_total = sum(receita_por_periodo.values())
    cmv_total = sum(cmv_por_periodo.values())
    margem_bruta_total = receita_total - cmv_total
    resultado_total = sum(linha_resultado[i] for i in range(1, len(linha_resultado), 2))
    margem_bruta_pct = margem_bruta_total / receita_total * 100 if receita_total else 0
    resultado_pct = resultado_total / receita_total * 100 if receita_total else 0

    st.subheader("KPIs acumulados do período selecionado")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Receita acumulada", moeda(receita_total))
    k2.metric("CMV acumulado", moeda(cmv_total))
    k3.metric("Margem Bruta", moeda(margem_bruta_total), perc(margem_bruta_pct))
    k4.metric("Resultado DRE", moeda(resultado_total), perc(resultado_pct))

    dre_formatada = formatar_tabela_valor_percentual(tabela_mes_percentual(linhas, periodos))
    botao_pdf_dashboard(
        "dashboard_dre.pdf",
        "Dashboard DRE Gerencial",
        f"Período selecionado: {', '.join(periodos)}",
        {
            "Receita acumulada": moeda(receita_total),
            "CMV acumulado": moeda(cmv_total),
            "Margem Bruta": f"{moeda(margem_bruta_total)} | {perc(margem_bruta_pct)}",
            "Resultado DRE": f"{moeda(resultado_total)} | {perc(resultado_pct)}",
        },
        dre_formatada,
        key="pdf_dre"
    )
    st.dataframe(estilizar_tabela_principal(dre_formatada, linhas_azuis=["RECEITA"], linhas_resultado=["RESULTADO"]), use_container_width=True, hide_index=True)

    st.subheader("Treemap de Despesas - DRE")
    treemap_despesas(confirmadas_periodo, ordem_dre, "Composição das despesas e % sobre Receita", receita_total, "a Receita")

    st.subheader("Drill por Conta de Resultado")
    conta_sel = st.selectbox("Selecione a conta de resultado", ordem_dre, key="dre_conta")
    mostrar_kpi_conta(confirmadas_periodo, conta_sel, receita_total, "Receita")
    mostrar_drill_conta(confirmadas_periodo, conta_sel, periodos, chave_unica="dre")

    st.subheader("Observações")
    c1, c2, c3 = st.columns(3)
    c1.metric("Títulos em aberto / atrasados", len(atrasadas_periodo))
    c2.metric("Valor em aberto", moeda(atrasadas_periodo["Valor total"].sum()))
    c3.metric("Planos sem classificação", sem_classificacao_periodo["Plano de contas"].nunique())

    with st.expander("Ver planos de contas sem classificação", expanded=False):
        mostrar_planos_sem_classificacao(sem_classificacao_periodo)

    with st.expander(":red[🚨 Ver drill dos títulos em aberto / atrasados]", expanded=False):
        mostrar_drill_atrasados(atrasadas_periodo)

    with st.expander("Ver drill de Ajustes e Aplicações", expanded=False):
        mostrar_drill_ajustes_aplicacoes(confirmadas_periodo, periodos)

# ============================================================
# DFC
# ============================================================
elif pagina == "DFC":
    st.header("DFC Gerencial")
    ordem_dfc = [
        "DESPESA COM PESSOAL", "DESPESAS OPERACIONAIS", "DESPESAS FINANCEIRAS",
        "DESPESAS ADMINISTRATIVAS", "DESPESAS COMERCIAIS", "IMPOSTOS/deduções", "FORNECEDORES",
    ]

    linhas = []
    receb_por_periodo, despesas_por_conta = {}, {}
    linha_receb = ["RECEBIMENTO"]
    for p in periodos:
        r = recebimentos_periodo_df.loc[recebimentos_periodo_df["PERIODO"] == p, "RECEBIMENTO"].sum()
        receb_por_periodo[p] = r
        linha_receb += [r, 100 if r else 0]
    linhas.append(linha_receb)

    for conta in ordem_dfc:
        linha, total_conta_periodos = [conta], {}
        for p in periodos:
            valor = confirmadas_periodo[(confirmadas_periodo["CONTA_RESULTADO_NORM"] == normalizar_texto(conta)) & (confirmadas_periodo["PERIODO"] == p)]["Valor total"].sum()
            total_conta_periodos[p] = valor
            receb = receb_por_periodo.get(p, 0)
            linha += [valor, (valor / receb * 100) if receb else 0]
        despesas_por_conta[conta] = total_conta_periodos
        linhas.append(linha)

    linha_resultado = ["RESULTADO CAIXA"]
    for p in periodos:
        receb = receb_por_periodo.get(p, 0)
        resultado = receb - sum(despesas_por_conta[c].get(p, 0) for c in ordem_dfc)
        linha_resultado += [resultado, (resultado / receb * 100) if receb else 0]
    linhas.append(linha_resultado)

    receb_total = sum(receb_por_periodo.values())
    saidas_total = sum(sum(despesas_por_conta[c].values()) for c in ordem_dfc)
    resultado_caixa_total = receb_total - saidas_total
    resultado_caixa_pct = resultado_caixa_total / receb_total * 100 if receb_total else 0

    st.subheader("KPIs acumulados do período selecionado")
    k1, k2, k3 = st.columns(3)
    k1.metric("Recebimento acumulado", moeda(receb_total))
    k2.metric("Saídas acumuladas", moeda(saidas_total))
    k3.metric("Resultado Caixa", moeda(resultado_caixa_total), perc(resultado_caixa_pct))

    dfc_formatada = formatar_tabela_valor_percentual(tabela_mes_percentual(linhas, periodos))
    botao_pdf_dashboard(
        "dashboard_dfc.pdf",
        "Dashboard DFC Gerencial",
        f"Período selecionado: {', '.join(periodos)}",
        {
            "Recebimento acumulado": moeda(receb_total),
            "Saídas acumuladas": moeda(saidas_total),
            "Resultado Caixa": f"{moeda(resultado_caixa_total)} | {perc(resultado_caixa_pct)}",
        },
        dfc_formatada,
        key="pdf_dfc"
    )
    st.dataframe(estilizar_tabela_principal(dfc_formatada, linhas_azuis=["RECEBIMENTO"], linhas_resultado=["RESULTADO CAIXA"]), use_container_width=True, hide_index=True)

    st.subheader("Treemap de Despesas - DFC")
    treemap_despesas(confirmadas_periodo, ordem_dfc, "Composição das saídas e % sobre Recebimento", receb_total, "o Recebimento")

    st.subheader("Drill por Conta de Resultado")
    conta_sel = st.selectbox("Selecione a conta de resultado", ordem_dfc, key="dfc_conta")
    mostrar_kpi_conta(confirmadas_periodo, conta_sel, receb_total, "Recebimento")
    mostrar_drill_conta(confirmadas_periodo, conta_sel, periodos, chave_unica="dfc")

    st.subheader("Observações")
    c1, c2, c3 = st.columns(3)
    c1.metric("Títulos em aberto / atrasados", len(atrasadas_periodo))
    c2.metric("Valor em aberto", moeda(atrasadas_periodo["Valor total"].sum()))
    c3.metric("Planos sem classificação", sem_classificacao_periodo["Plano de contas"].nunique())
    with st.expander("Ver planos de contas sem classificação", expanded=False):
        mostrar_planos_sem_classificacao(sem_classificacao_periodo)

    with st.expander(":red[🚨 Ver drill dos títulos em aberto / atrasados]", expanded=False):
        mostrar_drill_atrasados(atrasadas_periodo)

    with st.expander("Ver drill de Ajustes e Aplicações", expanded=False):
        mostrar_drill_ajustes_aplicacoes(confirmadas_periodo, periodos)

# ============================================================
# PROJETOS
# ============================================================
elif pagina == "Projetos":
    st.header("Análise de Projetos")
    col_mes_pr = achar_coluna(projetos, ["MÊS", "MES"])
    col_ano_pr = achar_coluna(projetos, ["ANO"])
    col_projeto = achar_coluna(projetos, ["PROJETO", "CLIENTE"])
    col_receita_pr = achar_coluna(projetos, ["RECEITA"])
    col_cmv_pr = achar_coluna(projetos, ["CMV"])
    col_markup = achar_coluna(projetos, ["MARKUP"])
    col_margem_rs = achar_coluna(projetos, ["MARGEM B R$", "MARGEM BRUTA R$", "MARGEM"])
    col_margem_pct = achar_coluna(projetos, ["MARGEM B %", "MARGEM BRUTA %"])

    if not all([col_mes_pr, col_ano_pr, col_projeto, col_receita_pr, col_cmv_pr, col_markup]):
        st.error("Não consegui localizar as colunas principais da aba PROJETOS.")
        st.write(list(projetos.columns))
        st.stop()

    projetos["PERIODO"] = projetos.apply(lambda r: mes_ano_label(r[col_mes_pr], r[col_ano_pr]), axis=1)
    projetos["PROJETO_NOME"] = projetos[col_projeto].astype(str).str.strip()
    projetos["RECEITA_NUM"] = converter_numero_br(projetos[col_receita_pr])
    projetos["CMV_NUM"] = converter_numero_br(projetos[col_cmv_pr])
    projetos["MARKUP_NUM"] = pd.to_numeric(projetos[col_markup], errors="coerce").fillna(0)
    projetos["MARGEM_RS_NUM"] = converter_numero_br(projetos[col_margem_rs]) if col_margem_rs else projetos["RECEITA_NUM"] - projetos["CMV_NUM"]
    if col_margem_pct:
        projetos["MARGEM_PCT_NUM"] = pd.to_numeric(projetos[col_margem_pct], errors="coerce").fillna(0)
        projetos["MARGEM_PCT_NUM"] = np.where(projetos["MARGEM_PCT_NUM"].abs() <= 1, projetos["MARGEM_PCT_NUM"] * 100, projetos["MARGEM_PCT_NUM"])
    else:
        projetos["MARGEM_PCT_NUM"] = np.where(projetos["RECEITA_NUM"] != 0, projetos["MARGEM_RS_NUM"] / projetos["RECEITA_NUM"] * 100, 0)
    projetos["CMV_PCT_NUM"] = np.where(projetos["RECEITA_NUM"] != 0, projetos["CMV_NUM"] / projetos["RECEITA_NUM"] * 100, 0)

    periodos_proj = ordenar_periodos(projetos["PERIODO"].dropna().unique())
    periodo_sel = st.selectbox("Selecione o mês para detalhar", periodos_proj)
    projetos_mes = projetos[projetos["PERIODO"] == periodo_sel].copy()

    receita_total = projetos_mes["RECEITA_NUM"].sum()
    cmv_total = projetos_mes["CMV_NUM"].sum()
    margem_total = projetos_mes["MARGEM_RS_NUM"].sum()
    markup_medio = receita_total / cmv_total if cmv_total else 0
    cmv_pct_total = cmv_total / receita_total * 100 if receita_total else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Receita do mês", moeda(receita_total))
    c2.metric("CMV do mês", moeda(cmv_total))
    c3.metric("% CMV", perc(cmv_pct_total))
    c4.metric("Margem bruta", moeda(margem_total))
    c5.metric("Markup médio", numero(markup_medio))

    st.subheader("Resumo mensal de projetos")
    resumo = projetos.groupby("PERIODO", as_index=False).agg(RECEITA=("RECEITA_NUM", "sum"), CMV=("CMV_NUM", "sum"), MARGEM_BRUTA=("MARGEM_RS_NUM", "sum"))
    resumo["%CMV"] = np.where(resumo["RECEITA"] != 0, resumo["CMV"] / resumo["RECEITA"] * 100, 0)
    resumo["MARKUP"] = np.where(resumo["CMV"] != 0, resumo["RECEITA"] / resumo["CMV"], 0)
    resumo["MARGEM_%"] = np.where(resumo["RECEITA"] != 0, resumo["MARGEM_BRUTA"] / resumo["RECEITA"] * 100, 0)
    resumo["ORDEM"] = resumo["PERIODO"].apply(lambda p: periodos_proj.index(p) if p in periodos_proj else 999)
    resumo = resumo.sort_values("ORDEM").drop(columns=["ORDEM"])
    resumo_fmt = resumo.copy()
    for c in ["RECEITA", "CMV", "MARGEM_BRUTA"]:
        resumo_fmt[c] = resumo_fmt[c].apply(moeda)
    resumo_fmt["%CMV"] = resumo_fmt["%CMV"].apply(perc)
    resumo_fmt["MARKUP"] = resumo_fmt["MARKUP"].apply(numero)
    resumo_fmt["MARGEM_%"] = resumo_fmt["MARGEM_%"].apply(perc)
    st.dataframe(resumo_fmt, use_container_width=True, hide_index=True)

    st.subheader(f"Detalhamento dos projetos - {periodo_sel}")
    detalhe = projetos_mes[["PROJETO_NOME", "RECEITA_NUM", "CMV_NUM", "CMV_PCT_NUM", "MARKUP_NUM", "MARGEM_RS_NUM", "MARGEM_PCT_NUM"]].copy()
    detalhe.columns = ["Projeto/Cliente", "Receita", "CMV", "%CMV", "Markup", "Margem Bruta R$", "Margem Bruta %"]
    detalhe = detalhe.sort_values("Receita", ascending=False)
    detalhe_fmt = detalhe.copy()
    detalhe_fmt["Receita"] = detalhe_fmt["Receita"].apply(moeda)
    detalhe_fmt["CMV"] = detalhe_fmt["CMV"].apply(moeda)
    detalhe_fmt["%CMV"] = detalhe_fmt["%CMV"].apply(perc)
    detalhe_fmt["Markup"] = detalhe_fmt["Markup"].apply(numero)
    detalhe_fmt["Margem Bruta R$"] = detalhe_fmt["Margem Bruta R$"].apply(moeda)
    detalhe_fmt["Margem Bruta %"] = detalhe_fmt["Margem Bruta %"].apply(perc)
    st.dataframe(detalhe_fmt, use_container_width=True, hide_index=True)

    st.subheader("Gráficos por Projeto/Cliente")
    if not projetos_mes.empty:
        graf = projetos_mes.groupby("PROJETO_NOME", as_index=False).agg(Receita=("RECEITA_NUM", "sum"), CMV=("CMV_NUM", "sum"))
        graf["%CMV"] = np.where(graf["Receita"] != 0, graf["CMV"] / graf["Receita"] * 100, 0)
        graf = graf.sort_values("Receita", ascending=False)
        graf_long = graf.melt(id_vars=["PROJETO_NOME", "%CMV"], value_vars=["Receita", "CMV"], var_name="Indicador", value_name="Valor")
        fig = px.bar(
            graf_long,
            x="PROJETO_NOME",
            y="Valor",
            color="Indicador",
            barmode="group",
            custom_data=["%CMV"],
            title=f"Receita x CMV por Projeto/Cliente - {periodo_sel}",
        )
        fig.update_traces(hovertemplate="<b>%{x}</b><br>%{fullData.name}: R$ %{y:,.2f}<br>%CMV do cliente: %{customdata[0]:.2f}%<extra></extra>")
        fig.update_layout(xaxis_title="Projeto/Cliente", yaxis_title="Valor")
        st.plotly_chart(fig, use_container_width=True)

        fig2 = px.treemap(graf, path=["PROJETO_NOME"], values="Receita", custom_data=["CMV", "%CMV"], title=f"Representatividade da Receita por Projeto/Cliente - {periodo_sel}")
        fig2.update_traces(hovertemplate="<b>%{label}</b><br>Receita: R$ %{value:,.2f}<br>CMV: R$ %{customdata[0]:,.2f}<br>%CMV: %{customdata[1]:.2f}%<extra></extra>")
        st.plotly_chart(fig2, use_container_width=True)


# ============================================================
# PERGUNTAS E RESPOSTAS - AGENTE DE BI
# ============================================================
elif pagina == "Perguntas e Respostas":
    st.markdown(
        """
        <div style="padding:26px;border-radius:20px;background:linear-gradient(135deg,#071E41,#0B5ED7);color:white;margin-bottom:18px;box-shadow:0 8px 22px rgba(0,0,0,.16);">
            <div style="font-size:13px;letter-spacing:.08em;text-transform:uppercase;opacity:.85;">Última página • BI Conversacional</div>
            <h1 style="margin:6px 0 0 0;font-size:36px;">Perguntas e Respostas Gerenciais</h1>
            <p style="font-size:17px;margin-top:10px;margin-bottom:0;max-width:980px;">
                O agente identifica a intenção da pergunta, localiza conta de resultado ou plano de contas, calcula com Pandas e entrega tabela, gráfico e leitura gerencial.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption("Arquitetura: pergunta livre → intenção → parâmetros → cálculo em Pandas → resposta visual.")

    cta1, cta2, cta3, cta4 = st.columns(4)
    cta1.metric("Modo", "Agente BI")
    cta2.metric("Cálculo", "Pandas")
    cta3.metric("IA externa", "Não usa")
    cta4.metric("Rotas", "Dinâmicas")

    st.info(
        "Exemplos: **Compare despesas com pessoal de outubro até abril**, "
        "**Compare margem bruta de OUT/25 a ABR/26**, **O que impactou o resultado de março para abril?**, "
        "**Detalhe energia**, **Onde posso economizar?**, **E se reduzir pessoal em 10%?**, "
        "ou **Faça um diagnóstico financeiro**."
    )

    exemplos = gerar_100_exemplos_perguntas()
    exemplos_extra = [
        "Compare despesas com pessoal de outubro até abril.",
        "Compare margem bruta de outubro até abril.",
        "Qual foi a margem bruta de ABR/25?",
        "O que impactou o resultado de março para abril?",
        "Quais são as maiores despesas do período?",
        "Onde posso economizar de janeiro até abril?",
        "Faça um diagnóstico de saúde financeira.",
        "E se reduzir despesas com pessoal em 10%?",
        "E se aumentar receita em 15%?",
        "Analise a eficiência de despesas com pessoal sobre a receita.",
        "Compare energia de outubro até abril.",
        "Detalhe energia elétrica.",
        "Mostre o ponto de equilíbrio do período.",
        "Faça uma análise dos projetos de janeiro até abril.",
        "Qual projeto teve maior margem?",
    ]
    exemplos = exemplos_extra + [e for e in exemplos if e not in exemplos_extra]

    with st.expander("Ver exemplos de perguntas que o usuário pode fazer", expanded=False):
        col_a, col_b = st.columns(2)
        metade = int(np.ceil(len(exemplos[:110]) / 2))
        with col_a:
            for i, ex in enumerate(exemplos[:metade], start=1):
                st.markdown(f"**{i}.** {ex}")
        with col_b:
            for i, ex in enumerate(exemplos[metade:110], start=metade + 1):
                st.markdown(f"**{i}.** {ex}")

    pergunta_modelo = st.selectbox(
        "Perguntas prontas para testar",
        options=[""] + exemplos_extra,
        index=0,
        help="Escolha uma pergunta pronta ou digite livremente no chat abaixo."
    )

    if "chat_gerencial" not in st.session_state:
        st.session_state.chat_gerencial = []

    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Limpar conversa", use_container_width=True):
            st.session_state.chat_gerencial = []
            st.rerun()

    if pergunta_modelo:
        if st.button("Enviar pergunta pronta", use_container_width=True):
            resposta = executar_agente_bi(pergunta_modelo, periodos)
            st.session_state.chat_gerencial.append({"role": "user", "content": pergunta_modelo})
            st.session_state.chat_gerencial.append({"role": "assistant", "content": resposta})
            st.rerun()

    pergunta = st.chat_input("Digite sua pergunta sobre DRE, DFC, despesas, planos de contas ou projetos...")

    if pergunta:
        resposta = executar_agente_bi(pergunta, periodos)
        st.session_state.chat_gerencial.append({"role": "user", "content": pergunta})
        st.session_state.chat_gerencial.append({"role": "assistant", "content": resposta})

    for idx_msg, msg in enumerate(st.session_state.chat_gerencial):
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant":
                renderizar_resposta_bi(msg["content"], chave_base=f"msg_{idx_msg}")
            else:
                st.markdown(msg["content"])

    st.divider()
    st.subheader("Base de referência disponível")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Meses DRE/Receita", receita_cmv["PERIODO"].nunique())
    c2.metric("Meses DFC/Recebimento", recebimentos["PERIODO"].nunique())
    c3.metric("Lançamentos confirmados", f"{len(confirmadas):,}".replace(",", "."))
    c4.metric("Projetos", f"{len(projetos_chat):,}".replace(",", ".") if not projetos_chat.empty else "0")

    with st.expander("Ver períodos disponíveis"):
        st.write(periodo_para_texto_opcoes())

# ============================================================
# PONTO DE EQUILÍBRIO
# ============================================================
elif pagina == "Ponto de Equilíbrio":
    st.header("Ponto de Equilíbrio / Necessidade de Caixa")
    st.caption("Cálculo: soma da conta no período selecionado ÷ quantidade de meses selecionados.")

    ordem_pe = [
        "DESPESA COM PESSOAL", "AJUSTE", "DESPESAS OPERACIONAIS", "APLICAÇÃO",
        "DESPESAS FINANCEIRAS", "DESPESAS ADMINISTRATIVAS", "DESPESAS COMERCIAIS",
        "IMPOSTOS/deduções", "FORNECEDORES",
    ]

    periodos_pe = periodos
    qtd_meses = len(periodos_pe)

    st.info(
        f"Período considerado: {', '.join(periodos_pe)} | "
        f"Quantidade de meses para divisão: {qtd_meses}"
    )

    linhas = []
    for conta in ordem_pe:
        total_periodo = confirmadas_periodo[
            (confirmadas_periodo["CONTA_RESULTADO_NORM"] == normalizar_texto(conta)) &
            (confirmadas_periodo["PERIODO"].isin(periodos_pe))
        ]["Valor total"].sum()

        media_mensal = total_periodo / qtd_meses if qtd_meses else 0
        linhas.append([conta, total_periodo, qtd_meses, media_mensal])

    pe = pd.DataFrame(
        linhas,
        columns=["Conta de Resultado", "Total no Período", "Meses", "Média Mensal"]
    )

    necessidade_mes = pe["Média Mensal"].sum()
    necessidade_semana = necessidade_mes / 4
    necessidade_dia = necessidade_semana / 7

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Meses selecionados", qtd_meses)
    c2.metric("Necessidade de Caixa mês", moeda(necessidade_mes))
    c3.metric("Necessidade de Caixa semana", moeda(necessidade_semana))
    c4.metric("Necessidade de Caixa dia", moeda(necessidade_dia))

    pe["% sobre necessidade"] = np.where(
        necessidade_mes != 0,
        pe["Média Mensal"] / necessidade_mes * 100,
        0
    )

    pe_fmt = pe.copy()
    pe_fmt["Total no Período"] = pe_fmt["Total no Período"].apply(moeda)
    pe_fmt["Média Mensal"] = pe_fmt["Média Mensal"].apply(moeda)
    pe_fmt["% sobre necessidade"] = pe_fmt["% sobre necessidade"].apply(perc)

    st.subheader("Média mensal por Conta de Resultado")
    botao_pdf_dashboard(
        "dashboard_ponto_equilibrio.pdf",
        "Dashboard Ponto de Equilíbrio",
        f"Período selecionado: {', '.join(periodos_pe)}",
        {
            "Meses selecionados": qtd_meses,
            "Necessidade de Caixa mês": moeda(necessidade_mes),
            "Necessidade de Caixa semana": moeda(necessidade_semana),
            "Necessidade de Caixa dia": moeda(necessidade_dia),
        },
        pe_fmt,
        key="pdf_pe"
    )
    st.dataframe(pe_fmt, use_container_width=True, hide_index=True)

    fig = px.treemap(
        pe,
        path=["Conta de Resultado"],
        values="Média Mensal",
        custom_data=["Total no Período", "Média Mensal", "% sobre necessidade"],
        title="Composição da necessidade média mensal de caixa"
    )
    fig.update_traces(
        texttemplate="%{label}<br>%{customdata[2]:.2f}%",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Total no período: R$ %{customdata[0]:,.2f}<br>"
            "Média mensal: R$ %{customdata[1]:,.2f}<br>"
            "% sobre necessidade: %{customdata[2]:.2f}%"
            "<extra></extra>"
        )
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Drill das Contas do Ponto de Equilíbrio")
    conta_sel = st.selectbox("Selecione a conta para detalhar", ordem_pe, key="pe_conta")

    dados_conta = confirmadas_periodo[
        (confirmadas_periodo["CONTA_RESULTADO_NORM"] == normalizar_texto(conta_sel)) &
        (confirmadas_periodo["PERIODO"].isin(periodos_pe))
    ].copy()
    total_conta_periodo = dados_conta["Valor total"].sum()
    media_conta = total_conta_periodo / qtd_meses if qtd_meses else 0
    perc_conta = media_conta / necessidade_mes * 100 if necessidade_mes else 0

    k1, k2, k3 = st.columns(3)
    k1.metric("Total da conta no período", moeda(total_conta_periodo))
    k2.metric("Média mensal da conta", moeda(media_conta))
    k3.metric("% sobre necessidade mensal", perc(perc_conta))

    mostrar_drill_conta(confirmadas_periodo[confirmadas_periodo["PERIODO"].isin(periodos_pe)], conta_sel, periodos_pe, chave_unica="pe")
