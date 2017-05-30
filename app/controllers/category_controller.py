from app.database import session

from app.controllers.auth_controller import login_session
from app.models.category_model import Category
from app.models.course_model import Course

from flask import (
    Blueprint,
    jsonify,
    request,
)

category_ctrl = Blueprint('category', __name__, static_folder='static', template_folder='templates')


@category_ctrl.route('', methods=['GET', 'POST'])
def categories_function():
    if request.method == 'GET':
        return getallcategories()
    if request.method == 'POST':
        # if 'username' in login_session:
        return newcategory()
        # else:
        #     return error403()


@category_ctrl.route('/<int:id>', methods=['PUT', 'DELETE'])
def categories_function_id(id):
        if request.method == 'PUT':
            # if 'username' in login_session:
            return editcategory(id)
            # else:
            #     return error403()
        if request.method == 'DELETE':
            # if 'username' in login_session:
            return deletecategory(id)
            # else:
            #     return error403()


def getallcategories():
    categories = session.query(Category).all()
    return jsonify(Categories=[c.serialize for c in categories])


def newcategory():
    name = request.args.get('name')
    print name
    if name:
        category = Category(name=name)
        session.add(category)
        session.commit()
    else:
        return "Category name is required."
    return jsonify(Category=category.serialize)


def editcategory(id):
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


def deletecategory(id):
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