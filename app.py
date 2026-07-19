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

        # Geração do arquivo Excel totalmente via XlsxWriter (Risco zero de perder formatação)
        buffer = io.BytesIO()
        workbook = io.BytesIO()
        
        # Inicializando o construtor direto no buffer
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            wb = writer.book
            ws = wb.add_worksheet('Trocas Formatado')
            ws.hide_gridlines(2) # Garante que as linhas de grade fiquem visíveis no Excel do celular

            # --- CRITÉRIOS DE FORMATAÇÃO E DESIGN ---
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

            # Gravando o cabeçalho preto da tabela
            headers = ["Fornecedor / Produto", "Código Interno", "Última Compra", "Estoque", "Total"]
            for col_num, header in enumerate(headers):
                ws.write(0, col_num, header, fmt_header)

            row_idx = 1

            # Processamento em paralelo (Visualização na Tela + Geração do Excel Estilizado)
            for supplier, products in suppliers_dict.items():
                st.markdown(f'<div class="supplier-header">{supplier.upper()}</div>', unsafe_allow_html=True)
                
                # Excel: Linha do Fornecedor Destacada (Vermelho, Negrito, Fonte maior)
                ws.write(row_idx, 0, supplier.upper(), fmt_supplier)
                row_idx += 1

                sub_qty = 0
                sub_val = 0.0

                for p in products:
                    # Excel: Escrita célula por célula do produto para fixar os formatos individuais
                    ws.write(row_idx, 0, p['Produto'], fmt_product)
                    ws.write(row_idx, 1, p['Código Interno'], fmt_center)
                    ws.write(row_idx, 2, p['Última Compra'], fmt_center)
                    ws.write(row_idx, 3, p['Estoque'], fmt_qty)
                    ws.write(row_idx, 4, p['Total'], fmt_money)
                    
                    sub_qty += p['Estoque']
                    sub_val += p['Total']
                    row_idx += 1

                grand_total_qty += sub_qty
                grand_total_val += sub_val

                # Renderizando as tabelas dinâmicas do Streamlit na tela
                prod_df = pd.DataFrame(products)
                view_df = prod_df.copy()
                view_df['Total'] = view_df['Total'].map('R$ {:,.2f}'.format)
                st.dataframe(view_df, use_container_width=True, hide_index=True)
                st.markdown(f'<div class="total-supplier">TOTAL {supplier.upper()}: {sub_qty} itens — R$ {sub_val:,.2f}</div>', unsafe_allow_html=True)

                # Excel: Linha do Subtotal (Vermelho e Negrito)
                ws.write(row_idx, 0, f"TOTAL {supplier.upper()}", fmt_subtotal)
                ws.write(row_idx, 3, sub_qty, fmt_sub_qty)
                ws.write(row_idx, 4, sub_val, fmt_sub_val)
                
                # Excel: Pula a linha em branco de espaçamento regulamentar
                row_idx += 2

            # Excel: Fechamento com o Total Geral Consolidado de tudo
            ws.write(row_idx, 0, "TOTAL GERAL DOS FORNECEDORES", fmt_grand)
            ws.write(row_idx, 1, "", fmt_grand)
            ws.write(row_idx, 2, "", fmt_grand)
            ws.write(row_idx, 3, grand_total_qty, fmt_grand_qty)
            ws.write(row_idx, 4, grand_total_val, fmt_grand_val)

            # Redimensionamento inteligente das colunas no Excel gerado
            ws.set_column(0, 0, 45)
            ws.set_column(1, 4, 15)

        # Tela: Caixa final de resumo geral
        st.markdown(f'<div class="grand-total-box">TOTAL GERAL DOS FORNECEDORES<br>Estoque: {grand_total_qty} | R$ {grand_total_val:,.2f}</div>', unsafe_allow_html=True)

        # Configurações do Menu Lateral de Ações
        st.sidebar.markdown("### 📥 Ações")
        st.sidebar.download_button(
            label="💾 Exportar para Excel (.xlsx)",
            data=buffer.getvalue(),
            file_name="Relatorio_Trocas_Formatado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # Correção definitiva da Impressão: Quebra o isolamento do iframe chamando a janela mãe do navegador (parent)
        st.sidebar.markdown("""
            <button onclick="parent.window.print()" style="width:100%; padding:12px; background-color:#0078d4; color:white; border:none; border-radius:4px; font-weight:bold; cursor:pointer; font-size:14px;">🖨️ Imprimir Relatório</button>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Erro no processamento dos dados: {e}")
