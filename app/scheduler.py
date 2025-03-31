from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit
from flask import Flask

scheduler = BackgroundScheduler(daemon=True)

def init_scheduler(app):
    hour = 20
    minute = 59
    
    scheduler.remove_all_jobs()
    
    scheduler.add_job(
        id='enviar_relatorio_semanal',
        func=enviar_relatorio_agendado,
        args=[app],
        trigger=CronTrigger(
            day_of_week='sun',
            hour=hour,
            minute=minute,
            timezone='America/Sao_Paulo'
        ),
        replace_existing=True
    )
    
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
    app.logger.info(f"Agendador iniciado - Relatório semanal configurado para domingos às {hour}:{minute} (UTC-3)")

def enviar_relatorio_agendado(app):
    """Função que será chamada pelo agendador"""
    with app.app_context():
        try:
            if app.config.get('ENV') == 'development':
                app.logger.info("Modo desenvolvimento - Simulando envio de relatório")
                return
            
            with app.test_client() as client:
                response = client.post('/relatorio-semanal')
                
                if response.status_code != 200:
                    error_msg = response.get_json().get('message', 'Erro desconhecido')
                    raise Exception(f"Erro na rota: {error_msg}")
                
                app.logger.info("Relatório semanal enviado com sucesso")
                
        except Exception as e:
            app.logger.error(f"Falha crítica no relatório agendado: {str(e)}")