import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import unicodedata
from pathlib import Path
from io import BytesIO

st.set_page_config(page_title="Indicadores Financeiros", layout="wide")

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


def mostrar_drill_conta(df, conta_resultado, periodos, chave_unica=""):
    dados = df[df["CONTA_RESULTADO_NORM"] == normalizar_texto(conta_resultado)].copy()
    if dados.empty:
        st.info("Não há lançamentos para esta conta de resultado.")
        return

    st.markdown("**Consolidado por Plano de Contas**")
    consolidado = montar_pivot(dados, ["Plano de contas"], periodos)
    st.dataframe(formatar_pivot_valores(consolidado, periodos), use_container_width=True, hide_index=True)

    st.markdown("**Detalhamento por descrição dentro do Plano de Contas**")
    planos = consolidado["Plano de contas"].tolist() if not consolidado.empty else sorted(dados["Plano de contas"].dropna().unique())
    plano_sel = st.selectbox("Selecione o Plano de Contas para detalhar", planos, key=f"plano_{chave_unica}_{normalizar_texto(conta_resultado)}")
    detalhado = montar_pivot(dados[dados["Plano de contas"] == plano_sel], ["Plano de contas", "Descrição"], periodos)
    st.dataframe(formatar_pivot_valores(detalhado, periodos), use_container_width=True, hide_index=True)


def mostrar_drill_atrasados(atrasadas):
    st.subheader("Drill de Títulos Atrasados")
    if atrasadas.empty:
        st.info("Não há títulos atrasados.")
        return
    agrup = atrasadas.groupby(["CONTA_RESULTADO", "Plano de contas"], dropna=False, as_index=False).agg(
        QTD=("Valor total", "count"), VALOR=("Valor total", "sum")
    ).sort_values("VALOR", ascending=False)
    agrup_fmt = agrup.copy()
    agrup_fmt["VALOR"] = agrup_fmt["VALOR"].apply(moeda)
    st.markdown("**Resumo por Conta de Resultado e Plano de Contas**")
    st.dataframe(agrup_fmt, use_container_width=True, hide_index=True)

    detalhe = atrasadas[["Data de confirmação", "PERIODO", "CONTA_RESULTADO", "Plano de contas", "Descrição", "Valor total", "Situação"]].copy()
    detalhe["Data de confirmação"] = detalhe["Data de confirmação"].dt.strftime("%d/%m/%Y")
    detalhe["Valor total"] = detalhe["Valor total"].apply(moeda)
    st.markdown("**Detalhamento dos títulos**")
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
# INTERFACE / LEITURA
# ============================================================

st.title("Indicadores Financeiros")
st.caption("DRE | DFC | Projetos | Ponto de Equilíbrio")

# ============================================================
# LEITURA AUTOMÁTICA DA PLANILHA
# Para Streamlit Cloud, coloque a planilha no mesmo repositório
# com este nome exato ou ajuste a variável NOME_PLANILHA abaixo.
# ============================================================

NOME_PLANILHA = "CONTAS A PAGAR SAMUEL ANTUNES.xlsx"
CAMINHO_PLANILHA = Path(__file__).parent / NOME_PLANILHA

if not CAMINHO_PLANILHA.exists():
    st.error(
        f"Planilha não encontrada: {NOME_PLANILHA}. "
        "Coloque o arquivo Excel na mesma pasta/repositório deste app.py."
    )
    st.stop()

st.success(f"Planilha carregada automaticamente: {NOME_PLANILHA}")
xls = pd.ExcelFile(CAMINHO_PLANILHA)
contas = pd.read_excel(xls, "relatorio_contas_pagar")
base_raw = pd.read_excel(xls, "BASE", header=None)
receita_cmv = pd.read_excel(xls, "RECEITA E CMV")
recebimentos = pd.read_excel(xls, "RECEBIMENTO")
projetos = pd.read_excel(xls, "PROJETOS")

contas.columns = [str(c).strip() for c in contas.columns]
receita_cmv.columns = [str(c).strip() for c in receita_cmv.columns]
recebimentos.columns = [str(c).strip() for c in recebimentos.columns]
projetos.columns = [str(c).strip() for c in projetos.columns]
base = preparar_base(base_raw)

# Contas a pagar
col_plano = achar_coluna(contas, ["Plano de contas"])
col_data_conf = achar_coluna(contas, ["Data de confirmação"])
col_situacao = achar_coluna(contas, ["Situação", "Situacao"])
col_valor_total = achar_coluna(contas, ["Valor total"])
col_descricao = achar_coluna(contas, ["Descrição", "Descricao"])
if not all([col_plano, col_data_conf, col_situacao, col_valor_total, col_descricao]):
    st.error("Não consegui localizar todas as colunas necessárias na aba relatorio_contas_pagar.")
    st.write("Colunas encontradas:", list(contas.columns))
    st.stop()

