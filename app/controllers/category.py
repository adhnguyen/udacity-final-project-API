from app.controllers.auth import auth
from app.libraries.response_message import error_message, info_message
from app.database import session
from app.models.category import Category
from app.models.course import Course

from flask import (
    Blueprint,
    jsonify,
    request,
)

page = Blueprint('category', __name__, static_folder='static', template_folder='templates')


@page.route('/')
@page.route('/categories', methods=['GET'])
def get_all_categories():
    categories = session.query(Category).all()
    return jsonify(Categories=[c.serialize for c in categories]), 200


@page.route('/categories', methods=['POST'])
@auth.login_required
def add_category():
    name = request.form.get('name')
    if name:
        category = Category(name=name)
        session.add(category)
        session.commit()
    else:
        return error_message(400, "Course name is required.")
    return jsonify(Category=category.serialize), 200


@page.route('/categories/<int:category_id>', methods=['PUT'])
@auth.login_required
def edit_category(category_id):
    try:
        category = session.query(Category).filter_by(id=category_id).one()
    except:
        return error_message(404, "Cannot update: Category not found.")
    name = request.form.get('name')
    if name:
        category.name = name
        session.add(category)
        session.commit()
    else:
        return error_message(400, "Course name is required.")
    return jsonify(Category=category.serialize), 200


@page.route('/categories/<int:category_id>', methods=['DELETE'])
@auth.login_required
def delete_category(category_id):
    try:
        category = session.query(Category).filter_by(id=category_id).one()
    except:
        return error_message(404, "Cannot delete: Category not found.")
    session.query(Course).filter_by(category_id=category_id).delete()
    session.delete(category)
    session.commit()
    return info_message(200, "Category and sub-courses was successfully deleted.")
