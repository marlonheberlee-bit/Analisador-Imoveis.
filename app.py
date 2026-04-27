import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(
    page_title="Analisador Imobiliário V8",
    page_icon="🏢",
    layout="wide"
)

# =============================
# FUNÇÕES AUXILIARES
# =============================

def moeda(valor):
    if pd.isna(valor) or valor is None:
        return "R$ 0"
    return f"R$ {valor:,.0f}".replace(",", ".")


def percentual(valor):
    if pd.isna(valor) or valor is None:
        return "0,00%"
    return f"{valor:.2f}%".replace(".", ",")


def calcular_nota(roi_total, multiplo_capital, aporte_sobre_valor, anos_entrega):
    """
    Nota de 0 a 10 baseada em:
    - ROI total
    - múltiplo do capital
    - eficiência do aporte
    - prazo até entrega
    """
    nota = 0

    # ROI total
    if roi_total >= 100:
        nota += 3.0
    elif roi_total >= 70:
        nota += 2.5
    elif roi_total >= 50:
        nota += 2.0
    elif roi_total >= 30:
        nota += 1.3
    elif roi_total >= 15:
        nota += 0.8

    # Múltiplo do capital
    if multiplo_capital >= 2.0:
        nota += 3.0
    elif multiplo_capital >= 1.7:
        nota += 2.5
    elif multiplo_capital >= 1.4:
        nota += 2.0
    elif multiplo_capital >= 1.2:
        nota += 1.2
    elif multiplo_capital >= 1.0:
        nota += 0.7

    # Quanto menor o aporte em relação ao valor do imóvel, melhor a alavancagem
    if aporte_sobre_valor <= 35:
        nota += 2.0
    elif aporte_sobre_valor <= 50:
        nota += 1.5
    elif aporte_sobre_valor <= 70:
        nota += 1.0
    else:
        nota += 0.5

    # Prazo
    if anos_entrega <= 2:
        nota += 2.0
    elif anos_entrega <= 3:
        nota += 1.5
    elif anos_entrega <= 5:
        nota += 1.0
    else:
        nota += 0.5

    return min(round(nota, 1), 10)


def classificar_nota(nota):
    if nota >= 8.5:
        return "🔥 Excelente oportunidade"
    elif nota >= 7:
        return "✅ Bom negócio"
    elif nota >= 5.5:
        return "⚠️ Aceitável, exige atenção"
    else:
        return "❌ Fraco ou arriscado"


# =============================
# CABEÇALHO
# =============================

st.title("🏢 Analisador Imobiliário Profissional V8")
st.caption("Análise de fluxo, valorização, aporte, retorno total na venda e nota estratégica para investidor.")

st.divider()

# =============================
# ENTRADAS
# =============================

col1, col2, col3 = st.columns(3)

with col1:
    nome = st.text_input("Nome do empreendimento", "Empreendimento Exemplo")
    localizacao = st.text_input("Localização", "Porto Belo / SC")
    valor_imovel = st.number_input("Valor atual do imóvel", min_value=0.0, value=1351000.0, step=10000.0)
    metragem = st.number_input("Metragem privativa m²", min_value=0.0, value=90.0, step=1.0)

with col2:
    ano_atual = datetime.now().year
    ano_entrega = st.number_input("Ano de entrega", min_value=ano_atual, max_value=2045, value=2030, step=1)
    valorizacao_anual = st.slider("Valorização anual estimada", 0.0, 30.0, 12.0, 0.5) / 100
    cub_anual = st.slider("Reajuste anual estimado CUB/INCC", 0.0, 15.0, 4.3, 0.1) / 100
    anos_analise = st.slider("Anos para simulação", 1, 10, 5)

with col3:
    entrada = st.number_input("Entrada", min_value=0.0, value=100000.0, step=5000.0)
    parcela_mensal = st.number_input("Parcela mensal inicial", min_value=0.0, value=3000.0, step=500.0)
    meses_parcelas = st.number_input("Quantidade de parcelas", min_value=0, value=60, step=1)
    reforco_anual = st.number_input("Reforço anual", min_value=0.0, value=30000.0, step=5000.0)

