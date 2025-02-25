import os
import csv
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from models import Transaction, db
from config import SECRET_KEY, SQLALCHEMY_DATABASE_URI


app = Flask(__name__)
app.secret_key = SECRET_KEY  # config.py에서 가져온 값 사용
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI  # 이미 설정된 값 사용
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
USERS_CSV = 'users.csv'
    
db.init_app(app)


# ✅ Flask 앱 컨텍스트 안에서 DB 테이블 생성
with app.app_context():
    db.create_all()






# 사용자 클래스
class User:
    def __init__(self, id, username, password, balance, is_admin):
        self.id = id
        self.username = username
        self.password = password
        self.balance = balance
        self.is_admin = is_admin

def get_current_user():
    username = session.get('username')
    if not username:
        return None
    
    users = get_users()
    for user in users:
        if user.username == username:
            return user
    return None

def get_all_transactions():
    with app.app_context():  # 컨텍스트를 추가해서 SQLAlchemy 오류 방지
        return Transaction.query.all()


def get_users():
    users = []
    if os.path.exists(USERS_CSV):
        with open(USERS_CSV, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                users.append(User(
                    id=int(row['id']),
                    username=row['username'],
                    password=row['password'],
                    balance=float(row['balance']),
                    is_admin=row['is_admin'].strip().lower() == 'true'
                ))
    return users  # ✅ 불필요한 덮어쓰기 제거



# 사용자 정보 CSV 저장
def save_users(users):
    with open(USERS_CSV, 'w', encoding='utf-8', newline='') as file:
        fieldnames = ['id', 'username', 'password', 'balance', 'is_admin']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for user in users:
            writer.writerow({
                'id': user.id,
                'username': user.username,
                'password': user.password,
                'balance': user.balance,
                'is_admin': 'true' if user.is_admin else 'false'
            })


# 현재 로그인한 사용자 가져오기
def get_current_user():
    username = session.get('username')
    if not username:
        return None
    users = get_users()
    return next((user for user in users if user.username == username), None)


@app.route('/')
def home():
    user = get_current_user()
    return render_template('index.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        users = get_users()
        user = next((u for u in users if u.username == username), None)

        if not user:
            return render_template("login.html", message="존재하지 않는 사용자입니다.")

        if password != user.password:
            return render_template("login.html", message="비밀번호가 틀렸습니다.")

        session['username'] = user.username
        session['is_admin'] = user.is_admin
        return redirect(url_for('dashboard'))

    return render_template("login.html")


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('is_admin', None)
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    if user.is_admin:
        users = get_users()
        return render_template('admin_dashboard.html', user=user, users=users)
    
    return render_template('dashboard.html', user=user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return render_template('register.html', message="⚠️ 사용자명과 비밀번호를 입력하세요.")

        users = get_users()

        # 중복된 아이디 체크
        if any(user.username == username for user in users):
            return render_template('register.html', message="⚠️ 이미 존재하는 사용자명입니다.")

        new_id = max([user.id for user in users], default=0) + 1
        new_user = User(new_id, username, password, 0.0, False)  # 초기 잔액 0.0 설정
        users.append(new_user)

        save_users(users)

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/delete_user', methods=['POST'])
def delete_user():
    user_id = request.form.get('user_id')
    if not user_id:
        return "사용자 ID가 제공되지 않았습니다.", 400

    users = get_users()
    new_users = [user for user in users if str(user.id) != user_id]

    save_users(new_users)
    return redirect(url_for('dashboard'))

@app.route('/change_password', methods=['POST'])
def change_password():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    new_password = request.form['new_password']
    users = get_users()
    for u in users:
        if u.id == user.id:
            u.password = new_password

    save_users(users)
    return redirect(url_for('dashboard'))

@app.route('/send_money', methods=['POST'])
def send_money():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    recipient_username = request.form['recipient']
    amount = float(request.form['amount'])

    users = get_users()

    sender = next((u for u in users if u.username == user.username), None)
    recipient = next((u for u in users if u.username == recipient_username), None)

    if sender and recipient and sender.balance >= amount:
        sender.balance -= amount
        recipient.balance += amount
        save_users(users)

        # 거래 내역 저장
        transaction = Transaction(sender=user.username, recipient=recipient_username, amount=amount)
        db.session.add(transaction)
        db.session.commit()

        return redirect(url_for('dashboard'))

    return render_template("dashboard.html", user=user, message="⚠️ 송금 실패! 잔액 부족 또는 사용자 없음.")

@app.route('/admin')
def admin_dashboard():
    user = get_current_user()
    if not user or not user.is_admin:
        return redirect(url_for('dashboard'))
    
    users = get_users()  # 관리자니까 모든 사용자 정보 가져옴
    transactions = get_all_transactions()  # 전체 거래 내역 가져옴
    
    return render_template("admin_dashboard.html", user=user, users=users, transactions=transactions)
    
@app.route('/give_salary', methods=['POST'])
def give_salary():
    user = get_current_user()
    if not user or not user.is_admin:
        return redirect(url_for('login'))

    salary_amount = float(request.form['salary_amount'])
    users = get_users()

    for u in users:
        u.balance += salary_amount

    save_users(users)
    return redirect(url_for('dashboard'))

@app.route('/add_user', methods=['POST'])
def add_user():
    user = get_current_user()
    if not user or not user.is_admin:
        return redirect(url_for('login'))

    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return "사용자명과 비밀번호를 입력하세요.", 400

    users = get_users()

    # 중복된 아이디 체크
    if any(u.username == username for u in users):
        return "이미 존재하는 사용자명입니다.", 400

    new_id = max([u.id for u in users], default=0) + 1
    new_user = User(new_id, username, password, 0.0, False)  # 초기 잔액 0.0
    users.append(new_user)

    save_users(users)
    return redirect(url_for('dashboard'))

@app.route('/update_user', methods=['POST'])
def update_user():
    user_id = int(request.form['user_id'])
    new_balance = float(request.form['balance'])
    is_admin = 'is_admin' in request.form  # 체크박스 선택 여부 확인

    users = get_users()
    updated = False  # 업데이트 여부 확인

    for user in users:
        if user.id == user_id:
            user.balance = new_balance  # ✅ 잔액 업데이트
            user.is_admin = is_admin  # ✅ 관리자 여부 업데이트
            updated = True

    if updated:
        save_users(users)  # ✅ 변경 사항 저장

    return redirect(url_for('dashboard'))



if __name__ == '__main__':
    app.run(debug=True)
