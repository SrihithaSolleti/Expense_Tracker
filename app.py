from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from datetime import datetime
import os
from dotenv import load_dotenv
import json
import pytz

# Load environment variables
load_dotenv()

# Set timezone to IST
IST = pytz.timezone('Asia/Kolkata')

app = Flask(__name__)

# Configure secret key and database URI from environment variables
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'mysql+pymysql://sql12772650:X451YtmjfN@sql12.freesqldatabase.com:3306/sql12772650')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    upi_id = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    profile_image = db.Column(db.String(200), default='default.jpg')
    phone = db.Column(db.String(15))
    transactions = db.relationship('Transaction', backref='user', lazy=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'incoming' or 'outgoing'
    description = db.Column(db.String(200))
    category = db.Column(db.String(50))  # New field for transaction category
    date = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Split(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    tip_percentage = db.Column(db.Float)
    date = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    participants = db.Column(db.Text, nullable=False)
    settlements = db.Column(db.Text, nullable=False)

# Helper function to format datetime in IST
def format_datetime(dt):
    if dt.tzinfo is None:
        dt = IST.localize(dt)
    return dt.strftime('%Y-%m-%d %H:%M:%S')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
            
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, name=name, email=email, password_hash=password_hash)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/profile-page')
@login_required
def profile_page():
    return render_template('profile.html')

@app.route('/check-balance')
@login_required
def check_balance():
    return render_template('check_balance.html')

@app.route('/splitter')
@login_required
def splitter():
    return render_template('splitter.html')

@app.route('/transactions')
@login_required
def transactions_page():
    return render_template('transactions.html')

@app.route('/stats')
@login_required
def stats():
    return render_template('stats.html')

# API Routes
@app.route('/api/transactions', methods=['GET', 'POST'])
@login_required
def transactions():
    if request.method == 'POST':
        data = request.json
        transaction = Transaction(
            amount=data['amount'],
            type=data['type'],
            description=data.get('description', ''),
            category=data.get('category', ''),
            user_id=current_user.id
        )
        db.session.add(transaction)
        db.session.commit()
        return jsonify({'message': 'Transaction added successfully'})
    
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': t.id,
        'amount': t.amount,
        'type': t.type,
        'description': t.description,
        'category': t.category,
        'date': format_datetime(t.date)
    } for t in transactions])

@app.route('/api/profile', methods=['GET', 'PUT'])
@login_required
def profile():
    if request.method == 'PUT':
        data = request.json
        user = current_user
        user.name = data.get('name', user.name)
        user.email = data.get('email', user.email)
        user.upi_id = data.get('upi_id', user.upi_id)
        user.phone = data.get('phone', user.phone)
        
        db.session.commit()
        return jsonify({'message': 'Profile updated successfully'})
    
    return jsonify({
        'username': current_user.username,
        'name': current_user.name,
        'email': current_user.email,
        'upi_id': current_user.upi_id,
        'phone': current_user.phone,
        'profile_image': current_user.profile_image,
        'created_at': current_user.created_at.strftime('%Y')
    })

@app.route('/api/change-password', methods=['POST'])
@login_required
def change_password():
    data = request.json
    if bcrypt.check_password_hash(current_user.password_hash, data['current_password']):
        current_user.password_hash = bcrypt.generate_password_hash(data['new_password']).decode('utf-8')
        db.session.commit()
        return jsonify({'message': 'Password changed successfully'})
    return jsonify({'error': 'Current password is incorrect'}), 400

@app.route('/api/verify-password', methods=['POST'])
@login_required
def verify_password():
    try:
        data = request.get_json()
        if not data or 'password' not in data:
            return jsonify({'success': False, 'error': 'Password is required'}), 400
            
        password = data['password']
        if bcrypt.check_password_hash(current_user.password_hash, password):
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Incorrect password'}), 401
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/balance', methods=['GET'])
@login_required
def get_balance():
    try:
        user_transactions = Transaction.query.filter_by(user_id=current_user.id).all()
        total_balance = 0
        incoming = 0
        outgoing = 0
        
        for transaction in user_transactions:
            if transaction.type == 'incoming':
                total_balance += transaction.amount
                incoming += transaction.amount
            else:  # outgoing
                total_balance -= transaction.amount
                outgoing += transaction.amount
                
        return jsonify({
            'balance': total_balance,
            'formatted_balance': f"₹{total_balance:,.2f}",
            'incoming': f"₹{incoming:,.2f}",
            'outgoing': f"₹{outgoing:,.2f}"
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/transactions/<int:transaction_id>', methods=['PUT', 'DELETE'])
@login_required
def update_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    
    # Verify that the transaction belongs to the current user
    if transaction.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if request.method == 'PUT':
        data = request.json
        transaction.amount = data.get('amount', transaction.amount)
        transaction.type = data.get('type', transaction.type)
        transaction.description = data.get('description', transaction.description)
        transaction.category = data.get('category', transaction.category)
        
        db.session.commit()
        return jsonify({'message': 'Transaction updated successfully'})
    
    elif request.method == 'DELETE':
        db.session.delete(transaction)
        db.session.commit()
        return jsonify({'message': 'Transaction deleted successfully'})

@app.route('/api/splits', methods=['GET', 'POST'])
@login_required
def splits():
    if request.method == 'POST':
        data = request.json
        try:
            participants_json = json.dumps(data['participants'])
            settlements_json = json.dumps(data['settlements'])
            
            split = Split(
                title=data['title'],
                total_amount=data['total_amount'],
                tip_percentage=data.get('tip_percentage', 0),
                user_id=current_user.id,
                participants=participants_json,
                settlements=settlements_json
            )
            db.session.add(split)
            db.session.commit()
            return jsonify({'message': 'Split saved successfully', 'id': split.id})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    
    splits = Split.query.filter_by(user_id=current_user.id).order_by(Split.date.desc()).all()
    return jsonify([{
        'id': s.id,
        'title': s.title,
        'total_amount': s.total_amount,
        'tip_percentage': s.tip_percentage,
        'date': format_datetime(s.date),
        'participants': json.loads(s.participants),
        'settlements': json.loads(s.settlements)
    } for s in splits])

@app.route('/api/splits/<int:split_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def split_detail(split_id):
    split = Split.query.get_or_404(split_id)
    
    # Verify that the split belongs to the current user
    if split.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if request.method == 'PUT':
        data = request.json
        try:
            split.title = data['title']
            split.total_amount = data['total_amount']
            split.tip_percentage = data.get('tip_percentage', 0)
            split.participants = json.dumps(data['participants'])
            split.settlements = json.dumps(data['settlements'])
            split.date = datetime.now(IST)
            
            db.session.commit()
            return jsonify({'message': 'Split updated successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    
    elif request.method == 'DELETE':
        db.session.delete(split)
        db.session.commit()
        return jsonify({'message': 'Split deleted successfully'})
    
    return jsonify({
        'id': split.id,
        'title': split.title,
        'total_amount': split.total_amount,
        'tip_percentage': split.tip_percentage,
        'date': format_datetime(split.date),
        'participants': json.loads(split.participants),
        'settlements': json.loads(split.settlements)
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("Server starting on http://localhost:8080")
    app.run(host='0.0.0.0', port=8080, debug=True) 