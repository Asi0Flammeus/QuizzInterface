from flask import Flask, render_template, request
import os
import yaml

app = Flask(__name__)

# Declare a global variable for the current question index
QUESTION_INDEX = 0

def save_changes():
    """Save changes to the current YAML file."""
    global QUESTION_INDEX, quizz_directory, questions
    yaml_path = os.path.join(quizz_directory, questions[QUESTION_INDEX])
    with open(yaml_path, 'w') as w:
        new_data = {
            'course': request.form['course'],
            'part': int(request.form['part']),
            'chapter': int(request.form['chapter']),
            'difficulty': request.form['difficulty'],
            'duration': int(request.form.get('duration', '15')),
            'author': request.form['author'],
            'tags': request.form.getlist('tag'),
            'question': request.form['question'],
            'answer': request.form['answer'],
            'wrong_answers': request.form.getlist('wrong_answer'),
            'explanation': request.form['explanation'],
            'reviewed': request.form.get('reviewed') == 'True'
        }
        yaml.dump(new_data, w, default_flow_style=False, indent=2)

@app.route('/', methods=['GET', 'POST'])
def index():
    global QUESTION_INDEX, quizz_directory, questions

    quizz_directory = "./questions/"
    questions = os.listdir(quizz_directory)
    questions.sort()

    if request.method == 'POST':
        if request.form.get('button1'):  # Previous button
            save_changes()
            QUESTION_INDEX -= 1
            if QUESTION_INDEX < 0:
                QUESTION_INDEX = len(questions) - 1

        elif request.form.get('button2'):  # Next button
            save_changes()
            QUESTION_INDEX += 1
            if QUESTION_INDEX >= len(questions):
                QUESTION_INDEX = 0

        elif request.form.get('button3'):  # Save button
            save_changes()

    yaml_path = os.path.join(quizz_directory, questions[QUESTION_INDEX])
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)

    return render_template('review_question.html',
                           QUESTION_INDEX=QUESTION_INDEX,
                           course=data['course'],
                           part=data['part'],
                           chapter=data['chapter'],
                           difficulty=data['difficulty'],
                           duration=int(data['duration']),
                           author=data['author'],
                           tags=data['tags'],
                           question=data['question'],
                           answer=data['answer'],
                           wrong_answers=data['wrong_answers'],
                           explanation=data['explanation'],
                           reviewed=bool(data['reviewed'])
                           )

if __name__ == '__main__':
    app.run(debug=True)

