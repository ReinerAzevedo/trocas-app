import streamlit as st
import pandas as pd
import io
import re
from datetime import datetime

# Configuração de página
st.set_page_config(
    page_title="Gerenciador de Trocas v4.8", 
    page_icon="🔄", 
    layout="wide"
)

# Base64 da imagem original do Logo (Fidelidade 100% P&B)
LOGO_B64 = "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36TfxsH830mRryv/G93e/C/19yIifndkL4m/1/vH1N+v8Dfs86+K3zv82f5b4G/O+3t438/i/QG+d3eA39Xy/vD/m/zfeYf/uP+2vN/R0X79/4G34m6f+R408d6X79P7/T/vS4l/68SfaE99xX8X39p23wS8/fjfgt/JvE8D/Dvx/xfe66bfP6XqI1N/f/5eN/27x/ve5G/i//Tq1+I4/IeBv6Xm7Xn/D+X/yfv53+b+40v/I3t+vS/M6j48f/f/0M7yN1/wD3S8A74/e3S/8n3bA/1P1L+35u14L373L/4e4O3w/tP+/8v3p/39GvB+41m5v+veI3838D/6f/M9U+fG78Lff+/vJ3+f++24G307fPf67/b/E/33m463E4yA3SfyDk+8f8D/S337c7k7YlCflsTv2t3m08x/+l0S/9fD52H/m5P+1pX9pA7+3X3eI3G4eH0d8b+N+J4Q32+/v23uXyv/O36d4s8D373+X9D/3f7mAt+nI7eBf0t/N3/E0b6Rfx9NfO/6/6B/s4iI+TjR0Xj67Xp/f5u/736Lp3v3I9s73p38x7c8aAze1X+B4i1i3+32L02856V3lq8X/M0I426w8A0V5c20x/fX8B/n82531+a9rO19b3Xv1bSAn+J/hO4xS/3b4p/uP63v4s3fI16P5+i+sP7iP4X+7qfv9525i+L9oXsf99uY2fT59S/6f+d/D34j65eNn//rP32xS/P3L8Dfh/C++lD+1pXvv4X7u5f/jP53mPe3+/s3e390uP5o/u20v1++H0/T34lA4o3/aI3+67cff3q5+8Pj//C3/H4a8I+wz09y2XkfvP+I0f6jxf/q4e9J9O/142L/J3P/M8/9H70//h2a/t3mInXp/5/9e3yLw9S8B+jxf7d/u4A/s8e2X/c3p/920S029P3L7xX0f1z+/hP/5//vI/kbfG+S6bvd198A/5HwfQe4I2f8D/1eXfC99v1x+/j/945C/z/1Efrf9XwA1I5f8A1/n348vE7v/+9v7n4z/kX4e1p34zR2j/s3/G2648L/y9//7vO9+LvxR02C13u835j83e/u74//b9/d5f4i+f2D++e699X0b77g0efmfgG4x3E38e3m/pD09923SfeC+f3v6D+52K77P3p2pTuh314/0t7S/37rI//8P3v//5Cj0KPR/3b8L5Xf6H2N+x3Nfze1O3xT5N3X3/8O//e7I96f131L8Hfe7zP//eS964y/sffpA8i5+G/5v3X0d+r075v69wr+i1R/I4L6xTf++Ld4+O/p770KvfN+F4/o+4z3E7f3jLp/mDveB/6/eF8e3a5R9H+E/r2G+Lfl/0a498D3J/j3/8R8P+N7G/y/1d+n4ve3/8m3X2s/Ife70f+k921C3473gveL94y9fT/+20b43xP2mDveJ+m3v4v/b/3t53qKfl84p026L2l/pX/3zvd2+N9Tfx/+L+vfrxHveb2xL9m/078d1Sfv7q1e7e/C36a7/233X/C/Xv0s3j/t/S4a0T0Y72/831v8Dfl31f+1A3y3+04IuIe//6lA7/b8p8p/Bv6S98sU76Nve/+jU/5O9n4/I12s4LvhfwO65/S7j2p6v0vEew7Xz2s371f/sUv3v2A85536u9a/D+0a7x/Rfc6/9d77e4m038+H1/M9Ivg98j2k31/lS1H+U+u/S0v9vU/S4X9J29v5p913r33E6b8R+O4M4F3GfxfvI+B4E0f438T3Ue74l9B34Xn6f3f/3jH/2+yvx/+K13f9f3X636H/Xv03In49qKIn0f/bAt76O34O4M/162P63qS/R3pM7I+A8LfxD0j/3uK/33cK0Zc4Ivwx7/03G/jftoH/3b4p/k++uG69+9S7x++693m/1+D/S3f03wT5vX+03x+/Xf8Zf3e390eOvv3R6R7x/t8G/v+8X/A/4f+j4e/fXvfD11+cffTvxv/G7v1e8P+bvwH+v3iPlu//62iXv8eK/y1v26P7S+/90b3U/4XUvynA0f6Xifj3X5p3f2jM/vP5v9v/18bfX29/x+I/l74X6vveJv4v5feP0v+p6pU/o/+/e02Lvw9//3SvxN//P4m/B/3P+DvfX2D/Svhf4N+Z+K679/e29XvK3//fH/f+f/z286O9D/XvvxHf+4L3Gv9V/d7943fxe8N/z50mvh/38ffo7yG//5m/f44v3oP824mIuInuX1sS/zN8t3O1/+M591f4t2z/Wv9e/s40qC2uI9XU744a+uA08ffH23/S/7b43x8e92L0b2L3n+q9z7/f/Zve//p282f1p4y2p+5/8H8+3iPfP3I/+qOAnkX056I42d//m9e/391d/A2h/V94n6J89e/3fS2G/770fQn3H1fSfyN//+jve3sI69f3D/L3o2+P/8n062jxf13/n/6P5Sft47tC8j9d09+b+P/28p/p/+DvxT2mInpP//X/X3f0j9f9/fL9G2f/fEa938jI+x/f3T8e3d8f+Sfe3R/d46S/r4/172/p6H5w2z8S/Qd8f+9vN5K+/fN1d0u8v17j/4p8f/G3/P/83Qv+/8s/o/4a1r2I6pX+/Z18/f3l791s/o9C/M3Xvyz6d+B/+fA6p9a/vOiv4e9s6m/C/66G//v/V7438Xeb+f+3s+c7qfvX1d8p0v82o797yD+Gvn0x+fIqB/sP+/xP9G8C4X5x/aO266Xv33GfS3X/c9/H4X3f/S+4I4m8/75e+/3j0fd6o+1/+G3B96p2f38n+I+m+P7q99D2uY//yX8X3i8Cfwve4/sX4x6D74n/C+q/sXpXev/Xo53+B+G73Hfg/d/sP9sR94I/G307+H+93zfyfyN+X979eP/YwX/S36Hq/sT3a5323xRfvIe29xf5O/f3/H/q9Y7zXgD/x31fi+/l8P/o39P35+qXv8X/6t/d+4v4fuj+X3u3j/93e8//f/S/8jX6m9n1d2s05j04Aujq6vKSAtS32L29vVEz1Eikm5YyJ63IAt54/o//4956/i4u0Lw725x0cKAnXbxe4s/4x/Iet//R/1pffv6r+7a9X83I4m97j36S94p3fL3G/f1kEevqXyO/Rz+6C/526t1R9O9c33v3eSfi/iY8s6hfe1iBf3333h3/Y/v/LpSvy1EAt6N915i/y4x7A9z/eO3O7OQfJ37/B//7v2N5//+aIn4f3m/0t5/ve+/5d6T/9fS/239Y+p/2vxC/j/b833S073r74d643v5v1eX/Xo7i34b/lEfvfej/3fA40q+L33vPvyx0vyx/V/U18H4Svhv322v1D9S17+P3O7mH5/i4d8R/tSdeA+rfeve2A34O+O7S33v1d9943/kInb9fxf26/i8S9v2+H97T34/+qvevBvxO5P0Yj/87965G3GffyLsp+p9F3S00/S/g+4m/6f8H3m/1+99vR/m30T9cE/93+A/hbxR57/l3/z/2/4f8H1f391z43jXq364+wD9X7+/qf9I2PqL/FfA2+R8S3a34u+l/A+o//e1A9144/f7gI30CvhvA+4C3925Ufwt7Hyr8ve4+/434+9E/Q8f/v5fSvwv3i/jvyq+J393G/Xf2/T2Ufwd6l4vvBv+P5N3S4z/m3o/8X1T+Pvvf9veC/wnUf3yG+/2L7u4C3f5n3N8X/835N+ffQ+/m0f/36O/p8l+J//51H//A+xX3z1bI30f8j8I3303dD4v22+u6mX93/f+076/w53ePfI3+e1L1+y72/QfUf3u6X678v0f+bvbXnO5e8RzS428i5C+12f45vj/5S+aB1e91s3d/+e63fH2B34Xj/Yx8f4d9/bXGfw73r4DvwP4c424w49m6+2D6P9vfj/1v6m8pTfh8v821/+eEfwu4D3o/q90eO/C/C+C/y98vXp9E/3+g34fF21O8Hvf9G+J/42+13Tfl/6sRftD/G8P9o/f44b36u9/XhD4p3P+38f9b9x087x3y5/Mfx/v+M3xf1X/Ld3eXf+r/2vG/1G8S3mO23zvd4L3u3f8r3G+xH/S4I+G9A2e8s2I/2oH/Lft/bH//o/l7jL5p+XudX/6O8XfC/y2//e5pSnh31Pvx99738L4K99f131L53y7/9n5N8Dfl315/+a4O3i037x/4s913gG9P78I14l8TvwO3O/q3x3/2/v8o3p4UfSfx9xT9n4jve+/r3u71917f30r1qPfI1+z99/mfeL9H3a2/t/G33veq++L/SvdD6P+f+y8534X7x7x/5L53wveP4C2E9/L4feZ3Qffv8f3E23pveo+O/2z724TfC/J93f8zve8vX5/7SbfP+L12v/30m9mI94I7075/9Xed+0T3f8/2iP//pTvx332fBf3/GvA9/1+K/v3w/S8U9+F098C/J3Xv36m/d+23TfwNufvuS8T/zO/vN+633Xff8R3+E/HvxvuG3xfuDfx903aFvvPvvB7e5fDfgN5L5ftX734M3c193jvxP9x73j3+93d395vv8feN7kXz+/q7G8Xv6fce961m350f2f3/Ivt3uPvB2wfeT0f438T3Ue74l9/m8+378S3q76A03qfI+49fXf5mIn6fAnz3I9w/3/6/5e6j+Nse+I37N/9fS/e2H0v1r2C/xX/fB7147i56m+L9Ivf/Cvh/x9e3Bf8/77d2I3+r/yDvf+53/P0m/G2e/n2D7q9rO2sU/5e9O4/f4j8Afp74e4XveX29+fD/X6j/iO//2vv+yv9m/I3A29u/v8/fe43e74r3z3g7iLcfvT9pvd894O4q4X2d0e74e6f4O/4N5u+eXvT1uBv490L379C3T/x3lDse+b4/z/cQpB2/v4v8Tfh2vJ2u+H/U3/L294y6f5g73gbA/yLef3x3d4S54x14+8D7aYjvZfA3g/e8e5v3612I/3/sR32X+/vI/yL0/+d/oP6e4H+B4e/l1f4H8ffn+9v1/rX+i57yvd2989i/L6l+1n+i/c68r/b7z/vvv8TfA/A2+/7S4S7S72L4u5/p6L7SvbN/r3yP+n/E/x2/6sI3M/7e8n+K/6L6W672i9b9Y43/Tvyvcv9pI65L392K+8B/M5+Dfx/+xI19/O+H/wn4z8f/Ea/3n9234R3f3/3m3kC2D04JqP3x8oKk9Xfx33s8LIn90ffIux9eG35P229E308S32e185N4vy+p7/sT9P4X/K0s3v8L7/XpfiX7yNve+f/J637S77/r8ZzS0f24f11G/mfeH0tO3A/+DqM+N97XzEfy78v/79p3/f8C/1j/G/5a/y+S5A3uPvD24S+r3v/p3y/3X/H8/c//f9G++KOP7/c/iP2T+9A5333fR5Lvdv4e8//3eP8nI12UoE5kGqP0n6iR7eG5Xj+/I+E50X1Y5S1X0p/P2b23/O+L0/924sI4xPz/Gv2bT6IflGf41/i65+d++S3Bf6fInKjeP/L14v2S7r9J//+a9394/Ie8X/X92N94X644S/v/Bf/7iH30X4i9j4x1/X0s8f8x3fIe//tF33/v+O3wff5G7kL/+uPvw+d4/Dvev+/3s//j1/6C+219p7Lq84O//413v1n2E/2d5K/r/0/9S8S+3v/X4O+/mft37PfxsR/svevj/3/u3xrvg/1+kO+fA5N4/e6I/8e3o4fC5xPq52P+k8eP3v8oX0e386P5iPfLvv8u/vX0x8j7O/eJvyD/o3S34j2qf4b3LwKx2d/f64l1H9y2yNf2+9x/G06kXzrf+kP0/62uD/z/0f/E6SseLfZi2SPlI0i8O2d3m5I/j/v9d9P//O99N+Lfe1d58Tse1I/T4j8L4/Nif1zR/38R3b9F9fT44/i2o+X2f93I+9zE3wUqSfyfF/2//v320X2U/vG9k31I/q9K/6j/f3x3I/bfU3z8/a+eR+o7O2T/48/44P2f1e29u3zffyM++vf3//8H"

