from flask import jsonify, request
from app import db
from app.api.auth import basic_auth, token_auth
from app.api import bp

@bp.route('/token', methods=['POST'])
@basic_auth.login_required
def get_token():
    token = basic_auth.current_user().get_token()
    db.session.commit()
    return jsonify({'token': token})

@bp.route('/token', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    token = token_auth.current_user().revoke_token()
    db.session.commit()
    return '', 204
