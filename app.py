import streamlit as st
import pandas as pd
import io
import re
from datetime import datetime

# Configuração de página
st.set_page_config(
    page_title="Gerenciador de Trocas v4.1", 
    page_icon="🔄", 
    layout="wide"
)

# Estilização CSS completa com seletores genéricos diretos para garantir a aplicação de cores
st.markdown("""
    <style>
    .version-header {
        font-size: 11px !important;
        color: #777777 !important;
        text-align: right;
        margin-bottom: 5px;
    }
    .supplier-header {
        color: #FF0000 !important;
        font-weight: bold !important;
        font-size: 16px !important;
        margin-top: 12px !important;
        margin-bottom: 2px !important;
    }
    .total-supplier {
        color: #FF0000 !important;
        font-weight: bold !important;
        font-size: 14px !important;
        margin-top: 2px !important;
        margin-bottom: 8px !important;
        border-bottom: 2px solid #FF0000;
        padding-bottom: 4px;
    }
    .grand-total-box {
        background-color: #FF0000 !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        font-size: 18px !important;
        padding: 8px !important;
        border-radius: 5px !important;
        text-align: center !important;
        margin-top: 15px !important;
    }
    .dept-tag {
        font-size: 10px !important;
        font-weight: bold !important;
        color: #555555 !important;
        background-color: #eeeeee !important;
        padding: 2px 5px !important;
        border-radius: 3px !important;
        margin-left: 5px !important;
    }

    /* UPLOAD CARDS DESTACADOS */
    .upload-card-merc {
        border: 2px solid #1E88E5;
        background-color: #f0f7ff;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .upload-card-perec {
        border: 2px solid #E53935;
        background-color: #fff5f5;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 10px;
    }

    /* 1. BOTÃO DE PROCESSAR PLANILHAS (TELA INICIAL) */
    .btn-processar button {
        background-color: #2E7D32 !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 16px !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 8px !important;
    }

    /* 2. BOTÕES DE FILTRO DE DEPARTAMENTO (TOPO) */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button {
        background-color: #1E88E5 !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 6px !important;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {
        background-color: #E53935 !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 6px !important;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) button {
        background-color: #6A1B9A !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 6px !important;
    }

    /* 3. BOTÕES DA BARRA LATERAL (USA ENVOLTÓRIOS DIV EXCLUSIVOS PARA NÃO FALHAR) */
    .btn-limpar button {
        background-color: #D32F2F !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        border: none !important;
    }

    .btn-marcar button {
        background-color: #2E7D32 !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
    }
    .btn-desmarcar button {
        background-color: #455A64 !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
    }

    .btn-excel button {
        background-color: #107C41 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        border: none !important;
    }

    .btn-wsp button {
        background-color: #25D366 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        border: none !important;
    }

    /* Cópia Rápida Expander Header */
    div[data-testid="stSidebar"] details {
        border: 2px solid #00838F !important;
        background-color: #e0f7fa !important;
        border-radius: 6px !important;
    }

    /* 4. BOTÕES POR FORNECEDOR (PAINEL CENTRAL) */
    .btn-relatorio-ind button {
        background-color: #1565C0 !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 6px !important;
    }
    .btn-recibo-ind button {
        background-color: #D84315 !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 6px !important;
    }

    @media (max-width: 600px) {
        .stButton>button { width: 100% !important; padding: 4px !important; }
        .supplier-header { font-size: 15px !important; }
        .total-supplier { font-size: 13px !important; }
    }
    </style>
""", unsafe_allow_html=True)

# Cabeçalho de Versão
versao_app = "v4.1"
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
if 'usuario_planilha' not in st.session_state:
    st.session_state['usuario_planilha'] = "reinerca"
if 'data_planilha_bruta' not in st.session_state:
    st.session_state['data_planilha_bruta'] = "Não identificada"

