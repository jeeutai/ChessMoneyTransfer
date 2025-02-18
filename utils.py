import csv
import os

USER_FILE = "users.csv"

def read_users():
    """CSV 파일에서 회원 정보를 읽어오는 함수"""
    users = []
    if not os.path.exists(USER_FILE):
        return users  # 파일이 없으면 빈 리스트 반환
    with open(USER_FILE, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            users.append(row)
    return users

def save_user(username, password, balance=1000):
    """새로운 회원 정보를 CSV 파일에 저장하는 함수"""
    users = read_users()
    user_id = len(users) + 1  # 자동으로 ID 증가
    with open(USER_FILE, mode="a", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([user_id, username, password, balance])

def find_user(username):
    """사용자 이름으로 회원 정보를 찾는 함수"""
    users = read_users()
    for user in users:
        if user["username"] == username:
            return user
    return None

def update_balance(username, amount):
    """사용자의 잔액을 업데이트하는 함수"""
    users = read_users()
    updated_users = []
    success = False

    for user in users:
        if user["username"] == username:
            new_balance = int(user["balance"]) + amount
            if new_balance < 0:
                return False  # 잔액 부족
            user["balance"] = str(new_balance)
            success = True
        updated_users.append(user)

    if success:
        with open(USER_FILE, mode="w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["id", "username", "password", "balance"])
            writer.writeheader()
            writer.writerows(updated_users)
        return True
    return False

def transfer_money(sender, receiver, amount):
    """송금 기능 - 보낸 사람 잔액 감소, 받는 사람 잔액 증가"""
    amount = int(amount)
    
    # 송금할 수 있는지 체크
    if update_balance(sender, -amount):  
        if update_balance(receiver, amount):
            return True
        else:
            # 받는 사람이 없거나 에러가 났으면 다시 돌려놓기
            update_balance(sender, amount)
    return False

