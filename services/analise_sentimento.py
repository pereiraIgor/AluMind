import json
import requests
from typing import Dict, Any

def analise_sentimentos(feedback_text: str, api_key: str) -> Dict[str, Any]:
    """
    Analisa o sentimento de um texto usando a API OpenRouter.
    
    Args:
        feedback_text: Texto a ser analisado
        api_key: Chave de API do OpenRouter
    
    Returns:
        Dicionário com análise de sentimento e features identificadas
    
    Raises:
        Exception: Em caso de erros na API ou processamento
    """
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "AluMind"
        }
        
        payload = {
            "model": "deepseek/deepseek-chat-v3:free",
            "messages": [
                {
                    "role": "system",
                    "content": """Você é um analisador de sentimentos especializado. Siga estas regras:
                        1. CLASSIFIQUE o sentimento geral como: POSITIVO, NEGATIVO, INCONCLUSIVO 

                        2. IDENTIFIQUE todos os recursos/funcionalidades mencionados (features), extraindo:
                        - Código único em MAIÚSCULAS (padrão: CATEGORIA_SUBCATEGORIA)
                        - Descrição concisa da solicitação

                        3. FORMATE a resposta como JSON válido com:
                        - sentiment (geral)
                        - features (array de objetos, um para cada ponto identificado)

                        IMPORTANTE: 
                        - Não inclua vírgulas após o último elemento de objetos/arrays
                        - Mantenha a sintaxe JSON válida

                        Exemplo CORRETO:
                        {
                        "sentiment": "POSITIVO",
                        "features": [
                            {
                            "code": "PERFORMANCE_LOAD_TIME",
                            "description": "Tempo de carregamento aumentou"
                            }
                        ]
                        }"""
                },
                {
                    "role": "user",
                    "content": feedback_text
                }
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.3 
        }

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=20
        )

        response.raise_for_status()
        result = response.json()

        message_content = result['choices'][0]['message']['content']

        if '```json' in message_content:
            message_content = message_content.split('```json')[1].split('```')[0].strip()
        elif '```' in message_content:
            message_content = message_content.split('```')[1].strip()
        content = json.loads(message_content)

        if not isinstance(content.get('sentiment'), str) or not isinstance(content.get('features'), list):
            raise ValueError("Estrutura de resposta inválida da API")

        features = []
        for feature in content['features']:
            try:
                features.append({
                    'code': feature.get('code', 'NO_FEATURE'),
                    'description': feature.get('description', 'Descrição não fornecida')
                })
            except (AttributeError, TypeError):
                continue

        return {
            'sentiment': content['sentiment'].upper(),
            'features': features,
            'analysis_id': result['id']
        }

    except json.JSONDecodeError as e:
        raise Exception(f"Falha ao decodificar JSON: {str(e)}\nConteúdo problemático: {json_content}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Erro na requisição à API: {str(e)}")
    except Exception as e:
        raise Exception(f"Erro inesperado: {str(e)}")