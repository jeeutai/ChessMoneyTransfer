 from threading import Thread
import time
import requests

# 이 함수는 Flask 애플리케이션이 계속 실행될 수 있도록 주기적으로 HTTP 요청을 보냅니다.
def keep_alive():
    while True:
        try:
            # 로컬에서 Flask 앱이 실행 중일 때 요청을 보내도록 설정
            response = requests.get("https://chessmoneytransfer.onrender.com")
            print("Sent keep-alive request: ", response.status_code)
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
        time.sleep(10)  # 50초마다 요청을 보냄

# Flask 앱 실행
def start_flask():
    from app import app
    app.run(debug=True, use_reloader=False)

if __name__ == "__main__":
    # 두 개의 스레드를 생성해서 Flask 앱과 keep-alive 기능을 동시에 실행
    thread1 = Thread(target=start_flask)
    thread2 = Thread(target=keep_alive)
    
    thread1.start()
    thread2.start()
