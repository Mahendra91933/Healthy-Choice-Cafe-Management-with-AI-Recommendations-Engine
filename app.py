from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import os
import random
import time
from datetime import datetime
import csv
from sklearn.neighbors import NearestNeighbors
import pandas as pd
import numpy as np


app = Flask(__name__)
CORS(app)
app.secret_key = 'your_secret_key_here'  # Change to a secure key in production

# In-memory storage for OTP (temporary)
otp_store = {}
login_otp_store = {}

# In-memory storage for data
users = []
guest_orders = []
login_history = []

# Generate random 4-digit OTP
def generate_otp():
    return str(random.randint(1000, 9999))

# Load food items from CSV
def load_food_items():
    try:
        with open('FoodItem_export_clean.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            items = []
            for row in reader:
                item = {
                    'id': row.get('id', ''),
                    'name': row.get('name', ''),
                    'description': row.get('description', ''),
                    'price': float(row.get('price', 0)),
                    'category': row.get('category', ''),
                    'subcategory': row.get('subcategory', ''),
                    'image_url': row.get('image_url', ''),
                    'protein': float(row.get('protein', 0)),
                    'carbs': float(row.get('carbs', 0)),
                    'fats': float(row.get('fats', 0)),
                    'calories': float(row.get('calories', 0)),
                    'restaurant': row.get('restaurant', ''),
                    'cuisine': row.get('cuisine', '')
                }
                items.append(item)
            return items
    except Exception as e:
        print(f"Error loading food items: {e}")
        return []

# Initialize NearestNeighbors model for recommendations
def initialize_recommendation_model():
    items = load_food_items()
    if not items:
        return None, None

    # Create feature matrix from nutritional data
    features = []
    item_ids = []
    for item in items:
        features.append([
            item['protein'],
            item['carbs'],
            item['fats'],
            item['calories']
        ])
        item_ids.append(item['id'])

    features_df = pd.DataFrame(features, columns=['protein', 'carbs', 'fats', 'calories'])
    features_scaled = (features_df - features_df.mean()) / features_df.std()

    # Fit NearestNeighbors model
    nn_model = NearestNeighbors(n_neighbors=6, algorithm='auto')  # 6 to get 5 recommendations + itself
    nn_model.fit(features_scaled)

    return nn_model, items

# Get food recommendations based on nutritional similarity
def get_food_recommendations(item_id, num_recommendations=5):
    nn_model, items = initialize_recommendation_model()
    if nn_model is None or not items:
        return []

    # Find the item
    target_item = next((item for item in items if item['id'] == item_id), None)
    if not target_item:
        return []

    # Create feature vector for target item
    target_features = pd.DataFrame([[
        target_item['protein'],
        target_item['carbs'],
        target_item['fats'],
        target_item['calories']
    ]], columns=['protein', 'carbs', 'fats', 'calories'])

    # Scale features
    items_df = pd.DataFrame([[item['protein'], item['carbs'], item['fats'], item['calories']] for item in items],
                           columns=['protein', 'carbs', 'fats', 'calories'])
    target_features_scaled = (target_features - items_df.mean()) / items_df.std()

    # Find nearest neighbors
    distances, indices = nn_model.kneighbors(target_features_scaled, n_neighbors=num_recommendations+1)

    # Get recommended items (excluding the item itself)
    recommendations = []
    for idx in indices[0][1:]:  # Skip first item (itself)
        recommendations.append(items[idx])

    return recommendations

@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    mobile = data.get('mobile')

    if not mobile:
        return jsonify({'error': 'Mobile number is required'}), 400

    otp = generate_otp()
    otp_id = str(int(time.time() * 1000))

    otp_store[otp_id] = {
        'otp': otp,
        'mobile': mobile,
        'expiry': time.time() + 120  # 2 minutes
    }

    return jsonify({
        'success': True,
        'otpId': otp_id,
        'otp': otp,  # Include OTP for testing (remove in production)
        'message': 'OTP sent successfully'
    })

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    otp_id = data.get('otpId')
    otp = data.get('otp')

    if not otp_id or not otp:
        return jsonify({'error': 'OTP ID and OTP are required'}), 400

    stored_otp = otp_store.get(otp_id)

    if not stored_otp:
        return jsonify({'error': 'Invalid OTP ID'}), 400

    if time.time() > stored_otp['expiry']:
        del otp_store[otp_id]
        return jsonify({'error': 'OTP expired'}), 400

    if stored_otp['otp'] != otp:
        return jsonify({'error': 'Invalid OTP'}), 400

    # OTP verified successfully
    del otp_store[otp_id]
    return jsonify({'success': True, 'message': 'OTP verified successfully'})

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    mobile = data.get('mobile')
    email = data.get('email')

    if not name or not mobile or not email:
        return jsonify({'error': 'Name, mobile, and email are required'}), 400

    # Check if guest order already exists
    existing_guest = next((o for o in guest_orders if o['mobile'] == mobile or o['email'] == email), None)
    if existing_guest:
        return jsonify({'error': 'You have already placed a guest order. Please login instead.'}), 400

    # Check if user already exists
    existing_user = next((u for u in users if u['mobile'] == mobile or u['email'] == email), None)
    if existing_user:
        return jsonify({'error': 'User already exists'}), 400

    # Create new user
    new_user = {
        'id': len(users) + 1,
        'name': name,
        'mobile': mobile,
        'email': email,
        'dob': None,
        'gender': None
    }
    users.append(new_user)

    return jsonify({'success': True, 'message': 'User registered successfully'})

@app.route('/check-user', methods=['POST'])
def check_user():
    data = request.get_json()
    mobile = data.get('mobile')

    if not mobile:
        return jsonify({'error': 'Mobile number is required'}), 400

    user = next((u for u in users if u['mobile'] == mobile), None)

    if user:
        user_data = {
            'id': user['id'],
            'name': user['name'],
            'mobile': user['mobile'],
            'email': user['email'],
            'dob': user['dob'],
            'gender': user['gender']
        }
        return jsonify({'exists': True, 'user': user_data})
    else:
        return jsonify({'exists': False})

@app.route('/update-profile', methods=['POST'])
def update_profile():
    data = request.get_json()
    mobile = data.get('mobile')
    name = data.get('name')
    dob = data.get('dob')
    gender = data.get('gender')

    if not mobile:
        return jsonify({'error': 'Mobile number is required'}), 400

    user = next((u for u in users if u['mobile'] == mobile), None)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Update user fields
    if name:
        user['name'] = name
    if dob:
        user['dob'] = dob
    if gender:
        user['gender'] = gender

    updated_user = {
        'id': user['id'],
        'name': user['name'],
        'mobile': user['mobile'],
        'email': user['email'],
        'dob': user['dob'],
        'gender': user['gender']
    }

    return jsonify({'success': True, 'message': 'Profile updated successfully', 'user': updated_user})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    mobile = data.get('mobile')

    if not mobile:
        return jsonify({'error': 'Mobile number is required'}), 400

    user = next((u for u in users if u['mobile'] == mobile), None)
    if not user:
        return jsonify({'error': 'User not registered'}), 404

    otp = generate_otp()
    otp_id = str(int(time.time() * 1000))

    login_otp_store[otp_id] = {
        'otp': otp,
        'mobile': mobile,
        'expiry': time.time() + 120  # 2 minutes
    }

    return jsonify({
        'success': True,
        'otpId': otp_id,
        'otp': otp,  # Include OTP for testing (remove in production)
        'message': 'Login OTP sent successfully'
    })

@app.route('/verify-login-otp', methods=['POST'])
def verify_login_otp():
    data = request.get_json()
    otp_id = data.get('otpId')
    otp = data.get('otp')

    if not otp_id or not otp:
        return jsonify({'error': 'OTP ID and OTP are required'}), 400

    stored_otp = login_otp_store.get(otp_id)

    if not stored_otp:
        return jsonify({'error': 'Invalid OTP ID'}), 400

    if time.time() > stored_otp['expiry']:
        del login_otp_store[otp_id]
        return jsonify({'error': 'OTP expired'}), 400

    if stored_otp['otp'] != otp:
        return jsonify({'error': 'Invalid OTP'}), 400

    user = next((u for u in users if u['mobile'] == stored_otp['mobile']), None)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    user_id = user['id']

    # Record login history
    new_login_history = {
        'id': len(login_history) + 1,
        'user_id': user_id,
        'login_time': datetime.now().isoformat()
    }
    login_history.append(new_login_history)

    # Store user name in session
    session['user_name'] = user['name']
    session['user_id'] = user_id

    del login_otp_store[otp_id]

    return jsonify({'success': True, 'message': 'Login successful', 'userId': user_id})

@app.route('/login-count', methods=['POST'])
def login_count():
    data = request.get_json()
    mobile = data.get('mobile')

    if not mobile:
        return jsonify({'error': 'Mobile number is required'}), 400

    user = next((u for u in users if u['mobile'] == mobile), None)
    if not user:
        return jsonify({'loginCount': 0})

    login_count_value = len([lh for lh in login_history if lh['user_id'] == user['id']])
    return jsonify({'loginCount': login_count_value})

@app.route('/get-login-history', methods=['POST'])
def get_login_history():
    data = request.get_json()
    mobile = data.get('mobile')

    if not mobile:
        return jsonify({'error': 'Mobile number is required'}), 400

    user = next((u for u in users if u['mobile'] == mobile), None)
    if not user:
        return jsonify({'loginHistory': []})

    user_login_history = [lh for lh in login_history if lh['user_id'] == user['id']]
    user_login_history.sort(key=lambda x: x['login_time'], reverse=True)
    history_data = [{
        'id': entry['id'],
        'login_time': entry['login_time']
    } for entry in user_login_history]
    return jsonify({'loginHistory': history_data})

@app.route('/food-items', methods=['GET'])
def get_food_items():
    items = load_food_items()
    return jsonify(items)

@app.route('/recommendations/<item_id>', methods=['GET'])
def get_recommendations(item_id):
    try:
        recommendations = get_food_recommendations(item_id)
        return jsonify({'success': True, 'recommendations': recommendations})
    except Exception as e:
        print(f"Error getting recommendations: {e}")
        return jsonify({'success': False, 'error': 'Failed to get recommendations'}), 500

@app.route('/generate-invoice', methods=['POST'])
def generate_invoice():
    data = request.get_json()
    order_items = data.get('orderItems')
    total_amount = data.get('totalAmount')
    payment_method = data.get('paymentMethod')
    customer_name = data.get('customerName')
    customer_mobile = data.get('customerMobile')

    if not order_items or not total_amount or not payment_method:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        # Create PDF
        filename = f"invoice_{int(time.time())}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Header
        title_style = styles['Heading1']
        title_style.alignment = 1  # Center alignment
        title = Paragraph("Cafe Zone", title_style)
        story.append(title)

        subtitle = Paragraph("Invoice", styles['Heading2'])
        story.append(subtitle)
        story.append(Spacer(1, 12))

        # Invoice details
        invoice_info = [
            f"Date: {datetime.now().strftime('%Y-%m-%d')}",
            f"Time: {datetime.now().strftime('%H:%M:%S')}",
            f"Invoice #: CZ{int(time.time() * 1000)}"
        ]

        if customer_name:
            invoice_info.append(f"Customer: {customer_name}")
        if customer_mobile:
            invoice_info.append(f"Mobile: {customer_mobile}")

        for info in invoice_info:
            story.append(Paragraph(info, styles['Normal']))
        story.append(Spacer(1, 12))

        # Order details header
        story.append(Paragraph("Order Details:", styles['Heading3']))
        story.append(Spacer(1, 6))

        # Table data
        table_data = [['Item', 'Qty', 'Price', 'Total']]
        for item in order_items:
            table_data.append([
                item['name'],
                str(item['quantity']),
                f"₹{item['price']}",
                f"₹{(item['price'] * item['quantity']):.2f}"
            ])

        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
        story.append(Spacer(1, 12))

        # Calculate amounts
        subtotal = float(total_amount) - 50  # Subtract delivery fee
        gst_amount = subtotal * 0.18
        delivery_fee = 50

        amounts = [
            f"Subtotal: ₹{subtotal:.2f}",
            f"GST (18%): ₹{gst_amount:.2f}",
            f"Delivery Fee: ₹{delivery_fee:.2f}",
            f"Total Amount: ₹{total_amount}"
        ]

        for amount in amounts:
            story.append(Paragraph(amount, styles['Normal']))
        story.append(Spacer(1, 6))

        story.append(Paragraph(f"Payment Method: {payment_method}", styles['Normal']))
        story.append(Spacer(1, 12))

        # Footer
        footer_style = styles['Normal']
        footer_style.fontSize = 8
        footer_style.textColor = colors.gray
        story.append(Paragraph("Thank you for choosing Cafe Zone!", footer_style))
        story.append(Paragraph("For any queries, contact us at support@cafezone.com", footer_style))

        doc.build(story)

        # Read PDF as base64
        with open(filename, 'rb') as f:
            pdf_data = f.read()
        import base64
        pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')

        # Clean up
        os.remove(filename)

        return jsonify({
            'success': True,
            'pdf': pdf_base64,
            'invoiceNumber': f"CZ{int(time.time() * 1000)}"
        })

    except Exception as e:
        print(f"Error generating invoice: {e}")
        return jsonify({'error': 'Failed to generate invoice'}), 500

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    item_id = data.get('item_id')
    quantity = data.get('quantity', 1)

    if not item_id:
        return jsonify({'error': 'Item ID is required'}), 400

    # Get or create cart in session
    cart = session.get('cart', {})
    cart[str(item_id)] = cart.get(str(item_id), 0) + quantity
    session['cart'] = cart

    return jsonify({'success': True, 'message': 'Item added to cart', 'cart': cart})

@app.route('/save-order', methods=['POST'])
def save_order():
    data = request.get_json()
    name = data.get('name')
    mobile = data.get('mobile')
    email = data.get('email')
    order_data = data.get('order_data')  # JSON string of cart items
    total_amount = data.get('total_amount')
    payment_method = data.get('payment_method')
    diet_preference = data.get('diet_preference')  # 'diet', 'non-diet', or None
    user_id = data.get('user_id')  # Optional for logged-in users

    if not name or not mobile or not email or not order_data or not total_amount or not payment_method:
        return jsonify({'error': 'All fields are required'}), 400

    # Save to guest_orders list
    new_order = {
        'id': len(guest_orders) + 1,
        'user_id': user_id,
        'name': name,
        'mobile': mobile,
        'email': email,
        'order_data': order_data,
        'total_amount': total_amount,
        'payment_method': payment_method,
        'diet_preference': diet_preference,
        'order_date': datetime.now().isoformat()
    }
    guest_orders.append(new_order)

    print(f"Guest order saved: {name}, {mobile}, {email}, {total_amount}, diet: {diet_preference}, user_id: {user_id}")

    return jsonify({'success': True, 'message': 'Order saved successfully', 'order_id': new_order['id']})

@app.route('/get-guest-orders', methods=['POST'])
def get_guest_orders():
    data = request.get_json()
    mobile = data.get('mobile')
    email = data.get('email')

    if not mobile and not email:
        return jsonify({'error': 'Mobile or email is required'}), 400

    # Filter orders
    orders = guest_orders
    if mobile:
        orders = [o for o in orders if o['mobile'] == mobile]
    if email:
        orders = [o for o in orders if o['email'] == email]

    # Sort by order_date descending
    orders.sort(key=lambda x: x['order_date'], reverse=True)

    orders_data = [{
        'id': order['id'],
        'name': order['name'],
        'mobile': order['mobile'],
        'email': order['email'],
        'order_data': order['order_data'],
        'total_amount': order['total_amount'],
        'payment_method': order['payment_method'],
        'diet_preference': order['diet_preference'],
        'order_date': order['order_date']
    } for order in orders]

    return jsonify({'success': True, 'orders': orders_data})

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

# Routes for HTML pages
@app.route('/')
def home():   
    return render_template('login.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/cart')
def cart_page():
    return render_template('cart.html')

@app.route('/orders')
def orders_page():
    return render_template('orders.html')

@app.route('/payment')
def payment_page():
    return render_template('payment.html')

@app.route('/payment.html')
def payment_html_page():
    return render_template('payment.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile_page():
    if request.method == 'POST':
        data = request.get_json()
        mobile = data.get('mobile')

        if not mobile:
            return jsonify({'error': 'Mobile number is required'}), 400

        user = next((u for u in users if u['mobile'] == mobile), None)

        if user:
            user_data = {
                'id': user['id'],
                'name': user['name'],
                'mobile': user['mobile'],
                'email': user['email'],
                'dob': user['dob'],
                'gender': user['gender']
            }
            return jsonify({'exists': True, 'user': user_data})
        else:
            return jsonify({'exists': False})

    return render_template('profile.html')

@app.route('/profile-data', methods=['POST'])
def get_profile_data():
    data = request.get_json()
    mobile = data.get('mobile')

    if not mobile:
        return jsonify({'error': 'Mobile number is required'}), 400

    user = next((u for u in users if u['mobile'] == mobile), None)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    user_data = {
        'id': user['id'],
        'name': user['name'],
        'mobile': user['mobile'],
        'email': user['email'],
        'dob': user['dob'],
        'gender': user['gender']
    }

    # Get login count
    login_count_value = len([lh for lh in login_history if lh['user_id'] == user['id']])

    # Get login history
    user_login_history = [lh for lh in login_history if lh['user_id'] == user['id']]
    user_login_history.sort(key=lambda x: x['login_time'], reverse=True)
    history_data = [{
        'id': entry['id'],
        'login_time': entry['login_time']
    } for entry in user_login_history]

    # Get orders
    orders = [o for o in guest_orders if o['mobile'] == mobile]
    orders.sort(key=lambda x: x['order_date'], reverse=True)
    orders_data = [{
        'id': order['id'],
        'name': order['name'],
        'mobile': order['mobile'],
        'email': order['email'],
        'order_data': order['order_data'],
        'total_amount': order['total_amount'],
        'payment_method': order['payment_method'],
        'diet_preference': order['diet_preference'],
        'order_date': order['order_date']
    } for order in orders]

    # Calculate nutritional insights
    total_orders = len(orders)
    if total_orders > 0:
        total_protein = 0
        total_carbs = 0
        total_fats = 0
        total_calories = 0

        for order in orders:
            try:
                items = eval(order['order_data'])  # Assuming order_data is a string representation of list
                for item in items:
                    total_protein += (item.get('protein', 0) * item.get('quantity', 1))
                    total_carbs += (item.get('carbs', 0) * item.get('quantity', 1))
                    total_fats += (item.get('fats', 0) * item.get('quantity', 1))
                    total_calories += (item.get('calories', 0) * item.get('quantity', 1))
            except:
                pass

        avg_protein = total_protein / total_orders
        avg_carbs = total_carbs / total_orders
        avg_fats = total_fats / total_orders
        avg_calories = total_calories / total_orders
    else:
        avg_protein = avg_carbs = avg_fats = avg_calories = 0

    # Determine preference
    diet_orders = sum(1 for o in orders if o['diet_preference'] == 'diet')
    non_diet_orders = sum(1 for o in orders if o['diet_preference'] == 'non-diet')
    if diet_orders > non_diet_orders:
        preference = 'Diet'
    elif non_diet_orders > diet_orders:
        preference = 'Non-Diet'
    else:
        preference = 'Mixed'

    return jsonify({
        'user': user_data,
        'loginCount': login_count_value,
        'loginHistory': history_data,
        'totalOrders': total_orders,
        'avgProtein': round(avg_protein, 1),
        'avgCarbs': round(avg_carbs, 1),
        'avgFats': round(avg_fats, 1),
        'avgCalories': round(avg_calories),
        'preference': preference
    })

@app.route('/welcome', methods=['GET'])
def welcome():
    return jsonify({'message': 'Welcome to Cafe Zone!'})

@app.route('/cafeteria')
def cafeteria():
    # Fetch all food items from CSV
    items = load_food_items()
    user_name = session.get('user_name', 'Guest')
    return render_template('cafeteria.html', items=items, user_name=user_name)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
