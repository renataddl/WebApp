from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

# Inicializa o aplicativo Flask
app = Flask(__name__)

# Configura o banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

# Inicializa as extensões do Flask
db = SQLAlchemy(app)  # SQLAlchemy para ORM (Object-Relational Mapping)
bcrypt = Bcrypt(app)  # Bcrypt para hash de senhas

# Definição do modelo User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Coluna ID, chave primária
    username = db.Column(db.String(50), unique=True, nullable=False)  # Coluna username, única e não nula
    email = db.Column(db.String(100), unique=True, nullable=False)  # Coluna email, única e não nula
    password = db.Column(db.String(100), nullable=False)  # Coluna password, não nula

# Rota para cadastro de usuários
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json  # Obtém os dados JSON do corpo da requisição
    # Gera o hash da senha
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    # Cria uma nova instância de User
    new_user = User(username=data['username'], email=data['email'], password=hashed_password)
    # Adiciona o novo usuário à sessão do banco de dados
    db.session.add(new_user)
    # Confirma a transação
    db.session.commit()
    # Retorna uma resposta de sucesso
    return jsonify({"message": "User created successfully."}), 201

# Rota para login de usuários
@app.route('/login', methods=['POST'])
def login():
    data = request.json  # Obtém os dados JSON do corpo da requisição
    # Consulta o usuário pelo email
    user = User.query.filter_by(email=data['email']).first()
    # Verifica se o usuário existe e se a senha está correta
    if user and bcrypt.check_password_hash(user.password, data['password']):
        # Retorna uma resposta de sucesso
        return jsonify({"message": "Login successful."}), 200
    else:
        # Retorna uma resposta de credenciais inválidas
        return jsonify({"message": "Invalid credentials."}), 401

# Bloco de inicialização da aplicação
if __name__ == '__main__':
    with app.app_context():
        # Cria as tabelas no banco de dados, se ainda não existirem
        db.create_all()
    # Executa o aplicativo Flask no modo de depuração
    app.run(debug=True)
