from flask import Blueprint, jsonify, request, render_template
from app.models import Post, Feature
from app import db
from services.analise_sentimento import analise_sentimentos
from services.gerar_email import gerar_texto_email
from .validators import validate_feedback_request 
from flask import current_app
from sqlalchemy import func
from datetime import datetime, timedelta, timezone


bp = Blueprint('main', __name__)

@bp.route('/hello')
def hello():
    return "<p>Hello, World!</p>"

@bp.route('/feedbacks', methods=['POST'])
def feedbacks():
    error_response, data = validate_feedback_request(request)
    if error_response:
        return error_response
    
    feedback = data['feedback']
    id = data.get('id') 
   
    if not isinstance(feedback, str) or not feedback.strip():
        return jsonify({
            "status": "error", 
            "message": "Feedback must be a non-empty string"
        }), 400

    try:
        analysis_result = analise_sentimentos(feedback, current_app.config['OPENROUTER_API_KEY'])
    
        # print("Análise retornada:", analysis_result)
        
        post = Post(
            id=id,
            text=feedback,
            sentiment=analysis_result['sentiment']
        )

        if 'features' in analysis_result and isinstance(analysis_result['features'], list):
            for feature in analysis_result['features']:
                try:
                    post.features.append(Feature(
                        code=feature.get('code', 'NO_FEATURE'),
                        reason=feature.get('description', feature.get('reason', 'Descrição não fornecida')),
                    ))
                except Exception as feature_error:
                    print(f"Erro ao processar feature: {feature_error}")
                    continue
        
        db.session.add(post)
        db.session.commit()

        return jsonify({
            "id": str(post.id),
            "sentiment": post.sentiment,
            "requested_features": [
            {
                "code": feature.code,
                "reason": feature.reason
            } for feature in post.features
            ]
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(e),
            "type": type(e).__name__
        }), 500
    

@bp.route('/relatorio')
def relatorio():
    posts = Post.query.all()
    total_posts = len(posts)
    
    positivos = Post.query.filter_by(sentiment='POSITIVO').count()
    porcentagem_positivos = (positivos / total_posts * 100) if total_posts > 0 else 0
    
    top_features = (
        db.session.query(
            Feature.code,
            func.count(Feature.code).label('total')
        )
        .group_by(Feature.code)
        .order_by(func.count(Feature.code).desc())
        .limit(5) 
        .all()
    )
    
    return render_template(
        'relatorio.html',
        posts=posts,
        porcentagem_positivos=round(porcentagem_positivos, 2),
        top_features=top_features,
        total_posts=total_posts
    )

@bp.route('/enviar-relatorio-semanal')
def enviar_relatorio_semanal():
    data_fim = datetime.now(timezone.utc)
    data_inicio = data_fim - timedelta(days=7)

    posts = Post.query.filter(Post.date_posted.between(data_inicio, data_fim)).all()
    total_posts = len(posts)

    positivos = sum(1 for post in posts if post.sentiment == 'POSITIVO')
    negativos = sum(1 for post in posts if post.sentiment == 'NEGATIVO')
    porcentagem_positivos = (positivos / total_posts * 100) if total_posts > 0 else 0
    porcentagem_negativos = (negativos / total_posts * 100) if total_posts > 0 else 0

    top_features = [
        {"code": f[0], "total": f[1]}  
        for f in db.session.query(
            Feature.code,
            func.count(Feature.code).label('total')
        )
        .filter(Feature.post_id.in_([post.id for post in posts]))
        .group_by(Feature.code)
        .order_by(func.count(Feature.code).desc())
        .limit(3)
        .all()
    ]
    texto_email = gerar_texto_email(
        porcentagem_positivos,
        porcentagem_negativos,
        top_features,
        current_app.config['OPENROUTER_API_KEY']
    )
    return texto_email

    # 6. Envia o e-mail
    # enviar_email(
    #     destinatarios=["stakeholder1@email.com", "stakeholder2@email.com"],
    #     assunto=f"Relatório Semanal de Feedbacks - {data_fim.strftime('%d/%m/%Y')}",
    #     corpo=texto_email
    # )

    return "E-mail enviado com sucesso!"


