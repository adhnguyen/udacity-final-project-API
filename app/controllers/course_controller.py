from app.database import session

from app.controllers.auth_controller import auth, login_session
from app.models.category_model import Category
from app.models.course_model import Course

from flask import (
    Blueprint,
    jsonify,
    request,
)

course_ctrl = Blueprint('course', __name__, static_folder='static', template_folder='templates')


@course_ctrl.route('/categories/<int:category_id>/courses', methods=['GET'])
def courses_function_get(category_id):
    try:
        category = session.query(Category).filter_by(id=category_id).one()
    except:
        return error404()
    courses = session.query(Course).filter_by(category_id=category_id).all()
    return jsonify(Category=category.serialize, Courses=[c.serialize for c in courses])


@course_ctrl.route('/categories/<int:category_id>/courses', methods=['POST'])
# @auth.login_required
def courses_function_post(category_id):
    try:
        category = session.query(Category).filter_by(id=category_id).one()
    except:
        return error404()
    name = request.args.get('name')
    if name:
        course = Course(name=name,
                        description=request.args.get('description'),
                        img_url=request.args.get('img-url'),
                        intro_video_url=request.args.get('intro-video-url'),
                        category_id=category.id)
        session.add(course)
        session.commit()
    else:
        return "Course name is required."
    return jsonify(Course=course.serialize)


@course_ctrl.route('/categories/<int:category_id>/courses/<int:course_id>', methods=['GET'])
def course_function_id_get(category_id, course_id):
    try:
        course = session.query(Course).filter_by(id=course_id, category_id=category_id).one()
    except:
        return error404()
    return jsonify(Course=course.serialize)


@course_ctrl.route('/categories/<int:category_id>/courses/<int:course_id>', methods=['PUT'])
# @auth.login_required
def course_function_id_put(category_id, course_id):
    try:
        course = session.query(Course).filter_by(id=course_id, category_id=category_id).one()
    except:
        return error404()
    if not not request.args.get('name'):  # if 'name' is a non-empty value
        course.name = request.args.get('name')

    if request.args.get('description'):
        course.description = request.args.get('description')

    if request.args.get('img-url'):
        course.img_url = request.args.get('img-url')

    if request.args.get('intro-video-url'):
        course.intro_video_url = request.args.get('intro-video-url')

    session.add(course)
    session.commit()
    return jsonify(Course=course.serialize)


@course_ctrl.route('/categories/<int:category_id>/courses/<int:course_id>', methods=['DELETE'])
# @auth.login_required
def course_function_id_put_delete(category_id, course_id):
    try:
        course = session.query(Course).filter_by(id=course_id, category_id=category_id).one()
    except:
        return error404()
    session.delete(course)
    session.commit()
    return "Course was successfully deleted."


def error403():
    return "403 FORBIDDEN"


def error404():
    return "404 FILE NOT FOUND"
