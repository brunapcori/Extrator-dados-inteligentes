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
# GUIA DIDÁTICO PARA O ALUNO: CONFIGURAÇÃO DE SEGREDOS (.streamlit/secrets.toml)
# ==============================================================================
# Boas práticas de segurança em nuvem recomendam NUNCA versionar ou expor chaves
# de API em código de produção. Para rodar este app localmente:
#
# 1. Na raiz do seu projeto, crie uma pasta chamada `.streamlit` (com o ponto na frente).
# 2. Dentro dela, crie um arquivo chamado `secrets.toml`.
# 3. Adicione o seguinte conteúdo:
#
#    AZURE_OPENAI_API_KEY = "sua_chave_aqui"
#    AZURE_OPENAI_ENDPOINT = "https://seu-recurso.services.ai.azure.com/"
#    AZURE_OPENAI_DEPLOYMENT = "gpt-4.1-mini"
#    AZURE_OPENAI_API_VERSION = "2024-05-01-preview"
#
# O código abaixo possui um fallback automático com os dados fornecidos para fins didáticos,
# mas sempre priorizará o `secrets.toml` caso exista!
# ==============================================================================

import json
import streamlit as st
from openai import AzureOpenAI

# ------------------------------------------------------------------------------
# 1. Configuração da Página e Identidade Visual
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Extrator Inteligente | Azure AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS personalizada para um design refinado
st.markdown("""
<style>
    .main-title {
        font-size: 2.3rem;
        font-weight: 700;
        color: #0078D4; /* Azul Microsoft */
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #555555;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #0078D4;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. Carregamento de Configurações e Inicialização do Cliente Azure
# ------------------------------------------------------------------------------
DEFAULT_ENDPOINT = "https://marcelomaffeis-05082026-resource.services.ai.azure.com/"
DEFAULT_API_KEY = "6t2pTNsmNafDyo53MDAFIrvvQRBZXP7dLcr5j3TLxMS34LQVq3ZUJQQJ99CHACHYHv6XJ3w3AAAAACOGT7os"
DEFAULT_MODEL = "gpt-4.1-mini"
API_VERSION = "2024-05-01-preview"

# Leitura segura com prioridade para st.secrets
api_key = st.secrets.get("AZURE_OPENAI_API_KEY", DEFAULT_API_KEY)
raw_endpoint = st.secrets.get("AZURE_OPENAI_ENDPOINT", DEFAULT_ENDPOINT)
endpoint = raw_endpoint.replace("&quot;", "").strip().rstrip("/")
deployment_name = st.secrets.get("