# Estilização CSS completa com seletores de alta precisão
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

    /* 1. BOTÃO PROCESSAR PLANILHAS (TELA INICIAL) */
    div[data-testid="stElementContainer"]:has(#marker-processar) + div[data-testid="stElementContainer"] button {
        background-color: #2E7D32 !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 16px !important;
        border-radius: 6px !important;
        border: none !important;
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

    /* 3. BOTÕES DA BARRA LATERAL (SIDEBAR) */
    /* Limpar Painel */
    div[data-testid="stElementContainer"]:has(#marker-limpar) + div[data-testid="stElementContainer"] button {
        background-color: #C62828 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        border: none !important;
    }

    /* Marcar e Desmarcar */
    div[data-testid="stElementContainer"]:has(#marker-marcar) + div[data-testid="stElementContainer"] button {
        background-color: #1976D2 !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
    }
    div[data-testid="stElementContainer"]:has(#marker-desmarcar) + div[data-testid="stElementContainer"] button {
        background-color: #E53935 !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
    }

    /* Exportar Excel (Verde Floresta Escuro) */
    div[data-testid="stElementContainer"]:has(#marker-excel) + div[data-testid="stElementContainer"] button {
        background-color: #0D622A !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        border: none !important;
    }

    /* Baixar Relatório HTML WhatsApp (Verde WhatsApp Vibrante) */
    div[data-testid="stElementContainer"]:has(#marker-wsp) + div[data-testid="stElementContainer"] button {
        background-color: #25D366 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        border: none !important;
    }

    /* Sanfona Cópia Rápida na Barra Lateral */
    section[data-testid="stSidebar"] [data-testid="stExpander"],
    section[data-testid="stSidebar"] details {
        border: 2px solid #00838F !important;
        background-color: #E0F7FA !important;
        border-radius: 6px !important;
    }
    section[data-testid="stSidebar"] [data-testid="stExpander"] summary,
    section[data-testid="stSidebar"] details summary,
    section[data-testid="stSidebar"] details summary * {
        color: #006064 !important;
        font-weight: bold !important;
    }

    /* 4. BOTÕES POR FORNECEDOR NA TABELA CENTRAL */
    /* Coluna 1: Relatório (Azul Cobalto) */
    div[data-testid="stMainBlockContainer"] div[data-testid="stHorizontalBlock"] > div:nth-child(1) div.stDownloadButton button {
        background-color: #1565C0 !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 6px !important;
    }
    /* Coluna 2: Recibo / Vale-Troca (VERMELHO ALERTA DESTACADO) */
    div[data-testid="stMainBlockContainer"] div[data-testid="stHorizontalBlock"] > div:nth-child(2) div.stDownloadButton button {
        background-color: #D32F2F !important;
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
versao_app = "v4.8"
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
        st.markdown('<div id="marker-processar"></div>', unsafe_allow_html=True)
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

# --- RENDERIZAÇÃO E FILTROS ---
if st.session_state['suppliers_dict'] is not None:
    suppliers_dict_full = st.session_state['suppliers_dict']

    # 1. BOTÃO DE LIMPAR PAINEL
    st.sidebar.markdown('<div id="marker-limpar"></div>', unsafe_allow_html=True)
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
        st.markdown('<div id="marker-marcar"></div>', unsafe_allow_html=True)
        st.button("✅ Marcar", on_click=marcar_visiveis, use_container_width=True)
    with btn_col2:
        st.markdown('<div id="marker-desmarcar"></div>', unsafe_allow_html=True)
        st.button("❌ Desmarcar", on_click=desmarcar_visiveis, use_container_width=True)

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

    # 5. BOTÕES DE AÇÕES LATERAIS COM MARCADORES
    st.sidebar.markdown("### 📥 Ações")
    
    st.sidebar.markdown('<div id="marker-excel"></div>', unsafe_allow_html=True)
    st.sidebar.download_button(
        label="📊 Exportar Seleção para Excel",
        data=buffer_excel.getvalue(),
        file_name=f"{nome_arquivo_base}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
    
    st.sidebar.markdown('<div id="marker-wsp"></div>', unsafe_allow_html=True)
    st.sidebar.download_button(
        label="💬 Baixar Relatório HTML (WhatsApp)",
        data=html_print,
        file_name=f"{nome_arquivo_base}.html",
        mime="text/html",
        use_container_width=True
    )

    st.sidebar.markdown('<div id="marker-copia"></div>', unsafe_allow_html=True)
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

    # RENDERIZAÇÃO DAS TABELAS
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
            st.download_button(
                label=f"📄 Relatório ({supplier.upper()})",
                data=html_ind,
                file_name=f"{str_data_arquivo}-Troca-{supplier.replace(' ', '_')}.html",
                mime="text/html",
                key=f"btn_ind_{supplier}",
                use_container_width=True
            )

        # HTML DO RECIBO COM O LOGO ORIGINAL EMBARCADO EM BASE64 À ESQUERDA
        html_recibo = f"""<html><head><meta charset='utf-8'><style>
            body {{ font-family: 'Courier New', Courier, monospace; padding: 15px; max-width: 620px; margin: auto; border: 2px dashed #000; background-color: #fafafa; }}
            .header-container {{ display: flex; align-items: center; justify-content: center; gap: 15px; margin-bottom: 12px; border-bottom: 2px solid #000; padding-bottom: 10px; }}
            .logo-img {{ width: 55px; height: 55px; flex-shrink: 0; object-fit: contain; }}
            h2 {{ margin: 0; font-size: 15px; font-weight: bold; font-family: Arial, sans-serif; text-align: left; text-transform: uppercase; line-height: 1.25; color: #000; }}
            .info-box {{ font-size: 11px; margin-bottom: 12px; border-bottom: 1px solid #000; padding-bottom: 10px; line-height: 1.4; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 12px; }}
            th {{ border-bottom: 2px solid #000; font-size: 11px; text-align: left; padding: 4px 0; }}
            td {{ padding: 6px 0; font-size: 11px; border-bottom: 1px dotted #ccc; }}
            .tot-box {{ border-top: 2px solid #000; border-bottom: 2px solid #000; font-size: 13px; font-weight: bold; padding: 8px 0; margin-bottom: 20px; }}
            .sig-section {{ margin-top: 35px; display: flex; justify-content: space-between; font-size: 10px; text-align: center; }}
            .sig-line {{ border-top: 1px solid #000; width: 46%; padding-top: 4px; }}
            .center {{ text-align: center; }} .right {{ text-align: right; }}
            .no-print {{ text-align: center; margin-bottom: 15px; }}
            .btn-print {{ background-color: #000; color: #fff; border: none; padding: 8px 12px; font-weight: bold; cursor: pointer; }}
            @media print {{ .no-print {{ display: none; }} }}
        </style></head><body>
            <div class="no-print">
                <button class="btn-print" onclick="window.print()">🖨️ Imprimir / Salvar Recibo PDF</button>
            </div>
            <div class="header-container">
                <img src="data:image/png;base64,{LOGO_B64}" class="logo-img" alt="Logo">
                <h2>RELAÇÃO DE TROCAS / DEVOLUÇÕES - APROVAÇÃO NF</h2>
            </div>
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
            <div style='font-size:10px; text-align:center; margin-bottom:25px;'>Declaro que conferi os itens discriminados acima para emissão da NF de troca/devolução.</div>
            <div class="sig-section">
                <div class="sig-line">Assinatura Promotor/Representante/Motorista</div>
                <div class="sig-line" style="float:right;">Conferente da Loja</div>
                <div style="clear:both;"></div>
            </div>
        </body></html>"""

        with col_act2:
            st.download_button(
                label=f"🧾 Recibo / Vale-Troca ({supplier.upper()})",
                data=html_recibo,
                file_name=f"{str_data_arquivo}-RECIBO-{supplier.replace(' ', '_')}.html",
                mime="text/html",
                key=f"btn_rec_{supplier}",
                use_container_width=True
            )

    st.markdown(f'<div class="grand-total-box">TOTAL GERAL DOS SELECIONADOS<br>Estoque: {grand_total_qty} | R$ {grand_total_val:,.2f}</div>', unsafe_allow_html=True)
