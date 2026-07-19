import streamlit as st
import pandas as pd
import io

# Configuração da página para funcionar bem em PC e Celular
st.set_page_config(
    page_title="Gerenciador de Trocas", 
    page_icon="🔄", 
    layout="centered"
)

# Estilização CSS para a visualização nativa da tela
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

uploaded_file = st.file_uploader("Selecione a planilha (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Lendo os dados brutas a partir da linha 16
        df = pd.read_excel(uploaded_file, sheet_name=0)
        df_clean = df.iloc[16:].copy()
        df_clean.columns = df_clean.iloc[0]
        df_clean = df_clean.iloc[1:].reset_index(drop=True)

        current_supplier = None
        suppliers_dict = {}

        for idx, row in df_clean.iterrows():
            f = row['Fornecedor']
            if pd.notna(f):
                current_supplier = str(f).strip()
            if pd.notna(row['Código Interno']):
                if current_supplier not in suppliers_dict:
                    suppliers_dict[current_supplier] = []
                
                data_compra = str(row['Última Compra']).split()[0] if pd.notna(row['Última Compra']) else ""
                
                suppliers_dict[current_supplier].append({
                    'Produto': row['Produto'],
                    'Código Interno': int(row['Código Interno']),
                    'Última Compra': data_compra,
                    'Estoque': int(row['Estoque']) if pd.notna(row['Estoque']) else 0,
                    'Total': float(row['Total']) if pd.notna(row['Total']) else 0.0
                })

        grand_total_qty = 0
        grand_total_val = 0.0

        # Criar buffer para o novo arquivo Excel altamente estilizado
        buffer = io.BytesIO()
        
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            workbook  = writer.book
            worksheet = workbook.add_worksheet('Trocas Formatado')
            worksheet.hide_gridlines(2) # Mostra as linhas de grade normais

            # --- DEFINIÇÃO DOS FORMATOS ESTILO MODELO ---
            fmt_header = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': 'black', 'font_name': 'Arial', 'font_size': 11, 'align': 'center'})
            fmt_supplier = workbook.add_format({'bold': True, 'font_color': 'red', 'font_name': 'Arial', 'font_size': 14})
            fmt_product = workbook.add_format({'font_name': 'Arial', 'font_size': 10})
            fmt_code_date = workbook.add_format({'font_name': 'Arial', 'font_size': 10, 'align': 'center'})
            fmt_qty = workbook.add_format({'font_name': 'Arial', 'font_size': 10, 'num_format': '#,##0', 'align': 'center'})
            fmt_money = workbook.add_format({'font_name': 'Arial', 'font_size': 10, 'num_format': 'R$ #,##0.00'})
            
            fmt_subtotal = workbook.add_format({'bold': True, 'font_color': 'red', 'font_name': 'Arial', 'font_size': 11})
            fmt_subtotal_qty = workbook.add_format({'bold': True, 'font_color': 'red', 'font_name': 'Arial', 'font_size': 11, 'num_format': '#,##0', 'align': 'center'})
            fmt_subtotal_val = workbook.add_format({'bold': True, 'font_color': 'red', 'font_name': 'Arial', 'font_size': 11, 'num_format': 'R$ #,##0.00'})
            
            fmt_grand_total = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': 'red', 'font_name': 'Arial', 'font_size': 12})
            fmt_grand_qty = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': 'red', 'font_name': 'Arial', 'font_size': 12, 'num_format': '#,##0', 'align': 'center'})
            fmt_grand_val = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': 'red', 'font_name': 'Arial', 'font_size': 12, 'num_format': 'R$ #,##0.00'})

            # Escrever o cabeçalho principal no Excel
            headers = ["Fornecedor / Produto", "Código Interno", "Última Compra", "Estoque", "Total"]
            for col_num, header in enumerate(headers):
                worksheet.write(0, col_num, header, fmt_header)

            excel_row = 1

            # Renderização na tela e construção do Excel em paralelo
            for supplier, products in suppliers_dict.items():
                st.markdown(f'<div class="supplier-header">{supplier.upper()}</div>', unsafe_allow_html=True)
                
                # Excel: Linha do fornecedor (Vermelho, Negrito, Maior)
                worksheet.write(excel_row, 0, supplier.upper(), fmt_supplier)
                excel_row += 1

                sub_qty = 0
                sub_val = 0.0

                for p in products:
                    # Excel: Dados dos produtos
                    worksheet.write(excel_row, 0, p['Produto'], fmt_product)
                    worksheet.write(excel_row, 1, p['Código Interno'], fmt_code_date)
                    worksheet.write(excel_row, 2, p['Última Compra'], fmt_code_date)
                    worksheet.write(excel_row, 3, p['Estoque'], fmt_qty)
                    worksheet.write(excel_row, 4, p['Total'], fmt_money)
                    
                    sub_qty += p['Estoque']
                    sub_val += p['Total']
                    excel_row += 1

                grand_total_qty += sub_qty
                grand_total_val += sub_val

                # Tela: Exibição da tabela e subtotal
                prod_df = pd.DataFrame(products)
                view_df = prod_df.copy()
                view_df['Total'] = view_df['Total'].map('R$ {:,.2f}'.format)
                st.dataframe(view_df, use_container_width=True, hide_index=True)
                st.markdown(f'<div class="total-supplier">TOTAL {supplier.upper()}: {sub_qty} itens — R$ {sub_val:,.2f}</div>', unsafe_allow_html=True)

                # Excel: Linha do subtotal do fornecedor (Vermelho e Negrito)
                worksheet.write(excel_row, 0, f"TOTAL {supplier.upper()}", fmt_subtotal)
                worksheet.write(excel_row, 3, sub_qty, fmt_subtotal_qty)
                worksheet.write(excel_row, 4, sub_val, fmt_subtotal_val)
                
                # Excel: Pula uma linha em branco para espaçamento
                excel_row += 2

            # Excel: Linha do Total Geral Absoluto no fim
            worksheet.write(excel_row, 0, "TOTAL GERAL DOS FORNECEDORES", fmt_grand_total)
            worksheet.write(excel_row, 1, "", fmt_grand_total)
            worksheet.write(excel_row, 2, "", fmt_grand_total)
            worksheet.write(excel_row, 3, grand_total_qty, fmt_grand_qty)
            worksheet.write(excel_row, 4, grand_total_val, fmt_grand_val)

            # Ajustar a largura das colunas do Excel automaticamente
            worksheet.set_column(0, 0, 45) # Coluna de produtos mais larga
            worksheet.set_column(1, 4, 15) # Outras colunas tamanho padrão

        # Tela: Caixa final de resumo
        st.markdown(f'<div class="grand-total-box">TOTAL GERAL DOS FORNECEDORES<br>Estoque: {grand_total_qty} | R$ {grand_total_val:,.2f}</div>', unsafe_allow_html=True)

        # Barra lateral de ações
        st.sidebar.markdown("### 📥 Ações")
        st.sidebar.download_button(
            label="💾 Exportar para Excel (.xlsx)",
            data=buffer.getvalue(),
            file_name="Relatorio_Trocas_Formatado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # Correção estável do botão de impressão via injeção HTML limpa
        st.sidebar.markdown("""
            <script>
            function docPrint() { window.print(); }
            </script>
            <button onclick="window.print()" style="width:100%; padding:10px; background-color:#0078d4; color:white; border:none; border-radius:4px; font-weight:bold; cursor:pointer;">🖨️ Imprimir Relatório</button>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Erro ao processar a planilha: {e}")
