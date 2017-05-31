from app.database import session

from app.controllers.response_message import error_message, info_message
from app.models.category import Category
from app.models.course import Course

from flask import (
    Blueprint,
    jsonify,
    request,
)

page = Blueprint('course', __name__, static_folder='static', template_folder='templates')


@page.route('/categories/<int:category_id>/courses', methods=['GET'])
def get_courses_by_category_id(category_id):
    try:
        category = session.query(Category).filter_by(id=category_id).one()
    except:
        return error_message(404, "Category not found.")
    courses = session.query(Course).filter_by(category_id=category_id).all()
    return jsonify(Category=category.serialize, Courses=[c.serialize for c in courses])


@page.route('/categories/<int:category_id>/courses', methods=['POST'])
# @auth.login_required
def add_course(category_id):
    try:
        category = session.query(Category).filter_by(id=category_id).one()
    except:
        return error_message(404, "Cannot add new course to this category: Category not found.")
    name = request.form['name']
    if name:
        course = Course(name=name,
                        description=request.form['description'],
                        img_url=request.form['img-url'],
                        intro_video_url=request.form['intro-video-url'],
                        category_id=category.id)
        session.add(course)
        session.commit()
    else:
        return error_message(1000, "Course name is required.")
    return jsonify(Course=course.serialize)


@page.route('/categories/<int:category_id>/courses/<int:course_id>', methods=['GET'])
def get_course_by_id(category_id, course_id):
    try:
        course = session.query(Course).filter_by(id=course_id, category_id=category_id).one()
    except:
        return error_message(404, "Course not found.")
    return jsonify(Course=course.serialize)


@page.route('/categories/<int:category_id>/courses/<int:course_id>', methods=['PUT'])
# @auth.login_required
def edit_course(category_id, course_id):
    try:
        course = session.query(Course).filter_by(id=course_id, category_id=category_id).one()
    except:
        return error_message(404, "Cannot update: Course not found.")
    if not not request.form['name']:  # if 'name' is a non-empty value then update else keep current value
        print "get here!"
        course.name = request.form['name']

    course.description = request.form['description']
    course.img_url = request.form['img-url']
    course.intro_video_url = request.form['intro-video-url']

    session.add(course)
    session.commit()
    return jsonify(Course=course.serialize)


@page.route('/categories/<int:category_id>/courses/<int:course_id>', methods=['DELETE'])
# @auth.login_required
def delete_course(category_id, course_id):
    try:
        course = session.query(Course).filter_by(id=course_id, category_id=category_id).one()
    except:
        return error_message(404, "Cannot delete: Course not found.")
    session.delete(course)
    session.commit()
    return info_message(200, "Course was successfully deleted.")
