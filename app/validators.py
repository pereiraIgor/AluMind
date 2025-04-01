from flask import jsonify

def validate_feedback_request(request):
    """
    Valida o request de feedback
    Retorna uma tupla (error_response, data) onde:
    - error_response é None se a validação passar
    - data é o JSON parseado se válido
    """
    if not request.is_json:
        return jsonify({
            "status": "error",
            "message": "Missing JSON in request"
        }), 400, None

    try:
        data = request.get_json()
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Invalid JSON format",
            "details": str(e)
        }), 400, None

    required_fields = ['feedback', 'id']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return jsonify({
            "status": "error",
            "message": f"Missing required fields: {', '.join(missing_fields)}"
        }), 400, None
    
    if not isinstance(data.get('feedback'), str) or not data['feedback'].strip():
        return jsonify({
            "status": "error",
            "message": "Field 'feedback' must be a non-empty string"
        }), 400, None

    return None, data
