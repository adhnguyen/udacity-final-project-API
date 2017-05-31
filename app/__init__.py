from flask import Flask, redirect, url_for

app = Flask(__name__)

from app.controllers import auth
app.register_blueprint(blueprint=auth.page, url_prefix='/auth')

from app.controllers import category
app.register_blueprint(blueprint=category.page, url_prefix='')

from app.controllers import course
app.register_blueprint(blueprint=course.page, url_prefix='')
