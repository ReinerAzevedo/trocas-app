import streamlit as st
import pandas as pd
import io
from datetime import datetime

# Configuração de página
st.set_page_config(
    page_title="Gerenciador de Trocas v2.7", 
    page_icon="🔄", 
    layout="wide"
)

# Estilização CSS
st.markdown("""
    <style>
    .version-header {
        font-size: 11px !important;
        color: #777777 !important;
        text-align: right;
        margin-bottom: 10px;
    }
    .supplier-header {
        color: #FF0000 !important;
        font-weight: bold !important;
        font-size: 18px !important;
        margin-top: 20px !important;
        margin-bottom: 5px !important;
    }
    .total-supplier {
        color: #FF0000 !important;
        font-weight: bold !important;
        font-size: 15px !important;
        margin-top: 5px !important;
        margin-bottom: 20px !important;
        border-bottom: 2px solid #FF0000;
        padding-bottom: 8px;
    }
    .grand-total-box {
        background-color: #FF0000 !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        font-size: 20px !important;
        padding: 12px !important;
        border-radius: 5px !important;
        text-align: center !important;
        margin-top: 20px !important;
    }
    .dept-tag {
        font-size: 11px !important;
        font-weight: bold !important;
        color: #555555 !important;
        background-color: #eeeeee !important;
        padding: 2px 6px !important;
        border-radius: 3px !important;
        margin-left: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Cabeçalho de Versão
versao_app = "v2.7"
if 'data_compilacao' not in st.session_state:
    st.session_state['data_compilacao'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

st.markdown(f'<div class="version-header">Versão: {versao_app} | Painel Ativo desde: {st.session_state["data_compilacao"]}</div>', unsafe_allow_html=True)
st.title("🔄 Conversor de Planilhas de Trocas")

# Inicialização do Session State
if 'suppliers_dict' not in st.session_state:
    st.session_state['suppliers_dict'] = None
if 'filtro_depto' not in st.session_state:
    st.session_state['filtro_depto'] = "Ambas"
if 'selected_sups' not in st.session_state:
    st.session_state['selected_sups'] = set()
if 'data_planilha_bruta' not in st.session_state:
    st.session_state['data_planilha_bruta'] = "Não identificada"

# Botão de limpar painel
if st.session_state['suppliers_dict'] is not None:
    if st.sidebar.button("🗑️ Limpar Painel / Novo Upload", use_container_width=True):
        # Remove todas as chaves dinamicas salvas dos checkboxes
        for k in list(st.session_state.keys()):
            if k.startswith("cb_"):
                del st.session_state[k]
        st.session_state['suppliers_dict'] = None
        st.session_state['selected_sups'] = set()
        st.session_state['data_compilacao'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        st.session_state['data_planilha_bruta'] = "Não identificada"
        st.rerun()

# --- ÁREA DE UPLOAD ---
if st.session_state['suppliers_dict'] is None:
    st.write("Faça o upload das planilhas brutas de Mercearia e/ou Perecíveis:")
    col1, col2 = st.columns(2)
    with col1:
        file_mercearia = st.file_uploader("Planilha MERCEARIA (.xlsx)", type=["xlsx"], key="merc")
    with col2:
        file_pereciveis = st.file_uploader("Planilha PERECÍVEIS (.xlsx)", type=["xlsx"], key="perec")

    if file_mercearia or file_pereciveis:
        if st.button("🚀 Processar Planilhas Anexadas", use_container_width=True):
            temp_dict = {}
            datas_encontradas = []
            
            def ler_planilha(uploaded_file, depto_name):
                df = pd.read_excel(uploaded_file, sheet_name=0)
                try:
                    for r in range(min(15, len(df))):
                        linha_str = " ".join([str(val) for val in df.iloc[r].values if pd.notna(val)])
                        if "Data" in linha_str or "Emissão" in linha_str or "Periodo" in linha_str:
                            datas_encontradas.append(linha_str)
                except:
                    pass

                df_clean = df.iloc[16:].copy()
                df_clean.columns = df_clean.iloc[0]
                df_clean = df_clean.iloc[1:].reset_index(drop=True)

                current_supplier = None
                for idx, row in df_clean.iterrows():
                    f = row['Fornecedor']
                    if pd.notna(f):
                        current_supplier = str(f).strip().upper()
                    if pd.notna(row['Código Interno']):
                        if current_supplier not in temp_dict:
                            temp_dict[current_supplier] = []
                        
                        data_compra = str(row['Última Compra']).split()[0] if pd.notna(row['Última Compra']) else ""
                        
                        temp_dict[current_supplier].append({
                            'Produto': row['Produto'],
                            'Código Interno': int(row['Código Interno']),
                            'Última Compra': data_compra,
                            'Estoque': int(row['Estoque']) if pd.notna(row['Estoque']) else 0,
                            'Total': float(row['Total']) if pd.notna(row['Total']) else 0.0,
                            'Departamento': depto_name
                        })

            if file_mercearia: ler_planilha(file_mercearia, "MERCEARIA")
            if file_pereciveis: ler_planilha(file_pereciveis, "PERECÍVEIS")

            if temp_dict:
                st.session_state['suppliers_dict'] = dict(sorted(temp_dict.items()))
                st.session_state['selected_sups'] = set(temp_dict.keys())
                
                # Força o estado visual de todas as chaves dos checkboxes como True no upload
                for sup_name in temp_dict.keys():
                    st.session_state[f"cb_{sup_name}"] = True
                
                if datas_encontradas:
                    st.session_state['data_planilha_bruta'] = datas_encontradas[0]
                else:
                    st.session_state['data_planilha_bruta'] = datetime.now().strftime("%d/%m/%Y")
                    
                st.rerun()

# --- RENDERIZAÇÃO E FILTROS ---
if st.session_state['suppliers_dict'] is not None:
    suppliers_dict_full = st.session_state['suppliers_dict']

    # 1. Filtro Superior por Botões (Mercearia / Perecíveis / Ambas)
    st.markdown("### 🎯 Filtrar Departamento View:")
    f_col1, f_col2, f_col3 = st.columns(3)
    
    if f_col1.button("🏢 MERCEARIA", use_container_width=True):
        st.session_state['filtro_depto'] = "MERCEARIA"
    if f_col2.button("🥩 PERECÍVEIS", use_container_width=True):
        st.session_state['filtro_depto'] = "PERECÍVEIS"
    if f_col3.button("🔄 AMBAS PLANILHAS", use_container_width=True):
        st.session_state['filtro_depto'] = "Ambas"

    st.info(f"Visualizando: **{st.session_state['filtro_depto']}** | Data Referência da Planilha: **{st.session_state['data_planilha_bruta']}**")

    # 2. BARRA LATERAL: BUSCA E CHECKBOXES SINCRONIZADOS
    st.sidebar.markdown("### 📋 Selecionar Fornecedores")
    
    busca = st.sidebar.text_input("🔍 Buscar fornecedor:", "", placeholder="Digite o nome...", key="txt_busca").strip().upper()

    # Identifica fornecedores visíveis pela busca atual
    sups_visiveis_side = []
    for sup_name, items in suppliers_dict_full.items():
        depto = items[0]['Departamento']
        if st.session_state['filtro_depto'] == "Ambas" or depto == st.session_state['filtro_depto']:
            if busca == "" or busca in sup_name:
                sups_visiveis_side.append(sup_name)

    # Callbacks corrigidos para sincronizar o visual dos checkboxes e o conjunto de seleções
    def marcar_visiveis():
        for s in sups_visiveis_side:
            st.session_state[f"cb_{s}"] = True
            st.session_state['selected_sups'].add(s)

    def desmarcar_visiveis():
        for s in sups_visiveis_side:
            st.session_state[f"cb_{s}"] = False
            st.session_state['selected_sups'].discard(s)

    btn_col1, btn_col2 = st.sidebar.columns(2)
    btn_col1.button("✅ Marcar Exibidos", on_click=marcar_visiveis, use_container_width=True)
    btn_col2.button("❌ Desmarcar", on_click=desmarcar_visiveis, use_container_width=True)

    st.sidebar.caption(f"Selecionados acumulados: **{len(st.session_state['selected_sups'])}** de {len(suppliers_dict_full)}")
    st.sidebar.markdown("---")

    # Renderiza os checkboxes associando a chave visual de forma direta
    for sup_name in sups_visiveis_side:
        depto = suppliers_dict_full[sup_name][0]['Departamento']
        
        # Garante inicialização da chave visual caso seja um fornecedor novo
        if f"cb_{sup_name}" not in st.session_state:
            st.session_state[f"cb_{sup_name}"] = (sup_name in st.session_state['selected_sups'])

        def on_change_cb(name=sup_name):
            if st.session_state[f"cb_{name}"]:
                st.session_state['selected_sups'].add(name)
            else:
                st.session_state['selected_sups'].discard(name)

        st.sidebar.checkbox(
            f"{sup_name} ({depto[0]})", 
            key=f"cb_{sup_name}",
            on_change=on_change_cb
        )

    # Base filtrada real acumulada
    suppliers_filtered = {
        k: v for k, v in suppliers_dict_full.items() 
        if k in st.session_state['selected_sups'] and (st.session_state['filtro_depto'] == "Ambas" or v[0]['Departamento'] == st.session_state['filtro_depto'])
    }

    # 3. Totais por Departamento
    tot_merc_qty, tot_merc_val = 0, 0.0
    tot_perec_qty, tot_perec_val = 0, 0.0

    for s_name, products in suppliers_filtered.items():
        for p in products:
            if p['Departamento'] == "MERCEARIA":
                tot_merc_qty += p['Estoque']
                tot_merc_val += p['Total']
            elif p['Departamento'] == "PERECÍVEIS":
                tot_perec_qty += p['Estoque']
                tot_perec_val += p['Total']

    # Cartões de Resumo
    c_tot1, c_tot2, c_tot3 = st.columns(3)
    
    if st.session_state['filtro_depto'] in ["AMBAS", "Ambas", "MERCEARIA"] and tot_merc_qty > 0:
        c_tot1.metric("Total Mercearia", f"R$ {tot_merc_val:,.2f}", f"{tot_merc_qty} itens")
        
    if st.session_state['filtro_depto'] in ["AMBAS", "Ambas", "PERECÍVEIS"] and tot_perec_qty > 0:
        c_tot2.metric("Total Perecíveis", f"R$ {tot_perec_val:,.2f}", f"{tot_perec_qty} itens")
        
    if st.session_state['filtro_depto'] == "Ambas" and (tot_merc_qty > 0 and tot_perec_qty > 0):
        c_tot3.metric("TOTAL GERAL CONSOLIDADO", f"R$ {(tot_merc_val + tot_perec_val):,.2f}", f"{tot_merc_qty + tot_perec_qty} itens")

    st.markdown("---")

    # 4. GERAÇÃO DOS ARQUIVOS (EXCEL E HTML)
    buffer_excel = io.BytesIO()
    grand_total_qty = 0
    grand_total_val = 0.0

    with pd.ExcelWriter(buffer_excel, engine='xlsxwriter') as writer:
        wb = writer.book
        ws = wb.add_worksheet('Trocas Formatado')
        ws.hide_gridlines(2)

        fmt_header = wb.add_format({'bold': True, 'font_color': 'white', 'bg_color': 'black', 'font_name': 'Arial', 'font_size': 11})
        fmt_header_c = wb.add_format({'bold': True, 'font_color': 'white', 'bg_color': 'black', 'font_name': 'Arial', 'font_size': 11, 'align': 'center'})
        fmt_supplier = wb.add_format({'bold': True, 'font_color': '#FF0000', 'font_name': 'Arial', 'font_size': 11})
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

        ws.write(0, 0, "Fornecedor / Produto", fmt_header)
        ws.write(0, 1, "Código Interno", fmt_header_c)
        ws.write(0, 2, "Última Compra", fmt_header_c)
        ws.write(0, 3, "Estoque", fmt_header_c)
        ws.write(0, 4, "Total", fmt_header_c)

        excel_row = 1

        html_print = f"""<html><head><meta charset='utf-8'><style>
            body {{ font-family: Arial; padding: 20px; }}
            .v-info {{ font-size: 10px; color: #666; text-align: right; margin-bottom: 10px; }}
            h1 {{ font-size: 18px; text-align: center; margin-bottom: 5px; }}
            h3 {{ font-size: 11px; text-align: center; margin-bottom: 20px; font-weight: normal; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
            th {{ background: black; color: white; padding: 8px; font-size: 11px; border: 1px solid black; text-align: left; }}
            td {{ padding: 6px; font-size: 11px; border: 1px solid #ccc; }}
            .sup {{ color: red; font-weight: bold; font-size: 14px; padding-top: 15px; border: none; }}
            .sub {{ color: red; font-weight: bold; font-size: 12px; border-bottom: 2px solid red; }}
            .grand {{ background: red; color: white; font-weight: bold; font-size: 13px; }}
            .center {{ text-align: center; }} .right {{ text-align: right; }}
            .tag {{ font-size: 9px; background: #eee; color: #333; padding: 2px 5px; margin-left: 5px; border-radius: 3px; font-weight: normal; }}
        </style></head><body onload='window.print()'>
        <div class="v-info">Versão: {versao_app} | Processado em: {st.session_state["data_compilacao"]}</div>
        <h1>Relatório Selecionado de Estoque de Trocas</h1>
        <h3><b>Data da Planilha Bruta:</b> {st.session_state['data_planilha_bruta']} | <b>Filtro:</b> {st.session_state['filtro_depto']} | <b>Loja:</b> LU 10-MONGAGUA</h3>
        <table><thead><tr><th>Fornecedor / Produto</th><th>Código Interno</th><th>Última Compra</th><th class='center'>Estoque</th><th class='right'>Total</th></tr></thead><tbody>"""

        for supplier, products in suppliers_filtered.items():
            depto_tag = products[0]['Departamento']
            st.markdown(f'<div class="supplier-header">{supplier.upper()} <span class="dept-tag">{depto_tag}</span></div>', unsafe_allow_html=True)
            
            ws.write(excel_row, 0, supplier.upper(), fmt_supplier)
            html_print += f"<tr><td colspan='5' class='sup'>{supplier.upper()} <span class='tag'>{depto_tag}</span></td></tr>"
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

            prod_df = pd.DataFrame(products)[['Produto', 'Código Interno', 'Última Compra', 'Estoque', 'Total']]
            view_df = prod_df.copy()
            view_df['Total'] = view_df['Total'].map('R$ {:,.2f}'.format)
            st.dataframe(view_df, use_container_width=True, hide_index=True)
            st.markdown(f'<div class="total-supplier">TOTAL {supplier.upper()}: {sub_qty} itens — R$ {sub_val:,.2f}</div>', unsafe_allow_html=True)

            ws.write(excel_row, 0, f"TOTAL {supplier.upper()}", fmt_subtotal)
            ws.write(excel_row, 3, sub_qty, fmt_sub_qty)
            ws.write(excel_row, 4, sub_val, fmt_sub_val)
            
            html_print += f"<tr class='sub'><td>TOTAL {supplier.upper()}</td><td></td><td></td><td class='center'>{sub_qty}</td><td class='right'>R$ {sub_val:,.2f}</td></tr>"
            excel_row += 2

        ws.write(excel_row, 0, "TOTAL GERAL DOS SELECIONADOS", fmt_grand)
        ws.write(excel_row, 1, "", fmt_grand)
        ws.write(excel_row, 2, "", fmt_grand)
        ws.write(excel_row, 3, grand_total_qty, fmt_grand_qty)
        ws.write(excel_row, 4, grand_total_val, fmt_grand_val)
        
        html_print += f"<tr class='grand'><td style='padding:8px;'>TOTAL GERAL DOS SELECIONADOS</td><td></td><td></td><td class='center'>{grand_total_qty}</td><td class='right'>R$ {grand_total_val:,.2f}</td></tr>"
        html_print += "</tbody></table></body></html>"

        ws.set_column(0, 0, 45)
        ws.set_column(1, 4, 15)

    st.markdown(f'<div class="grand-total-box">TOTAL GERAL DOS SELECIONADOS<br>Estoque: {grand_total_qty} | R$ {grand_total_val:,.2f}</div>', unsafe_allow_html=True)

    # Menu Lateral de Ações
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📥 Ações")
    st.sidebar.download_button(
        label="💾 Exportar Seleção para Excel",
        data=buffer_excel.getvalue(),
        file_name="Relatorio_Trocas_Filtrado.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
    
    st.sidebar.download_button(
        label="🖨️ Imprimir Seleção (PDF)",
        data=html_print,
        file_name="Imprimir_Relatorio_Filtrado.html",
        mime="text/html",
        use_container_width=True
    )
