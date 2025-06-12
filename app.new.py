import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Simulador Fatura Uruguay", layout="wide")
st.title("📄 Simulador de Faturamento - Uruguay")

# Inicializa a sessão de estado
if 'itens' not in st.session_state:
    st.session_state.itens = []
if 'frete_adicionado' not in st.session_state:
    st.session_state.frete_adicionado = False
if 'taxa_adm_adicionada' not in st.session_state:
    st.session_state.taxa_adm_adicionada = False

st.markdown("Preencha os dados abaixo para simular os impostos:")

# Entradas para Produto
with st.expander("Adicionar Produto"):
    descricao = st.text_input("Descrição do Produto", key="desc_prod")
    quantidade = st.number_input("Quantidade", min_value=1, step=1, key="qtd_prod")
    preco_tabela = st.number_input("Preço Tabela (unitário)", min_value=0.0, key="preco_prod")
    comissao_reais = st.number_input("Comissão em R$", min_value=0.0, key="comissao_prod")
    desconto_promocional = st.number_input("Desconto Promocional em R$", min_value=0.0, help="Valor total de desconto promocional para este item.", key="desc_promo_prod")

    # Impostos para Produto
    iva_percentual = st.number_input("IVA (%)", min_value=0.0, value=22.0, key="iva_prod")
    percepcion_iva_percentual = st.number_input("Percepción IVA (%)", min_value=0.0, value=10.0, key="perc_iva_prod")
    imesi_percentual = st.number_input("IMESI (%)", min_value=0.0, value=0.0, key="imesi_prod")

    if st.button("Adicionar Produto"):
        if descricao and quantidade > 0 and preco_tabela >= 0:
            preco_liquido = preco_tabela - comissao_reais - desconto_promocional
            
            # Garante que preco_liquido não seja negativo para o cálculo do fator
            if preco_liquido < 0:
                st.warning("O Preço Líquido resultante é negativo. Verifique os valores de Tabela, Comissão e Desconto.")
                preco_liquido = 0.0 # Define como 0 para evitar erros de cálculo abaixo
            
            # Se preco_liquido for 0, o fator também será 0 para evitar divisão por zero se todos os percentuais forem 0
            if preco_liquido == 0 and (imesi_percentual == 0 and iva_percentual == 0 and percepcion_iva_percentual == 0):
                 fator = 1 # Para evitar divisão por zero se todos os impostos forem zero e preco_liquido for zero
            elif (1 + (imesi_percentual / 100)) == 0 or ((iva_percentual / 100) + (percepcion_iva_percentual / 100)) == -1:
                 # Evita divisão por zero em casos extremos do fator
                 st.error("Combinação de impostos pode levar a uma divisão por zero. Ajuste os percentuais.")
                 fator = 1 # Fallback
            else:
                 fator = 1 + (imesi_percentual / 100) + (1 + (imesi_percentual / 100)) * ((iva_percentual / 100) + (percepcion_iva_percentual / 100))

            na_unitario = preco_liquido / fator if fator != 0 else 0
            na_total = na_unitario * quantidade

            imesi = round(na_total * (imesi_percentual / 100), 2)
            iva = round((na_total + imesi) * (iva_percentual / 100), 2)
            percepcion_iva = round((na_total + imesi) * (percepcion_iva_percentual / 100), 2)
            comissao_total = comissao_reais * quantidade
            total_produto = round(na_total + imesi + iva + percepcion_iva + comissao_total, 2)

            st.session_state.itens.append(
                {
                    "Tipo": "Produto",
                    "Descrição": descricao,
                    "Qtd": quantidade,
                    "Vlr Tabela": preco_tabela,
                    "Promoção R$": desconto_promocional,
                    "Comissão R$ Unit.": comissao_reais, # Renomeado para clareza
                    "Base Produto": na_total,
                    "IMESI": imesi,
                    "IVA": iva,
                    "Percep IVA": percepcion_iva,
                    "Comissão Total": comissao_total,
                    "Total Item": total_produto # Renomeado para 'Total Item'
                }
            )
            st.success(f"Produto '{descricao}' adicionado com sucesso!")
        else:
            st.warning("Por favor, preencha a Descrição, Quantidade e Preço Tabela para adicionar o produto.")

