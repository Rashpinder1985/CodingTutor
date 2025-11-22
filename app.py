#!/usr/bin/env python3
"""
Adaptive Question Generator - Simple Web Interface
Flask-based web application for teachers to upload exit tickets and download questions.
"""

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import yaml
import tempfile
import json
import zipfile
import io
from datetime import datetime
from pathlib import Path

# Import our modules
from src.input_processor import InputProcessor
from src.question_generator import QuestionGenerator
from src.output_formatter import OutputFormatter

app = Flask(__name__)
app.secret_key = 'dev_secret_key_change_in_production'
CORS(app)

# Configuration
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'xlsx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_config():
    """Load configuration file."""
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

def create_download_zip(output_data):
    """Create a ZIP file with all exports."""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add main output
        zip_file.writestr('complete_output.json', json.dumps(output_data, indent=2))
        
        # Add level-based exports
        for level in ['beginner', 'intermediate', 'advanced']:
            level_questions = []
            for concept_key, concept_data in output_data['concepts'].items():
                level_data = concept_data['levels'][level]
                for question in level_data['questions']:
                    level_questions.append({
                        'id': question.get('question_id', ''),
                        'concept': concept_data['concept_name'],
                        'language': concept_data.get('programming_language'),
                        'question': question
                    })
            if level_questions:
                zip_file.writestr(
                    f'{level}_questions.json',
                    json.dumps({
                        'level': level,
                        'total_questions': len(level_questions),
                        'questions': level_questions
                    }, indent=2)
                )
        
        # Add by-concept exports
        for concept_key, concept_data in output_data['concepts'].items():
            filename = f"by_concept/{concept_key}.json"
            zip_file.writestr(filename, json.dumps({
                'concept': concept_data['concept_name'],
                'category': concept_data['course_category'],
                'language': concept_data.get('programming_language'),
                'affected_students': concept_data['affected_students'],
                'levels': concept_data['levels']
            }, indent=2))
    
    zip_buffer.seek(0)
    return zip_buffer

@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and question generation."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Please upload an Excel file (.xlsx)'}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Get filters
        concept_filter = request.form.get('concept_filter')
        language_filter = request.form.get('language_filter')
        
        # Load config
        config = load_config()
        
        # Process input
        processor = InputProcessor(filepath)
        processor.load_and_validate()
        processor.identify_incorrect_responses()
        concepts_data = processor.group_by_concept()
        
        if not concepts_data:
            os.unlink(filepath)
            return jsonify({'error': 'No incorrect responses found. Students answered all questions correctly!'}), 400
        
        # Apply filters
        if concept_filter and concept_filter != 'all':
            concepts_data = processor.filter_by_concept(concept_filter)
        
        if language_filter and language_filter != 'all':
            concepts_data = processor.filter_by_language(language_filter)
        
        if not concepts_data:
            os.unlink(filepath)
            return jsonify({'error': 'No concepts match the selected filters.'}), 400
        
        # Generate questions
        generator = QuestionGenerator(config)
        questions_data = generator.generate_all_concepts(concepts_data)
        
        # Format output
        summary = processor.get_summary()
        formatter = OutputFormatter(config)
        output_data = formatter.format_output(questions_data, filename, summary)
        
        # Save output
        output_filename = f"questions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        # Clean up uploaded file
        os.unlink(filepath)
        
        # Create response with summary
        response = {
            'success': True,
            'output_file': output_filename,
            'summary': {
                'total_concepts': summary['total_concepts'],
                'affected_students': summary['affected_students'],
                'programming_concepts': summary['programming_concepts'],
                'non_programming_concepts': summary['non_programming_concepts']
            },
            'concepts': {}
        }
        
        # Add concept details
        for concept_key, concept_data in output_data['concepts'].items():
            response['concepts'][concept_key] = {
                'name': concept_data['concept_name'],
                'category': concept_data['course_category'],
                'language': concept_data.get('programming_language'),
                'students': concept_data['affected_students'],
                'question_counts': {
                    'beginner': concept_data['levels']['beginner']['total_questions'],
                    'intermediate': concept_data['levels']['intermediate']['total_questions'],
                    'advanced': concept_data['levels']['advanced']['total_questions']
                }
            }
        
        return jsonify(response)
        
    except Exception as e:
        if os.path.exists(filepath):
            os.unlink(filepath)
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download generated JSON file."""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(filepath, as_attachment=True, download_name=filename)

@app.route('/download-all/<filename>')
def download_all(filename):
    """Download all formats as ZIP."""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    # Load the JSON file
    with open(filepath, 'r') as f:
        output_data = json.load(f)
    
    # Create ZIP
    zip_buffer = create_download_zip(output_data)
    
    # Generate filename
    zip_filename = filename.replace('.json', '_all_formats.zip')
    
    return send_file(
        zip_buffer,
        as_attachment=True,
        download_name=zip_filename,
        mimetype='application/zip'
    )

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    print("=" * 70)
    print("🚀 Adaptive Question Generator - Web Interface")
    print("=" * 70)
    print()
    print("✅ Starting web server...")
    print(f"📱 Open your browser and go to: http://localhost:5000")
    print()
    print("Press CTRL+C to stop the server")
    print("=" * 70)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

