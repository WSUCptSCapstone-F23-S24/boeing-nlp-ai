from flask import Flask, request, render_template, send_file
import os
from main import *

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
OUTPUT_FOLDER = 'output'
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_document():
    if 'document' not in request.files:
        return 'No file part', 400
    file = request.files['document']
    if file.filename == '':
        return 'No selected file', 400
    if file:
        filename = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filename)
        
        # Process the document
        entities_to_highlight = request.form.get('entities').upper().split(',')
        summary_length = float(request.form.get('summary_length', 20)) / 100
        
        formatted_sentences, tokens, entities, doc = process_large_document(filename)

        # Filter entities based on user selection
        highlighted_entities = [(ent, label) for ent, label in entities if label in entities_to_highlight]

        summary_sentences = generate_summary(doc, ratio=summary_length)
        
        # saving results to a file or directly return them to the user
        base_filename = os.path.splitext(file.filename)[0]  # Extract base filename without extension
        print(base_filename)
        output_filename = os.path.join(OUTPUT_FOLDER, f"processed_{base_filename}.txt")  # Change extension to .txt
        print_results_to_file(output_filename, formatted_sentences, highlighted_entities, summary_sentences)
        
        return send_file(output_filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)