# Entradas para Frete
with st.expander("Adicionar Frete"):
    valor_frete = st.number_input("Valor do Frete (total)", min_value=0.0, key="frete_val")
    iva_frete_percentual = st.number_input("IVA do Frete (%)", min_value=0.0, value=22.0, key="iva_frete")

    if st.button("Adicionar Frete"):
        if valor_frete >= 0:
            frete_base = round(valor_frete / (1 + (iva_frete_percentual / 100)), 2)
            frete_iva = round(valor_frete - frete_base, 2)

            st.session_state.itens.append(
                {
                    "Tipo": "Frete",
                    "Descrição": "Frete",
                    "Qtd": 1,
                    "Vlr Tabela": valor_frete,
                    "Promoção R$": 0.0,
                    "Comissão R$ Unit.": 0.0,
                    "Base Produto": frete_base,
                    "IMESI": 0.0,
                    "IVA": frete_iva,
                    "Percep IVA": 0.0,
                    "Comissão Total": 0.0,
                    "Total Item": valor_frete
                }
            )
            st.success("Frete adicionado com sucesso!")
        else:
            st.warning("Por favor, insira um valor para o Frete.")


# Entradas para Taxa Administrativa
with st.expander("Adicionar Taxa Administrativa"):
    valor_taxa_adm = st.number_input("Taxa Administrativa (total)", min_value=0.0, key="taxa_adm_val")
    iva_taxa_adm_percentual = st.number_input("IVA da Taxa Administrativa (%)", min_value=0.0, value=22.0, key="iva_taxa_adm")

    if st.button("Adicionar Taxa Administrativa"):
        if valor_taxa_adm >= 0:
            taxa_base = round(valor_taxa_adm / (1 + (iva_taxa_adm_percentual / 100)), 2)
            taxa_iva = round(valor_taxa_adm - taxa_base, 2)

            st.session_state.itens.append(
                {
                    "Tipo": "Taxa Administrativa",
                    "Descrição": "Taxa Administrativa",
                    "Qtd": 1,
                    "Vlr Tabela": valor_taxa_adm,
                    "Promoção R$": 0.0,
                    "Comissão R$ Unit.": 0.0,
                    "Base Produto": taxa_base,
                    "IMESI": 0.0,
                    "IVA": taxa_iva,
                    "Percep IVA": 0.0,
                    "Comissão Total": 0.0,
                    "Total Item": valor_taxa_adm
                }
            )
            st.success("Taxa Administrativa adicionada com sucesso!")
        else:
            st.warning("Por favor, insira um valor para a Taxa Administrativa.")


# Exibição da Nota
if st.session_state.itens:
    df = pd.DataFrame(st.session_state.itens)
    st.subheader("📋 Detalhamento da Nota")
    st.dataframe(df, use_container_width=True)

    # Botão para limpar a nota
    if st.button("Limpar Nota"):
        st.session_state.itens = []
        st.success("Nota limpa com sucesso!")
        st.experimental_rerun() # Recarrega a página para refletir a mudança

    totais = df[["Base Produto", "IMESI", "IVA", "Percep IVA", "Comissão Total", "Total Item"]].sum()

    st.markdown("### 🔢 Totais da Nota")
    st.write(f"**Base Produto (somatória):** R$ {totais['Base Produto']:.2f}")
    st.write(f"**IMESI (somatória):** R$ {totais['IMESI']:.2f}")
    st.write(f"**IVA (somatória):** R$ {totais['IVA']:.2f}")
    st.write(f"**Percepción IVA (somatória):** R$ {totais['Percep IVA']:.2f}")
    st.write(f"**Comissão Total (somatória):** R$ {totais['Comissão Total']:.2f}")
    st.write(f"**🔸 Total Geral da Nota:** R$ {totais['Total Item']:.2f}")

    # Verificação de Fechamento (inclui todos os totais)
    soma_partes = totais["Base Produto"] + totais["IMESI"] + totais["IVA"] + totais["Percep IVA"] + totais["Comissão Total"]

    st.markdown("### ✅ Verificação de Fechamento")
    st.write(f"Soma das Partes (Base Produto + IMESI + IVA + Percep IVA + Comissão Total): R$ {soma_partes:.2f}")
    st.write(f"Total Calculado (somatória dos 'Total Item'): R$ {totais['Total Item']:.2f}")

    if abs(soma_partes - totais['Total Item']) < 0.01:
        st.success("Fechamento Perfeito!")
    else:
        st.warning("Diferença encontrada entre soma das partes e o total! Pode haver arredondamentos.")

    # Download Excel
    buffer = BytesIO()
    df.to_excel(buffer, index=False, engine='openpyxl')
    st.download_button("📥 Baixar Excel", data=buffer.getvalue(), file_name="simulador_fatura_uruguai.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
else:
    st.info("Adicione produtos, frete ou taxa administrativa para iniciar a simulação.")