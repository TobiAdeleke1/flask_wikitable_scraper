import pytest

from flask import g, session
from webscrap_flask.db import get_db

def test_register_view(client, app):
    # test that viewing the page renders without template errors
    assert client.get('/auth/register').status_code == 200

    # test that successful registration redirects to the login page
    response = client.post('/auth/register',
                           data={'username':'testa', 'password':'testa'})

    assert response.headers["Location"] == "/auth/login"

    # test that the user was inserted into the database
    with app.app_context():   
        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'testa'",
                                 ).fetchone() is not None


@pytest.mark.parametrize(("username","password","message"), 
                        ( ('','', b'Username is required.'),
                         ('testa','', b'Password is required.'),
                         ('test','test', b'already registered') #not sure why it works but not "testone"
                         ))
def test_register_validate_input(client, username, password, message):
    response = client.post(
        '/auth/register',
        data={'username':username, 'password':password}
    )
    assert message in response.data
    

def test_login(client, auth):
    # test that viewing the page renders without template errors
    assert client.get('/auth/login').status_code == 200

    # test that successful login redirects to the index page
    response = auth.login('test','test')
    assert response.headers['Location'] == '/'
    
    # login request set the user_id in the session
    # check that the user is loaded from the session
    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test' #NOTE: not in bytes in g'

@pytest.mark.parametrize(('username','password','message'),
                         (('a','test', b'Incorrect Username'),
                         ('test','a', b'Incorrect Password'),
                         
                         ))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username,password)
    assert message in response.data
 

def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert "user_id" not in session