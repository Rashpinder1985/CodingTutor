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
import logging
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env.local if it exists
env_local_path = Path(__file__).parent / '.env.local'
if env_local_path.exists():
    with open(env_local_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                # Parse export VAR="value" format
                if line.startswith('export '):
                    line = line[7:]  # Remove 'export '
                key, value = line.split('=', 1)
                # Remove quotes if present
                value = value.strip().strip('"').strip("'")
                os.environ[key] = value
                print(f"Loaded {key} from .env.local")

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
ALLOWED_EXTENSIONS = {'xlsx', 'txt', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Check for API keys on startup (log status)
print("\n" + "="*70)
print("🔑 API Key Status Check:")
gemini_key = os.getenv('GEMINI_API_KEY')
openai_key = os.getenv('OPENAI_API_KEY')
if gemini_key:
    print(f"✓ GEMINI_API_KEY: {gemini_key[:10]}...{gemini_key[-4:]}")
else:
    print("⚠️  GEMINI_API_KEY: Not set")
if openai_key:
    print(f"✓ OPENAI_API_KEY: {openai_key[:10]}...{openai_key[-4:]}")
else:
    print("ℹ️  OPENAI_API_KEY: Not set (optional)")
print("="*70 + "\n")

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
        llm_provider = data.get('llm_provider', 'auto')  # Get user's LLM choice
        
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
        
        # Override LLM provider based on user choice
        if llm_provider and llm_provider != 'auto':
            print(f"User selected LLM provider: {llm_provider}")
            config['llm']['provider'] = llm_provider
            # KEEP fallback enabled for reliability (even with specific provider)
            config['llm']['fallback_enabled'] = True
            print("  (Fallback still enabled for reliability)")
            
            # Set appropriate model for each provider
            if llm_provider == 'ollama':
                config['llm']['model'] = 'llama3.2'
            elif llm_provider == 'gemini':
                config['llm']['model'] = 'gemini-2.5-flash'
                # Verify Gemini API key is set
                gemini_key = os.getenv('GEMINI_API_KEY')
                if not gemini_key:
                    print("ERROR: GEMINI_API_KEY environment variable not set!")
                    print("  Will try to use fallback providers...")
                    # Don't return error, let it try fallback
                else:
                    print(f"✓ Gemini API key found: {gemini_key[:10]}...{gemini_key[-4:]}")
            elif llm_provider == 'openai':
                config['llm']['model'] = 'gpt-3.5-turbo'
                # Verify OpenAI API key is set
                openai_key = os.getenv('OPENAI_API_KEY')
                if not openai_key:
                    print("ERROR: OPENAI_API_KEY environment variable not set!")
                    print("  Will try to use fallback providers...")
                    # Don't return error, let it try fallback
        else:
            print("Using automatic fallback chain: Ollama → Gemini → OpenAI")
            # Keep fallback enabled for 'auto' mode
            config['llm']['fallback_enabled'] = True
        
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
        
        # Sanitize concept_key for filename (remove any remaining invalid characters)
        safe_concept_key = concept_key.replace('/', '_').replace('\\', '_').replace(':', '_')
        safe_concept_key = safe_concept_key.replace('*', '_').replace('?', '_').replace('"', '_')
        safe_concept_key = safe_concept_key.replace('<', '_').replace('>', '_').replace('|', '_')
        # Remove multiple consecutive underscores
        while '__' in safe_concept_key:
            safe_concept_key = safe_concept_key.replace('__', '_')
        safe_concept_key = safe_concept_key.strip('_')
        
        # Ensure upload folder exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Create Word document
        output_filename = f"concept_{safe_concept_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
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

@app.route('/analyze-activity', methods=['POST'])
def analyze_activity():
    """Analyze activity-based exit ticket with two-file upload."""
    try:
        # Check for both required files
        if 'exit_ticket' not in request.files or 'activity_template' not in request.files:
            return jsonify({'error': 'Both exit ticket and activity template files are required'}), 400
        
        exit_file = request.files['exit_ticket']
        activity_file = request.files['activity_template']
        
        if not exit_file.filename or not activity_file.filename:
            return jsonify({'error': 'Both files must have valid filenames'}), 400
        
        # Get LLM provider selection
        llm_provider = request.form.get('llm_provider', 'ollama')
        
        # Save uploaded files
        exit_filename = secure_filename(exit_file.filename)
        activity_filename = secure_filename(activity_file.filename)
        
        exit_path = os.path.join(app.config['UPLOAD_FOLDER'], exit_filename)
        activity_path = os.path.join(app.config['UPLOAD_FOLDER'], activity_filename)
        
        exit_file.save(exit_path)
        activity_file.save(activity_path)
        
        logger.info(f"Saved exit ticket: {exit_path}")
        logger.info(f"Saved activity template: {activity_path}")
        
        # Process files
        from src.activity_input_processor import ActivityInputProcessor
        from src.activity_analyzer import ActivityAnalyzer
        from src.activity_word_formatter import create_activity_report
        from src.llm_generator import LLMGenerator
        
        processor = ActivityInputProcessor()
        
        # Load and validate data
        students_data = processor.load_exit_ticket_excel(exit_path)
        activity_template = processor.load_activity_template(activity_path)
        
        # Validate responses
        students_data, warnings = processor.validate_responses(students_data)
        
        if not students_data:
            return jsonify({'error': 'No valid student responses found in exit ticket'}), 400
        
        logger.info(f"Loaded {len(students_data)} student responses")
        if warnings:
            logger.warning(f"Validation warnings: {warnings[:5]}")  # Log first 5 warnings
        
        # Configure LLM
        config = load_config()
        config['llm']['provider'] = llm_provider
        config['llm']['fallback_enabled'] = True  # Always enable fallback
        
        # Initialize LLM and analyzer
        llm_gen = LLMGenerator(config)  # Pass full config, not just config['llm']
        analyzer = ActivityAnalyzer(config, llm_gen)
        
        # Generate analysis report
        logger.info("Starting activity analysis...")
        results = analyzer.generate_analysis_report(students_data, activity_template)
        
        # Create Word document
        doc = create_activity_report(results)
        output_filename = f"activity_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        doc.save(output_path)
        
        logger.info(f"Activity analysis complete: {output_filename}")
        
        # Return results
        return jsonify({
            'success': True,
            'output_file': output_filename,
            'summary': {
                'total_students': results['metadata']['total_students'],
                'top_per_question': results['metadata']['top_responses_per_question'],
                'q1_analyzed': results['summary']['q1_responses_analyzed'],
                'q1_selected': results['summary']['q1_top_selected'],
                'q2_analyzed': results['summary']['q2_responses_analyzed'],
                'q2_selected': results['summary']['q2_top_selected'],
                'q3_analyzed': results['summary']['q3_responses_analyzed'],
                'q3_selected': results['summary']['q3_top_selected'],
                'scoring_method': results['metadata']['scoring_method']
            },
            'warnings': warnings[:10]  # Include first 10 warnings
        })
    
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        return jsonify({'error': str(ve)}), 400
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"ERROR in analyze_activity: {error_details}")
        return jsonify({'error': f'Error analyzing activity: {str(e)}'}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Get port from environment (for cloud deployment) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    is_production = os.environ.get('RENDER', False)
    
    print("=" * 70)
    print("🚀 Adaptive Question Generator - Web Interface")
    print("=" * 70)
    print()
    print("✅ Starting web server...")
    print(f"📱 Open your browser and go to: http://localhost:{port}")
    print()
    print("Press CTRL+C to stop the server")
    print("=" * 70)
    
    # In production (Render), gunicorn handles the server
    # This block only runs for local development
    app.run(debug=not is_production, host='0.0.0.0', port=port)

