from flask import Blueprint, request, jsonify
from commands.submit_data import SubmitCommandHandler
from queries.search_data import SearchQueryHandler
from domain.models import SubmitUserRequestModel
from pydantic import ValidationError

ingress_bp = Blueprint('ingress', __name__)

@ingress_bp.route('/submit-user-profile', methods=['POST'])
def secure_ingress():
    try:
        data = request.json
        # Validate Request
        cmd_req = SubmitUserRequestModel(**data)
        
        # Dispatch Command
        handler = SubmitCommandHandler()
        result = handler.handle(cmd_req)
        
        return jsonify(result), 200
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    except Exception as e:
        # In prod, log strict errors, don't expose internal details
        return jsonify({"error": str(e)}), 500

@ingress_bp.route('/search', methods=['GET'])
def search():
    try:
        nid = request.args.get('nid')
        if not nid:
            return jsonify({"error": "Missing nid param"}), 400
            
        # Dispatch Query
        handler = SearchQueryHandler()
        results = handler.handle(nid)
        
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
