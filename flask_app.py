from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from pymongo import MongoClient
import bcrypt
from expert import *
from expert import PsychologicalAssessment

app = Flask(__name__)
app.secret_key = 'your_secret_key'
client = MongoClient('mongodb+srv://admin:admin@cluster0.jjgbu2m.mongodb.net/')
db = client['ChatBot']
collection = db['chats']
users_collection = db['user']
users = {}
session={}
expert = PsychologicalAssessment(model)

def generate_password_hash(password):
    """Genera un hash de la contraseña"""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def check_password_hash(hashed_password, password):
    """Verifica que la contraseña coincide con el hash almacenado"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = users_collection.find_one({'username': username})

        if user  and check_password_hash(user['password'], password):
            session['username']=username
            print(session['username'])
            return redirect(url_for('chat'))
        else:
            flash('Nombre de usuario o contraseña incorrectos')
            return redirect(url_for('login'))
        
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Validar si el usuario ya existe
        existing_user = users_collection.find_one({'username': username})
        if existing_user:
            flash('El nombre de usuario ya está en uso')
            return redirect(url_for('signup'))

        else:
            hashed_password = generate_password_hash(password)
            users_collection.insert_one({
                'username': username,
                'password': hashed_password,
                'chats': []
            })
            flash('Registro exitoso. Ahora puedes iniciar sesión.')
            return redirect(url_for('login'))   

    return render_template('signup.html')

@app.route('/chat')
def chat():
    user = users_collection.find_one({'username': session['username']})
    chats = user.get('chats', [])
    data = {'userName': session['username'], 'chats': chats}
    return render_template('chat.html', data=data)

@app.route('/chat-messages', methods=['POST'])
def chatMessages():
    '''
    interaction with the expert here
    '''
    user_message = request.form['message']
    lista_strings = user_message.split(',')

    # Convertir la lista de strings a una lista de enteros
    lista_enteros = [int(numero) for numero in lista_strings]

    user_sleep_quality_input = lista_enteros[0]
    user_depression_level_input = lista_enteros[1]
    user_stress_level_input = lista_enteros[2]
    user_anxiety_level_input = lista_enteros[3]

    if user_sleep_quality_input > 6:
        user_sleep_case = 2
    elif user_sleep_quality_input > 3:
        user_sleep_case = 1
    else:
        user_sleep_case = 0

    if user_depression_level_input > 6:
        user_depression_case = 2
    elif user_depression_level_input > 3:
        user_depression_case = 1
    else:
        user_depression_case = 0

    if user_stress_level_input > 6:
        user_stress_case = 2
    elif user_stress_level_input > 3:
        user_stress_case = 1
    else:
        user_stress_case = 0

    if user_anxiety_level_input > 6:
        user_anxiety_case = 2
    elif user_anxiety_level_input > 3:
        user_anxiety_case = 1
    else:
        user_anxiety_case = 0
    print(lista_enteros)
    evidence ={
      'Anxiety': user_anxiety_case,
      'Depression': user_depression_case, 
      'Stress': user_stress_case,  
      'SleepProblems': user_sleep_case,  
    }
    psychological_Issue_probability = inference.query(variables=['PsychologicalIssue'], evidence=evidence)

    expert = PsychologicalAssessment(model)
    expert.reset()
    expert.declare(Fact(sleep_quality=user_sleep_quality_input))
    expert.declare(Fact(depression_level=user_depression_level_input))
    expert.declare(Fact(stress_level=user_stress_level_input))
    expert.declare(Fact(anxiety_level=user_anxiety_level_input))
    expert.declare(Fact(psycological_issue_probability=psychological_Issue_probability))
    expert.run()
    
    responses=expert.get_responses()
    mensaje_con_bot="aaa"
    print(mensaje_con_bot)
    bot_response = f"{mensaje_con_bot}"
    general_response=[]
    documento = {
        'usuario': user_message,
        'bot': bot_response
    }
    user = users_collection.find_one({'username': session['username']})     
    if user:
        for res in responses:
            new_message_id = len(user['chats']) + 1

            new_message = {
                'id': new_message_id,
                'usuario': user_message,
                'bot': res
            }
            
            users_collection.update_one(
                {'username': session['username']},
                {
                    '$push': {'chats': new_message},
                    '$inc': {'message_count': 1} 
                }
            )
            
    result = collection.insert_one(documento)

    return jsonify({'response': responses})

if __name__ == "__main__":
    app.run(debug=True)