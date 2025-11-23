#!/usr/bin/env python3
"""
Adaptive Question Generator - Simple Web Interface
Flask-based web application for teachers to upload exit tickets and download questions.
"""

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for, session
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import yaml
import tempfile
import json
import zipfile
import io
import uuid
from datetime import datetime
from pathlib import Path

# Import our modules
from src.input_processor import InputProcessor
from src.question_generator import QuestionGenerator
from src.output_formatter import OutputFormatter
from src.word_formatter import create_word_document

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
    """Handle file upload and analysis (NO question generation)."""
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
        
        # Get summary
        summary = processor.get_summary()
        
        # Generate unique session ID and save processed data
        session_id = str(uuid.uuid4())
        session_data = {
            'concepts_data': concepts_data,
            'summary': summary,
            'filename': filename
        }
        
        # Save to temp file
        session_file = os.path.join(app.config['UPLOAD_FOLDER'], f'session_{session_id}.json')
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
        
        # Clean up uploaded file
        os.unlink(filepath)
        
        # Create response with concept list (NO questions generated yet)
        response = {
            'success': True,
            'session_id': session_id,
            'summary': {
                'total_concepts': summary['total_concepts'],
                'affected_students': summary['affected_students'],
                'programming_concepts': summary['programming_concepts'],
                'non_programming_concepts': summary['non_programming_concepts']
            },
            'concepts': {}
        }
        
        # Add concept details WITHOUT question counts
        for concept_key, concept_data in concepts_data.items():
            response['concepts'][concept_key] = {
                'key': concept_key,
                'name': concept_data['concept_name'],
                'category': concept_data['course_category'],
                'language': concept_data.get('programming_language'),
                'students': concept_data['affected_students'],
                'student_count': len(concept_data['affected_students']),
                'status': 'pending'
            }
        
        return jsonify(response)
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR in upload_file: {error_details}")
        
        try:
            if 'filepath' in locals() and os.path.exists(filepath):
                os.unlink(filepath)
        except:
            pass
        
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

@app.route('/generate-concept', methods=['POST'])
def generate_concept():
    """Generate questions for a single concept."""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        concept_key = data.get('concept_key')
        
        if not session_id or not concept_key:
            return jsonify({'error': 'Missing session_id or concept_key'}), 400
        
        # Load session data
        session_file = os.path.join(app.config['UPLOAD_FOLDER'], f'session_{session_id}.json')
        if not os.path.exists(session_file):
            return jsonify({'error': 'Session expired or invalid'}), 404
        
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        
        concepts_data = session_data['concepts_data']
        
        if concept_key not in concepts_data:
            return jsonify({'error': f'Concept {concept_key} not found'}), 404
        
        # Load config
        config = load_config()
        
        # Generate questions for ONLY this concept
        single_concept_data = {concept_key: concepts_data[concept_key]}
        generator = QuestionGenerator(config)
        questions_data = generator.generate_all_concepts(single_concept_data)
        
        if not questions_data or concept_key not in questions_data:
            return jsonify({'error': 'Failed to generate questions'}), 500
        
        # Format output for single concept
        concept_output = {
            'concept_key': concept_key,
            'concept_name': concepts_data[concept_key]['concept_name'],
            'category': concepts_data[concept_key]['course_category'],
            'language': concepts_data[concept_key].get('programming_language'),
            'affected_students': concepts_data[concept_key]['affected_students'],
            'levels': questions_data[concept_key]
        }
        
        # Create Word document
        output_filename = f"concept_{concept_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        
        # Generate Word document
        doc = create_word_document(concept_output)
        doc.save(output_path)
        
        # Extract question counts safely
        beginner_count = 0
        intermediate_count = 0
        advanced_count = 0
        
        # The structure is nested: concept_key -> levels -> beginner/intermediate/advanced -> questions
        if 'levels' in questions_data[concept_key]:
            levels = questions_data[concept_key]['levels']
            if 'beginner' in levels and 'questions' in levels['beginner']:
                beginner_count = len(levels['beginner']['questions'])
            if 'intermediate' in levels and 'questions' in levels['intermediate']:
                intermediate_count = len(levels['intermediate']['questions'])
            if 'advanced' in levels and 'questions' in levels['advanced']:
                advanced_count = len(levels['advanced']['questions'])
        
        # Return response
        return jsonify({
            'success': True,
            'concept_key': concept_key,
            'output_file': output_filename,
            'question_counts': {
                'beginner': beginner_count,
                'intermediate': intermediate_count,
                'advanced': advanced_count
            }
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR in generate_concept: {error_details}")
        return jsonify({'error': f'Error generating questions: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download generated Word document."""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    # Set the correct MIME type for Word documents
    mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    return send_file(filepath, as_attachment=True, download_name=filename, mimetype=mimetype)

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

