from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import csv
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chessmoney.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    is_admin = db.Column(db.Boolean, default=False)

def save_users_to_csv():
    with open('users.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'username', 'password', 'balance', 'is_admin'])
        users = User.query.all()
        for user in users:
            writer.writerow([user.id, user.username, user.password, user.balance, user.is_admin])

def load_users_from_csv():
    if not os.path.exists('users.csv'):
        return
    with open('users.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)  # 헤더 스킵
        for row in reader:
            if len(row) < 5:  # 데이터가 부족한 경우
                continue  # 무시하고 다음 줄로 이동
            user = User(
                id=int(row[0]), 
                username=row[1], 
                password=row[2], 
                balance=float(row[3]), 
                is_admin=row[4].strip().lower() == 'true'  # 문자열 공백 제거 후 비교
            )
            db.session.merge(user)
        db.session.commit()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', user=user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        # DB에서 첫 번째 사용자 체크
        is_first_user = User.query.first() is None  # 첫 번째 사용자인지 확인

        new_user = User(username=username, password=hashed_password, is_admin=is_first_user)
        db.session.add(new_user)
        db.session.commit()
        save_users_to_csv()
        return redirect(url_for('login'))
    return render_template('register.html')
    
@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin'):
        flash("관리자만 접근 가능합니다!", "danger")
        return redirect(url_for('dashboard'))

    users = User.query.all()
    return render_template('admin.html', users=users)

@app.route('/update_balance/<int:user_id>', methods=['POST'])
def update_balance(user_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash("관리자만 접근 가능합니다!", "danger")
        return redirect(url_for('dashboard'))

    user = User.query.get(user_id)
    if user:
        new_balance = float(request.form['balance'])
        user.balance = new_balance
        db.session.commit()
        save_users_to_csv()
        flash(f"{user.username}의 잔액이 {new_balance}으로 변경되었습니다!", "success")
    
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash("관리자만 접근 가능합니다!", "danger")
        return redirect(url_for('dashboard'))

    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        save_users_to_csv()
        flash(f"{user.username} 계정이 삭제되었습니다!", "success")
    
    return redirect(url_for('admin_dashboard'))



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        load_users_from_csv()
    app.run(debug=True)
