#!/usr/bin/env python3
"""
Adaptive Question Generator - Web UI for Teachers
Open-source web interface for uploading exit tickets and downloading questions.
"""

import streamlit as st
import pandas as pd
import yaml
import json
import tempfile
import os
from pathlib import Path
from datetime import datetime
import zipfile
import io

# Import our existing modules
from src.input_processor import InputProcessor
from src.question_generator import QuestionGenerator
from src.output_formatter import OutputFormatter

# Page configuration
st.set_page_config(
    page_title="Adaptive Question Generator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        margin: 1rem 0;
    }
    .stDownloadButton button {
        width: 100%;
        background-color: #28a745;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


def load_config():
    """Load configuration file."""
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)


def validate_excel_file(df):
    """Validate the uploaded Excel file structure."""
    required_columns = [
        'Student_ID', 'Question_ID', 'Student_Answer', 'Correct_Answer',
        'Concept', 'Question_Type', 'Course_Category'
    ]
    missing_columns = [col for col in required_columns if col not in df.columns]
    return len(missing_columns) == 0, missing_columns


def process_and_generate(uploaded_file, config, concept_filter=None, language_filter=None):
    """Process Excel file and generate questions."""
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name
    
    try:
        # Process input
        processor = InputProcessor(tmp_path)
        processor.load_and_validate()
        processor.identify_incorrect_responses()
        concepts_data = processor.group_by_concept()
        
        if not concepts_data:
            return None, None, "No incorrect responses found. Students answered all questions correctly!"
        
        # Apply filters
        if concept_filter and concept_filter != "All Concepts":
            concepts_data = processor.filter_by_concept(concept_filter)
        
        if language_filter and language_filter != "All Languages":
            concepts_data = processor.filter_by_language(language_filter)
        
        if not concepts_data:
            return None, None, "No concepts match the selected filters."
        
        # Generate questions
        generator = QuestionGenerator(config)
        questions_data = generator.generate_all_concepts(concepts_data)
        
        # Format output
        summary = processor.get_summary()
        formatter = OutputFormatter(config)
        output_data = formatter.format_output(questions_data, uploaded_file.name, summary)
        
        return output_data, summary, None
        
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def export_by_level(output_data):
    """Export questions by difficulty level."""
    exports = {}
    
    for level in ['beginner', 'intermediate', 'advanced']:
        level_questions = []
        
        for concept_key, concept_data in output_data['concepts'].items():
            level_data = concept_data['levels'][level]
            
            for question in level_data['questions']:
                level_questions.append({
                    'id': question.get('question_id', ''),
                    'concept': concept_data['concept_name'],
                    'language': concept_data.get('programming_language'),
                    'question': question,
                    'learning_resources': level_data.get('learning_resources', [])
                })
        
        if level_questions:
            exports[level] = {
                'level': level,
                'total_questions': len(level_questions),
                'generated_at': datetime.now().isoformat(),
                'questions': level_questions
            }
    
    return exports


def create_download_zip(output_data):
    """Create a ZIP file with all exports."""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add main output
        zip_file.writestr('complete_output.json', 
                         json.dumps(output_data, indent=2))
        
        # Add level-based exports
        level_exports = export_by_level(output_data)
        for level, data in level_exports.items():
            zip_file.writestr(f'{level}_questions.json',
                            json.dumps(data, indent=2))
        
        # Add by-concept exports
        for concept_key, concept_data in output_data['concepts'].items():
            concept_export = {
                'concept': concept_data['concept_name'],
                'category': concept_data['course_category'],
                'language': concept_data.get('programming_language'),
                'affected_students': concept_data['affected_students'],
                'levels': concept_data['levels'],
                'generated_at': datetime.now().isoformat()
            }
            filename = f"by_concept/{concept_key}.json"
            zip_file.writestr(filename, json.dumps(concept_export, indent=2))
    
    zip_buffer.seek(0)
    return zip_buffer


