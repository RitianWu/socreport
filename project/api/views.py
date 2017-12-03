# project/api/views.py


from flask import Blueprint, jsonify

report_blueprint = Blueprint('report', __name__)


@report_blueprint.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })
