from fastapi.testclient import TestClient
from app.main import app, main as main_func


def test_root_endpoint_returns_null():
	client = TestClient(app)
	response = client.get('/')
	assert response.status_code == 200
	assert response.json() is None


def test_main_function_prints(capsys):
	main_func()
	captured = capsys.readouterr()
	assert "Hello from fonte!" in captured.out
