from flask import Flask, render_template, request
import os
import yaml
from pathlib import Path

app = Flask(__name__)

# Global variables
QUESTION_INDEX = 0
QUIZZ_DIRECTORY = None
questions = []

def get_available_courses():
    """Get list of available courses from the bitcoin-educational-content directory."""
    try:
        current_dir = Path(__file__).resolve().parent
        courses_dir = current_dir.parent / "bitcoin-educational-content" / "courses"
        print(f"Looking for courses in: {courses_dir}")
        
        if not courses_dir.exists():
            raise FileNotFoundError(f"Courses directory not found at: {courses_dir}")
        
        available_courses = []
        for course_dir in courses_dir.iterdir():
            quizz_dir = course_dir / "quizz"
            if course_dir.is_dir() and quizz_dir.exists() and any(quizz_dir.iterdir()):
                available_courses.append(course_dir.name)
        
        if not available_courses:
            raise FileNotFoundError("No courses with quiz content found")
        
        return sorted(available_courses), str(courses_dir)
    
    except Exception as e:
        print(f"Error in get_available_courses: {str(e)}")
        raise

def get_question_dirs(quizz_dir):
    """Get sorted list of question directories (001, 002, etc.)"""
    try:
        quizz_path = Path(quizz_dir)
        question_dirs = []
        
        for item in quizz_path.iterdir():
            if item.is_dir() and item.name.isdigit():
                # Verify that required files exist
                if (item / "en.yml").exists() and (item / "question.yml").exists():
                    question_dirs.append(item)
        
        return sorted(question_dirs, key=lambda x: int(x.name))
    
    except Exception as e:
        print(f"Error in get_question_dirs: {str(e)}")
        raise

def load_yaml_file(file_path):
    """Safely load a YAML file with error handling."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                print(f"Warning: {file_path} is empty")
                return {}
            
            data = yaml.safe_load(content)
            return data if data is not None else {}
            
    except yaml.YAMLError as e:
        print(f"YAML Error in {file_path}:")
        print(f"Content:\n{content}")
        print(f"Error: {str(e)}")
        raise
    except Exception as e:
        print(f"Error reading {file_path}: {str(e)}")
        raise

def load_question_data(question_dir):
    """Load and merge data from en.yml and question.yml files."""
    try:
        # Load metadata from question.yml
        question_path = question_dir / "question.yml"
        question_data = load_yaml_file(question_path)
        
        # Load content from en.yml
        en_path = question_dir / "en.yml"
        en_data = load_yaml_file(en_path)
        
        # Merge data
        data = {
            'id': question_data.get('id', ''),
            'chapterId': question_data.get('chapterId', ''),
            'difficulty': question_data.get('difficulty', ''),
            'duration': question_data.get('duration', 15),
            'author': question_data.get('author', ''),
            'tags': question_data.get('tags', []),
            'question': en_data.get('question', ''),
            'answer': en_data.get('answer', ''),
            'wrong_answers': en_data.get('wrong_answers', []),
            'explanation': en_data.get('explanation', '').strip(),
            'reviewed': en_data.get('reviewed', False)
        }
        
        return data
        
    except Exception as e:
        print(f"Error loading question data from {question_dir}: {str(e)}")
        raise

def read_file_lines(file_path):
    """Read file lines while preserving exact format."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read().splitlines()

def format_explanation(text):
    """Format explanation text with manual line wrapping and indentation."""
    words = text.strip().split()
    lines = []
    current_line = []
    current_count = 0
    
    for word in words:
        if current_count + len(word) + 1 <= 60:
            current_line.append(word)
            current_count += len(word) + 1
        else:
            lines.append("  " + " ".join(current_line))
            current_line = [word]
            current_count = len(word) + 1
    
    if current_line:
        lines.append("  " + " ".join(current_line))
    
    return "|\n" + "\n".join(lines)

