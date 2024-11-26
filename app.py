import os
import yt_dlp
import subprocess
from flask import Flask, request, render_template, jsonify, send_from_directory

app = Flask(__name__)

# Route utama yang menyajikan halaman index.html
@app.route('/')
def index():
    return render_template('index.html')

# Endpoint untuk mengonversi video
@app.route('/convert', methods=['POST'])
def convert_to_mp3():
    url = request.json['url']  # Mengambil URL dari request

    # Setup untuk menyimpan file
    download_dir = 'download'
    os.makedirs(download_dir, exist_ok=True)

    # Menggunakan yt-dlp untuk mengekstrak metadata video
    ydl_opts = {
        'quiet': True,  # Tidak menampilkan output yang tidak perlu
        'force_generic_extractor': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)  # Tidak mengunduh, hanya mengambil info
        title = info_dict.get('title', 'No title available')
        thumbnail = info_dict.get('thumbnail', '')

    # Tentukan path untuk file yang akan didownload dan di-convert
    mp3_filename = os.path.join(download_dir, f"{info_dict['id']}.mp3")
    webm_filename = os.path.join(download_dir, f"{info_dict['id']}.webm")

    # Hapus file yang sudah ada untuk mencegah prompt 'overwrite'
    if os.path.exists(mp3_filename):
        os.remove(mp3_filename)
    if os.path.exists(webm_filename):
        os.remove(webm_filename)

    # Setup untuk mendownload video
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': webm_filename,
        'noplaylist': True,  # Hanya download satu video
        'quiet': True,  # Tidak menampilkan output yang tidak perlu
        'progress': False,  # Menonaktifkan progress bar
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)

    # Konversi menggunakan FFmpeg ke MP3
    subprocess.run(['ffmpeg', '-i', webm_filename, '-vn', '-ar', '44100', '-ac', '2', '-b:a', '192k', mp3_filename])

    # Mengembalikan data ke frontend
    return jsonify({
        'title': title,
        'thumbnail': thumbnail,
        'download_url': f'/download/{os.path.basename(mp3_filename)}'
    })

# Endpoint untuk mendownload file
@app.route('/download/<filename>')
def download(filename):
    return send_from_directory('download', filename)

if __name__ == '__main__':
    app.run(debug=True)
