import requests
from typing import Dict, Any

def chamada_api_llm(
    prompt: str,
    api_key: str,
    instrucoes_sistema: str,
    model: str = "deepseek/deepseek-chat-v3:free",
    temperature: float = 0.3,
    timeout: int = 20
):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "AluMind"
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": instrucoes_sistema},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"},
        "temperature": temperature
    }
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=timeout
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Erro na requisição à API: {str(e)}")
    