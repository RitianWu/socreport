# project/api/views.py


from flask import Blueprint, jsonify, request
from project import db
from project.api.models import Report
from sqlalchemy import exc

report_blueprint = Blueprint('report', __name__)


@report_blueprint.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'Pong'
    })


@report_blueprint.route('/reports', methods=['POST'])
def add_report():
    post_data = request.get_json()
    if not post_data:
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload'
        }
        return jsonify(response_object), 400
    name = post_data.get('name')
    url = post_data.get('url')
    try:
        report = Report.query.filter(Report.url == url).first()
        if not report:
            report_object = Report(name=name, url=url)
            db.session.add(report_object)
            db.session.commit()
            response_object = {
                'status': 'success',
                'message': 'Report add success',
                'data': {
                    'report_id': report_object.id
                }
            }
            return jsonify(response_object), 201
        else:
            response_object = {
                'status': 'fail',
                'message': 'Report already exists'
            }
            return jsonify(response_object), 400
    except exc.IntegrityError as e:
        db.session.rollback()
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload'
        }
        return jsonify(response_object), 400


@report_blueprint.route('/reports/<report_id>', methods=['GET'])
def get_single_report(report_id):
    """Get single report details"""
    response_object = {
        'status': 'fail',
        'message': 'Report does not exist'
    }
    try:
        report_object = Report.query.filter(Report.id == int(report_id)).first()
        if not report_object:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'message': 'Query success',
                'data': {
                    'name': report_object.name,
                    'url': report_object.url,
                    'create_time': report_object.create_time
                }
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404


@report_blueprint.route('/reports', methods=['GET'])
def get_all_reports():
    """Get all reports"""
    reports = Report.query.all()
    reports_list = []
    for report in reports:
        report_object = {
            'id': report.id,
            'name': report.name,
            'url': report.url,
            'create_time': report.create_time
        }
        reports_list.append(report_object)
    response_object = {
        'status': 'success',
        'message': 'Query success',
        'data': {
            'reports': reports_list
        }
    }
    return jsonify(response_object), 200
