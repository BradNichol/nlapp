from flask import flash, redirect, render_template, request, url_for, Blueprint, jsonify
from app.models import Product, Customer, Recipes
from app import db
from app.utils import db_connect, serialize
from flask_login import login_required


products = Blueprint('products', __name__, template_folder='templates')

@products.route("/products", methods=["GET", "POST"])
@login_required
def showproducts():

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
        customer_id = request.form.get('customer_id')
        recipe_id = request.form.get('recipe_id')
        run_rate = request.form.get('run_rate')

        addProduct = Product(product_sku=product_sku, customer_id=customer_id, recipe_id=recipe_id, run_rate=run_rate)
        db.session.add(addProduct)
        db.session.commit()

        flash('Product added')
        return redirect(url_for('products.showproducts'))


@products.route("/products/edit", methods=["GET", "POST"])
@login_required
def edit():
    """ Update Ingredients """
    
    if request.method == "POST":
        
        # get id and name for ingredient
        pid = request.form.get('id')
        name = request.form.get('product_name')
        protein = request.form.get('editProtein')
        carbs = request.form.get('editCarbs')
        sugars = request.form.get('editSugars')
        fat = request.form.get('editFats')
        saturates = request.form.get('editSaturates')
        fibre = request.form.get('editFibre')
        salt = request.form.get('editSalt')
        sodium = request.form.get('editSodium')

        # update ingredient
        con = db_connect()
        cur = con.cursor()
        sql = """UPDATE ingredients SET name=?, protein=?, carbohydrates=?, sugars=?, fats=?, saturates=?, fibre=?, salt=?, sodium=? WHERE id=?"""

        cur.execute(sql, (name, protein, carbs, sugars, fat, saturates, fibre, salt, sodium, pid ))
        con.commit()
        con.close()

        return redirect(url_for('ingredients.showIngredients'))

    # returns JSON data to display the correct ingredient that user wants to edit on modal
    elif request.method == "GET":
        
        product_code = request.args.get("product_code")
        con = db_connect()
        cur = con.cursor()
        cur.execute("SELECT * FROM ingredients WHERE product_code = :product_code", {'product_code': product_code})
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