def main():
    # Header
    st.markdown('<div class="main-header">📚 Adaptive Question Generator for Teachers</div>', 
                unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Generate personalized practice questions from student exit tickets</div>', 
                unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("ℹ️ About")
        st.info("""
        This tool helps teachers:
        - Upload student exit ticket responses
        - Automatically identify struggling areas
        - Generate adaptive questions (3 levels)
        - Download platform-ready JSON files
        
        **Powered by Ollama (Local AI)**
        """)
        
        st.header("📋 Required Excel Format")
        st.code("""
Columns needed:
• Student_ID
• Question_ID
• Student_Answer
• Correct_Answer
• Concept
• Question_Type
• Course_Category
• Programming_Language (optional)
        """)
        
        st.header("🎯 Features")
        st.markdown("""
        ✅ Free & Open Source
        ✅ Privacy-Focused (Local AI)
        ✅ Multi-level Questions
        ✅ Instant Downloads
        ✅ Platform-Ready Formats
        """)
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["📤 Upload & Generate", "📖 Instructions", "❓ Help"])
    
    with tab1:
        # File upload
        st.header("Step 1: Upload Your Exit Ticket Excel File")
        uploaded_file = st.file_uploader(
            "Choose an Excel file (.xlsx)",
            type=['xlsx'],
            help="Upload your exit ticket responses in Excel format"
        )
        
        if uploaded_file:
            # Preview uploaded data
            try:
                df = pd.read_excel(uploaded_file)
                
                st.success(f"✅ File uploaded successfully! Found {len(df)} responses.")
                
                # Validate structure
                is_valid, missing_cols = validate_excel_file(df)
                
                if not is_valid:
                    st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
                    st.info("Please check the sidebar for required column names.")
                    return
                
                # Show preview
                with st.expander("👀 Preview Data (First 10 rows)"):
                    st.dataframe(df.head(10))
                
                # Show statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Students", df['Student_ID'].nunique())
                with col2:
                    st.metric("Total Responses", len(df))
                with col3:
                    incorrect = len(df[df['Student_Answer'].astype(str) != df['Correct_Answer'].astype(str)])
                    st.metric("Incorrect", incorrect)
                with col4:
                    concepts = df['Concept'].nunique()
                    st.metric("Concepts", concepts)
                
                st.markdown("---")
                
                # Filters
                st.header("Step 2: Configure Generation (Optional)")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Get unique concepts
                    concepts_list = ["All Concepts"] + sorted(df['Concept'].unique().tolist())
                    concept_filter = st.selectbox(
                        "Filter by Concept",
                        concepts_list,
                        help="Generate questions for specific concept only"
                    )
                
                with col2:
                    # Get unique languages
                    if 'Programming_Language' in df.columns:
                        languages = df['Programming_Language'].dropna().unique().tolist()
                        languages_list = ["All Languages"] + sorted([str(l) for l in languages])
                    else:
                        languages_list = ["All Languages"]
                    
                    language_filter = st.selectbox(
                        "Filter by Language",
                        languages_list,
                        help="For programming courses only"
                    )
                
                st.markdown("---")
                
                # Generate button
                st.header("Step 3: Generate Questions")
                
                if st.button("🚀 Generate Questions", type="primary", use_container_width=True):
                    with st.spinner("🔄 Analyzing student responses and generating questions... This may take a few minutes."):
                        try:
                            # Load config
                            config = load_config()
                            
                            # Process and generate
                            concept_filter_val = None if concept_filter == "All Concepts" else concept_filter
                            language_filter_val = None if language_filter == "All Languages" else language_filter
                            
                            output_data, summary, error = process_and_generate(
                                uploaded_file,
                                config,
                                concept_filter_val,
                                language_filter_val
                            )
                            
                            if error:
                                st.warning(f"⚠️ {error}")
                                return
                            
                            # Store in session state
                            st.session_state['output_data'] = output_data
                            st.session_state['summary'] = summary
                            st.session_state['generated'] = True
                            
                            st.success("✅ Questions generated successfully!")
                            st.balloons()
                            
                        except Exception as e:
                            st.error(f"❌ Error generating questions: {str(e)}")
                            st.exception(e)
                
                # Display results if generated
                if st.session_state.get('generated', False):
                    st.markdown("---")
                    st.header("Step 4: Download Questions")
                    
                    output_data = st.session_state['output_data']
                    summary = st.session_state['summary']
                    
                    # Summary
                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.markdown(f"""
                    **Generation Summary:**
                    - 📊 Total Concepts: {summary['total_concepts']}
                    - 👥 Affected Students: {summary['affected_students']}
                    - 💻 Programming Concepts: {summary['programming_concepts']}
                    - 📚 Non-Programming Concepts: {summary['non_programming_concepts']}
                    """)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Concept breakdown
                    with st.expander("📋 View Concept Breakdown"):
                        for concept_key, concept_data in output_data['concepts'].items():
                            st.markdown(f"**{concept_data['concept_name']}**")
                            st.write(f"- Category: {concept_data['course_category']}")
                            if concept_data.get('programming_language'):
                                st.write(f"- Language: {concept_data['programming_language']}")
                            st.write(f"- Students: {', '.join(concept_data['affected_students'])}")
                            
                            for level in ['beginner', 'intermediate', 'advanced']:
                                level_data = concept_data['levels'][level]
                                st.write(f"  • {level.title()}: {level_data['total_questions']} questions")
                            st.markdown("---")
                    
                    # Download options
                    st.subheader("📥 Download Options")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        # Complete output
                        json_str = json.dumps(output_data, indent=2)
                        st.download_button(
                            label="📄 Complete Output (JSON)",
                            data=json_str,
                            file_name=f"questions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json",
                            help="All questions with full metadata"
                        )
                    
                    with col2:
                        # By level (ZIP)
                        level_exports = export_by_level(output_data)
                        if level_exports:
                            # Create individual downloads
                            for level, data in level_exports.items():
                                json_str = json.dumps(data, indent=2)
                                st.download_button(
                                    label=f"📊 {level.title()} Questions",
                                    data=json_str,
                                    file_name=f"{level}_questions.json",
                                    mime="application/json",
                                    help=f"{data['total_questions']} {level} level questions"
                                )
                    
                    with col3:
                        # All formats (ZIP)
                        zip_buffer = create_download_zip(output_data)
                        st.download_button(
                            label="📦 All Formats (ZIP)",
                            data=zip_buffer,
                            file_name=f"questions_all_formats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                            mime="application/zip",
                            help="Complete package with all export formats"
                        )
                    
                    st.markdown("---")
                    
                    # Preview questions
                    st.subheader("👀 Preview Generated Questions")
                    
                    # Select concept to preview
                    concept_keys = list(output_data['concepts'].keys())
                    if concept_keys:
                        preview_concept = st.selectbox(
                            "Select concept to preview",
                            concept_keys,
                            format_func=lambda x: output_data['concepts'][x]['concept_name']
                        )
                        
                        preview_level = st.selectbox("Select level", ['beginner', 'intermediate', 'advanced'])
                        
                        concept_data = output_data['concepts'][preview_concept]
                        level_data = concept_data['levels'][preview_level]
                        
                        if level_data['questions']:
                            question = level_data['questions'][0]
                            
                            st.markdown(f"**Question Type:** {question.get('type', 'N/A')}")
                            st.markdown(f"**Question:** {question.get('question', question.get('title', 'N/A'))}")
                            
                            if question.get('options'):
                                st.markdown("**Options:**")
                                for key, value in question['options'].items():
                                    marker = "✅" if key == question.get('correct_answer') else "  "
                                    st.markdown(f"{marker} {key}. {value}")
                            
                            if question.get('explanation'):
                                st.markdown(f"**Explanation:** {question['explanation']}")
                            
                            # Show learning resources
                            if level_data.get('learning_resources'):
                                with st.expander("📚 Learning Resources"):
                                    for resource in level_data['learning_resources']:
                                        st.markdown(f"- [{resource['name']}]({resource['url']})")
                
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")
    
    with tab2:
        st.header("📖 How to Use This Tool")
        
        st.markdown("""
        ### Step-by-Step Instructions
        
        #### 1️⃣ Prepare Your Exit Ticket Data
        
        Create an Excel file with the following columns:
        
        | Column | Description | Example |
        |--------|-------------|---------|
        | Student_ID | Unique student identifier | S001 |
        | Question_ID | Question identifier | Q1 |
        | Student_Answer | What student answered | A |
        | Correct_Answer | The correct answer | B |
        | Concept | Topic being tested | Python Loops |
        | Question_Type | Type of question | MCQ |
        | Course_Category | "programming" or "non-programming" | programming |
        | Programming_Language | (Optional) Language name | python |
        
        #### 2️⃣ Upload Your File
        
        - Click "Browse files" or drag and drop
        - System validates your file automatically
        - Preview your data to ensure it's correct
        
        #### 3️⃣ Configure (Optional)
        
        - **Filter by Concept**: Generate questions for specific topics only
        - **Filter by Language**: For programming courses, focus on one language
        
        #### 4️⃣ Generate Questions
        
        - Click "Generate Questions" button
        - Wait while AI analyzes responses (1-10 minutes)
        - System creates questions at 3 difficulty levels
        
        #### 5️⃣ Download Results
        
        Choose your preferred format:
        - **Complete Output**: All questions with metadata
        - **By Level**: Separate files for beginner/intermediate/advanced
        - **All Formats (ZIP)**: Everything in one package
        
        #### 6️⃣ Upload to Your Platform
        
        - Open your LMS (Moodle, Canvas, etc.)
        - Import the JSON files
        - Assign to students based on their level
        
        ### Question Levels
        
        **Beginner**: Multiple choice questions testing basic understanding
        - Foundation building
        - Syntax and definitions
        - Need 3/4 correct to advance
        
        **Intermediate**: Code snippets and scenarios
        - Applied practice
        - Debugging and completion
        - Need 3/3 correct to advance
        
        **Advanced**: Full programming problems
        - Mastery level
        - Complete implementations
        - With test cases
        """)
    
    with tab3:
        st.header("❓ Frequently Asked Questions")
        
        with st.expander("What if my Excel file is rejected?"):
            st.markdown("""
            Make sure your Excel file has all required columns:
            - Student_ID
            - Question_ID
            - Student_Answer
            - Correct_Answer
            - Concept
            - Question_Type
            - Course_Category
            
            Programming_Language is optional but recommended for programming courses.
            """)
        
        with st.expander("How long does generation take?"):
            st.markdown("""
            - Small files (1-2 concepts): 1-2 minutes
            - Medium files (3-5 concepts): 3-5 minutes
            - Large files (6+ concepts): 5-10 minutes
            
            Time depends on number of concepts, not number of students.
            """)
        
        with st.expander("What if no questions are generated?"):
            st.markdown("""
            Questions are only generated for concepts where students made mistakes.
            
            If students answered everything correctly, no questions will be generated.
            
            Check that Student_Answer ≠ Correct_Answer for at least some rows.
            """)
        
        with st.expander("Can I generate questions multiple times?"):
            st.markdown("""
            Yes! Each time you generate:
            - Questions will be different (AI generates variations)
            - You can use filters to focus on specific concepts
            - All generations are independent
            """)
        
        with st.expander("What format are the downloaded files?"):
            st.markdown("""
            All files are in JSON format, which is:
            - Readable by humans
            - Compatible with most LMS platforms
            - Easy to parse programmatically
            - Standard industry format
            """)
        
        with st.expander("Is my data secure?"):
            st.markdown("""
            Yes! This tool:
            - Runs completely locally on your machine
            - Uses Ollama (local AI, not cloud)
            - Doesn't send data to external servers
            - Doesn't store data after generation
            """)
        
        with st.expander("How do I use the questions in my LMS?"):
            st.markdown("""
            Most LMS platforms (Moodle, Canvas, Blackboard) can import JSON:
            
            1. Download the JSON file
            2. In your LMS, go to Quiz/Assignment import
            3. Select JSON format
            4. Upload the file
            5. Configure quiz settings
            6. Assign to students
            
            See PLATFORM_UPLOAD_GUIDE.md for detailed instructions.
            """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>Adaptive Question Generator | Powered by Ollama | Open Source</p>
        <p>Made with ❤️ for Teachers</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    # Initialize session state
    if 'generated' not in st.session_state:
        st.session_state['generated'] = False
    
    main()

