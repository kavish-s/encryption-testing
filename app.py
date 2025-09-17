import os
import time
from flask import Flask, render_template, request, flash, redirect, url_for
from helpers.encryption import encrypt_chunked, encrypt_non_chunked, aes_encrypt
from helpers.comparison_log import log_comparison, get_comparison_log

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'supersecretkey'

@app.route('/')
def index():
    log_data = get_comparison_log()
    return render_template('index.html', log_data=log_data)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file:
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        encrypted_filepath = f"{filepath}.enc"
        chunked_encrypted_filepath = f"{filepath}.chunked.enc"

        # Standard AES
        start_time_aes = time.time()
        with open(filepath, 'rb') as in_file, open(encrypted_filepath, 'wb') as out_file:
            aes_encrypt(in_file, out_file)
        end_time_aes = time.time()

        # Chunked AES
        start_time_chunked = time.time()
        with open(filepath, 'rb') as in_file, open(chunked_encrypted_filepath, 'wb') as out_file:
            encrypt_chunked(in_file, out_file)
        end_time_chunked = time.time()

        os.remove(filepath) # Clean up original file

        aes_time = end_time_aes - start_time_aes
        chunked_time = end_time_chunked - start_time_chunked
        # Get sizes and then remove encrypted files
        aes_size = os.path.getsize(encrypted_filepath)
        chunked_size = os.path.getsize(chunked_encrypted_filepath)
        
        # Remove encrypted files after getting their sizes
        os.remove(encrypted_filepath)
        os.remove(chunked_encrypted_filepath)

        log_comparison(filename, aes_time, aes_size, chunked_time, chunked_size)

        flash('File processed and comparison data logged successfully.')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)