from app.controllers.auth import auth
from app.libraries.response_message import error_message, data_message
from app.database import session
from app.models.category import Category
from app.models.course import Course

from flask import (
    Blueprint,
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
    return data_message(200, {"Category": category.serialize, "Courses": [c.serialize for c in courses]},
                        "Successfully returned all courses by given category.")


@page.route('/categories/<int:category_id>/courses', methods=['POST'])
@auth.login_required
def add_course(category_id):
    try:
        category = session.query(Category).filter_by(id=category_id).one()
    except:
        return error_message(404, "Cannot add new course to this category: Category not found.")
    name = request.form.get('name')
    if name:
        course = Course(name=name,
                        description=request.form.get('description'),
                        img_url=request.form.get('img-url'),
                        intro_video_url=request.form.get('intro-video-url'),
                        category_id=category.id)
        session.add(course)
        session.commit()
    else:
        return error_message(400, "Course name is required.")
    return data_message(200, {"Course": course.serialize}, "Successfully added a course.")


@page.route('/categories/<int:category_id>/courses/<int:course_id>', methods=['GET'])
def get_course_by_id(category_id, course_id):
    try:
        course = session.query(Course).filter_by(id=course_id, category_id=category_id).one()
    except:
        return error_message(404, "Course not found.")
    return data_message(200, {"Course": course.serialize},
                        "Successfully returned the selected course.")


@page.route('/categories/<int:category_id>/courses/<int:course_id>', methods=['PUT'])
@auth.login_required
def edit_course(category_id, course_id):
    try:
        course = session.query(Course).filter_by(id=course_id, category_id=category_id).one()
    except:
        return error_message(404, "Cannot update: Course not found.")
    if request.form.get('name'):  # if 'name' is a non-empty value then update else keep current value
        course.name = request.form('name')

    course.description = request.form.get('description')
    course.img_url = request.form.get('img-url')
    course.intro_video_url = request.form.get('intro-video-url')

    session.add(course)
    session.commit()
    return data_message(200, {"Course": course.serialize}, "Successfully updated the course.")


@page.route('/categories/<int:category_id>/courses/<int:course_id>', methods=['DELETE'])
@auth.login_required
def delete_course(category_id, course_id):
    try:
        course = session.query(Course).filter_by(id=course_id, category_id=category_id).one()
    except:
        return error_message(404, "Cannot delete: Course not found.")
    session.delete(course)
    session.commit()
    return data_message(200, None, "Course was successfully deleted.")
