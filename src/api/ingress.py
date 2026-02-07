from flask import Blueprint, request, jsonify
from commands.submit_data import SubmitCommandHandler
from queries.search_data import SearchQueryHandler
from domain.models import SubmitUserRequestModel
from pydantic import ValidationError
import logging

ingress_bp = Blueprint('ingress', __name__)
logger = logging.getLogger(__name__)

@ingress_bp.route('/submit-user-profile', methods=['POST'])
def secure_ingress():
    try:
        data = request.json
        logger.info(f"Received submit-user-profile request. Keys: {list(data.keys()) if data else 'None'}")
        
        # Validate Request
        cmd_req = SubmitUserRequestModel(**data)
        
        # Dispatch Command
        handler = SubmitCommandHandler()
        result = handler.handle(cmd_req)
        
        logger.info("submit-user-profile processed successfully")
        return jsonify(result), 200
    except ValidationError as e:
        logger.error(f"Validation error in submit-user-profile: {e.errors()}")
        return jsonify({"error": e.errors()}), 400
    except Exception as e:
        logger.error(f"Error in submit-user-profile: {str(e)}")
        # In prod, log strict errors, don't expose internal details
        return jsonify({"error": str(e)}), 500

@ingress_bp.route('/search', methods=['GET'])
def search():
    try:
        nid = request.args.get('nid')
        logger.info(f"Received search request")
        
        if not nid:
            logger.warning("Missing nid param in search request")
            return jsonify({"error": "Missing nid param"}), 400
            
        # Dispatch Query
        handler = SearchQueryHandler()
        results = handler.handle(nid)
        
        logger.info(f"Search returned {len(results)} results")
        return jsonify(results), 200
    except Exception as e:
        logger.error(f"Error in search: {str(e)}")
        return jsonify({"error": str(e)}), 500
