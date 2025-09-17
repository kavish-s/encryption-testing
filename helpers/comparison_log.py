import json
import os

def log_comparison(filename, aes_time, aes_size, chunked_time, chunked_size):
    log_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'comparison_log.json')
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            data = json.load(f)
    else:
        data = []
    entry = {
        'filename': filename,
        'aes_time': aes_time,
        'aes_size': aes_size,
        'chunked_time': chunked_time,
        'chunked_size': chunked_size
    }
    data.append(entry)
    with open(log_path, 'w') as f:
        json.dump(data, f)

def get_comparison_log():
    log_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'comparison_log.json')
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            return json.load(f)
    return []
