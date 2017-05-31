from flask import jsonify


def error_message(code, message):
    return jsonify({'type': 'error', 'code': code, 'message': message})


def info_message(code, message):
    return jsonify({'type': 'info', 'code': code, 'message': message})

