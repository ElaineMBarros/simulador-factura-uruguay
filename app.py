import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simulador Fatura Uruguay", layout="wide")

st.title("📄 Simulador de Faturamento - Uruguay")

st.markdown("Preencha os dados abaixo para simular os impostos:")

# Entradas do produto
descricao = st.text_input("Descrição do Produto")
quantidade = st.number_input("Quantidade", min_value=1, step=1)
preco_tabela = st.number_input("Preço Tabela (unitário)", min_value=0.0)
comissao_reais = st.number_input("Comissão em R$", min_value=0.0)
desconto_promocional = st.number_input("Desconto Promocional em R$", min_value=0.0)

# Impostos (%)
iva_percentual = st.number_input("IVA (%)", min_value=0.0, value=22.0)
percepcion_iva_percentual = st.number_input("Percepción IVA (%)", min_value=0.0, value=10.0)
imesi_percentual = st.number_input("IMESI (%)", min_value=0.0, value=0.0)

# Frete e Taxa Administrativa
valor_frete = st.number_input("Valor do Frete (total)", min_value=0.0)
valor_taxa_adm = st.number_input("Taxa Administrativa (total)", min_value=0.0)

# Botão de simulação
if st.button("Simular Nota"):
    preco_liquido = preco_tabela - comissao_reais - desconto_promocional
    parte_produto = preco_liquido

    fator = 1 + (imesi_percentual / 100) + (1 + (imesi_percentual / 100)) * ((iva_percentual / 100) + (percepcion_iva_percentual / 100))
    na_unitario = parte_produto / fator
    na_total = na_unitario * quantidade

    imesi = round(na_total * (imesi_percentual / 100), 2)
    iva = round((na_total + imesi) * (iva_percentual / 100), 2)
    percepcion_iva = round((na_total + imesi) * (percepcion_iva_percentual / 100), 2)
    comissao_total = comissao_reais * quantidade

    total_produto = round(na_total + imesi + iva + percepcion_iva + comissao_total, 2)

    # Cálculo do frete e taxa com IVA por dentro
    frete_base = round(valor_frete / (1 + (iva_percentual / 100)), 2)
    frete_iva = round(valor_frete - frete_base, 2)

    taxa_base = round(valor_taxa_adm / (1 + (iva_percentual / 100)), 2)
    taxa_iva = round(valor_taxa_adm - taxa_base, 2)

    total_geral = total_produto + valor_frete + valor_taxa_adm

    # Tabela final
    df = pd.DataFrame([
        {
            "Descrição": descricao,
            "Qtd": quantidade,
            "Vlr Tabela": preco_tabela,
            "Promoção R$": desconto_promocional,
            "Comissão R$": comissao_reais,
            "Base Produto": na_total,
            "IMESI": imesi,
            "IVA": iva,
            "Percep IVA": percepcion_iva,
            "Comissão Total": comissao_total,
            "Total Produto": total_produto
        },
        {
            "Descrição": "Frete",
            "Qtd": 1,
            "Vlr Tabela": valor_frete,
            "Promoção R$": 0.0,
            "Comissão R$": 0.0,
            "Base Produto": frete_base,
            "IMESI": 0.0,
            "IVA": frete_iva,
            "Percep IVA": 0.0,
            "Comissão Total": 0.0,
            "Total Produto": valor_frete
        },
        {
            "Descrição": "Taxa Administrativa",
            "Qtd": 1,
            "Vlr Tabela": valor_taxa_adm,
            "Promoção R$": 0.0,
            "Comissão R$": 0.0,
            "Base Produto": taxa_base,
            "IMESI": 0.0,
            "IVA": taxa_iva,
            "Percep IVA": 0.0,
            "Comissão Total": 0.0,
            "Total Produto": valor_taxa_adm
        }
    ])

    st.success(f"Total Geral da Nota: R$ {total_geral:.2f}")
    st.dataframe(df)

    # Download Excel
    excel_bytes = df.to_excel(index=False, engine='openpyxl')
    st.download_button("📥 Baixar Excel", data=excel_bytes, file_name="simulador_faturamento.xlsx")
