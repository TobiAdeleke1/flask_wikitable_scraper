import pytest

from webscrap_flask.db import get_db

def test_index(client, auth):
    response = client.get('/')
    assert b'Log In' in response.data
    assert b'Register' in response.data

    auth.login()
    response = client.get('/')
    assert b'Log Out' in response.data
    assert b'testone title' in response.data
    assert b'by testone on 2018-01-01' in response.data
    assert b'testone\nurl' in response.data
    assert b'Edit' in response.data
    assert b'href="/1/update"' in response.data

@pytest.mark.parametrize('path',
                          ('/create',
                          '/1/update',
                          '/1/delete'))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers['Location'] == 'auth/login'

def test_author_required(app, client, auth):
    with app.app_context():
        db = get_db()
        db.execute("UPDATE post_url SET user_id=2 WHERE id=1")
        db.commit()

    auth.login()
    assert client.post('/1/update').status_code == 403 #forbidden
    assert client.post('/1/delete').status_code == 403
    assert b'href="/1/update"' not in  client.get('/').data

@pytest.mark.parametrize('path', (
        '/2/update',
        '/2/delete',
    ))
def test_post_exists(client, auth, path):
    auth.login()
    response = client.post(path)
    assert response.status_code == 404 

def test_create(client, auth, app):
    auth.login()
    assert client.get('/create').status_code == 200

    client.post(
        '/create',
        data={'title':'New Link', 'url':'https://new-link'}
    )

    with app.app_context():
        db = get_db()
        # count = db.execute("SELECT COUNT(id) FROM post_urls").fetchone()
        count = db.execute("SELECT COUNT(id) FROM post_urls").fetchone()[0]
        assert count == 2

def test_update(client, auth, app):
    auth.login()
    assert client.get('/1/update').status_code == 200

    client.post('/1/update',
                data={'title':'updated', 'url':''}
    )

    with app.app_context():
        db = get_db()
        post = db.execute("SELECT * FROM post_urls WHERE id=1").fetchone()
        assert post['title'] == 'updated'


@pytest.mark.parametrize(
        'path',
        ('/create', '/1/update',
    ))
def test_validate_create_update_data(client, auth, path):
    auth.login()
    response = client.post(path, data={'title':'', 'url':''})
    assert b'A Title Is Required' in response.data



def test_delete(client, auth, app):
    auth.login()
    response = client.post('/1/delete')
    assert response.headers['Location'] == '/'

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post_urls WHERE id = 1').fetchone()
        assert post is None