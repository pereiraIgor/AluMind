import json
import requests
from typing import Dict, Any, List
from app.utils.api_client import chamada_api_llm

def analise_sentimentos(feedback_text: str, api_key: str):
    INSTRUCOES_SISTEMA = """Você é um analisador de sentimentos especializado. Siga estas regras:
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

    try:
        # Chamada única à API
        resposta = chamada_api_llm(
            prompt=feedback_text,
            api_key=api_key,
            instrucoes_sistema=INSTRUCOES_SISTEMA
        )
        
        # Processamento específico para análise de sentimentos
        message_content = resposta['choices'][0]['message']['content']
        
        # Limpeza do conteúdo
        if '```json' in message_content:
            message_content = message_content.split('```json')[1].split('```')[0].strip()
        elif '```' in message_content:
            message_content = message_content.split('```')[1].strip()
        content = json.loads(message_content)

        if not isinstance(content.get('sentiment'), str) or not isinstance(content.get('features'), list):
            raise ValueError("Estrutura de resposta inválida")

        features = [
            {
                'code': f.get('code', 'NO_FEATURE'),
                'description': f.get('description', 'Descrição não fornecida')
            }
            for f in content['features'] if isinstance(f, dict)
        ]

        return {
            'sentiment': content['sentiment'].upper(),
            'features': features,
            'analysis_id': resposta['id']
        }

    except json.JSONDecodeError as e:
        raise Exception(f"Falha ao decodificar JSON: {str(e)}")
    except Exception as e:
        raise Exception(f"Erro na análise: {str(e)}")