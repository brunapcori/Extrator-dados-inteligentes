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
# 2. Barra Lateral: Configurações de Conexão com Diagnóstico Automático
# ------------------------------------------------------------------------------
secret_endpoint = st.secrets.get("AZURE_OPENAI_ENDPOINT", "")
secret_key = st.secrets.get("AZURE_OPENAI_API_KEY", "")
secret_model = st.secrets.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")

with st.sidebar:
    st.header("🔑 Configurações de Conexão")
    st.caption("Insira as credenciais do Microsoft Azure AI Foundry.")

    meu_endpoint = st.text_input(
        label="MEU_ENDPOINT",
        value=secret_endpoint,
        placeholder="https://seu-recurso.services.ai.azure.com/",
        help="Insira o URL completo do recurso gerado no portal Azure."
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
        placeholder="gpt-4o-mini",
        help="Nome exato da implantação (Deployment) criada na aba 'Deployments' do Azure AI Foundry."
    )

    api_version = st.selectbox(
        label="Versão da API",
        options=[
            "2024-06-01",
            "2024-08-01-preview",
            "2024-02-15-preview",
            "2024-05-01-preview",
            "2023-05-15"
        ],
        index=0,
        help="Seletor de compatibilidade para diferentes versões do Azure OpenAI."
    )

    tentar_correcao_auto = st.checkbox(
        "Tentar fallback automático de deployment (gpt-4o-mini)",
        value=True,
        help="Caso 'gpt-4.1-mini' devolva 404, tenta automaticamente 'gpt-4o-mini'."
    )

    st.divider()
    st.caption("🔒 Nenhuma credencial informada é guardada ou exposta no código.")

# ------------------------------------------------------------------------------
# 3. Função de Sanitização e Validação de URL
# ------------------------------------------------------------------------------
def limpar_endpoint(url: str) -> str:
    """Normaliza o endpoint removendo aspas, espaços e barras finais."""
    if not url:
        return ""
    limpo = url.replace("&quot;", "").replace('"', '').strip()
    limpo = re.sub(r"/+\$", "", limpo)
    # Se o utilizador inseriu um caminho relativo ao chat completions, remove-o
    limpo = re.sub(r"/openai/deployments.*\$", "", limpo)
    limpo = re.sub(r"/models.*\$", "", limpo)
    return limpo

endpoint_formatado = limpar_endpoint(meu_endpoint)

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
# 5. Execução do Processamento e Tratamento de Erros
# ------------------------------------------------------------------------------
if processar:
    if not minha_chave.strip() or not endpoint_formatado or not meu_modelo.strip():
        st.error("⚠️ Preencha 'MINHA_CHAVE', 'MEU_ENDPOINT' e 'MEU_MODELO' na barra lateral.")
    elif not texto_usuario.strip():
        st.warning("⚠️ Insira um texto para processamento.")
    else:
        with st.spinner("A comunicar com o serviço Azure OpenAI..."):
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

            # Lista de tentativas: primeiro o modelo digitado, seguido de fallbacks se ativado
            modelos_para_tentar = [meu_modelo.strip()]
            if tentar_correcao_auto:
                for fallback in ["gpt-4o-mini", "gpt-4o", "gpt-4"]:
                    if fallback not in modelos_para_tentar:
                        modelos_para_tentar.append(fallback)

            sucesso = False
            ultimo_erro = None

            for mod in modelos_para_tentar:
                try:
                    client = AzureOpenAI(
                        api_key=minha_chave.strip(),
                        azure_endpoint=endpoint_formatado,
                        api_version=api_version
                    )

                    response = client.chat.completions.create(
                        model=mod,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": texto_usuario}
                        ],
                        response_format={"type": "json_object"},
                        temperature=0.1
                    )

                    conteudo_raw = response.choices[0].message.content
                    dados_extraidos = json.loads(conteudo_raw)
                    sucesso = True
                    
                    if mod != meu_modelo.strip():
                        st.info(f"💡 O modelo original retornou 404, mas a requisição obteve sucesso com o deployment alternativo: **`{mod}`**.")
                    break

                except Exception as ex:
                    ultimo_erro = ex
                    # Se for 404 e tiver mais modelos na lista, tenta o próximo
                    if "404" in str(ex) and mod != modelos_para_tentar[-1]:
                        continue
                    break

            if sucesso:
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

            else:
                st.error(f"Erro na comunicação com o serviço Azure OpenAI: {ultimo_erro}")
                st.warning(
                    "🔧 **Ações recomendadas para corrigir o 404 no Azure AI Foundry:**\n\n"
                    "1. **Verifique o nome em 'Deployments':** Vá ao portal do [Azure AI Studio](https://ai.azure.com/) > separador **Deployments** e confira o valor exato da coluna **Deployment name**. O modelo padrão do OpenAI é **`gpt-4o-mini`** (com 'o'), enquanto no ecrã está preenchido `gpt-4.1-mini`.\n"
                    "2. **Verifique se o URL está completo:** O endpoint deve terminar com o domínio completo (por exemplo: `.services.ai.azure.com` ou `.openai.azure.com`).\n"
                    "3. **Alterne a versão da API:** Tente selecionar `2024-08-01-preview` ou `2024-02-15-preview` na barra lateral."
                )
