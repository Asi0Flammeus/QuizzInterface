from flask import Flask, render_template, request
import os
import yaml

app = Flask(__name__)

# Declare a global variable for the current question index
current_question_index = 0

def save_changes():
    """Save changes to the current YAML file."""
    global current_question_index, directorio_db, questions
    actual_yaml = os.path.join(directorio_db, questions[current_question_index])
    with open(actual_yaml, 'w') as w:
        new_data = {
            'course': request.form['course'],
            'section': request.form['section'],
            'chapter': request.form['chapter'],
            'difficulty': request.form['difficulty'],
            'duration': request.form['duration'],
            'author': request.form['author'],
            'tags': request.form.getlist('tag'),
            'question': request.form['question'],
            'answer': request.form['answer'],
            'wrong_answers': request.form.getlist('wrong_answer'),
            'explanation': request.form['explanation'],
            'reviewed': request.form.get('reviewed', 'False')
        }
        yaml.dump(new_data, w)

@app.route('/', methods=['GET', 'POST'])
def index():
    global current_question_index, directorio_db, questions

    directorio_db = "./db/questions/"
    questions = os.listdir(directorio_db)
    questions.sort()

    if request.method == 'POST':
        if request.form.get('button1'):  # Previous button
            save_changes()  # Save before moving
            current_question_index -= 1
            if current_question_index < 0:
                current_question_index = len(questions) - 1

        elif request.form.get('button2'):  # Next button
            save_changes()  # Save before moving
            current_question_index += 1
            if current_question_index >= len(questions):
                current_question_index = 0

        elif request.form.get('button3'):  # Save button
            save_changes()

    archivo_yaml = os.path.join(directorio_db, questions[current_question_index])
    with open(archivo_yaml, 'r') as f:
        data = yaml.safe_load(f)

    return render_template('review_question.html',
                           archivo_yaml=archivo_yaml,
                           course=data['course'],
                           section=data['section'],
                           chapter=data['chapter'],
                           difficulty=data['difficulty'],
                           duration=data['duration'],
                           author=data['author'],
                           tags=data['tags'],
                           question=data['question'],
                           answer=data['answer'],
                           wrong_answers=data['wrong_answers'],
                           explanation=data['explanation'],
                           reviewed=data['reviewed']
                           )

if __name__ == '__main__':
    app.run(debug=True)