# --- ÁREA DE UPLOAD COM DESTACADOS ---
if st.session_state['suppliers_dict'] is None:
    st.write("Faça o upload das planilhas brutas de Mercearia e/ou Perecíveis:")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="upload-card-merc"><b>🛒 MERCEARIA (Planilha Bruta)</b></div>', unsafe_allow_html=True)
        file_mercearia = st.file_uploader("Anexar Mercearia (.xlsx)", type=["xlsx"], key="merc")
        
    with col2:
        st.markdown('<div class="upload-card-perec"><b>🥩 PERECÍVEIS (Planilha Bruta)</b></div>', unsafe_allow_html=True)
        file_pereciveis = st.file_uploader("Anexar Perecíveis (.xlsx)", type=["xlsx"], key="perec")

    if file_mercearia or file_pereciveis:
        st.markdown('<div class="btn-processar">', unsafe_allow_html=True)
        if st.button("🚀 Processar Planilhas Anexadas", use_container_width=True):
            temp_dict = {}
            extracted_info = {'user': None, 'date': None}
            
            def ler_planilha(uploaded_file, depto_name):
                try:
                    df_head = pd.read_excel(uploaded_file, header=None, nrows=16)
                    for r in range(len(df_head)):
                        for c in range(len(df_head.columns)):
                            val = str(df_head.iat[r, c])
                            if ("Usuário:" in val or "Usuario:" in val or "reinerca" in val) and not extracted_info['user']:
                                m_user = re.search(r'Usu[áa]rio:\s*([^\s-]+)', val, re.IGNORECASE)
                                if m_user:
                                    extracted_info['user'] = m_user.group(1)
                                
                                m_date = re.search(r'(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}|\d{2}/\d{2}/\d{4})', val)
                                if m_date:
                                    extracted_info['date'] = m_date.group(1)
                except:
                    pass

                df = pd.read_excel(uploaded_file, sheet_name=0)
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
                        
                        data_compra_str = str(row['Última Compra']).split()[0] if pd.notna(row['Última Compra']) else ""
                        
                        is_critico = False
                        try:
                            d_compra = datetime.strptime(data_compra_str, "%Y-%m-%d")
                            if (datetime.now() - d_compra).days > 60:
                                is_critico = True
                        except:
                            try:
                                d_compra = datetime.strptime(data_compra_str, "%d/%m/%Y")
                                if (datetime.now() - d_compra).days > 60:
                                    is_critico = True
                            except:
                                pass

                        temp_dict[current_supplier].append({
                            'Produto': row['Produto'],
                            'Código Interno': int(row['Código Interno']),
                            'Última Compra': data_compra_str,
                            'Estoque': int(row['Estoque']) if pd.notna(row['Estoque']) else 0,
                            'Total': float(row['Total']) if pd.notna(row['Total']) else 0.0,
                            'Departamento': depto_name,
                            'Critico': is_critico
                        })

            if file_mercearia: ler_planilha(file_mercearia, "MERCEARIA")
            if file_pereciveis: ler_planilha(file_pereciveis, "PERECÍVEIS")

            if temp_dict:
                st.session_state['suppliers_dict'] = dict(sorted(temp_dict.items()))
                st.session_state['selected_sups'] = set(temp_dict.keys())
                
                for sup_name in temp_dict.keys():
                    st.session_state[f"cb_{sup_name}"] = True
                
                st.session_state['usuario_planilha'] = extracted_info['user'] if extracted_info['user'] else "reinerca"
                st.session_state['data_planilha_bruta'] = extracted_info['date'] if extracted_info['date'] else datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- RENDERIZAÇÃO E FILTROS ---
