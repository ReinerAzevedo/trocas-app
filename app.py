import streamlit as st
import pandas as pd
import io

# Configuração estável de layout
st.set_page_config(
    page_title="Gerenciador de Trocas", 
    page_icon="🔄", 
    layout="centered"
)

# Estilização CSS para a visualização na tela do celular/PC
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
        # Leitura exata da planilha do sistema
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

        # Início do buffer para a exportação do Excel
        buffer_excel = io.BytesIO()
        
        with pd.ExcelWriter(buffer_excel, engine='xlsxwriter') as writer:
            wb = writer.book
            ws = wb.add_worksheet('Trocas Formatado')
            ws.hide_gridlines(2)

            # Formatos do Excel
            fmt_header = wb.add_format({'bold': True, 'font_color': 'white', 'bg_color': 'black', 'font_name': 'Arial', 'font_size': 11, 'align': 'center'})
            fmt_supplier = wb.add_format({'bold': True, 'font_color': '#FF0000', 'font_name': 'Arial', 'font_size': 14})
            fmt_product = wb.add_format({'font_name': 'Arial', 'font_size': 10})
            fmt_center = wb.add_format({'font_name': 'Arial', 'font_size': 10, 'align': 'center'})
            fmt_qty = wb.add_format({'font_name': 'Arial', 'font_size': 10, 'num_format': '#,##0', 'align': 'center'})
            fmt_money = wb.add_format({'font_name': 'Arial', 'font_size': 10, 'num_format': 'R$ #,##0.00'})
            fmt_subtotal = wb.add_format({'bold': True, 'font_color': '#FF0000', 'font_name': 'Arial', 'font_size': 11})
            fmt_sub_qty = wb.add_format({'bold': True, 'font_color': '#FF0000', 'font_name': 'Arial', 'font_size': 11, 'num_format': '#,##0', 'align': 'center'})
            fmt_sub_val = wb.add_format({'bold': True, 'font_color': '#FF0000', 'font_name': 'Arial', 'font_size': 11, 'num_format': 'R$ #,##0.00'})
            fmt_grand = wb.add_format({'bold': True, 'font_color': 'white', 'bg_color': '#FF0000', 'font_name': 'Arial', 'font_size': 12})
            fmt_grand_qty = wb.add_format({'bold': True, 'font_color': 'white', 'bg_color': '#FF0000', 'font_name': 'Arial', 'font_size': 12, 'num_format': '#,##0', 'align': 'center'})
            fmt_grand_val = wb.add_format({'bold': True, 'font_color': 'white', 'bg_color': '#FF0000', 'font_name': 'Arial', 'font_size': 12, 'num_format': 'R$ #,##0.00'})

            headers = ["Fornecedor / Produto", "Código Interno", "Última Compra", "Estoque", "Total"]
            for col_num, header in enumerate(headers):
                ws.write(0, col_num, header, fmt_header)

            excel_row = 1

            # --- INÍCIO DA MONTAGEM DO HTML DE IMPRESSÃO ---
            html_print = """<html><head><meta charset='utf-8'><style>
                body { font-family: Arial; padding: 20px; }
                h1 { font-size: 18px; text-align: center; margin-bottom: 20px; }
                table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
                th { background: black; color: white; padding: 8px; font-size: 11px; border: 1px solid black; text-align: left; }
                td { padding: 6px; font-size: 11px; border: 1px solid #ccc; }
                .sup { color: red; font-weight: bold; font-size: 14px; padding-top: 15px; border: none; }
                .sub { color: red; font-weight: bold; font-size: 12px; border-bottom: 2px solid red; }
                .grand { background: red; color: white; font-weight: bold; font-size: 13px; }
                .center { text-align: center; } .right { text-align: right; }
            </style></head><body onload='window.print()'>
            <h1>Relatório de Estoque de Trocas por Fornecedor ou Produto</h1>
            <table><thead><tr><th>Fornecedor / Produto</th><th>Código Interno</th><th>Última Compra</th><th class='center'>Estoque</th><th class='right'>Total</th></tr></thead><tbody>"""

            for supplier, products in suppliers_dict.items():
                # Interface Tela
                st.markdown(f'<div class="supplier-header">{supplier.upper()}</div>', unsafe_allow_html=True)
                
                # Excel & HTML Impressão
                ws.write(excel_row, 0, supplier.upper(), fmt_supplier)
                html_print += f"<tr><td colspan='5' class='sup'>{supplier.upper()}</td></tr>"
                excel_row += 1

                sub_qty = 0
                sub_val = 0.0

                for p in products:
                    ws.write(excel_row, 0, p['Produto'], fmt_product)
                    ws.write(excel_row, 1, p['Código Interno'], fmt_center)
                    ws.write(excel_row, 2, p['Última Compra'], fmt_center)
                    ws.write(excel_row, 3, p['Estoque'], fmt_qty)
                    ws.write(excel_row, 4, p['Total'], fmt_money)
                    
                    html_print += f"<tr><td>{p['Produto']}</td><td class='center'>{p['Código Interno']}</td><td class='center'>{p['Última Compra']}</td><td class='center'>{p['Estoque']}</td><td class='right'>R$ {p['Total']:,.2f}</td></tr>"
                    
                    sub_qty += p['Estoque']
                    sub_val += p['Total']
                    excel_row += 1

                grand_total_qty += sub_qty
                grand_total_val += sub_val

                # Dataframe Tela
                prod_df = pd.DataFrame(products)
                view_df = prod_df.copy()
                view_df['Total'] = view_df['Total'].map('R$ {:,.2f}'.format)
                st.dataframe(view_df, use_container_width=True, hide_index=True)
                st.markdown(f'<div class="total-supplier">TOTAL {supplier.upper()}: {sub_qty} itens — R$ {sub_val:,.2f}</div>', unsafe_allow_html=True)

                # Subtotal no Excel & HTML Impressão
                ws.write(excel_row, 0, f"TOTAL {supplier.upper()}", fmt_subtotal)
                ws.write(excel_row, 3, sub_qty, fmt_sub_qty)
                ws.write(excel_row, 4, sub_val, fmt_sub_val)
                
                html_print += f"<tr class='sub'><td>TOTAL {supplier.upper()}</td><td></td><td></td><td class='center'>{sub_qty}</td><td class='right'>R$ {sub_val:,.2f}</td></tr>"
                
                excel_row += 2

            # Total Geral no Excel & HTML Impressão
            ws.write(excel_row, 0, "TOTAL GERAL DOS FORNECEDORES", fmt_grand)
            ws.write(excel_row, 1, "", fmt_grand)
            ws.write(excel_row, 2, "", fmt_grand)
            ws.write(excel_row, 3, grand_total_qty, fmt_grand_qty)
            ws.write(excel_row, 4, grand_total_val, fmt_grand_val)
            
            html_print += f"<tr class='grand'><td style='padding:8px;'>TOTAL GERAL DOS FORNECEDORES</td><td></td><td></td><td class='center'>{grand_total_qty}</td><td class='right'>R$ {grand_total_val:,.2f}</td></tr>"
            html_print += "</tbody></table></body></html>"

            ws.set_column(0, 0, 45)
            ws.set_column(1, 4, 15)

        # Caixa final de resumo na tela
        st.markdown(f'<div class="grand-total-box">TOTAL GERAL DOS FORNECEDORES<br>Estoque: {grand_total_qty} | R$ {grand_total_val:,.2f}</div>', unsafe_allow_html=True)

        # Barra lateral de ações estáveis
        st.sidebar.markdown("### 📥 Ações")
        st.sidebar.download_button(
            label="💾 Exportar para Excel (.xlsx)",
            data=buffer_excel.getvalue(),
            file_name="Relatorio_Trocas_Formatado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # SOLUÇÃO COMPATÍVEL MOBILE: Baixar o espelho HTML que dispara a impressão nativa ao abrir
        st.sidebar.download_button(
            label="🖨️ Imprimir / Gerar PDF",
            data=html_print,
            file_name="Imprimir_Relatorio_Trocas.html",
            mime="text/html"
        )

    except Exception as e:
        st.error(f"Erro no processamento dos dados: {e}")
