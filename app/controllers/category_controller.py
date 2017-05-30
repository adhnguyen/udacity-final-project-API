from app.database import session

from app.controllers.auth_controller import auth, login_session
from app.models.category_model import Category
from app.models.course_model import Course

from flask import (
    Blueprint,
    jsonify,
    request,
)

category_ctrl = Blueprint('category', __name__, static_folder='static', template_folder='templates')


@category_ctrl.route('/categories', methods=['GET'])
def categories_function_get():
    categories = session.query(Category).all()
    return jsonify(Categories=[c.serialize for c in categories])


@category_ctrl.route('/categories', methods=['POST'])
# @auth.login_required
def categories_function_post():
    name = request.args.get('name')
    print name
    if name:
        category = Category(name=name)
        session.add(category)
        session.commit()
    else:
        return "Category name is required."
    return jsonify(Category=category.serialize)


@category_ctrl.route('/categories/<int:id>', methods=['PUT'])
# @auth.login_required
def categories_function_id_put(id):
    try:
        category = session.query(Category).filter_by(id=id).one()
    except:
        return error404()
    name = request.args.get('name')
    if name:
        category.name = name
        session.add(category)
        session.commit()
    else:
        return "Category name is required."
    return jsonify(Category=category.serialize)


@category_ctrl.route('/categories/<int:id>', methods=['DELETE'])
# @auth.login_required
def categories_function_id_delete(id):
    try:
        category = session.query(Category).filter_by(id=id).one()
    except:
        return error404()
    session.query(Course).filter_by(category_id=id).delete()
    session.delete(category)
    session.commit()
    return "Category and sub-courses was successfully deleted."


def error403():
    return "403 FORBIDDEN"


def error404():
    return "404 FILE NOT FOUND"