st.divider()

# =============================
# CÁLCULOS PRINCIPAIS
# =============================

anos_entrega = max(ano_entrega - ano_atual, 1)
valor_m2 = valor_imovel / metragem if metragem > 0 else 0

linhas = []
total_aportado_acumulado = entrada

for ano in range(1, anos_analise + 1):
    meses_no_ano = min(12, max(meses_parcelas - ((ano - 1) * 12), 0))

    parcela_reajustada = parcela_mensal * ((1 + cub_anual) ** (ano - 1))
    reforco_reajustado = reforco_anual * ((1 + cub_anual) ** (ano - 1))

    aporte_parcelas = parcela_reajustada * meses_no_ano
    aporte_reforco = reforco_reajustado if meses_no_ano > 0 else 0

    if ano == 1:
        aporte_ano = entrada + aporte_parcelas + aporte_reforco
        total_aportado_acumulado = aporte_ano
    else:
        aporte_ano = aporte_parcelas + aporte_reforco
        total_aportado_acumulado += aporte_ano

    valor_estimado = valor_imovel * ((1 + valorizacao_anual) ** ano)
    lucro_bruto = valor_estimado - valor_imovel

    # AQUI ESTÁ A LÓGICA QUE VOCÊ PEDIU:
    # O dinheiro que volta para a mão do investidor na venda é o aporte + o lucro.
    retorno_total_venda = total_aportado_acumulado + lucro_bruto

    roi_total = (lucro_bruto / total_aportado_acumulado) * 100 if total_aportado_acumulado > 0 else 0
    multiplo_capital = retorno_total_venda / total_aportado_acumulado if total_aportado_acumulado > 0 else 0
    rentabilidade_mensal_equivalente = ((retorno_total_venda / total_aportado_acumulado) ** (1 / (ano * 12)) - 1) * 100 if total_aportado_acumulado > 0 and retorno_total_venda > 0 else 0

    linhas.append({
        "Ano": ano,
        "Aporte no ano": aporte_ano,
        "Total aportado": total_aportado_acumulado,
        "Valor estimado do imóvel": valor_estimado,
        "Lucro bruto": lucro_bruto,
        "💰 Retorno total na venda": retorno_total_venda,
        "Múltiplo do capital": multiplo_capital,
        "ROI sobre aporte": roi_total,
        "Rentabilidade mensal equivalente": rentabilidade_mensal_equivalente
    })


df = pd.DataFrame(linhas)

# Último ano analisado
ultimo = df.iloc[-1]
aporte_final = ultimo["Total aportado"]
valor_final = ultimo["Valor estimado do imóvel"]
lucro_final = ultimo["Lucro bruto"]
retorno_final = ultimo["💰 Retorno total na venda"]
roi_final = ultimo["ROI sobre aporte"]
multiplo_final = ultimo["Múltiplo do capital"]
aporte_sobre_valor = (aporte_final / valor_imovel) * 100 if valor_imovel > 0 else 0
nota = calcular_nota(roi_final, multiplo_final, aporte_sobre_valor, anos_entrega)
classificacao = classificar_nota(nota)

# =============================
# PAINEL EXECUTIVO
# =============================

st.subheader("📊 Painel Executivo")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Valor por m²", moeda(valor_m2))
m2.metric("Total aportado", moeda(aporte_final))
m3.metric("Lucro estimado", moeda(lucro_final))
m4.metric("💰 Retorno na venda", moeda(retorno_final))

m5, m6, m7, m8 = st.columns(4)
m5.metric("Valor futuro estimado", moeda(valor_final))
m6.metric("ROI sobre aporte", percentual(roi_final))
m7.metric("Múltiplo do capital", f"{multiplo_final:.2f}x")
m8.metric("Nota do negócio", f"{nota}/10")

st.info(f"**Classificação:** {classificacao}")

st.divider()

# =============================
# TABELA PROFISSIONAL
# =============================

