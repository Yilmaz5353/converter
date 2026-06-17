import os
from flask import Flask, render_template, request, send_file, jsonify
from moviepy.video.io.VideoFileClip import VideoFileClip

app = Flask(__name__)

# Yüklenen ve dönüştürülen dosyaların kaydedileceği klasör
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_video():
    if 'video' not in request.files:
        return jsonify({'error': 'Lütfen bir video dosyası seçin.'}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'Dosya seçilmedi.'}), 400

    if file:
        # Dosya isimlerini güvenli hale getir ve kaydet
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(video_path)
        
        # Çıktı olarak alınacak MP3 dosyasının adı
        mp3_filename = os.path.splitext(file.filename)[0] + '.mp3'
        mp3_path = os.path.join(app.config['UPLOAD_FOLDER'], mp3_filename)
        
        try:
            # Video dosyasını aç ve sesi ayıkla
            video = VideoFileClip(video_path)
            if video.audio is None:
                return jsonify({'error': 'Bu videoda ses parçası bulunamadı.'}), 400
                
            video.audio.write_audiofile(mp3_path, bitrate="192k")
            video.close() # Belleği temizle
            
            # Orijinal video dosyasını sunucudan sil (Yer kaplamasın)
            os.remove(video_path)
            
            return jsonify({'success': True, 'download_url': f'/download/{mp3_filename}'})
        
        except Exception as e:
            # Hata durumunda yüklenen dosyayı temizle
            if os.path.exists(video_path):
                os.remove(video_path)
            return jsonify({'error': f'Dönüştürme hatası: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "Dosya bulunamadı veya süresi doldu.", 404

if __name__ == '__main__':
    # Local test için
    app.run(debug=True)