contas["Plano de contas"] = contas[col_plano].astype(str).str.strip()
contas["Descrição"] = contas[col_descricao].astype(str).str.strip()
contas["Situação"] = contas[col_situacao].astype(str).str.strip()
contas["Valor total"] = converter_numero_br(contas[col_valor_total])
contas["Data de confirmação"] = pd.to_datetime(contas[col_data_conf], dayfirst=True, errors="coerce")
contas["ANO"] = contas["Data de confirmação"].dt.year
contas["MES_NUM"] = contas["Data de confirmação"].dt.month
contas["PERIODO"] = contas.apply(
    lambda r: f"{MESES_ABREV.get(int(r['MES_NUM']), '')}/{str(int(r['ANO']))[-2:]}" if pd.notna(r["MES_NUM"]) and pd.notna(r["ANO"]) else "",
    axis=1,
)
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
        "ANO": 2025,
        "MES_NUM": 11,
        "PERIODO": "NOV/25",
        "PLANO_NORM": normalizar_texto("Matéria prima"),
        "CONTA_RESULTADO": "FORNECEDORES",
        "CONTA_RESULTADO_NORM": normalizar_texto("FORNECEDORES"),
    },
])

contas = pd.concat([contas, lancamentos_manuais], ignore_index=True)

confirmadas = contas[contas["Situação"].apply(normalizar_texto).eq("CONFIRMADO")].copy()
atrasadas = contas[contas["Situação"].apply(normalizar_texto).str.contains("ATRAS", na=False)].copy()
sem_classificacao = confirmadas[confirmadas["CONTA_RESULTADO"].eq("")].copy()

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

periodos = ordenar_periodos(sorted(set(receita_cmv["PERIODO"].dropna()) | set(recebimentos["PERIODO"].dropna()) | set(confirmadas["PERIODO"].dropna())))
periodos = [p for p in periodos if p and p != "/"]

# ============================================================
# FILTRO GLOBAL DE PERÍODO
# Esse filtro conversa com DRE, DFC, Observações e Ponto de Equilíbrio.
# ============================================================

st.sidebar.subheader("Filtro de Período")
periodos_filtrados = st.sidebar.multiselect(
    "Selecione os meses",
    options=periodos,
    default=periodos,
    help="Esse filtro altera DRE, DFC, Observações e Ponto de Equilíbrio."
)

if not periodos_filtrados:
    st.warning("Selecione pelo menos um mês no filtro lateral.")
    st.stop()

periodos = ordenar_periodos(periodos_filtrados)

confirmadas_periodo = confirmadas[confirmadas["PERIODO"].isin(periodos)].copy()
atrasadas_periodo = atrasadas[atrasadas["PERIODO"].isin(periodos)].copy()
sem_classificacao_periodo = sem_classificacao[sem_classificacao["PERIODO"].isin(periodos)].copy()
receita_cmv_periodo = receita_cmv[receita_cmv["PERIODO"].isin(periodos)].copy()
recebimentos_periodo_df = recebimentos[recebimentos["PERIODO"].isin(periodos)].copy()

pagina = st.sidebar.radio("Multipages", ["DRE", "DFC", "Projetos", "Ponto de Equilíbrio"])

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
    c1.metric("Títulos atrasados", len(atrasadas_periodo))
    c2.metric("Valor atrasado", moeda(atrasadas_periodo["Valor total"].sum()))
    c3.metric("Planos sem classificação", sem_classificacao_periodo["Plano de contas"].nunique())

    if not sem_classificacao_periodo.empty:
        st.warning("Existem planos de contas sem Conta de Resultado na aba BASE.")
        sem = sem_classificacao_periodo.groupby("Plano de contas", as_index=False)["Valor total"].sum().sort_values("Valor total", ascending=False)
        sem["Valor total"] = sem["Valor total"].apply(moeda)
        st.dataframe(sem, use_container_width=True, hide_index=True)

    with st.expander("Ver drill dos títulos atrasados", expanded=False):
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
    c1.metric("Títulos atrasados", len(atrasadas_periodo))
    c2.metric("Valor atrasado", moeda(atrasadas_periodo["Valor total"].sum()))
    c3.metric("Planos sem classificação", sem_classificacao_periodo["Plano de contas"].nunique())
    with st.expander("Ver drill dos títulos atrasados", expanded=False):
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