def save_question_data(question_dir, form_data):
    """Save form data while preserving file structure and order."""
    try:
        question_path = question_dir / "question.yml"
        en_path = question_dir / "en.yml"
        
        # Load current content preserving format
        current_question_lines = read_file_lines(question_path)
        current_en_lines = read_file_lines(en_path)
        
        # Load data for comparison
        with open(question_path, 'r', encoding='utf-8') as f:
            current_question_data = yaml.safe_load(f) or {}
        with open(en_path, 'r', encoding='utf-8') as f:
            current_en_data = yaml.safe_load(f) or {}

        # Track changes for each field
        field_changed = {
            'question': False,
            'answer': False,
            'wrong_answers': False,
            'explanation': False,
            'reviewed': False
        }
        
        # Pre-check which fields have actually changed
        if form_data.get('question') and form_data.get('question') != current_en_data.get('question'):
            field_changed['question'] = True
            
        if form_data.get('answer') and form_data.get('answer') != current_en_data.get('answer'):
            field_changed['answer'] = True
            
        new_wrong_answers = [wa for wa in form_data.getlist('wrong_answer') if wa.strip()]
        if new_wrong_answers != current_en_data.get('wrong_answers'):
            field_changed['wrong_answers'] = True
            
        new_explanation = form_data.get('explanation', '').strip()
        if new_explanation and new_explanation != current_en_data.get('explanation', '').strip():
            field_changed['explanation'] = True
            
        new_reviewed = form_data.get('reviewed') == 'True'
        if new_reviewed != current_en_data.get('reviewed'):
            field_changed['reviewed'] = True

        # Update question.yml while preserving order
        question_changed = False
        new_question_lines = []
        i = 0
        while i < len(current_question_lines):
            line = current_question_lines[i]
            
            if line.startswith('id:') or line.startswith('chapterId:'):
                new_question_lines.append(line)
                
            elif line.startswith('difficulty:') and 'difficulty' in form_data:
                new_value = form_data.get('difficulty')
                if new_value and new_value != current_question_data.get('difficulty'):
                    line = f'difficulty: {new_value}'
                    question_changed = True
                new_question_lines.append(line)
                
            elif line.startswith('duration:'):
                new_value = form_data.get('duration')
                if new_value and int(new_value) != current_question_data.get('duration'):
                    line = f'duration: {new_value}'
                    question_changed = True
                new_question_lines.append(line)
                
            elif line.startswith('author:') and 'author' in form_data:
                new_value = form_data.get('author')
                if new_value and new_value != current_question_data.get('author'):
                    line = f'author: {new_value}'
                    question_changed = True
                new_question_lines.append(line)
                
            elif line.startswith('tags:'):
                new_tags = form_data.getlist('tag')
                current_tags = current_question_data.get('tags', [])
                
                if new_tags and new_tags != current_tags:
                    question_changed = True
                    new_question_lines.append('tags:')
                    for tag in new_tags:
                        if tag.strip():
                            new_question_lines.append(f'  - {tag}')
                    while i + 1 < len(current_question_lines) and current_question_lines[i + 1].startswith('  -'):
                        i += 1
                else:
                    new_question_lines.append(line)
                    while i + 1 < len(current_question_lines) and current_question_lines[i + 1].startswith('  -'):
                        i += 1
                        new_question_lines.append(current_question_lines[i])
            else:
                new_question_lines.append(line)
            i += 1

        # Update en.yml while preserving order
        new_en_lines = []
        i = 0
        while i < len(current_en_lines):
            line = current_en_lines[i]
            
            if line.startswith('question:'):
                if field_changed['question']:
                    line = f'question: {form_data.get("question")}'
                new_en_lines.append(line)
            
            elif line.startswith('answer:'):
                if field_changed['answer']:
                    line = f'answer: {form_data.get("answer")}'
                new_en_lines.append(line)
            
            elif line.startswith('explanation:'):
                if field_changed['explanation']:
                    line = 'explanation: ' + format_explanation(new_explanation)
                    new_en_lines.append(line)
                    # Skip existing explanation lines
                    while i + 1 < len(current_en_lines) and (
                        current_en_lines[i + 1].startswith('  ') or 
                        current_en_lines[i + 1].startswith(' |')):
                        i += 1
                else:
                    # Keep original explanation format
                    new_en_lines.append(line)
                    while i + 1 < len(current_en_lines) and (
                        current_en_lines[i + 1].startswith('  ') or 
                        current_en_lines[i + 1].startswith(' |')):
                        i += 1
                        new_en_lines.append(current_en_lines[i])
            
            elif line.startswith('reviewed:'):
                if field_changed['reviewed']:
                    line = f'reviewed: {str(new_reviewed).lower()}'
                new_en_lines.append(line)
            
            elif line.startswith('wrong_answers:'):
                if field_changed['wrong_answers']:
                    new_en_lines.append('wrong_answers:')
                    for answer in new_wrong_answers:
                        new_en_lines.append(f'  - {answer}')
                    while i + 1 < len(current_en_lines) and current_en_lines[i + 1].startswith('  -'):
                        i += 1
                else:
                    new_en_lines.append(line)
                    while i + 1 < len(current_en_lines) and current_en_lines[i + 1].startswith('  -'):
                        i += 1
                        new_en_lines.append(current_en_lines[i])
            else:
                new_en_lines.append(line)
            i += 1

        # Save files only if changed
        if question_changed:
            print(f"Saving changes to question.yml in {question_dir}")
            with open(question_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_question_lines) + '\n')
        
        if any(field_changed.values()):
            print(f"Saving changes to en.yml in {question_dir}")
            with open(en_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_en_lines) + '\n')
        
        if not any(field_changed.values()) and not question_changed:
            print("No changes detected, skipping file updates")
            
    except Exception as e:
        print(f"Error saving question data to {question_dir}: {str(e)}")
        raise

