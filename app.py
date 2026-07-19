import streamlit as st
import pandas as pd
import io

# Configuração da página para funcionar bem em PC e Celular
st.set_page_config(
    page_title="Gerenciador de Trocas", 
    page_icon="🔄", 
    layout="centered"
)

# Estilização CSS para forçar o visual idêntico ao modelo das fotos
st.markdown("""
    <style>
    .supplier-header {
        color: #FF0000 !important;
        font-weight: bold !important;
        font-size: 20px !important;
        margin-top: 25px !important;
        margin-bottom: 5px !important;
    }
    .total-supplier {
        color: #FF0000 !important;
        font-weight: bold !important;
        font-size: 16px !important;
        margin-top: 5px !important;
        margin-bottom: 25px !important;
        border-bottom: 2px solid #FF0000;
        padding-bottom: 10px;
    }
    .grand-total-box {
        background-color: #FF0000 !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        font-size: 22px !important;
        padding: 15px !important;
        border-radius: 5px !important;
        text-align: center !important;
        margin-top: 40px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🔄 Conversor de Planilhas de Trocas")
st.write("Faça o upload da planilha bruta para gerar o relatório formatado.")

# 1. Upload do arquivo bruto
uploaded_file = st.file_uploader("Selecione a planilha (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Lendo os dados brutos a partir da linha 16 (padrão do sistema)
        df = pd.read_excel(uploaded_file, sheet_name=0)
        df_clean = df.iloc[16:].copy()
        df_clean.columns = df_clean.iloc[0]
        df_clean = df_clean.iloc[1:].reset_index(drop=True)

        # Processando e agrupando os dados por fornecedor
        current_supplier = None
        suppliers_dict = {}

        for idx, row in df_clean.iterrows():
            f = row['Fornecedor']
            if pd.notna(f):
                current_supplier = str(f).strip()
            if pd.notna(row['Código Interno']):
                if current_supplier not in suppliers_dict:
                    suppliers_dict[current_supplier] = []
                
                # Tratamento de data
                data_compra = str(row['Última Compra']).split()[0] if pd.notna(row['Última Compra']) else ""
                
                suppliers_dict[current_supplier].append({
                    'Produto': row['Produto'],
                    'Código': int(row['Código Interno']),
                    'Última Compra': data_compra,
                    'Estoque': int(row['Estoque']) if pd.notna(row['Estoque']) else 0,
                    'Total': float(row['Total']) if pd.notna(row['Total']) else 0.0
                })

        # Totais Gerais acumulados
        grand_total_qty = 0
        grand_total_val = 0.0

        # Lista para remontar o Excel exportável
        export_rows = []

        # 2. Exibição do Layout Visual na Tela
        for supplier, products in suppliers_dict.items():
            # Nome do Fornecedor em Vermelho Grande e Negrito
            st.markdown(f'<div class="supplier-header">{supplier.upper()}</div>', unsafe_allow_html=True)
            
            # Criando a tabela de produtos
            prod_df = pd.DataFrame(products)
            
            # Formatando as colunas de valores para exibição na tela
            view_df = prod_df.copy()
            view_df['Total'] = view_df['Total'].map('R$ {:,.2f}'.format)
            
            st.dataframe(view_df, use_container_width=True, hide_index=True)
            
            # Cálculos dos subtotais
            sub_qty = prod_df['Estoque'].sum()
            sub_val = prod_df['Total'].sum()
            
            grand_total_qty += sub_qty
            grand_total_val += sub_val

            # Subtotal em Vermelho e Negrito com linha separadora (espaçamento)
            st.markdown(f'<div class="total-supplier">TOTAL {supplier.upper()}: {sub_qty} itens — R$ {sub_val:,.2f}</div>', unsafe_allow_html=True)

            # Guardando os dados para a exportação do Excel estruturado
            export_rows.append({"Fornecedor / Produto": supplier.upper(), "Código Interno": "", "Última Compra": "", "Estoque": "", "Total": ""})
            for p in products:
                export_rows.append({"Fornecedor / Produto": p['Produto'], "Código Interno": p['Código'], "Última Compra": p['Última Compra'], "Estoque": p['Estoque'], "Total": p['Total']})
            export_rows.append({"Fornecedor / Produto": f"TOTAL {supplier.upper()}", "Código Interno": "", "Última Compra": "", "Estoque": sub_qty, "Total": sub_val})
            export_rows.append({"Fornecedor / Produto": "", "Código Interno": "", "Última Compra": "", "Estoque": "", "Total": ""}) # Linha em branco de espaçamento

        # Adiciona o Total Geral no fim da exportação
        export_rows.append({"Fornecedor / Produto": "TOTAL GERAL DOS FORNECEDORES", "Código Interno": "", "Última Compra": "", "Estoque": grand_total_qty, "Total": grand_total_val})

        # Exibindo o Total Geral na Tela (Caixa Vermelha de Destaque)
        st.markdown(f'<div class="grand-total-box">TOTAL GERAL DOS FORNECEDORES<br>Estoque: {grand_total_qty} | R$ {grand_total_val:,.2f}</div>', unsafe_allow_html=True)

        # 3. Geração do botão de Exportação para Excel (.xlsx)
        df_export = pd.DataFrame(export_rows)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_export.to_excel(writer, index=False, sheet_name='Trocas Formatado')
        
        st.sidebar.markdown("### 📥 Ações")
        st.sidebar.download_button(
            label="💾 Exportar para Excel (.xlsx)",
            data=buffer.getvalue(),
            file_name="Relatorio_Trocas_Formatado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # Botão prático para abrir a janela de impressão nativa do celular/PC
        st.sidebar.button("🖨️ Imprimir Relatório", on_click=lambda: st.js_code("window.print();"))

    except Exception as e:
        st.error(f"Erro ao processar a planilha: {e}. Certifique-se de que o arquivo segue o padrão do sistema.")