st.subheader("🏦 Tabela Profissional do Investidor")
st.caption("A coluna 💰 mostra quanto dinheiro volta para sua mão na venda: total aportado + lucro pela valorização.")

# Formatação visual da tabela
df_formatado = df.copy()
df_formatado["Aporte no ano"] = df_formatado["Aporte no ano"].apply(moeda)
df_formatado["Total aportado"] = df_formatado["Total aportado"].apply(moeda)
df_formatado["Valor estimado do imóvel"] = df_formatado["Valor estimado do imóvel"].apply(moeda)
df_formatado["Lucro bruto"] = df_formatado["Lucro bruto"].apply(moeda)
df_formatado["💰 Retorno total na venda"] = df_formatado["💰 Retorno total na venda"].apply(lambda x: "💰 " + moeda(x))
df_formatado["Múltiplo do capital"] = df_formatado["Múltiplo do capital"].apply(lambda x: f"{x:.2f}x")
df_formatado["ROI sobre aporte"] = df_formatado["ROI sobre aporte"].apply(percentual)
df_formatado["Rentabilidade mensal equivalente"] = df_formatado["Rentabilidade mensal equivalente"].apply(percentual)

st.dataframe(df_formatado, use_container_width=True, hide_index=True)

st.divider()

# =============================
# LEITURA ESTRATÉGICA
# =============================

st.subheader("🧠 Leitura Estratégica")

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("### Pontos fortes")
    if multiplo_final >= 2:
        st.success("Excelente multiplicação do capital investido.")
    elif multiplo_final >= 1.5:
        st.success("Boa eficiência de capital.")
    else:
        st.warning("Multiplicação de capital moderada.")

    if aporte_sobre_valor <= 50:
        st.success("Aporte relativamente baixo em relação ao valor do imóvel, indicando boa alavancagem.")
    else:
        st.warning("Aporte elevado em relação ao valor do imóvel, exigindo mais caixa.")

    if valorizacao_anual >= 10 / 100:
        st.success("Valorização projetada forte para estratégia de ganho de capital.")
    else:
        st.warning("Valorização projetada conservadora/moderada.")

with col_b:
    st.markdown("### Pontos de atenção")
    if cub_anual > 8 / 100:
        st.error("Reajuste anual elevado pode pressionar o fluxo de caixa.")
    elif cub_anual > 5 / 100:
        st.warning("Reajuste anual exige acompanhamento.")
    else:
        st.success("Reajuste anual considerado controlado na simulação.")

    if anos_entrega > 5:
        st.warning("Prazo longo até entrega aumenta risco de mercado e de execução.")
    else:
        st.success("Prazo de entrega dentro de uma janela razoável.")

    if roi_final < 30:
        st.warning("ROI baixo para operação de risco imobiliário.")
    else:
        st.success("ROI projetado compatível com estratégia de valorização.")

st.divider()

# =============================
# RESUMO FINAL
# =============================

st.subheader("💼 Resumo Final para Decisão")

st.markdown(f"""
### {nome}
**Localização:** {localizacao}  
**Valor atual:** {moeda(valor_imovel)}  
**Valor estimado ao final da simulação:** {moeda(valor_final)}  
**Total aportado:** {moeda(aporte_final)}  
**Lucro estimado pela valorização:** {moeda(lucro_final)}  
**💰 Dinheiro que volta na venda:** {moeda(retorno_final)}  
**Múltiplo do capital:** {multiplo_final:.2f}x  
**ROI sobre o aporte:** {percentual(roi_final)}  
**Nota:** {nota}/10 — {classificacao}

---

#### Interpretação objetiva
Se você aportar **{moeda(aporte_final)}** e o imóvel valorizar **{moeda(lucro_final)}**, o retorno total estimado na venda será de aproximadamente:

# 💰 {moeda(retorno_final)}

Esse número representa o capital que volta para sua mão: **valor aportado + ganho de valorização**.
""")

st.caption("Atenção: esta é uma simulação financeira. Não considera impostos, corretagem, distrato, financiamento, vacância, custos de escritura, ITBI, condomínio, reformas ou variações reais de mercado.")
