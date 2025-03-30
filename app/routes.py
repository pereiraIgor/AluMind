from flask import Blueprint, jsonify, request
from app.models import Post, Feature
from app import db
from services.analise_sentimento import analise_sentimentos
from .validators import validate_feedback_request 
from flask import current_app

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