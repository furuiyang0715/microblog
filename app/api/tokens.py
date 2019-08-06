from flask import jsonify, g
from app import db
from app.api import bp
from app.api.auth import basic_auth, token_auth


@bp.route('/tokens', methods=['POST'])
@basic_auth.login_required
# 使用了HTTPBasicAuth实例中的@basic_auth.login_required装饰器，它将指示Flask-HTTPAuth验证身份
# 并且仅当提供的凭证是有效的才运行下面的视图函数。
def get_token():
    # 数据库提交在生成token后发出，以确保token及其到期时间被写回到数据库。
    token = g.current_user.get_token()
    db.session.commit()
    return jsonify({'token': token})


@bp.route('/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    g.current_user.revoke_token()
    db.session.commit()
    return '', 204
