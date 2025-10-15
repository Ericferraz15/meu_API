from meu_API import create_app


def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing#type: ignore


def test_hello(client):
    response = client.get('/hello')
    assert response.data == b'Hello World!'