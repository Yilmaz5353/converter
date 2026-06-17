import os
from flask import Flask, request, jsonify, send_from_directory
# MoviePy yeni sürüm import yöntemi
from moviepy.video.io.VideoFileClip import VideoFileClip

app = Flask(__name__)

# 📌 RENDER İÇİN KRİTİK: Sadece /tmp klasörüne yazma iznimiz var!
UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

@app.route('/convert', methods=['POST'])
def convert_video():
    if 'video' not in request.files:
        return jsonify({'success': False, 'error': 'Dosya seçilmedi'}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'Dosya adı boş'}), 400

    if file:
        # Dosya isimlerini güvenli şekilde oluşturuyoruz
        video_path = os.path.join(UPLOAD_FOLDER, file.filename)
        audio_filename = os.path.splitext(file.filename)[0] + '.mp3'
        audio_path = os.path.join(UPLOAD_FOLDER, audio_filename)
        
        try:
            # 1. Videoyu geçici klasöre kaydet
            file.save(video_path)
            
            # 2. Dönüştürme (RAM sızıntısını önlemek için 'with' yapısı kullanıyoruz)
            # logger=None yapıyoruz ki log ekranını gereksiz şişirip sunucuyu yormasın
            with VideoFileClip(video_path) as clip:
                clip.audio.write_audiofile(audio_path, logger=None)
            
            # 3. İşlem bittiğinde orijinal MP4'ü silelim ki sunucunun hafızası dolmasın
            if os.path.exists(video_path):
                os.remove(video_path)
                
            return jsonify({
                'success': True,
                'download_url': f'/download/{audio_filename}'
            })
            
        except Exception as e:
            # Hata oluşursa arkada çöp dosya bırakmamak için temizlik yapıyoruz
            if os.path.exists(video_path): os.remove(video_path)
            if os.path.exists(audio_path): os.remove(audio_path)
            return jsonify({'success': False, 'error': str(e)}), 500

# 📌 MP3 dosyasını güvenli klasörden kullanıcıya indiren rota
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)