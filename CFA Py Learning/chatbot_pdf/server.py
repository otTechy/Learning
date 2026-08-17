from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import PyPDF2

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        text = extract_text_from_pdf(filepath)
        key_terms = extract_key_terms(text)
        return jsonify({'key_terms': key_terms})
    return jsonify({'error': 'Unknown error'}), 500

def extract_text_from_pdf(pdf_path):
    text = ''
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ''
    return text

def extract_key_terms(text):
    # Simple key term extraction: most frequent words (excluding stopwords)
    import re
    from collections import Counter
    stopwords = set(['the', 'and', 'to', 'of', 'in', 'a', 'is', 'for', 'on', 'with', 'as', 'by', 'at', 'an', 'be', 'are', 'from', 'that', 'this', 'it', 'or', 'was', 'which', 'has', 'have', 'not', 'but', 'can', 'will', 'if', 'their', 'they', 'we', 'you', 'all', 'any', 'so', 'do', 'no'])
    words = re.findall(r'\b\w+\b', text.lower())
    filtered = [w for w in words if w not in stopwords and len(w) > 2]
    most_common = Counter(filtered).most_common(10)
    return [w for w, _ in most_common]

if __name__ == '__main__':
    app.run(debug=True, port=5000)
