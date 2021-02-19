from app.api import bp
from flask import jsonify, request, url_for, abort
from app.models import User
from app import db
from app.api.errors import bad_request
from app.api.auth import token_auth


@bp.route('/users/<int:id>', methods = ['GET'])
@token_auth.login_required
def get_user(id):
    user = User.query.get_or_404(id).to_dict()
    return jsonify(user)

@bp.route('/users', methods= ['GET'])
@token_auth.login_required
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.coll_to_dict(User.query, page, per_page, 'api.get_users')
    return jsonify(data)

@bp.route('/users/<int:id>/followers', methods=['GET'])
@token_auth.login_required
def get_followers(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.coll_to_dict(user.followers, page, per_page,
                            'api.get_followers', id=id)
    return jsonify(data)

@bp.route('/users/<int:id>/followed', methods = ['GET'])
@token_auth.login_required
def get_followed(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.coll_to_dict(user.followed, page, per_page,
                            'api.get_followers', id=id)
    return jsonify(data)

@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    if 'username' not in data or 'email' not in data or 'password' not in data:
        return bad_request('The submitted data must contain email, username and password')
    if User.query.filter_by(username=data['username']).first():
        return bad_request('Username already taken')
    if User.query.filter_by(email=data['email']).first():
        return bad_request('There is an existing account with this email, try recovering your password')
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response

@bp.route('/users/<int:id>', methods = ['PUT'])
@token_auth.login_required
def update_user(id):
    if token_auth.current_user().id != id:
        abort(403)
    user = User.query.get_or_404(id)
    data = request.get_json() or {}
    if 'username' in data and user.username != data['username']:
        if User.query.filter_by(username=data['username']).first():
            return bad_request('Username already taken')
    if 'email' in data and user.email != data['email']:
        if User.query.filter_by(email=data['email']).first():
            return bad_request('Email already taken')
    user.from_dict(data)
    db.session.commit()
    return jsonify(user.to_dict())
