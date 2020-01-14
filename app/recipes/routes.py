from flask import flash, redirect, render_template, request, url_for, Blueprint, jsonify
from app import db
from app.models import Recipes, Ingredient, Customer
from app.utils import db_connect, serialize
from flask_login import login_required


recipes = Blueprint('recipes', __name__, template_folder='templates')


@recipes.route("/recipes/view")
@login_required
def viewRecipes():

    """ View all recipes """

    viewAll = Recipes.query.group_by('rname', 'version_number').all()
    return render_template("recipes.html", recipe=viewAll)


@recipes.route("/recipes/create", methods=["GET", "POST"])
@login_required
def createRecipe():

    """ Create a recipe """

    ingredients = Ingredient.query.with_entities(Ingredient.name, Ingredient.product_code)
    customers = Customer.query.with_entities(Customer.cname, Customer.id)
    
    return render_template('recipebuilder.html', ingredients=ingredients, customers=customers)


@recipes.route("/recipes/add", methods=["GET", "POST"])
@login_required
def addRecipe():


    """ Add recipe to database """

    rname = request.form.get('rname')
    customer_id = request.form.get('customer_id')
    flavour = request.form.get('flavour')
    bar_weight = request.form.get('bar_weight')
    ingredient_id = request.form.getlist('product_code')
    ingredient_amount = request.form.getlist('ingredient_amount')

    # For incrementing version number when user duplicates recipe or setting at 1 for new recipes
    con = db_connect()
    cur = con.cursor()
    cur.execute('SELECT MAX(version_number) AS version_number FROM recipes WHERE rname=:rname', {'rname':rname})
    maxVersion = cur.fetchall()

    if maxVersion[0]['version_number'] == None:
        version_number = 1

        sql = """INSERT INTO recipes (rname, customer_id, flavour, bar_weight, 
                version_number, ingredient_id, ingredient_amount) VALUES (?, ?, ?, ?, ?, ?, ?/100.0)"""
    
    else:
        version_number = maxVersion[0]['version_number'] + 1

        sql = """INSERT INTO recipes (rname, customer_id, flavour, bar_weight, 
                version_number, ingredient_id, ingredient_amount) VALUES (?, ?, ?, ?, ?, ?, ?)"""
    
    
    
    # adding multiple ingredients into database
    query_args = []
    for ind, ingredient in enumerate(ingredient_id):
        data = (rname, customer_id, flavour, bar_weight, version_number, ingredient, ingredient_amount[ind])
        query_args.append(data)
    
    
    cur.executemany(sql, query_args)
    con.commit()
    con.close()
    
    flash('Recipe successfully added')
    return redirect(url_for('recipes.recipesoverview', rname=rname, version_number=version_number))



@recipes.route("/recipes/overview/<path:rname>/<int:version_number>", methods=["GET", "POST"])
@login_required
def recipesoverview(rname, version_number):

    """ viewing recipe details """

    con = db_connect()
    cur = con.cursor()
    cur.execute("""SELECT *, round(protein*ingredient_amount, 2) AS SubTotalProtein, 
                        round(carbohydrates*ingredient_amount, 2) AS SubTotalCarbohydrates,
                        round(sugars*ingredient_amount, 2) AS SubTotalSugars, 
                        round(fats*ingredient_amount, 2) AS SubTotalFats, 
                        round(saturates*ingredient_amount, 2) AS SubTotalSaturates, 
                        round(fibre*ingredient_amount, 2) AS SubTotalFibre,  
                        round(salt*ingredient_amount, 2) AS SubTotalSalt, 
                        round(sodium*ingredient_amount, 2) AS SubTotalSodium,  
                        round(ingredient_amount*100, 2) AS SubTotalIngredient_amount
                        
                        FROM recipes JOIN ingredients ON ingredients.product_code = recipes.ingredient_id 
                        WHERE rname = :rname AND version_number = :version_number""", {'rname':rname, 'version_number':version_number})
    recipe = cur.fetchall()
    
    cur.execute("""SELECT cname FROM customers 
                        JOIN recipes ON recipes.customer_id = customers.id WHERE rname =:rname""", {'rname':rname})
    
    customer = cur.fetchall()

    # if not recipe created, flash message
    if not recipe:
        flash("Error")
        return redirect(url_for('recipes.viewRecipes'))
    
    # else show stock information
    return render_template("/recipeinfo.html", recipe=recipe, customer=customer)


@recipes.route("/recipes/edit", methods=["GET", "POST"])
@login_required
def editrecipes():

    """ Edit recipe ingredient details """
    
    if request.method == "POST":
        
        rname = request.form.get('rname')
        ingredient_id = request.form.get('ingredient_id')
        ingredient_amount = request.form.get('editAmount')
        
        version_number = request.form.get('version_number')
        
        # connect and update database
        con = db_connect()
        cur = con.cursor()
        
        sql = """UPDATE recipes SET ingredient_amount=?/100.0 WHERE rname=? AND ingredient_id=? AND version_number=?"""

        cur.execute(sql, (ingredient_amount, rname, ingredient_id, version_number))
        con.commit()
        con.close()

        return redirect(url_for('recipes.recipesoverview', rname=rname, version_number=version_number))
    
    elif request.method == "GET":
        ingredient_id = request.args.get("product_code")
        rname = request.args.get("rname")
        version_number = request.args.get('version_number')
        is_approved = request.args.get('is_approved')

        # for recipe approval
        if is_approved:
            if is_approved == '0':
                approved = 1
            elif is_approved == '1':
                approved = 0

            # connect and update database
            con = db_connect()
            cur = con.cursor()
            
            # update approval on current version
            sql = """UPDATE recipes SET approved=? WHERE rname=? AND version_number=?"""
            cur.execute(sql, (approved, rname, version_number))

            # remove approval from all other recipes (ensures users can only have one version approved)
            sql = """UPDATE recipes SET approved=? WHERE rname=? AND NOT version_number=?"""
            cur.execute(sql, (0, rname, version_number))
            con.commit()
            con.close()

        # for ingredient amount
        con = db_connect()
        cur = con.cursor()
        cur.execute(""" SELECT name, rname, ingredient_id, round(ingredient_amount*100, 2) AS ingredient_amount 
                        FROM recipes JOIN ingredients ON ingredients.product_code = recipes.ingredient_id 
                        WHERE rname = :rname AND ingredient_id =:ingredient_id AND version_number =:version_number""", {'rname':rname, 'ingredient_id':ingredient_id, 'version_number':version_number})
        ingredient = cur.fetchall()
        return jsonify(serialize(cur, ingredient))