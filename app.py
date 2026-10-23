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
# Para não expor suas credenciais publicamente no repositório do GitHub:
#
# 1. Você pode preencher os campos diretamente na barra lateral (Sidebar) do app,
#    com a chave protegida por máscara de senha.
# 2. Alternativamente, em ambiente local ou no Streamlit Cloud, crie o arquivo
#    `.streamlit/secrets.toml` com:
#
#    AZURE_OPENAI_API_KEY = "sua_chave_aqui"
#    AZURE_OPENAI_ENDPOINT = "https://seu-recurso.services.ai.azure.com/"
#    AZURE_OPENAI_DEPLOYMENT = "gpt-4.1-mini"
#
# Quando presentes no secrets.toml, os campos da barra lateral serão preenchidos
# automaticamente, mas ainda poderão ser alterados pelo usuário se necessário.
# ==============================================================================

import json
import streamlit as st
from openai import AzureOpenAI

# ------------------------------------------------------------------------------
# 1. Configuração da Página e Estilos Visuais
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Extrator Inteligente | Azure OpenAI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
        .main-header {
            font-size: 2.2rem;
            font-weight: 700;
            color: #0078D4;
            margin-bottom: 0.2rem;
        }
        .sub-header {
            font-size: 1.05rem;
            color: #4b5563;
            margin-bottom: 1.8rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ------------------------------------------------------------------------------
# 2. Barra Lateral: Coleta Segura de Credenciais do Usuário
# ------------------------------------------------------------------------------
API_VERSION = "2024-05-01-preview"

# Valores padrão recuperados de secrets (se existirem), ou vazios para preenchimento
secret_endpoint = st.secrets.get("AZURE_OPENAI_ENDPOINT", "")
secret_key = st.secrets.get("AZURE_OPENAI_API_KEY", "")
secret_model = st.secrets.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1-mini")

with st.sidebar:
    st.header("🔑 Configurações de Conexão")
    st.caption("Insira suas credenciais do Microsoft Azure AI Foundry com segurança.")

    meu_endpoint = st.text_input(
        label="MEU_ENDPOINT",
        value=secret_endpoint,
        placeholder="https://seu-recurso.services.ai.azure.com/",
        help="URL base do endpoint criado no Azure AI Foundry."
    )

    minha_chave = st.text_input(
        label="MINHA_CHAVE",
        value=secret_key,
        type="password",
        placeholder="••••••••••••••••••••••••",
        help="Chave de API (Key 1 ou Key 2) do seu recurso no Azure."
    )

    meu_modelo = st.text_input(
        label="MEU_MODELO",
        value=secret_model,
        placeholder="gpt-4.1-mini",
        help="Nome exato do deployment do modelo implantado no Azure Foundry."
    )

    st.divider()
    st.info(f"**Versão da API:** `{API_VERSION}`")
    st.caption("🔒 Nenhuma credencial informada acima é versionada ou salva no repositório.")

# Sanitização da URL do endpoint
endpoint_formatado = meu_endpoint.replace("&quot;", "").strip().rstrip("/")

# ------------------------------------------------------------------------------
# 3. Interface Principal
# ------------------------------------------------------------------------------
st.markdown('<div class="main-header">⚡ Extrator de Dados Inteligente</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Estruturação semântica e análise textual via Microsoft Azure OpenAI</div>', unsafe_allow_html=True)

texto_usuario = st.text_area(
    label="Texto para processamento:",
    placeholder="Cole aqui o texto (e-mails, mensagens de suporte, atas de reunião, relatórios)...",
    height=180
)

col_acao, _ = st.columns([1, 4])
processar = col_acao.button("🚀 Processar", type="primary", use_container_width=True)

# ------------------------------------------------------------------------------
# 4. Processamento com Validações e Chamada ao Azure OpenAI
# ------------------------------------------------------------------------------
if processar:
    if not minha_chave.strip() or not endpoint_formatado or not meu_modelo.strip():
        st.error("⚠️ Configurações incompletas! Preencha 'MINHA_CHAVE', 'MEU_ENDPOINT' e 'MEU_MODELO' na barra lateral para continuar.")
    elif not texto_usuario.strip():
        st.warning("⚠️ Insira um texto para processamento.")
    else:
        with st.spinner("Processando dados com o Azure OpenAI..."):
            system_prompt = (
                "Você é um analisador e extrator de dados altamente preciso e analítico.\n"
                "Sua única tarefa é analisar o texto enviado pelo usuário e retornar OBRIGATORIAMENTE "
                "um único objeto JSON válido, sem blocos markdown (como ```json) ou qualquer texto adicional.\n\n"
                "O JSON deve conter exatamente as seguintes chaves:\n"
                "- 'sentimento': string indicando o sentimento geral ('Positivo', 'Neutro' ou 'Negativo').\n"
                "- 'porcentagem_sentimento': float entre 0.0 e 100.0 representando a intensidade/certeza desse sentimento.\n"
                "- 'assunto_principal': resumo sucinto em uma frase sobre o tema central.\n"
                "- 'pessoas_citadas': lista de strings com todos os nomes de pessoas mencionadas (ou lista vazia [] caso não haja nenhuma).\n"
                "- 'nivel_de_urgencia': string estritamente com um dos seguintes valores: 'Baixo', 'Medio' ou 'Alto'."
            )

            try:
                # Inicialização dinâmica do cliente Azure OpenAI com as credenciais do usuário
                client = AzureOpenAI(
                    api_key=minha_chave.strip(),
                    azure_endpoint=endpoint_formatado,
                    api_version=API_VERSION
                )

                response = client.chat.completions.create(
                    model=meu_modelo.strip(),
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": texto_usuario}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.1
                )

                conteudo_raw = response.choices[0].message.content
                dados_extraidos = json.loads(conteudo_raw)

                st.success("Extração realizada com sucesso!")
                st.subheader("📊 Métricas Analíticas")

                col_sent, col_pct, col_urg = st.columns(3)

                sentimento = dados_extraidos.get("sentimento", "N/A")
                pct_sentimento = dados_extraidos.get("porcentagem_sentimento", 0.0)
                urgencia = dados_extraidos.get("nivel_de_urgencia", "N/A")

                with col_sent:
                    st.metric(label="Sentimento", value=str(sentimento))

                with col_pct:
                    valor_formatado = f"{pct_sentimento:.1f}%" if isinstance(pct_sentimento, (int, float)) else str(pct_sentimento)
                    st.metric(label="Porcentagem de Sentimento", value=valor_formatado)

                with col_urg:
                    st.metric(label="Nível de Urgência", value=str(urgencia))

                st.divider()

                col_assunto, col_pessoas = st.columns([2, 1])

                with col_assunto:
                    st.markdown("#### 🎯 Assunto Principal")
                    st.info(dados_extraidos.get("assunto_principal", "Nenhum assunto identificado."))

                with col_pessoas:
                    st.markdown("#### 👥 Pessoas Citadas")
                    pessoas = dados_extraidos.get("pessoas_citadas", [])
                    if pessoas and isinstance(pessoas, list):
                        for pessoa in pessoas:
                            st.write(f"- **{pessoa}**")
                    else:
                        st.caption("Nenhuma pessoa citada no texto.")

                st.markdown("#### 🗄️ JSON Estruturado")
                st.json(dados_extraidos)

            except json.JSONDecodeError as json_err:
                st.error(f"Erro ao decodificar a resposta JSON do modelo: {json_err}")
            except Exception as api_err:
                st.error(f"Erro na comunicação com o serviço Azure OpenAI: {api_err}")
