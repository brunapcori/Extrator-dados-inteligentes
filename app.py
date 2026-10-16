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
# Para evitar expor credenciais sensíveis no código de produção:
#
# 1. Crie uma pasta chamada `.streamlit` na raiz do projeto.
# 2. Crie um arquivo `secrets.toml` dentro dela.
# 3. Adicione as chaves:
#
#    AZURE_OPENAI_API_KEY = "sua_chave_aqui"
#    AZURE_OPENAI_ENDPOINT = "https://seu-recurso.services.ai.azure.com/"
#    AZURE_OPENAI_DEPLOYMENT = "gpt-4.1-mini"
#
# No Streamlit Cloud, adicione essas mesmas variáveis na aba "Settings > Secrets".
# ==============================================================================

import json
import streamlit as st
from openai import AzureOpenAI

# ------------------------------------------------------------------------------
# 1. Configuração da Página e Estilos
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Extrator Inteligente | Azure AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 70
