
import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Simulador de Nota Fiscal - Uruguai", layout="wide")

st.title("📄 Simulador de Nota Fiscal - Uruguai (com base no Preço Líquido)")

uploaded_file = st.file_uploader("📤 Faça upload do arquivo CSV com os dados do pedido", type=["csv"])

def calcular_impostos(row):
    preco_liquido = row["Preco_Liquido"]
    quantidade = row["Quantidade"]
    imesi_percentual = row["IMESI"]
    iva_percentual = row["IVA"]
    percepcion_iva_percentual = row["Percepcion_IVA"]
    comissao = row["Comissao"]

    fator = 1 + (imesi_percentual / 100) + (1 + (imesi_percentual / 100)) * ((iva_percentual / 100) + (percepcion_iva_percentual / 100))
    na_unit = preco_liquido / fator
    na_total = na_unit * quantidade

    valor_imesi = round(na_total * (imesi_percentual / 100), 2)
    valor_iva = round((na_total + valor_imesi) * (iva_percentual / 100), 2)
    valor_percepcion_iva = round((na_total + valor_imesi) * (percepcion_iva_percentual / 100), 2)

    total_item = round(na_total + valor_imesi + valor_iva + valor_percepcion_iva + (comissao * quantidade), 2)

    return pd.Series({
        "NA_Total": na_total,
        "IMESI": valor_imesi,
        "IVA": valor_iva,
        "Percepcion_IVA": valor_percepcion_iva,
        "Total_Item": total_item
    })

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("📊 Dados carregados:")
    st.dataframe(df)

    df_calculado = df.copy()
    calculos = df_calculado.apply(calcular_impostos, axis=1)
    df_resultado = pd.concat([df_calculado, calculos], axis=1)

    st.write("✅ Resultado com Cálculo dos Impostos:")
    st.dataframe(df_resultado)

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_resultado.to_excel(writer, index=False, sheet_name="Nota Calculada")
    excel_data = output.getvalue()

    st.download_button(
        label="📥 Baixar Excel com Nota Calculada",
        data=excel_data,
        file_name="nota_fiscal_calculada.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.warning("Por favor, envie um arquivo CSV com os dados do pedido.")
