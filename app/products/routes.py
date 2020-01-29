from flask import flash, redirect, render_template, request, url_for, Blueprint, jsonify
from app.models import Product, Customer, Recipes
from app import db
from app.utils import db_connect, serialize
from flask_login import login_required


products = Blueprint('products', __name__, template_folder='templates')

@products.route("/products", methods=["GET", "POST"])
@login_required
def viewproducts():

    """ Show all produicts """

    products = Product.query.all()
    customers = Customer.query.all()
    recipes = Recipes.query.filter_by(approved=1).all()

    return render_template("products.html", products=products, customers=customers, recipes=recipes)




@products.route("/products/add", methods=["POST"])
@login_required
def addproduct():

    """ Add new product """

    if request.method == "POST":

        # store product data from form 
        product_sku = request.form.get('product_sku')
        product_name = request.form.get('product_name')
        customer_id = request.form.get('customer_id')
        recipe_id = request.form.get('recipe_id')
        run_rate = request.form.get('run_rate')

        addProduct = Product(product_sku=product_sku, product_name=product_name, customer_id=customer_id, recipe_id=recipe_id, run_rate=run_rate)
        db.session.add(addProduct)
        db.session.commit()

        flash('Product added')
        return redirect(url_for('products.viewproducts'))


@products.route("/products/edit", methods=["GET", "POST"])
@login_required
def edit():
    """ Update Product """
    
    if request.method == "POST":
        
        # get id and name for product
        pid = request.form.get('id')
        product_sku = request.form.get('editProductSku')
        customer_id = request.form.get('editCustomerId')
        recipe_id = request.form.get('editRecipeId')
        run_rate = request.form.get('editRunRate')


        # update product
        product = Product.query.filter_by(id=pid).first()
        product.product_sku = product_sku
        product.customer_id = customer_id
        product.recipe_id = recipe_id
        product.run_rate = run_rate
        db.session.commit()

        flash('Successful. Product updated.')
        return redirect(url_for('products.viewproducts'))

    # returns JSON data to display the correct ingredient that user wants to edit on modal
    elif request.method == "GET":
        
        id = request.args.get("id")
        con = db_connect()
        cur = con.cursor()
        cur.execute("SELECT * FROM products WHERE id = :id", {'id': id})
        result = cur.fetchall()

        return jsonify(serialize(cur, result))



@products.route("/ingredients/delete", methods=["POST"])
@login_required
def deleteIngredient():

    """ Delete ingredient 
    
    Not implemented yet. Need to consider ramifications of 
    deleting product linked to other areas (i.e. stock, recipes etc)
    
    """
    
    if request.method == "POST":
        
        id = request.form.get('id')

        con = db_connect()
        cur = con.cursor()
        cur.execute("DELETE FROM ingredients WHERE id = :id ", {'id': id})
        con.commit()
        con.close()

        flash('Ingredient deleted')
        return redirect(url_for('ingredients.showIngredients'))