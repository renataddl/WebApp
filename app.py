from flask import Flask, make_response, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import base64

from appdb import Produtos
from appdb import Cart

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Chave pública para verificação de assinatura
PUBLIC_KEY = """-----BEGIN RSA PUBLIC KEY-----
MIGJAoGBAKoYpQoNg/wuAPi1gitHVEaRONG/HHtEvZI9sjJJTyVd7EHYaH9z4YXJ
Z3gpfKomi3wqOf5ZPRrHiWDknFFSedwfSMGzeYYw0/lSmdBjJ7Quq1cmtRsV+dPp
nXSn7zwOVAKGMxcPZGctnAgOMTRfirikBu
-----END RSA PUBLIC KEY-----"""

def verify_signature(data, signature):
    # Decode the base64 signature
    signature_bytes = base64.b64decode(signature)
    
    # Create a hash object
    hash_obj = SHA256.new(data.encode())
    
    # Load the public key
    public_key = RSA.import_key(PUBLIC_KEY)
    
    # Create a signature object
    verifier = pkcs1_15.new(public_key)
    
    # Verify the signature
    try:
        verifier.verify(hash_obj, signature_bytes)
        return True
    except (ValueError, TypeError):
        return False

@app.route('/', methods=['GET'])
def get_produtos():
    return make_response(jsonify(
        message='Lista de produtos',
        products=Produtos), 200
    )

@app.route('/cart', methods=['GET'])
def get_carrinho():
    return make_response(jsonify(
        message='Lista de produtos no carrinho',
        products=Cart), 200)

@app.route('/cart', methods=['POST'])
def add_carrinho():
    id_produto = request.json['id']
    produto = None

    for p in Produtos:
        if p['id'] == id_produto:
            produto = {
                'id_produto': p['id'],
                'name': p['name'],
                'price': p['price'],
                'image': p['image']
            }
            break

    if produto is not None:
        produto['id'] = 1 if len(Cart) == 0 else Cart[len(Cart) - 1]['id'] + 1
        Cart.append(produto)
        return make_response(jsonify(
            message='Produto adicionado no carrinho',
            product=produto), 200)

    return make_response(jsonify(message='Produto não encontrado'), 404)

@app.route('/cart/<id>', methods=["DELETE"])
def del_carrinho(id):
    id_produto_carrinho = int(id)
    produto = None

    for p in Cart:
        if p['id'] == id_produto_carrinho:
            produto = p
            break

    if produto is not None:
        Cart.remove(produto)
        return make_response(jsonify(
            message='Produto removido do carrinho',
            product=produto), 201)

    return make_response(jsonify(message='Produto não encontrado'), 200)

@socketio.on("add_cart")
def handle_message(data):
    product = data.get("product")
    emit("cart", {"product": product}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)