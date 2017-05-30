import httplib2
import json
import random
import requests
import string

from app.database import session
from app.models.user_model import User

from flask import (
    Blueprint,
    g,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)
from flask import session as login_session
from flask_httpauth import HTTPBasicAuth

from oauth2client.client import FlowExchangeError
from oauth2client.client import flow_from_clientsecrets

auth = HTTPBasicAuth()

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

auth_ctrl = Blueprint('auth', __name__, static_folder='static', template_folder='templates')


@auth.verify_password
def verify_password(username_or_token, password):
    if 'username' in login_session:
        return True
    else:
        return False


@auth_ctrl.route('/token')
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


# Create a state token to prevent request
# Store it in the login_session for later validation
@auth_ctrl.route('/login')
def show_login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('_main.html', view='login', STATE=state)


@auth_ctrl.route('/gconnect', methods=['POST'])
def gconnect():
    # Check if request was sent from the right user
    # if request.args.get('state') != login_session['state']:
    #     response = make_response(json.dumps('Invalid state parameter', 401))
    #     response.headers['Content-Type'] = 'application/json'
    #     return response

    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check if the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID doesn't match give user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content_Type'] = 'application/json'
        return response

    # Check to see if user is already logged in
    stored_credentials = login_session.get('credentials')
    store_gplus_id = login_session.get('gplus_id')
    if (stored_credentials is not None) and (gplus_id == store_gplus_id):
        response = make_response(json.dumps("Current user is already connected."), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)

    login_session['username'] = data["name"]
    login_session['picture'] = data["picture"]
    login_session['email'] = data["email"]

    user = session.query(User).filter_by(email=login_session['email']).first()
    if not user:
        user = User(username=login_session['name'],
                    picture=login_session['picture'],
                    email=login_session['email'])
        session.add(user)
        session.commit()

    # Make token
    token = user.generate_auth_token(600)

    return jsonify({'token': token.decode('ascii')})


@auth_ctrl.route('/gdisconnect')
def gdisconnect():
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps("Current user not connected."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Execute HTTP GET to disconnect current token
    url = "https://accounts.google.com/o/oauth2/revoke?token=%s" % credentials
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    # Reset the user's session.
    del login_session['username']
    del login_session['picture']
    del login_session['email']
    del login_session['credentials']
    del login_session['gplus_id']
    if result['status'] == '200':
        response = make_response(json.dumps("Successfully disconnected."), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('category.categories_function'))
    else:
        response = make_response(json.dumps("Fail to disconnect."), 400)
        response.headers['Content-Type'] = 'application/json'
        return response
