import httplib2
import json
import requests

from app.controllers.response_message import error_message, info_message
from app.database import session
from app.models.user import User

from flask import (
    Blueprint,
    g,
    jsonify,
    render_template,
    request,
)
from flask_httpauth import HTTPTokenAuth

from oauth2client.client import FlowExchangeError
from oauth2client.client import flow_from_clientsecrets

auth = HTTPTokenAuth()

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

page = Blueprint('auth', __name__, static_folder='static', template_folder='templates')


@auth.verify_token
def verify_token(token):
    user_id = User.verify_auth_token(token)
    if user_id:
        user = session.query(User).filter_by(id=user_id).one()
    else:
        return False
    g.user = user
    return True


@page.route('/token')
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


@page.route('/login')
def show_login():
    return render_template('login.html')


@page.route('/gconnect', methods=['POST'])
def gconnect():
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        return error_message(401, 'Failed to upgrade the authorization code.')

    # Check if the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort
    if result.get('error') is not None:
        return error_message(500, result.get('error'))

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        return error_message(401, "Token's user ID doesn't match give user ID.")

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        return error_message(401, "Token's client ID does not match app's.")

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    name = data["name"]
    picture = data["picture"]
    email = data["email"]

    user = session.query(User).filter_by(email=email).first()
    if not user:
        user = User(username=name, picture=picture, email=email)
        session.add(user)
        session.commit()

    # Make token
    token = user.generate_auth_token(600)

    return jsonify({'token': token.decode('ascii')})
