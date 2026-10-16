"""
MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# ==============================================================================
# GUIA DIDÁTICO: CONFIGURAÇÃO DE SEGREDOS (.streamlit/secrets.toml)
# ==============================================================================
# 1. Crie uma pasta chamada `.streamlit` na raiz do projeto.
# 2. Crie um ficheiro `secrets.toml` dentro dela.
# 3. Adicione as chaves:
#    AZURE_OPENAI_API_KEY = "sua_chave_aqui"
#    AZURE_OPENAI_ENDPOINT = "https://seu-recurso.services.ai.azure.com/"
#    AZURE_OPENAI_DEPLOYMENT = "gpt-4.1-mini"
# ==============================================================================

import json
import streamlit as st
from openai import AzureOpenAI

# ------------------------------------------------------------------------------
# 1. Configuração da Página e Tema Futurista com Alto Contraste
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="NEXUS AI | Extrator Neural",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS completa corrigindo áreas de texto, barra lateral e contraste
CSS_THEME = (
    "<style>\n"
    "    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@500;600;700&display=swap');\n"
    "    \n"
    "    /* Fundo da Aplicação */\n"
    "    .stApp {\n"
    "        background: radial-gradient(circle at top right, #0d1b2a 0%, #050b14 100%) !important;\n"
    "        color: #e0e6ed !important;\n"
    "        font-family: 'Rajdhani', sans-serif;\n"
    "    }\n"
    "    \n"
    "    /* Barra Lateral (Sidebar) no tema escuro */\n"
    "    section[data-testid='stSidebar'] {\n"
    "        background-color: #070e18 !important;\n"
    "        border-right: 1px solid rgba(0, 242, 254, 0.2) !important;\n"
    "    }\n"
    "    \n"
    "    /* Títulos */\n"
    "    .futuristic-title {\n"
    "        font-family: 'Orbitron', monospace;\n"
    "        font-size: 2.3rem;\n"
    "        font-weight: 900;\n"
    "        letter-spacing: 2px;\n"
    "        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%);\n"
    "        -webkit-background-clip: text;\n"
    "        -webkit-text-fill-color: transparent;\n"
    "        text-shadow: 0 0 25px rgba(0, 242, 254, 0.35);\n"
    "        margin-bottom: 0.1rem;\n"
    "    }\n"
    "    \n"
    "    .futuristic-sub {\n"
    "        font-size: 1.05rem;\n"
    "        color: #7f9cf5;\n"
    "        letter-spacing: 1px;\n"
    "        margin-bottom: 1.8rem;\n"
    "    }\n"
    "    \n"
    "    /* Rótulo da caixa de texto (Label) */\n"
    "    div[data-testid='stTextArea'] label {\n"
    "        color: #00f2fe !important;\n"
    "        font-size: 1.05rem !important;\n"
    "        font-weight: 600 !important;\n"
    "        letter-spacing: 1px !important;\n"
    "    }\n"
    "    \n"
    "    /* Caixa de Texto (Fundo escuro e letras brancas bem visíveis) */\n"
    "    div[data-testid='stTextArea'] textarea {\n"
    "        background-color: #0a1526 !important;\n"
    "        color: #ffffff !important;\n"
    "        font-family: 'Rajdhani', sans-serif !important;\n"
    "        font-size: 1.15rem !important;\n"
    "        border: 1px solid #00f2fe !important;\n"
    "        border-radius: 8px !important;\n"
    "        box-shadow: 0 0 10px rgba(0, 242, 254, 0.15) !important;\n"
    "    }\n"
    "    \n"
    "    div[data-testid='stTextArea'] textarea:focus {\n"
    "        border-color: #38bdf8 !important;\n"
    "        box-shadow: 0 0 15px rgba(56, 189, 248, 0.4) !important;\n"
    "    }\n"
    "    \n"
    "    div[data-testid='stTextArea'] textarea::placeholder {\n"
    "        color: #64748b !important;\n"
    "    }\n"
    "    \n"
    "    /* Botão Primário em Ciano Futurista */\n"
    "    div.stButton > button[kind='primary'] {\n"
    "        background: linear-gradient(90deg, #00f2fe 0%, #0078D4 100%) !important;\n"
    "        color: #050b14 !important;\n"
    "        font-family: 'Orbitron', monospace !important;\n"
    "        font-weight: 700 !important;\n"
    "        letter-spacing: 1px !important;\n"
    "        border: none !important;\n"
    "        box-shadow: 0 0 15px rgba(0, 242, 254, 0.4) !important;\n"
    "        transition: all 0.3s ease !important;\n"
    "    }\n"
    "    \n"
    "    div.stButton > button[kind='primary']:hover {\n"
    "        box-shadow: 0 0 25px rgba(0, 242, 254, 0.7) !important;\n"
    "        transform: scale(1.02);\n"
    "    }\n"
    "    \n"
    "    /* Cartões Glassmorphism */\n"
    "    .glass-card {\n"
    "        background: rgba(13, 27, 42, 0.75);\n"
    "        border: 1px solid rgba(0, 242, 254, 0.25);\n"
    "        border-radius: 12px;\n"
    "        padding: 18px;\n"
    "        box-shadow: 0 8px 32px 0 rgba(0, 20, 40, 0.4);\n"
    "        backdrop-filter: blur(8px);\n"
    "        margin-bottom: 15px;\n"
    "    }\n"
    "    \n"
    "    .badge-tag {\n"
    "        display: inline-block;\n"
    "        background: rgba(0, 242, 254, 0.12);\n"
    "        border: 1px solid #00f2fe;\n"
    "        color: #00f2fe;\n"
    "        padding: 5px 12px;\n"
    "        border-radius: 6px;\n"
    "        font-size: 0.95rem;\n"
    "        margin: 3px;\n"
    "    }\n"
    "    \n"
    "    /* Métricas */\n"
    "    div[data-testid='stMetric'] {\n"
    "        background: rgba(15, 23, 42, 0.85);\n"
    "        border: 1px solid rgba(79, 172, 254, 0.35);\n"
    "        padding: 14px 20px;\n"
    "        border-radius: 10px;\n"
    "        box-shadow: 0 0 15px rgba(79, 172, 254, 0.15);\n"
    "    }\n"
    "    \n"
    "    div[data-testid='stMetricLabel'] {\n"
    "        color: #94a3b8 !important;\n"
    "        font-size: 0.95rem !important;\n"
    "    }\n"
    "    \n"
    "    div[data-testid='stMetricValue'] {\n"
    "        color: #38bdf8 !important;\n"
    "        font-family: 'Orbitron', monospace !important;\n"
    "        font-size: 1.8rem !important;\n"
    "    }\n"
    "</style>\n"
)
st.markdown(CSS_THEME, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. Credenciais com Fallback Seguro
# ------------------------------------------------------------------------------
DEFAULT_ENDPOINT = "https://marcelomaffeis-05082026-resource.services.ai.azure.com/"
DEFAULT_API_KEY = "6t2pTNsmNafDyo53MDAFIrvvQRBZXP7dLcr5j3TLxMS34LQVq3ZUJQQJ99CHACHYHv6XJ3w3AAAAACOGT7os"
DEFAULT_MODEL = "gpt-4.1-mini"
API_VERSION = "2024-05-01-preview"

api_key = st.secrets.get("AZURE_OPENAI_API_KEY", DEFAULT_API_KEY)
raw_endpoint = st.secrets.get("AZURE_OPENAI_ENDPOINT", DEFAULT_ENDPOINT)
endpoint = raw_endpoint.replace("&quot;", "").strip().rstrip("/")
deployment_name = st.secrets.get("AZURE_OPENAI_DEPLOYMENT", DEFAULT_MODEL)

@st.cache_resource
def get_azure_client(key: str, ep: str) -> AzureOpenAI:
    return AzureOpenAI(
        api_key=key,
        azure_endpoint=ep,
        api_version=API_VERSION
    )

client = get_azure_client(api_key, endpoint)

# ------------------------------------------------------------------------------
# 3. Painel Lateral de Telemetria
# ------------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🛰️ TELEMETRIA DO SISTEMA")
    st.markdown(
        "<div class='glass-card'>"
        "<p style='margin:0; font-size:0.85rem; color:#94a3b8;'>NÓ CENTRAL</p>"
        "<p style='margin:0; font-weight:bold; color:#38bdf8;'>Microsoft Foundry</p>"
        "<hr style='border:0; border-top:1px solid rgba(255,255,255,0.1); margin:8px 0;'>"
        f"<p style='margin:0; font-size:0.85rem; color:#94a3b8;'>MODELO: <span style='color:#e2e8f0;'>{deployment_name}</span></p>"
        f"<p style='margin:0; font-size:0.85rem; color:#94a3b8;'>PROTOCOLO: <span style='color:#e2e8f0;'>{API_VERSION}</span></p>"
        "</div>",
        unsafe_allow_html=True
    )
    st.markdown("#### ⚡ Status Operacional")
    st.success("Rede Neural Conectada")
    st.caption("Modo de inferência estruturada em formato estrito JSON.")

# ------------------------------------------------------------------------------
# 4. Interface Principal
# ------------------------------------------------------------------------------
st.markdown("<div class='futuristic-title'>⚡ NEXUS DATA EXTRACTOR</div>", unsafe_allow_html=True)
st.markdown("<div class='futuristic-sub'>// Extração Semântica e Cognição Automatizada via Azure AI</div>", unsafe_allow_html=True)

texto_usuario = st.text_area(
    label="Transmissão de Dados para Decodificação:",
    placeholder="Cole aqui o texto a ser analisado...",
    height=170
)

col_action, _ = st.columns([1, 3])
processar = col_action.button("🔮 EXECUTAR EXTRAÇÃO", type="primary", use_container_width=True)

# ------------------------------------------------------------------------------
# 5. Processamento e Visualização de Resultados
# ------------------------------------------------------------------------------
if processar:
    if not texto_usuario.strip():
        st.warning("⚠️ Fluxo de dados nulo. Por favor, introduza texto para decodificação.")
    else:
        with st.spinner("⏳ A sintetizar tensores neurais no Azure AI..."):
            system_prompt = (
                "Você é um núcleo de inteligência analítica com capacidade de extração estruturada.\n"
                "Analise o texto fornecido e retorne ESTRITAMENTE um objeto JSON válido, "
                "sem markdown e sem explicações externas.\n"
                "Chaves obrigatórias no JSON:\n"
                "- 'sentimento': string ('Positivo', 'Neutro' ou 'Negativo')\n"
                "- 'porcentagem_sentimento': float de 0.0 a 100.0 (confiança ou intensidade)\n"
                "- 'assunto_principal': frase concisa descrevendo o tópico principal\n"
                "- 'pessoas_citadas': lista de strings com nomes próprios identificados (ou [] se não houver)\n"
                "- 'nivel_de_urgencia': string estrita ('Baixo', 'Medio' ou 'Alto')"
            )

            try:
                response = client.chat.completions.create(
                    model=deployment_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": texto_usuario}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.1
                )

                conteudo_raw = response.choices[0].message.content
                dados = json.loads(conteudo_raw)

                sentimento_val = dados.get("sentimento", "Indefinido")
                pct_val = dados.get("porcentagem_sentimento", 0.0)
                urgencia_val = dados.get("nivel_de_urgencia", "Indefinido")

                st.markdown("<h3 style='color:#38bdf8; font-family:Orbitron;'>🔬 TELEMETRIA DE RESULTADOS</h3>", unsafe_allow_html=True)

                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric(label="Polaridade Sentimental", value=str(sentimento_val))
                with c2:
                    st.metric(
                        label="Confiança Neural",
                        value=f"{pct_val:.1f}%" if isinstance(pct_val, (int, float)) else str(pct_val)
                    )
                with c3:
                    st.metric(label="Grau de Prioridade", value=str(urgencia_val))

                st.markdown("<br>", unsafe_allow_html=True)

                col_resumo, col_entidades = st.columns([1.8, 1.2])

                with col_resumo:
                    st.markdown(
                        "<div class='glass-card'>"
                        "<h4 style='color:#00f2fe; margin-top:0;'>📍 Sumário Central</h4>"
                        f"<p style='font-size:1.05rem; color:#e2e8f0;'>{dados.get('assunto_principal', 'Não catalogado.')}</p>"
                        "</div>",
                        unsafe_allow_html=True
                    )

                with col_entidades:
                    pessoas = dados.get("pessoas_citadas", [])
                    badges = "".join([f"<span class='badge-tag'>{p}</span>" for p in pessoas]) if pessoas else "<span style='color:#64748b;'>Nenhum vetor de identidade detetado.</span>"
                    st.markdown(
                        "<div class='glass-card'>"
                        "<h4 style='color:#00f2fe; margin-top:0;'>👤 Vetores de Identidade</h4>"
                        f"{badges}"
                        "</div>",
                        unsafe_allow_html=True
                    )

                with st.expander("📡 CARGA ÚTIL DA MATRIZ (RAW JSON)", expanded=False):
                    st.json(dados)

            except Exception as erro:
                st.error(f"Falha na comunicação com o nó Azure: {erro}")
