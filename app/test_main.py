from fastapi.testclient import TestClient
from fastapi import status

from app.main import app

client = TestClient(app)

def test_read_root():
	response = client.get("/")
	assert response.status_code == status.HTTP_404_NOT_FOUND
	assert response.json() == {"detail":"Not Found"}

def test_read_health():
	response = client.get("/health")
	assert response.status_code == status.HTTP_200_OK
	assert response.json() is True