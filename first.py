from flask import Flask, request, jsonify
import stripe
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

@app.route('/create-payment-intent', methods=['POST'])
def create_payment_intent():
    try:
        data = request.json
        amount = data['amount']
        currency = data.get('currency', 'usd')
        package = data.get('package', 'unknown')
        
        # Create a PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            metadata={
                'package': package
            },
            automatic_payment_methods={
                'enabled': True,
            },
        )
        
        return jsonify({
            'clientSecret': intent.client_secret
        }), 200
        
    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == '__main__':
    app.run(port=4242, debug=True)


    from flask import Flask, request, jsonify, session, redirect, url_for
import stripe

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Set a strong secret key for sessions

stripe.api_key = "sk_test_51S9jwmRDiPbjldjnwIL6LMziqvE7tJTWVkdk2ulCQ7hF6DcKeZeo5od63nXlKSZMGfElAPE16Ef6kLCek256oKFd00pSwl76u6"  # Use your Stripe secret key

# Products/Packages mapping (to Stripe Price IDs)
PRODUCTS = {
    "silver": "rk_test_51S9jwmRDiPbjldjn3Gkc40IEEUdjM6neUevqiTQBM8pena9GsIVDFjxzlKCNHchuTlNfTtmgJhJhupj4IRcuOmzT00feotCkQe",
    "gold": "rk_test_51S9jwmRDiPbjldjn9YyWFXuS9u0MYYBtU7d1U72ci1ma23t171bWst72NUlVQVY00ubaVsPzbkD5pnLAunCb6vyw00mb7DajTP"
}

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    data = request.json
    package = data.get('package')
    email = data.get('email')  # collect from frontend
    price_id = PRODUCTS.get(package)
    if not price_id:
        return jsonify({"error": "Invalid package"}), 400

    session_obj = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': price_id,
            'quantity': 1,
        }],
        mode='subscription',
        customer_email=email,
        success_url=url_for('payment_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('payment_cancel', _external=True),
    )
    return jsonify({'checkout_url': session_obj.url})

@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    signature = request.headers.get('stripe-signature')
    event = None
    webhook_secret = "sk_test_51S9jwmRDiPbjldjnwIL6LMziqvE7tJTWVkdk2ulCQ7hF6DcKeZeo5od63nXlKSZMGfElAPE16Ef6kLCek256oKFd00pSwl76u6"  # Get from Stripe dashboard

    try:
        event = stripe.Webhook.construct_event(
            payload, signature, webhook_secret
        )
    except ValueError:
        return '', 400
    except stripe.error.SignatureVerificationError:
        return '', 400

    # Handle payment success
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        email = session.get('customer_email')
        # Mark user as premium in your DB/session here

    return '', 200

@app.route('/premium-content')
def premium_content():
    # This should check from DB or session if user is premium
    if not session.get('is_premium'):
        return jsonify({"error": "You must purchase to access"}), 403
    # Show premium section
    return jsonify({"content": "Your premium videos/listings go here"})

@app.route('/payment-success')
def payment_success():
    # After Stripe payment, mark user as premium here (e.g. session or DB)
    session['is_premium'] = True
    return "Payment success! You are now a premium member."

@app.route('/payment-cancel')
def payment_cancel():
    return "Payment cancelled. Try again."

if __name__ == '__main__':
    app.run(port=5000)
