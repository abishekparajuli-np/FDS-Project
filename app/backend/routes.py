from flask import jsonify, Blueprint

main = Blueprint('main',__name__)

@main.route('/')
@main.route('/home')
def home():
    return jsonify

@main.route('/about')
def about():
    return jsonify

@main.route('/detector',methods=['POST','GET'])
def detector():
    return jsonify


    