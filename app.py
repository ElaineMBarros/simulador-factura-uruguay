import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Simulador Nota Fiscal Uruguai", layout="wide")
st.title("🧾 Simulador de Nota Fiscal - Uruguai")
st.markdown("---")

if 'produtos' not in st.session_state:
    st.session_state.produtos = []

def calcular_impostos(descricao, quantidade, preco_folheto, percentual_comissao, iva_percentual, imesi_percentual, percepcion_iva_percentual):
    valor_comissao = preco_folheto * (percentual_comissao / 100)
    parte_produto = preco_folheto - valor_comissao

    fator = 1 + (imesi_percentual / 100) + (1 + (imesi_percentual / 100)) * ((iva_percentual / 100) + (percepcion_iva_percentual / 100))
    na = parte_produto / fator

    imesi = na * (imesi_percentual / 100)
    iva = (na + imesi) * (iva_percentual / 100)
    percepcion_iva = (na + imesi) * (percepcion_iva_percentual / 100)

    total_item = (na + imesi + iva + percepcion_iva + valor_comissao) * quantidade

    return {
        'Descrição': descricao,
        'Qtd': quantidade,
        'Vlr Unitário': round(preco_folheto, 2),
        'Base Produto': round(na * quantidade, 2),
        'IMESI': round(imesi * quantidade, 2),
        'IVA': round(iva * quantidade, 2),
        'Percep IVA': round(percepcion_iva * quantidade, 2),
        'Comissão': round(valor_comissao * quantidade, 2),
        'Total Item': round(total_item, 2)
    }

def adicionar_item_com_iva(descricao, valor, iva_percentual):
    base = valor / (1 + (iva_percentual / 100))
    iva = base * (iva_percentual / 100)
    total = base + iva
    return {
        'Descrição': descricao,
        'Qtd': 1,
        'Vlr Unitário': round(total, 2),
        'Base Produto': round(base, 2),
        'IMESI': 0.0,
        'IVA': round(iva, 2),
        'Percep IVA': 0.0,
        'Comissão': 0.0,
        'Total Item': round(total, 2)
    }

st.sidebar.header("Cadastro de Produto")
descricao = st.sidebar.text_input("Descrição do Produto")
quantidade = st.sidebar.number_input("Quantidade", min_value=1, step=1)
preco_folheto = st.sidebar.number_input("Preço Unitário (Folheto)", min_value=0.0, step=0.01)
percentual_comissao = st.sidebar.number_input("Percentual de Comissão (%)", min_value=0.0, step=0.01)
iva_percentual = st.sidebar.number_input("Percentual de IVA (%)", min_value=0.0, step=0.01)
imesi_percentual = st.sidebar.number_input("Percentual de IMESI (%)", min_value=0.0, step=0.01)
percepcion_iva_percentual = st.sidebar.number_input("Percentual de Percepción IVA (%)", min_value=0.0, step=0.01)

if st.sidebar.button("Adicionar Produto"):
    produto = calcular_impostos(
        descricao, quantidade, preco_folheto, percentual_comissao,
        iva_percentual, imesi_percentual, percepcion_iva_percentual
    )
    st.session_state.produtos.append(produto)

st.sidebar.header("Adicionar Frete e Taxa")
if st.sidebar.button("Adicionar Frete"):
    valor_frete = st.sidebar.number_input("Valor do Frete (com IVA)", min_value=0.0, step=0.01)
    iva_frete = st.sidebar.number_input("IVA do Frete (%)", min_value=0.0, step=0.01)
    st.session_state.produtos.append(adicionar_item_com_iva("Frete", valor_frete, iva_frete))

if st.sidebar.button("Adicionar Taxa Administrativa"):
    valor_taxa = st.sidebar.number_input("Valor da Taxa Administrativa (com IVA)", min_value=0.0, step=0.01)
    iva_taxa = st.sidebar.number_input("IVA da Taxa (%)", min_value=0.0, step=0.01)
    st.session_state.produtos.append(adicionar_item_com_iva("Taxa Administrativa", valor_taxa, iva_taxa))

if st.sidebar.button("Limpar Nota"):
    st.session_state.produtos = []
    st.sidebar.success("Nota limpa com sucesso.")

st.markdown("## 🗒️ Lista de Produtos e Itens")
if len(st.session_state.produtos) > 0:
    df = pd.DataFrame(st.session_state.produtos)
    st.dataframe(df, use_container_width=True)

    totais = df[['Base Produto', 'IMESI', 'IVA', 'Percep IVA', 'Comissão', 'Total Item']].sum()

    st.markdown("---")
    st.subheader("🔹 Totais da Nota Fiscal")
    st.write(f"**Base Produto:** {totais['Base Produto']:.2f}")
    st.write(f"**IMESI:** {totais['IMESI']:.2f}")
    st.write(f"**IVA:** {totais['IVA']:.2f}")
    st.write(f"**Percepción IVA:** {totais['Percep IVA']:.2f}")
    st.write(f"**Comissão:** {totais['Comissão']:.2f}")
    st.write(f"**🔸 Total Geral da Nota:** {totais['Total Item']:.2f}")

    soma_partes = totais['Base Produto'] + totais['IMESI'] + totais['IVA'] + totais['Percep IVA'] + totais['Comissão']

    st.markdown("---")
    st.subheader("🔍 Verificação de Fechamento")
    st.write(f"**Soma das Partes:** {soma_partes:.2f}")
    st.write(f"**Total Calculado:** {totais['Total Item']:.2f}")

    if abs(soma_partes - totais['Total Item']) < 0.01:
        st.success("✅ Fechamento Perfeito! A soma das partes confere com o total da nota.")
    else:
        st.error("⚠️ Atenção! Diferença encontrada entre a soma das partes e o total da nota.")
else:
    st.info("Nenhum item adicionado na nota.")
