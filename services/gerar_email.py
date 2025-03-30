from typing import Dict, Any, List
from app.utils.api_client import chamada_api_llm

def gerar_texto_email(
    porcentagem_positivos: float,
    porcentagem_negativos: float,
    top_features: List[Dict[str, Any]],
    api_key: str
):

    INSTRUCOES_SISTEMA = """Você é um assistente que gera relatórios semanais para stakeholders. 
    Escreva um e-mail profissional (máximo 1 parágrafo) com os seguintes dados:

    - Feedbacks positivos: {porcentagem_positivos:.1f}%
    - Feedbacks negativos: {porcentagem_negativos:.1f}%
    - Principais funcionalidades pedidas:

    Inclua:
    1. Saudação inicial.
    2. Destaque os pontos positivos e negativos.
    3. Explique a importância de cada feature (seja conciso).
    4. Chamada para ação (ex.: "Vamos priorizar X na próxima sprint?")
    5. Coloque a data do relatório no final do e-mail.
    6. Assinatura padrão da empresa.
    7. Não use emojis ou linguagem informal.
    """

    prompt = f"""
    Dados para o relatório:
    - Positivos: {porcentagem_positivos:.1f}%
    - Negativos: {porcentagem_negativos:.1f}%
    - Features:
    {chr(10).join(f"- {f['code']} ({f.get('total',0)}x): {f.get('description','')}" for f in top_features)}
    """

    try:
        resposta = chamada_api_llm(
            prompt=prompt,
            api_key=api_key,
            instrucoes_sistema=INSTRUCOES_SISTEMA
        )
        return resposta['choices'][0]['message']['content']
    except Exception as e:
        raise Exception(f"Falha ao gerar e-mail: {str(e)}")
