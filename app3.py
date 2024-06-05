from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_sse import sse

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Definição do modelo User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Rotas de autenticação e cadastro de usuários

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(username=data['username'], email=data['email'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created successfully."}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        return jsonify({"message": "Login successful."}), 200
    else:
        return jsonify({"message": "Invalid credentials."}), 401

# Rota para página de notificações SSE
@app.route('/notifications')
def notifications():
    return render_template('notifications.html')

# Emitir notificações SSE
@app.route('/send_notification')
def send_notification():
    notification_message = request.args.get('message')
    sse.publish({"message": notification_message}, type='notification')
    return jsonify({"message": "Notification sent."}), 200

if __name__ == '__main__':
    with app.app_context():
        # Aqui está dentro do contexto da aplicação Flask
        db.create_all()
    app.run(debug=True)
