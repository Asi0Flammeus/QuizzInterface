from flask import Flask, render_template, Response, request
import os
import yaml

app = Flask(__name__)

# Declarar una variable global para el índice de la pregunta actual
current_question_index = 0

@app.route('/', methods=['GET', 'POST'])
def index():
    directorio_db = "./db/questions/"
    questions = os.listdir(directorio_db)
    questions.sort()

    # Verificar si se ha presionado el botón 2 y actualizar el índice
    if request.method == 'POST':
        if request.form.get('button1'):
            print('Previous')
            global current_question_index
            current_question_index -= 1
            # Asegurarse de no superar los límites de la lista
            if current_question_index == 0:
                current_question_index = 0
        elif request.form.get('button2'):
            print('Next')
            current_question_index
            current_question_index += 1
            # Asegurarse de no superar los límites de la lista
            if current_question_index >= len(questions):
                current_question_index = 0
        elif request.form.get('button3'):
            print('Save')
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
                    'wrong_answers': request.form.getlist('wrong_answer'),  # Obtener una lista de valores
                    'explanation': request.form['explanation'],
                    'reviewed': request.form['reviewed']
                }
                yaml.dump(new_data, w)
               

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
                           questions=questions,
                           answer=data['answer'],
                           wrong_answers=data['wrong_answers'],
                           explanation=data['explanation'],
                           reviewed=data['reviewed']
                           )

if __name__ == '__main__':
    app.run(debug=True)
