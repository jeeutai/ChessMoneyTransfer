from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "체스머니 송금 시스템에 오신 것을 환영합니다!"

if __name__ == "__main__":
    app.run(debug=True)
