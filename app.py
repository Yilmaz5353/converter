import os
from flask import Flask, send_from_directory

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

# 📌 KRİTİK AYAR: Tarayıcının kullanıcının işlemcisini (FFmpeg) tam performans 
# kullanabilmesi için bu güvenlik başlıklarını (Headers) göndermemiz şarttır.
@app.after_request
def add_security_headers(response):
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
    return response

if __name__ == '__main__':
    app.run(debug=True)