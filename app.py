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

import json
import re
import requests
import streamlit as st
from openai import AzureOpenAI

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
# 2. Barra Lateral: Configurações de Conexão
# ------------------------------------------------------------------------------
secret_endpoint = st.secrets.get("AZURE_OPENAI_ENDPOINT", "")
secret_key = st.secrets.get("AZURE_OPENAI_API_KEY", "")
secret_model = st.secrets.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1-mini")

with st.sidebar:
    st.header("🔑 Configurações de Conexão")
    st.caption("Insira as credenciais do Microsoft Azure AI Foundry com segurança.")

    meu_endpoint = st.text_input(
        label="MEU_ENDPOINT",
        value=secret_endpoint,
        placeholder="https://marcelomaffeis-7430-resource.services.ai.azure.com/",
        help="URL base do recurso gerado no portal do Azure."
    )

    minha_chave = st.text_input(
        label="MINHA_CHAVE",
        value=secret_key,
        type="password",
        placeholder="••••••••••••••••••••••••",
        help="Chave de API (Key 1 ou Key 2)."
    )

    meu_modelo = st.text_input(
        label="MEU_MODELO (Deployment Name)",
        value=secret_model,
        placeholder="gpt-4.1-mini",
        help="Nome do deployment ou modelo (ex: gpt-4.1-mini ou gpt-4o-mini)."
    )

    api_version = st.selectbox(
        label="Versão da API",
        options=["2024-06-01", "2024-02-15-preview", "2024-05-01-preview", "2024-08-01-preview"],
        index=0
    )

    st.divider()
    st.caption("🔒 Nenhuma credencial informada é guardada ou exposta no código.")

# ------------------------------------------------------------------------------
# 3. Normalização e Higienização do Endpoint
# ------------------------------------------------------------------------------
def normalizar_url(url: str) -> str:
    """Higieniza o endpoint e completa o domínio do Azure caso tenha sido cortado."""
    if not url:
        return ""
    limpo = url.replace("&quot;", "").replace('"', '').strip()
    limpo = re.sub(r"/+\$", "", limpo)
    limpo = re.sub(r"/openai/deployments.*\$", "", limpo)
    limpo = re.sub(r"/models.*\$", "", limpo)

    # Se foi colado um link cortado terminando em .se ou sem o domínio completo
    if limpo.endswith(".se") or limpo.endswith(".services") or limpo.endswith(".services.ai"):
        limpo = re.sub(r"\.(se|services|services\.ai)\$", ".services.ai.azure.com", limpo)

    return limpo

endpoint_formatado = normalizar_url(meu_endpoint)

# ------------------------------------------------------------------------------
# 4. Interface Principal
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
# 5. Função de Inferência com Resolução Universal (SDK + Foundry REST)
# ------------------------------------------------------------------------------
def executar_inferencia(ep: str, key: str, deployment: str, version: str, prompt_sistema: str, prompt_usuario: str):
    """Executa a requisição via AzureOpenAI SDK com fallback para Azure AI Foundry REST API."""
    # Lista de nomes de modelos para testar (o informado e possíveis variações comuns)
    candidatos_modelos = [deployment.strip()]
    if deployment.strip() == "gpt-4.1-mini":
        candidatos_modelos.append("gpt-4o-mini")

    ultimo_erro = None

    for mod in candidatos_modelos:
        # Método 1: SDK Oficial AzureOpenAI
        try:
            client = AzureOpenAI(
                api_key=key.strip(),
                azure_endpoint=ep,
                api_version=version
            )
            resp = client.chat.completions.create(
                model=mod,
                messages=[
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": prompt_usuario}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            return json.loads(resp.choices[0].message.content)
        except Exception as e:
            ultimo_erro = e
            if "404" not in str(e):
                raise e

        # Método 2: Rota REST nativa do Azure AI Foundry / Serverless (services.ai.azure.com)
        rotas_foundry = [
            f"{ep}/chat/completions?api-version={version}",
            f"{ep}/models/chat/completions?api-version=2024-05-01-preview",
            f"{ep}/openai/deployments/{mod}/chat/completions?api-version={version}"
        ]

        headers = {
            "Content-Type": "application/json",
            "api-key": key.strip()
        }

        payload = {
            "messages": [
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": prompt_usuario}
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }

        for rota in rotas_foundry:
            try:
                r = requests.post(rota, headers=headers, json=payload, timeout=30)
                if r.status_code == 200:
                    dados_resp = r.json()
                    conteudo = dados_resp["choices"][0]["message"]["content"]
                    return json.loads(conteudo)
            except Exception:
                continue

    raise ultimo_erro

# ------------------------------------------------------------------------------
# 6. Pipeline de Execução
# ------------------------------------------------------------------------------
if processar:
    if not minha_chave.strip() or not endpoint_formatado or not meu_modelo.strip():
        st.error("⚠️ Preencha 'MINHA_CHAVE', 'MEU_ENDPOINT' e 'MEU_MODELO' na barra lateral.")
    elif not texto_usuario.strip():
        st.warning("⚠️ Insira um texto para processamento.")
    else:
        with st.spinner("A processar os dados com a infraestrutura Microsoft Azure..."):
            system_prompt = (
                "Você é um analisador e extrator de dados analítico e rigoroso.\n"
                "Sua única tarefa é analisar o texto enviado pelo utilizador e retornar OBRIGATORIAMENTE "
                "um único objeto JSON válido, sem marcação markdown (como ```json) ou qualquer texto adicional.\n\n"
                "O JSON deve conter exatamente as seguintes chaves:\n"
                "- 'sentimento': string indicando o sentimento geral ('Positivo', 'Neutro' ou 'Negativo').\n"
                "- 'porcentagem_sentimento': float entre 0.0 e 100.0 representando a intensidade/certeza desse sentimento.\n"
                "- 'assunto_principal': resumo sucinto em uma frase sobre o tema central.\n"
                "- 'pessoas_citadas': lista de strings com todos os nomes de pessoas mencionadas (ou lista vazia [] caso não haja nenhuma).\n"
                "- 'nivel_de_urgencia': string estritamente com um dos seguintes valores: 'Baixo', 'Medio' ou 'Alto'."
            )

            try:
                dados_extraidos = executar_inferencia(
                    ep=endpoint_formatado,
                    key=minha_chave,
                    deployment=meu_modelo,
                    version=api_version,
                    prompt_sistema=system_prompt,
                    prompt_usuario=texto_usuario
                )

                st.success("Extração realizada com sucesso!")
                st.subheader("📊 Métricas Analíticas")

                col_sent, col_pct, col_urg = st.columns(3)

                sentimento = dados_extraidos.get("sentimento", "N/A")
                pct_sentimento = dados_extraidos.get("porcentagem_sentimento", 0.0)
                urgencia = dados_extraidos.get("nivel_de_urgencia", "N/A")

                with col_sent:
                    st.metric(label="Sentimento", value=str(sentimento))

                with col_pct:
                    valor_fmt = f"{pct_sentimento:.1f}%" if isinstance(pct_sentimento, (int, float)) else str(pct_sentimento)
                    st.metric(label="Porcentagem de Sentimento", value=valor_fmt)

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

            except Exception as erro_final:
                st.error(f"Erro na comunicação com o serviço Azure OpenAI: {erro_final}")
                st.info(
                    "💡 **Verificação final recomendada:**\n"
                    "No portal do Azure AI Studio / Foundry, confirme se o endpoint termina em `.services.ai.azure.com` "
                    "e se a implantação na secção 'Deployments' está ativa e saudável."
                )
