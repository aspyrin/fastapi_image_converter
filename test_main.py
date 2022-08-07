from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root():
    response = client.get('/')
    assert response.status_code == 200


def test_convert_to_grayscale():
    filename = "test_image.jpg"
    url = '/convert-to-grayscale'
    response = client.post(url, files={"file": ("filename", open(filename, "rb"), "image/jpeg")})
    assert response.status_code == 200
    assert int(response.headers["content-length"]) > 0


def test_convert_to_grayscale_from_url():
    data = {
        "url": "https://planbphoto.com/wp-content/uploads/Serze.jpg"
    }
    url = '/convert-to-grayscale-from-url'
    response = client.post(url, json=data)
    assert response.status_code == 200
    assert int(response.headers["content-length"]) > 0
