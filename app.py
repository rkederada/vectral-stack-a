from flask import Flask, jsonify, request

app = Flask(__name__)

# Simple in-memory data store
payments = []

@app.route('/')
def home():
    return jsonify({'service': 'payment-api', 'status': 'healthy', 'version': '1.0.0'})

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

@app.route('/payments', methods=['GET'])
def get_payments():
    return jsonify({'payments': payments, 'total': len(payments)})

@app.route('/payments', methods=['POST'])
def create_payment():
    data = request.json

    # Validate amount
    if data is None:
        return jsonify({'error': 'No data provided'}), 400

    amount = data.get('amount')
    currency = data.get('currency')

    if amount is None:
        return jsonify({'error': 'Amount is required'}), 400

    if amount <= 0:
        return jsonify({'error': 'Amount must be positive'}), 400

    if not currency:
        return jsonify({'error': 'Currency is required'}), 400

    supported_currencies = ['USD', 'EUR', 'GBP', 'JPY']
    if currency not in supported_currencies:
        return jsonify({'error': f'Currency must be one of {supported_currencies}'}), 400

    payment = {
        'id': len(payments) + 1,
        'amount': amount,
        'currency': currency,
        'status': 'processed'
    }
    payments.append(payment)
    return jsonify(payment), 201

@app.route('/payments/<int:payment_id>', methods=['GET'])
def get_payment(payment_id):
    payment = next((p for p in payments if p['id'] == payment_id), None)
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404
    return jsonify(payment)

@app.route('/payments/<int:payment_id>/refund', methods=['POST'])
def refund_payment(payment_id):
    payment = next((p for p in payments if p['id'] == payment_id), None)
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404
    if payment['status'] == 'refunded':
        return jsonify({'error': 'Payment already refunded'}), 400
    payment['status'] = 'refunded'
    return jsonify(payment)

if __name__ == '__main__':
    app.run(port=9000)