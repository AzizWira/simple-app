from pathlib import Path
import os
import sqlite3
from contextlib import closing
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)
DB_PATH = Path(os.environ.get('DB_PATH', '/data/visits.db'))

def connect_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH, timeout=10)
    db.execute('CREATE TABLE IF NOT EXISTS visits (id INTEGER PRIMARY KEY CHECK (id = 1), count INTEGER NOT NULL)')
    db.execute('INSERT OR IGNORE INTO visits(id, count) VALUES (1, 0)')
    db.commit()
    return db

@app.route('/')
def index():
    with closing(connect_db()) as db:
        with db:
            db.execute('UPDATE visits SET count = count + 1 WHERE id = 1')
            visits = db.execute('SELECT count FROM visits WHERE id = 1').fetchone()[0]
    return render_template_string('''<!doctype html>
<html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Praktikum Ahmad - Flask dan SQLite</title>
<style>body{font-family:Arial,sans-serif;background:#eef3f9;color:#203858;margin:0}main{max-width:700px;margin:70px auto;background:white;padding:36px;border-radius:12px}h1{font-size:28px}p{line-height:1.6}.count{font-size:30px;color:#1565c0;padding:20px;background:#eff6ff;border-radius:8px}small{color:#5d6c7f}</style></head>
<body><main><small>PRAKTIKUM KOMPUTASI AWAN</small><h1>Flask + SQLite + Docker + Jenkins</h1>
<p>Ahmad Aziz Wira Widodo<br>NIM 102062400112 | IS-07-02</p>
<p class="count">Kunjungan: {{ visits }}</p>
<p>Jumlah kunjungan disimpan pada database SQLite. Muat ulang halaman untuk menguji pembaruan data.</p>
<p>Database: <code>{{ database }}</code></p><a href="/health">Periksa koneksi database</a></main></body></html>''', visits=visits, database=str(DB_PATH))

@app.route('/health')
def health():
    try:
        with closing(connect_db()) as db:
            count = db.execute('SELECT count FROM visits WHERE id = 1').fetchone()[0]
        return jsonify(status='ok', database='SQLite', visits=count)
    except sqlite3.Error:
        return jsonify(status='error', database='SQLite'), 503

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
