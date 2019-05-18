
from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   jsonify,
                   url_for,
                   flash)
from catalogdb_setup import Base, Category, CategoryItem, User
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker

from flask import session as login_session
import json
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Item"

# Connect to Database and create database session
engine = create_engine('postgresql://catalog:password@localhost/catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Code from Udacity FullStack WebDev
# Section 3.Servers, Authorization, and CRUD
# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# Creating New Users
def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).first()
    return user.id


# User Information
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).first()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).first()
        return user.id
    except:
        flash("error")


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """ Method: gconnect to access via google sign -in Grant Access
        - Validates the state token.
        - Confirm that the token the client sends to the server
        matches the token that the server sent to the client

    Returns:
        Login status, if successful or failed.
    """

    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
                                'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # Obtaining Credentials of an Existing User
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
        login_session['user_id'] = user_id
    # Returns Welcome screen with login details.
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' "style = "width: 300px; height: 300px;\
                border-radius: 150px; \
                -webkit-border-radius: 150px;\
                -moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    """ Method: gdisconnect to disconnect and close session in application
    - User details are deleted from session

    Returns:
        If disconnection was succesful or not via status code
    """
    # retrieves access token stores in login_session
    access_token = login_session.get('access_token')
    # if user not connected
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps(
                                'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is %s', access_token)
    print('User name is: ')
    print(login_session['username'])
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
           % login_session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
    # if access token is validated delete user's login_session details
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['user_id']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    # else notify inhability to revoke
    else:
        response = make_response(
                   json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON API
@app.route('/catalog.json')
def showCategoriesJSON():
    """ Method: JSON catalog endpoints

    Returns:
        json file with all catalog information
    """
    all_data = session.query(Category)
    return jsonify(categories=[
           category.serialize for category in all_data.all()])


@app.route('/catalog/items/json')
def showCategoryItemsJSON():
    """ Method: JSON items endpoints

    Returns:
        json file with all items information
    """
    items = session.query(CategoryItem).all()
    return jsonify(items=[r.serialize for r in items])


@app.route('/catalog/<int:category_id>/<int:item_id>/json')
def showItemDetailsJSON(category_id, item_id):
    """ Method: JSON catalog specific item endpoints

    Returns:
        json file with specific item information
    """
    category = session.query(Category).filter_by(id=category_id).first()
    item = session.query(CategoryItem).filter_by(id=item_id).first()
    return jsonify(item=[item.serialize])


@app.route('/')
@app.route('/catalog')
def showCategories():
    """ Method: show all categories

    Returns:
        Categories template will all the availabe categories
    """
    category = session.query(Category).all()
    return render_template('categories.html', category=category)


@app.route('/catalog/<int:category_id>/')
@app.route('/catalog/<int:category_id>/items')
def showCategoryItems(category_id):
    """ Method: show all category items

    Returns:
        Category Item template will all the categoriy items
    """
    category = session.query(Category).filter_by(id=category_id).first()
    items = session.query(CategoryItem).filter_by(
        category_id=category_id).all()
    return render_template('categoryItems.html', category=category,
                           items=items)


@app.route('/catalog/<int:category_id>/<int:item_id>')
def showItemDetails(category_id, item_id):
    """ Method: shows category item details

    Returns:
        Item Description template will all item details
    """
    category = session.query(Category).filter_by(id=category_id).first()
    item = session.query(CategoryItem).filter_by(id=item_id).first()
    return render_template('itemDescription.html', category=category,
                           item=item)


# Add categoy items
@app.route('/catalog/new/', methods=['GET', 'POST'])
def addItemDetails():
    """ Method: adds new items to catalog

    Returns:
        On GET: Form to create new user
        On POST: Redirect to main page after successful item creation
    """
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newItem = CategoryItem(
            title=request.form['title'],
            user_id=login_session['user_id'],
            description=request.form['description'],
            category_id=request.form['category_id'])
        session.add(newItem)
        flash('New Category Item Successfully Created')
        session.commit()

        return redirect(url_for('showCategories'))
    else:
        categories = session.query(Category).all()
        return render_template('newCategoryItem.html', categories=categories)

    return render_template('newCategoryItem.html')


# Edit categoy items
@app.route('/catalog/<int:category_id>/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editItemDetails(category_id, item_id):
    """ Method: edit items, based on user access

    Returns:
        If authentication and authorization is meet allows to edit item
        Else redirects to login page

        On GET: form to update item
        On POST: main page, after item was upated
    """
    editedItem = session.query(CategoryItem).filter_by(id=item_id).first()
    creator = getUserInfo(editedItem.user_id)
    if 'username' not in (login_session or creator.id !=
                          login_session['user_id']):
        return redirect('/login')
    if request.method == 'POST':
        if request.form['title']:
            editedItem.title = request.form['title']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['category_id']:
            editedItem.category_id = request.form['category_id']
        session.add(editedItem)
        flash('Item Detail - %s Successfully Updated')
        session.commit()
        return redirect(url_for('showCategories', category_id=category_id))
    else:
        categories = session.query(Category).all()
        return render_template(
            'editCategoryItem.html', categories=categories, item_id=item_id,
            item=editedItem)
    return render_template('editCategoryItem.html')


# Delete categoy items
@app.route('/catalog/<int:category_id>/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteItemDetails(category_id, item_id):
    """ Method: delete items, based on user access

    Returns:
        If authentication and authorization is meet allows to delete item
        Else redirects to login page
        On GET: form to delete item
        On POST: main page, after item was deleted
    """
    itemToDelete = session.query(CategoryItem).filter_by(id=item_id).first()
    creator = getUserInfo(itemToDelete.user_id)
    if 'username' not in (login_session or creator.id !=
                          login_session['user_id']):
        return redirect('/login')
    if request.method == 'POST':
        session.delete(itemToDelete)
        flash('Item Detail - %s Successfully Deleted')
        session.commit()
        return redirect(url_for('showCategories', category_id=category_id))
    else:
        return render_template('deleteCategoryItem.html', item=itemToDelete)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000, threaded=False)