def initialize_quizz_directory():
    """Prompt user to select a course and initialize the quiz directory."""
    try:
        available_courses, courses_base_path = get_available_courses()
        
        print("\nAvailable courses:")
        for idx, course in enumerate(available_courses, 1):
            print(f"{idx}. {course}")
        
        while True:
            try:
                selection = input("\nSelect a course number: ")
                course_idx = int(selection) - 1
                if 0 <= course_idx < len(available_courses):
                    selected_course = available_courses[course_idx]
                    break
                print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
        
        quizz_path = Path(courses_base_path) / selected_course / "quizz"
        print(f"\nUsing quiz directory: {quizz_path}\n")
        
        return str(quizz_path)
        
    except Exception as e:
        print(f"Error in initialize_quizz_directory: {str(e)}")
        raise

@app.route('/', methods=['GET', 'POST'])
def index():
    global QUESTION_INDEX, QUIZZ_DIRECTORY, questions
    
    try:
        # Initialize quiz directory if needed
        if QUIZZ_DIRECTORY is None:
            QUIZZ_DIRECTORY = initialize_quizz_directory()
            questions = get_question_dirs(QUIZZ_DIRECTORY)
            
            if not questions:
                return "No question directories found in the selected course", 404
        
        # Handle form submissions
        if request.method == 'POST':
            current_dir = questions[QUESTION_INDEX]
            
            if request.form.get('button1'):  # Previous
                save_question_data(current_dir, request.form)
                QUESTION_INDEX = (QUESTION_INDEX - 1) % len(questions)
            elif request.form.get('button2'):  # Next
                save_question_data(current_dir, request.form)
                QUESTION_INDEX = (QUESTION_INDEX + 1) % len(questions)
            elif request.form.get('button3'):  # Save
                save_question_data(current_dir, request.form)
        
        # Load and display current question
        current_dir = questions[QUESTION_INDEX]
        data = load_question_data(current_dir)
        
        # Debug information
        print(f"\nLoading question from: {current_dir}")
        print(f"Loaded data: {data}")
        
        return render_template('review_question.html',
                              QUESTION_INDEX=QUESTION_INDEX,
                              chapterId=data['chapterId'],
                              difficulty=str(data['difficulty']),
                              duration=int(data['duration']),
                              author=data['author'],
                              tags=data['tags'],
                              question=data['question'],
                              answer=data['answer'],
                              wrong_answers=data['wrong_answers'],
                              explanation=data['explanation'],
                              reviewed=bool(data['reviewed']))
                             
    except Exception as e:
        error_msg = f"Application error: {str(e)}"
        print(error_msg)
        return error_msg, 500

if __name__ == '__main__':
    app.run(debug=True)
