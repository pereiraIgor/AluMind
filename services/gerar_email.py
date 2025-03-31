from typing import Dict, Any, List
from app.utils.api_client import chamada_api_llm
from datetime import datetime,timedelta
from flask import current_app, copy_current_request_context

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from threading import Thread

from dotenv import load_dotenv
import os
load_dotenv()

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


def enviar_email(destinatarios, assunto, corpo, html=None):
  
    smtp_server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('MAIL_PORT', 587))
    username = os.getenv('MAIL_USERNAME')
    password = os.getenv('MAIL_PASSWORD')
    sender = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@alumind.com')
    
    if not all([smtp_server, username, password]):
            raise Exception("Configuração de e-mail incompleta")

    msg = MIMEMultipart('alternative')
    msg['Subject'] = assunto
    msg['From'] = sender
    msg['To'] = ", ".join(destinatarios) if isinstance(destinatarios, list) else destinatarios

    part1 = MIMEText(corpo, 'plain')
    msg.attach(part1)
    
    if html:
        part2 = MIMEText(html, 'html')
        msg.attach(part2)

    @copy_current_request_context  # Preserva o contexto
    def enviar_async(app, msg):
        with app.app_context():  # Cria novo contexto
            try:
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.ehlo()
                    if current_app.config.get('MAIL_USE_TLS', True):
                        server.starttls()
                    server.login(username, password)
                    server.send_message(msg)
                    app.logger.info(f"E-mail enviado para {msg['To']}")
            except Exception as e:
                app.logger.error(f"Falha ao enviar e-mail: {str(e)}")

    # Passa a app atual para a thread
    Thread(target=enviar_async, args=(current_app._get_current_object(), msg)).start()