import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simulador de Nota Fiscal - Uruguai", layout="wide")
st.title("🧾 Simulador de Nota Fiscal - Uruguai")
st.markdown("---")

st.sidebar.header("🔧 Dados do Produto")

descricao = st.sidebar.text_input("Descrição do Produto")
quantidade = st.sidebar.number_input("Quantidade", min_value=1, step=1)
preco_folheto = st.sidebar.number_input("Preço Unitário (Folheto)", min_value=0.0, step=0.01)
percentual_comissao = st.sidebar.number_input("Percentual de Comissão (%)", min_value=0.0, step=0.01)
iva_percentual = st.sidebar.number_input("Percentual de IVA (%)", min_value=0.0, step=0.01)
imesi_percentual = st.sidebar.number_input("Percentual de IMESI (%)", min_value=0.0, step=0.01)
percepcion_iva_percentual = st.sidebar.number_input("Percentual de Percepción IVA (%)", min_value=0.0, step=0.01)

if "produtos" not in st.session_state:
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

if st.sidebar.button("Adicionar Produto"):
    if descricao != "" and preco_folheto > 0:
        produto = calcular_impostos(descricao, quantidade, preco_folheto, percentual_comissao, iva_percentual, imesi_percentual, percepcion_iva_percentual)
        st.session_state.produtos.append(produto)
    else:
        st.sidebar.warning("Preencha a descrição e o preço corretamente.")

st.markdown("## 🗒️ Lista de Produtos")
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

    # Exportar para Excel
    st.markdown("---")
    st.subheader("📥 Exportar Dados")
    excel = df.to_excel(index=False, engine='openpyxl')
    st.download_button("📥 Baixar Excel", data=excel, file_name="nota_fiscal_uruguay.xlsx")

else:
    st.info("Nenhum produto adicionado ainda.")

if st.sidebar.button("🗑️ Limpar Produtos"):
    st.session_state.produtos = []
    st.sidebar.success("Produtos resetados.")