if st.session_state['suppliers_dict'] is not None:
    suppliers_dict_full = st.session_state['suppliers_dict']

    # 1. BOTÃO DE LIMPAR PAINEL
    st.sidebar.markdown('<div class="btn-limpar">', unsafe_allow_html=True)
    if st.sidebar.button("🗑️ Limpar Painel / Novo Upload", use_container_width=True):
        for k in list(st.session_state.keys()):
            if k.startswith("cb_"):
                del st.session_state[k]
        st.session_state['suppliers_dict'] = None
        st.session_state['selected_sups'] = set()
        st.session_state['data_compilacao'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        st.session_state['data_planilha_bruta'] = "Não identificada"
        st.session_state['usuario_planilha'] = "reinerca"
        st.rerun()
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    # 2. SELEÇÃO DE FORNECEDORES
    st.sidebar.markdown("### 📋 Selecionar Fornecedores")
    busca = st.sidebar.text_input("🔍 Buscar fornecedor:", "", placeholder="Digite o nome...", key="txt_busca").strip().upper()

    sups_visiveis_side = []
    for sup_name, items in suppliers_dict_full.items():
        depto = items[0]['Departamento']
        if st.session_state['filtro_depto'] == "Ambas" or depto == st.session_state['filtro_depto']:
            if busca == "" or busca in sup_name:
                sups_visiveis_side.append(sup_name)

    def marcar_visiveis():
        for s in sups_visiveis_side:
            st.session_state[f"cb_{s}"] = True
            st.session_state['selected_sups'].add(s)

    def desmarcar_visiveis():
        for s in sups_visiveis_side:
            st.session_state[f"cb_{s}"] = False
            st.session_state['selected_sups'].discard(s)

    btn_col1, btn_col2 = st.sidebar.columns(2)
    with btn_col1:
        st.markdown('<div class="btn-marcar">', unsafe_allow_html=True)
        st.button("✅ Marcar", on_click=marcar_visiveis, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with btn_col2:
        st.markdown('<div class="btn-desmarcar">', unsafe_allow_html=True)
        st.button("❌ Desmarcar", on_click=desmarcar_visiveis, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.sidebar.caption(f"Selecionados acumulados: **{len(st.session_state['selected_sups'])}** de {len(suppliers_dict_full)}")

    # 3. BASE FILTRADA
    suppliers_filtered = {
        k: v for k, v in suppliers_dict_full.items() 
        if k in st.session_state['selected_sups'] and (st.session_state['filtro_depto'] == "Ambas" or v[0]['Departamento'] == st.session_state['filtro_depto'])
    }

    deptos_presentes = set()
    for s_name, products in suppliers_filtered.items():
        if products:
            deptos_presentes.add(products[0]['Departamento'])

    if len(deptos_presentes) == 1:
        depto_unico = list(deptos_presentes)[0]
        titulo_relatorio = f"Relatório de Trocas - {depto_unico}"
        str_segmento_arquivo = "Mercearia" if depto_unico == "MERCEARIA" else "Pereciveis"
    elif len(deptos_presentes) > 1:
        titulo_relatorio = "Relatório de Trocas - MERCEARIA / PERECÍVEIS"
        str_segmento_arquivo = "Mercearia-Pereciveis"
    else:
        titulo_relatorio = "Relatório de Trocas"
        str_segmento_arquivo = "Vazio"

    raw_date = st.session_state['data_planilha_bruta']
    match_date_digits = re.search(r'(\d{2})/(\d{2})/(\d{4})', raw_date)
    if match_date_digits:
        str_data_arquivo = f"{match_date_digits.group(1)}{match_date_digits.group(2)}{match_date_digits.group(3)}"
    else:
        str_data_arquivo = datetime.now().strftime("%d%m%Y")

    nome_arquivo_base = f"{str_data_arquivo}-Trocas-{str_segmento_arquivo}"

    # 4. GERAÇÃO DOS ARQUIVOS
    buffer_excel = io.BytesIO()
    grand_total_qty = 0
    grand_total_val = 0.0

    wsp_text = f"🚨 *RESUMO DE TROCAS - LU 10 MONGAGUÁ*\n"
    wsp_text += f"📅 *Data Ref:* {st.session_state['data_planilha_bruta']}\n"
    wsp_text += f"👤 *Usuário:* {st.session_state['usuario_planilha']}\n"
    wsp_text += f"-----------------------------------\n\n"

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
        data_geracao_agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        html_print = f"""<html><head><meta charset='utf-8'><meta name="viewport" content="width=device-width, initial-scale=1.0"><style>
            body {{ font-family: Arial, sans-serif; padding: 10px; color: #333; margin: 0; }}
            .v-info {{ font-size: 10px; color: #555; text-align: right; margin-bottom: 8px; line-height: 1.3; }}
            h1 {{ font-size: 16px; text-align: center; margin-top: 5px; margin-bottom: 5px; color: #000; }}
            h3 {{ font-size: 11px; text-align: center; margin-bottom: 12px; font-weight: normal; color: #444; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 12px; }}
            th {{ background: black; color: white; padding: 5px; font-size: 10px; border: 1px solid black; text-align: left; }}
            td {{ padding: 4px 5px; font-size: 10px; border: 1px solid #ccc; }}
            .sup {{ color: red; font-weight: bold; font-size: 12px; padding-top: 10px; border: none; }}
            .sub {{ color: red; font-weight: bold; font-size: 11px; border-bottom: 2px solid red; }}
            .grand {{ background: red; color: white; font-weight: bold; font-size: 13px; }}
            .center {{ text-align: center; }} .right {{ text-align: right; }}
            .tag {{ font-size: 8px; background: #eee; color: #333; padding: 1px 4px; margin-left: 4px; border-radius: 2px; font-weight: normal; }}
            .crit {{ font-size: 8px; background: #fdf2f2; color: #d9534f; border: 1px solid #d9534f; padding: 1px 4px; margin-left: 4px; border-radius: 2px; font-weight: bold; }}
            .no-print {{ text-align: center; margin-bottom: 12px; }}
            .btn-print {{ background-color: #0078d4; color: white; border: none; padding: 8px 15px; font-size: 12px; font-weight: bold; border-radius: 4px; cursor: pointer; }}
            @media print {{ .no-print {{ display: none; }} }}
        </style></head><body>
        <div class="no-print">
            <button class="btn-print" onclick="window.print()">🖨️ Imprimir / Salvar em PDF</button>
        </div>
        <div class="v-info">
            <b>Usuário Planilha:</b> {st.session_state['usuario_planilha']} | <b>Data/Hora Planilha:</b> {st.session_state['data_planilha_bruta']}<br>
            <b>Versão App:</b> {versao_app} | <b>Processado no App em:</b> {data_geracao_agora}
        </div>
        <h1>{titulo_relatorio}</h1>
        <h3><b>Loja:</b> LU 10-MONGAGUA</h3>
        <table><thead><tr><th>Fornecedor / Produto</th><th>Código Interno</th><th>Última Compra</th><th class='center'>Estoque</th><th class='right'>Total</th></tr></thead><tbody>"""

        for supplier, products in suppliers_filtered.items():
            depto_tag = products[0]['Departamento']
            ws.write(excel_row, 0, supplier.upper(), fmt_supplier)
            html_print += f"<tr><td colspan='5' class='sup'>{supplier.upper()} <span class='tag'>{depto_tag}</span></td></tr>"
            excel_row += 1

            sub_qty = 0
            sub_val = 0.0

            wsp_text += f"📦 *{supplier.upper()}* ({depto_tag})\n"

            for p in products:
                ws.write(excel_row, 0, p['Produto'], fmt_product)
                ws.write(excel_row, 1, p['Código Interno'], fmt_center)
                ws.write(excel_row, 2, p['Última Compra'], fmt_center)
                ws.write(excel_row, 3, p['Estoque'], fmt_qty)
                ws.write(excel_row, 4, p['Total'], fmt_money)
                
                tag_crit = " <span class='crit'>⚠️ +60d</span>" if p['Critico'] else ""
                html_print += f"<tr><td>{p['Produto']}{tag_crit}</td><td class='center'>{p['Código Interno']}</td><td class='center'>{p['Última Compra']}</td><td class='center'>{p['Estoque']}</td><td class='right'>R$ {p['Total']:,.2f}</td></tr>"
                
                alerta_wsp = " ⚠️" if p['Critico'] else ""
                wsp_text += f"  • {p['Produto']} (Cod: {p['Código Interno']}) - Qtd: {p['Estoque']} | R$ {p['Total']:,.2f}{alerta_wsp}\n"

                sub_qty += p['Estoque']
                sub_val += p['Total']
                excel_row += 1

            grand_total_qty += sub_qty
            grand_total_val += sub_val

            wsp_text += f"👉 *Subtotal:* {sub_qty} itens — R$ {sub_val:,.2f}\n\n"

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
        
        html_print += f"<tr class='grand'><td style='padding:6px;'>TOTAL GERAL DOS SELECIONADOS</td><td></td><td></td><td class='center'>{grand_total_qty}</td><td class='right'>R$ {grand_total_val:,.2f}</td></tr>"
        html_print += "</tbody></table></body></html>"

        wsp_text += f"-----------------------------------\n"
        wsp_text += f"💰 *TOTAL GERAL SELECIONADO:* {grand_total_qty} itens | R$ {grand_total_val:,.2f}"

        ws.set_column(0, 0, 45)
        ws.set_column(1, 4, 15)

    # 5. BOTÕES DE AÇÕES LATERAIS COM ENVOLTÓRIOS DIV EXCLUSIVOS
    st.sidebar.markdown("### 📥 Ações")
    
    st.sidebar.markdown('<div class="btn-excel">', unsafe_allow_html=True)
    st.sidebar.download_button(
        label="📊 Exportar Seleção para Excel",
        data=buffer_excel.getvalue(),
        file_name=f"{nome_arquivo_base}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    st.sidebar.markdown('<div class="btn-wsp">', unsafe_allow_html=True)
    st.sidebar.download_button(
        label="💬 Baixar Relatório HTML (WhatsApp)",
        data=html_print,
        file_name=f"{nome_arquivo_base}.html",
        mime="text/html",
        use_container_width=True
    )
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    with st.sidebar.expander("📲 Texto de Cópia Rápida (WhatsApp)"):
        st.text_area("Copie o texto abaixo e cole no WhatsApp:", value=wsp_text, height=200)

    st.sidebar.markdown("---")

    # 6. RENDERIZAÇÃO DOS CHECKBOXES
    for sup_name in sups_visiveis_side:
        depto = suppliers_dict_full[sup_name][0]['Departamento']
        
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

    # 7. RENDERIZAÇÃO DO PAINEL PRINCIPAL
    st.markdown("### 🎯 Filtrar Departamento View:")
    f_col1, f_col2, f_col3 = st.columns(3)
    
    if f_col1.button("🏢 MERCEARIA", use_container_width=True):
        st.session_state['filtro_depto'] = "MERCEARIA"
    if f_col2.button("🥩 PERECÍVEIS", use_container_width=True):
        st.session_state['filtro_depto'] = "PERECÍVEIS"
    if f_col3.button("🔄 AMBAS PLANILHAS", use_container_width=True):
        st.session_state['filtro_depto'] = "Ambas"

    st.info(f"Visualizando: **{st.session_state['filtro_depto']}** | Data Planilha: **{st.session_state['data_planilha_bruta']}**")

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

    c_tot1, c_tot2, c_tot3 = st.columns(3)
    
    if st.session_state['filtro_depto'] in ["AMBAS", "Ambas", "MERCEARIA"] and tot_merc_qty > 0:
        c_tot1.metric("Total Mercearia", f"R$ {tot_merc_val:,.2f}", f"{tot_merc_qty} itens")
        
    if st.session_state['filtro_depto'] in ["AMBAS", "Ambas", "PERECÍVEIS"] and tot_perec_qty > 0:
        c_tot2.metric("Total Perecíveis", f"R$ {tot_perec_val:,.2f}", f"{tot_perec_qty} itens")
        
    if st.session_state['filtro_depto'] == "Ambas" and (tot_merc_qty > 0 and tot_perec_qty > 0):
        c_tot3.metric("TOTAL GERAL CONSOLIDADO", f"R$ {(tot_merc_val + tot_perec_val):,.2f}", f"{tot_merc_qty + tot_perec_qty} itens")

    # --- GRÁFICO DINÂMICO ---
    if suppliers_filtered:
        chart_data = []
        for sup_name, prods in suppliers_filtered.items():
            tot_val = sum(p['Total'] for p in prods)
            chart_data.append({'Fornecedor': sup_name, 'Valor Total (R$)': round(tot_val, 2)})
        
        df_chart = pd.DataFrame(chart_data).sort_values(by='Valor Total (R$)', ascending=False)
        
        with st.expander("📊 Visão Gráfica - Ranking de Valores por Fornecedor", expanded=True):
            st.bar_chart(
                df_chart, 
                x='Fornecedor', 
                y='Valor Total (R$)', 
                color='#FF0000',
                height=250,
                use_container_width=True
            )

    st.markdown("---")

    # RENDERIZAÇÃO DAS TABELAS COM BOTOES COLORIDOS COM CLASSES EXCLUSIVAS
    for supplier, products in suppliers_filtered.items():
        depto_tag = products[0]['Departamento']
        st.markdown(f'<div class="supplier-header">{supplier.upper()} <span class="dept-tag">{depto_tag}</span></div>', unsafe_allow_html=True)

        sub_qty = sum(p['Estoque'] for p in products)
        sub_val = sum(p['Total'] for p in products)

        prod_df = pd.DataFrame(products)[['Produto', 'Código Interno', 'Última Compra', 'Estoque', 'Total', 'Critico']]
        view_df = prod_df.copy()
        
        view_df['Produto'] = view_df.apply(lambda r: f"⚠️ {r['Produto']} (+60d)" if r['Critico'] else r['Produto'], axis=1)
        view_df['Total'] = view_df['Total'].map('R$ {:,.2f}'.format)
        
        st.dataframe(view_df[['Produto', 'Código Interno', 'Última Compra', 'Estoque', 'Total']], use_container_width=True, hide_index=True)
        st.markdown(f'<div class="total-supplier">TOTAL {supplier.upper()}: {sub_qty} itens — R$ {sub_val:,.2f}</div>', unsafe_allow_html=True)

        col_act1, col_act2 = st.columns(2)

        html_ind = f"""<html><head><meta charset='utf-8'><style>
            body {{ font-family: Arial; padding: 20px; }}
            h2 {{ color: red; text-align: center; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            th {{ background: black; color: white; padding: 8px; font-size: 12px; }}
            td {{ padding: 6px; font-size: 11px; border: 1px solid #ccc; }}
            .sub {{ color: red; font-weight: bold; border-top: 2px solid red; }}
            .center {{ text-align: center; }} .right {{ text-align: right; }}
        </style></head><body>
            <h2>Relatório de Troca: {supplier.upper()}</h2>
            <p><b>Loja:</b> LU 10-MONGAGUA | <b>Data Referência:</b> {st.session_state['data_planilha_bruta']}</p>
            <table><thead><tr><th>Produto</th><th>Código Interno</th><th>Última Compra</th><th class='center'>Estoque</th><th class='right'>Total</th></tr></thead><tbody>"""
        for p in products:
            html_ind += f"<tr><td>{p['Produto']}</td><td class='center'>{p['Código Interno']}</td><td class='center'>{p['Última Compra']}</td><td class='center'>{p['Estoque']}</td><td class='right'>R$ {p['Total']:,.2f}</td></tr>"
        html_ind += f"<tr class='sub'><td>TOTAL {supplier.upper()}</td><td></td><td></td><td class='center'>{sub_qty}</td><td class='right'>R$ {sub_val:,.2f}</td></tr></tbody></table></body></html>"

        with col_act1:
            st.markdown('<div class="btn-relatorio-ind">', unsafe_allow_html=True)
            st.download_button(
                label=f"📄 Relatório ({supplier.upper()})",
                data=html_ind,
                file_name=f"{str_data_arquivo}-Troca-{supplier.replace(' ', '_')}.html",
                mime="text/html",
                key=f"btn_ind_{supplier}",
                use_container_width=True
            )
            st.markdown('</div>', unsafe_allow_html=True)

        html_recibo = f"""<html><head><meta charset='utf-8'><style>
            body {{ font-family: 'Courier New', Courier, monospace; padding: 15px; max-width: 600px; margin: auto; border: 2px dashed #000; background-color: #fafafa; }}
            h2 {{ text-align: center; margin-bottom: 2px; text-transform: uppercase; border-bottom: 2px solid #000; padding-bottom: 8px; }}
            .info-box {{ font-size: 11px; margin-bottom: 15px; border-bottom: 1px solid #000; padding-bottom: 10px; line-height: 1.4; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 15px; }}
            th {{ border-bottom: 2px solid #000; font-size: 11px; text-align: left; padding: 4px 0; }}
            td {{ padding: 6px 0; font-size: 11px; border-bottom: 1px dotted #ccc; }}
            .tot-box {{ border-top: 2px solid #000; border-bottom: 2px solid #000; font-size: 13px; font-weight: bold; padding: 8px 0; margin-bottom: 25px; }}
            .sig-section {{ margin-top: 40px; display: flex; justify-content: space-between; font-size: 11px; text-align: center; }}
            .sig-line {{ border-top: 1px solid #000; width: 45%; padding-top: 4px; }}
            .center {{ text-align: center; }} .right {{ text-align: right; }}
            .no-print {{ text-align: center; margin-bottom: 15px; }}
            .btn-print {{ background-color: #000; color: #fff; border: none; padding: 8px 12px; font-weight: bold; cursor: pointer; }}
            @media print {{ .no-print {{ display: none; }} }}
        </style></head><body>
            <div class="no-print">
                <button class="btn-print" onclick="window.print()">🖨️ Imprimir / Salvar Recibo PDF</button>
            </div>
            <h2>COMPROVANTE DE DEVOLUÇÃO / TROCA</h2>
            <div class="info-box">
                <b>LOJA:</b> LU 10-MONGAGUA<br>
                <b>FORNECEDOR:</b> {supplier.upper()}<br>
                <b>DEPARTAMENTO:</b> {depto_tag}<br>
                <b>DATA EMISSÃO PLANILHA:</b> {st.session_state['data_planilha_bruta']}<br>
                <b>AUDITOR / USUÁRIO:</b> {st.session_state['usuario_planilha']}
            </div>
            <table><thead><tr><th>PRODUTO</th><th class='center'>COD</th><th class='center'>QTD</th><th class='right'>TOTAL</th></tr></thead><tbody>"""
        
        for p in products:
            html_recibo += f"<tr><td>{p['Produto']}</td><td class='center'>{p['Código Interno']}</td><td class='center'>{p['Estoque']}</td><td class='right'>R$ {p['Total']:,.2f}</td></tr>"
            
        html_recibo += f"""</tbody></table>
            <div class="tot-box">
                <span style='float:left;'>TOTAL A DEVOLVER:</span>
                <span style='float:right;'>{sub_qty} itens — R$ {sub_val:,.2f}</span>
                <div style='clear:both;'></div>
            </div>
            <div style='font-size:10px; text-align:center; margin-bottom:30px;'>Declaro que recebi os itens discriminados acima para conferência/troca.</div>
            <div class="sig-section">
                <div class="sig-line">Assinatura Promotor / Repr.</div>
                <div class="sig-line" style="float:right;">Conferente da Loja</div>
                <div style="clear:both;"></div>
            </div>
        </body></html>"""

        with col_act2:
            st.markdown('<div class="btn-recibo-ind">', unsafe_allow_html=True)
            st.download_button(
                label=f"🧾 Recibo / Vale-Troca ({supplier.upper()})",
                data=html_recibo,
                file_name=f"{str_data_arquivo}-RECIBO-{supplier.replace(' ', '_')}.html",
                mime="text/html",
                key=f"btn_rec_{supplier}",
                use_container_width=True
            )
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="grand-total-box">TOTAL GERAL DOS SELECIONADOS<br>Estoque: {grand_total_qty} | R$ {grand_total_val:,.2f}</div>', unsafe_allow_html=True)
