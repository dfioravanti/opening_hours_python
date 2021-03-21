
from test.utils import load_data_results
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_one_day():
    """
    Test if the code works as intended when we have only one open day
    """
    test_data, test_data_results = load_data_results(base_filename="one_day")
    for data, result in zip(test_data, test_data_results):
        response = client.post('/prettify', data=data)
        assert response.status_code == 200
        assert response.json() == result


def test_two_days():
    """
    Test if the code works as intended when we have only two open days
    """
    test_data, test_data_results = load_data_results(base_filename="two_days")
    for data, result in zip(test_data, test_data_results):
        response = client.post('/prettify', data=data)
        assert response.status_code == 200
        assert response.json() == result


def test_full_days():
    """
    Test if the code works as intended when we having all days
    """
    test_data, test_data_results = load_data_results(base_filename="seven_days")
    for data, result in zip(test_data, test_data_results):
        response = client.post('/prettify', data=data)
        assert response.status_code == 200
        assert response.json() == result


def test_errors():
    """
    Test if errors are detected correctly 
    """
    test_data = load_data_results(base_filename="errors", only_data=True)
    for data in test_data:
        response = client.post('/prettify', data=data)
        assert response.status_code == 422
