import pytest

from flask import g, session
from webscrap_flask.db import get_db

def test_register_view(client, app):
    assert client.get('/auth/register').status_code == 200

    response = client.post('/auth/register',
                           data={'username':'test', 'password':'test'})
    assert response.headers['Location'] == '/auth/login'

    with app.app_context():   
        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'test'",
                                 ).fetchone() is not None


@pytest.mark.parametrize(("username","password","message"), 
                        ( ('','', b'Username is required.'),
                         ('test','', b'Password is required.'),
                         ('test','test', b'User ab is already registered')
                         ))
def test_register_validate_input(client, username, password, message):
    response = client.post(
        '/auth/register',
        data={'username':username, 'password':password}
    )
    assert message in response.data
    

def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    #NOTE: using the class created in 'conftest' with test username ='testone'
    response = auth.login()
    assert response.headers['Location'] == '/'

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'testone' #NOTE: not in bytes in g'

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