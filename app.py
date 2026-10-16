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
    "    /* Rótulo da caixa
