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
# Para evitar expor credenciais no código:
#
# 1. Crie uma pasta chamada `.streamlit` na raiz do projeto.
# 2. Crie um ficheiro `secrets.toml` dentro dela.
# 3. Adicione as seguintes chaves:
#
#    AZURE_OPENAI_API_KEY = "sua_chave_aqui"
#    AZURE_OPENAI_ENDPOINT = "https://seu-recurso.services.ai.azure.com/"
#    AZURE_OPENAI_DEPLOYMENT = "gpt-4.1-mini"
#
# No Streamlit Community Cloud, adicione estas variáveis em "Settings > Secrets".
# ==============================================================================

import json
import streamlit as st
from openai import AzureOpenAI

# ------------------------------------------------------------------------------
# 1. Configuração da Página
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Extrator Inteligente | Azure AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
# 3. Barra Lateral (Sidebar)
# ------------------------------------------------------------------------------
with st.sidebar:
    st.subheader("Infraestrutura Microsoft")
    st.info("**Plataforma:** Azure AI Foundry")
    st.caption(f"**Deployment:** `{deployment_name}`")
    st.caption(f"**API Version:** `{API_VERSION}`")
    st.divider()
    st.write(
        "Extrator de entidades, análise de sentimento e classificação de urgência "
        "com resposta estruturada em JSON via Azure OpenAI."
    )

# ------------------------------------------------------------------------------
# 4. Interface Principal
# ------------------------------------------------------------------------------
st.title("🧠 Extrator de Dados Inteligente")
st.caption("Análise semântica avançada de textos com Microsoft Azure OpenAI")

texto_usuario = st.text_area(
    label="Texto para processamento:",
    placeholder="Cole aqui o texto (e-mails, mensagens de suporte, atas de reunião, reclamações, etc.)...",
    height=180
)

col_btn, _ = st.columns([1, 4])
processar = col_btn.button("⚡ Processar", type="primary", use_container_width=True)

# ------------------------------------------------------------------------------
# 5. Processamento e Exibição Estruturada
# ------------------------------------------------------------------------------
if processar:
    if not texto_usuario.strip():
        st.warning("⚠️ Por favor, insira um texto antes de clicar em Processar.")
    else:
        with st.spinner("A analisar o texto com o Azure OpenAI..."):
            system_prompt = (
                "Você é um analisador e extrator de dados estritamente analítico e preciso.\n"
                "Sua tarefa é analisar o texto recebido e responder OBRIGATORIAMENTE com um único objeto JSON válido.\n"
                "Não inclua blocos markdown (como ```json) ou qualquer explicação antes ou depois do JSON.\n"
                "O JSON deve conter exatamente as seguintes chaves:\n"
                "1. 'sentimento': string indicando o sentimento geral ('Positivo', 'Neutro' ou 'Negativo').\n"
                "2. 'porcentagem_sentimento': número float de 0.0 a 100.0 representando a intensidade ou confiança desse sentimento.\n"
                "3. 'assunto_principal': resumo sucinto em uma frase sobre o tema principal do texto.\n"
                "4. 'pessoas_citadas': lista de strings com todos os nomes de pessoas mencionadas (ou lista vazia [] caso não haja nenhuma).\n"
                "5. 'nivel_de_urgencia': string estrita com um destes valores: 'Baixo', 'Medio' ou 'Alto'."
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

                st.success("Processamento concluído com sucesso!")
                st.subheader("📊 Informações Estruturadas")

                col1, col2, col3 = st.columns(3)
                sentimento_val = dados.get("sentimento", "N/A")
                pct_val = dados.get("porcentagem_sentimento", 0.0)
                urgencia_val = dados.get("nivel_de_urgencia", "N/A")

                with col1:
                    st.metric(label="Sentimento Detectado", value=str(sentimento_val))

                with col2:
                    st.metric(
                        label="Confiança / Intensidade",
                        value=f"{pct_val:.1f}%" if isinstance(pct_val, (int, float)) else str(pct_val)
                    )

                with col3:
                    st.metric(label="Nível de Urgência", value=str(urgencia_val))

                st.divider()

                col_resumo, col_pessoas = st.columns([2, 1])

                with col_resumo:
                    st.markdown("#### 🎯 Assunto Principal")
                    st.info(dados.get("assunto_principal", "Não identificado."))

                with col_pessoas:
                    st.markdown("#### 👥 Pessoas Citadas")
                    pessoas = dados.get("pessoas_citadas", [])
                    if pessoas and isinstance(pessoas, list):
                        for p in pessoas:
                            st.write(f"• **{p}**")
                    else:
                        st.caption("Nenhuma pessoa citada no texto.")

                st.markdown("#### 🗄️ Resposta Bruta (JSON)")
                st.json(dados)

            except Exception as erro:
                st.error(f"Erro ao comunicar com a API do Azure: {erro}")
