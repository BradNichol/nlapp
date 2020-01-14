from flask import flash, redirect, render_template, request, url_for, Blueprint, jsonify
from app.models import Ingredient
from app import db
from app.utils import db_connect, serialize
from flask_login import login_required


ingredients = Blueprint('ingredients', __name__)

@ingredients.route("/ingredients", methods=["GET", "POST"])
@login_required
def showIngredients():

    """ Show all ingredients """

    product = Ingredient.query.all()
    return render_template("ingredients.html", ingredients=product)




@ingredients.route("/ingredients/new", methods=["POST"])
@login_required
def newIngredients():

    """ Add new ingredient """

    if request.method == "POST":

        # store ingredient data from form 
        name = request.form.get('ingredient')
        product_code = request.form.get('productcode')
        group = request.form.get('ingredientType')
        protein = request.form.get('protein')
        carbs = request.form.get('carbohydrates')
        sugars = request.form.get('sugars')
        fat = request.form.get('fats')
        saturates = request.form.get('saturates')
        fibre = request.form.get('fibre')
        salt = request.form.get('salt')
        sodium = request.form.get('sodium')

        #enter ingredient into database
        ingredient = Ingredient(name=name, product_code=product_code, group=group, protein=protein, carbohydrates=carbs, sugars=sugars, fats=fat, saturates=saturates, fibre=fibre, salt=salt, sodium=sodium )
        db.session.add(ingredient)
        db.session.commit()

        flash('Ingredient added')
        return redirect(url_for('ingredients.showIngredients'))


@ingredients.route("/ingredients/edit", methods=["GET", "POST"])
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



@ingredients.route("/ingredients/delete", methods=["POST"])
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