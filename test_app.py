import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# ─── PASSING TESTS ───────────────────────────────────

def test_home(client):
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert data['service'] == 'payment-api'
    assert data['status'] == 'healthy'

def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json()['status'] == 'healthy'

def test_get_payments_empty(client):
    response = client.get('/payments')
    assert response.status_code == 200
    assert response.get_json()['total'] == 0

def test_create_payment_success(client):
    response = client.post('/payments', json={
        'amount': 100.00,
        'currency': 'USD'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['amount'] == 100.00
    assert data['currency'] == 'USD'
    assert data['status'] == 'processed'

def test_create_payment_eur(client):
    response = client.post('/payments', json={
        'amount': 50.00,
        'currency': 'EUR'
    })
    assert response.status_code == 201

def test_get_payment_by_id(client):
    client.post('/payments', json={'amount': 75.00, 'currency': 'GBP'})
    response = client.get('/payments/1')
    assert response.status_code == 200

def test_refund_payment(client):
    client.post('/payments', json={'amount': 200.00, 'currency': 'USD'})
    response = client.post('/payments/1/refund')
    assert response.status_code == 200
    assert response.get_json()['status'] == 'refunded'

# ─── FAILING TESTS ───────────────────────────────────
# These tests will deliberately fail to trigger Vectral

def test_create_payment_no_amount(client):
    response = client.post('/payments', json={'currency': 'USD'})
    assert response.status_code == 400
    # This will FAIL — wrong assertion to trigger Vectral
    assert response.get_json()['error'] == 'Wrong error message'

def test_create_payment_negative_amount(client):
    response = client.post('/payments', json={
        'amount': -50,
        'currency': 'USD'
    })
    # This will FAIL — wrong status code to trigger Vectral
    assert response.status_code == 201

def test_unsupported_currency(client):
    response = client.post('/payments', json={
        'amount': 100,
        'currency': 'XYZ'
    })
    assert response.status_code == 400
    # This will FAIL — wrong assertion to trigger Vectral
    assert response.get_json()['supported'] == ['USD']