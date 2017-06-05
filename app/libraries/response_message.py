from flask import jsonify


def error_message(code, message):
    return jsonify({'result': 'fail', 'code': code, 'message': message}), code


def data_message(code, data, message):
    if data is not None:
        return jsonify({'result': 'success', 'code': code, 'data': data, 'message': message}), code
    else:
        return jsonify({'result': 'success', 'code': code, 'message': message}), code