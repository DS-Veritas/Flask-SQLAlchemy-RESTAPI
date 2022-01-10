from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

# Init app
app = Flask(__name__)

# To make sure that we can correctly locate the database file
basedir = os.path.abspath(os.path.dirname(__file__))

# Set up database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Initialize Marshmallow
ma = Marshmallow(app)

# Product Class / Model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(200))
    price = db.Column(db.Float)
    qty = db.Column(db.Integer)

    # id will be assigned automatically in an increasing order
    def __init__(self, name, description, price, qty):
        self.name = name
        self.description = description
        self.price = price
        self.qty = qty

# Product Schema
class ProductSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'description', 'price', 'qty')

# Initialize the Schema
product_schema = ProductSchema()
# To handle multiple products (Have to be distinguished)
products_schema = ProductSchema(many=True)

# Create a Product
@app.route('/product', methods=['POST'])
def add_product():
    name = request.json['name']
    description = request.json['description']
    price = request.json['price']
    qty = request.json['qty']

    # Turn received json information into the Product class
    new_product = Product(name, description, price, qty)

    # Add created Product class into db (SQLAlchemy) 
    db.session.add(new_product)
    # To apply (save) the change, we need to commit
    db.session.commit()
    
    # Since it is dealing with a single item, we use product_schema
    # So, when the user post the product, it returns the information about the created product
    return product_schema.jsonify(new_product)

# Get All Products
@app.route('/product', methods=['GET'])
def get_products():
    # Since the class is using SQLAlchemy db.model, we can use .query.all()
    # , which returns all objects belong to the Product class 
    all_products = Product.query.all()
    result = products_schema.dump(all_products)
    # No longer need to use 'result.data'
    return jsonify(result)

# Get single Products
@app.route('/product/<id>', methods=['GET'])
def get_product(id):
    # Since the class is using SQLAlchemy db.model, we can use .query.all()
    # , which returns all objects belong to the Product class 
    product = Product.query.get(id)
    # No longer need to use 'result.data'
    return product_schema.jsonify(product)

# Update a Product (PUT Request is used for an update)
@app.route('/product/<id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get(id)

    name = request.json['name']
    description = request.json['description']
    price = request.json['price']
    qty = request.json['qty']

    product.name = name
    product.description = description
    product.price = price
    product.qty = qty

    # For an update, we don't need to add. Just commit. 
    db.session.commit()
    
    # Since it is dealing with a single item, we use product_schema
    # So, when the user post the product, it returns the information about the created product
    return product_schema.jsonify(product)

# Delete single Products
@app.route('/product/<id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get(id)
    db.session.delete(product)
    
    # Make sure to commit after delete
    db.session.commit()

    return product_schema.jsonify(product)

"""
@app.route('/', methods=['Get'])
def get():
    return jsonify({'msg': 'Hello World'})
"""

# Run Server
if __name__ == '__main__':
    # This is same as "flask run" in the command line
    app.run(debug=True)