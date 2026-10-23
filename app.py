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
# Boas práticas de segurança em desenvolvimento de software recomendam nunca
# versionar chaves de API diretamente em repositórios públicos como o GitHub.
#
# Para rodar com segurança na sua máquina:
# 1. Crie uma pasta chamada `.streamlit` na raiz do projeto.
# 2. Crie um arquivo `secrets.toml` dentro dela:
#
#    AZURE_OPENAI_API_KEY = "1gsyJYiGIr1rIjIm6heIq96VWJI5gMgXeXCaYCHx5WeeWGm3AMYvJQQJ99CJACHYHv6XJ3w3AAAAACOGUF3S"
#    AZURE_OPENAI_ENDPOINT = "https://marcelomaffeis-7430-resource.services.ai.azure.com/openai/v1"
#    AZURE_OPENAI_DEPLOYMENT = "gpt-4.1-mini"
#
# Na barra lateral, o usuário pode inserir ou alterar essas três variáveis
# diretamente na interface.
# ==============================================================================

import json
import streamlit as st
from openai import OpenAI

# ------------------------------------------------------------------------------
# 1. Configuração da Página e Estilos
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
# 2. Barra Lateral: Solicitação das Credenciais
# ------------------------------------------------------------------------------
DEFAULT_ENDPOINT = "https://marcelomaffeis-7430-resource.services.ai.azure.com/openai/v1"
DEFAULT_CHAVE = "1gsyJYiGIr1rIjIm6heIq96VWJI5gMgXeXCaYCHx5WeeWGm3AMYvJQQJ99CJACHYHv6XJ3w3AAAAACOGUF3S"
DEFAULT_MODELO = "gpt-4.1-mini"

with st.sidebar:
    st.header("🔑 Configurações de Conexão")
    st.caption("Insira os parâmetros de conexão com o Microsoft Foundry:")

    meu_endpoint = st.text_input(
        label="MEU_ENDPOINT",
        value=st.secrets.get("AZURE_OPENAI_ENDPOINT", DEFAULT_ENDPOINT),
        placeholder="https://seu-recurso.services.ai.azure.com/openai/v1",
        help="URL de conexão direta da API."
    )

    minha_chave = st.text_input(
        label="MINHA_CHAVE",
        value=st.secrets.get("AZURE_OPENAI_API_KEY", DEFAULT_CHAVE),
        type="password",
        placeholder="••••••••••••••••••••••••",
        help="Chave de autenticação do recurso."
    )

    meu_modelo = st.text_input(
        label="MEU_MODELO",
        value=st.secrets.get("AZURE_OPENAI_DEPLOYMENT", DEFAULT_MODELO),
        placeholder="gpt-4.1-mini",
        help="Nome do modelo ou implantação a ser chamado."
    )

    st.divider()
    st.caption("🔒 Nenhuma credencial informada é exposta publicamente.")

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
# 4. Processamento com o Modelo
# ------------------------------------------------------------------------------
if processar:
    endpoint_limpo = meu_endpoint.replace("&quot;", "").replace('"', '').strip().rstrip("/")
    chave_limpa = minha_chave.strip()
    modelo_limpo = meu_modelo.strip()

    if not chave_limpa or not endpoint_limpo or not modelo_limpo:
        st.error("⚠️ Preencha MINHA_CHAVE, MEU_ENDPOINT e MEU_MODELO na barra lateral antes de continuar.")
    elif not texto_usuario.strip():
        st.warning("⚠️ Insira um texto para processamento.")
    else:
        with st.spinner("Processando texto com o Azure OpenAI..."):
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
                # Conexão direta utilizando o endpoint OpenAI /v1 do Azure
                client = OpenAI(
                    api_key=chave_limpa,
                    base_url=endpoint_limpo
                )

                response = client.chat.completions.create(
                    model=modelo_limpo,
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

                # Exibição das métricas
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

                # Exibição estruturada de assunto e pessoas
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
                st.error(f"Erro na comunicação com a API: {api_err}")
