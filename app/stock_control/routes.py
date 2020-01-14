from flask import flash, redirect, render_template, request, url_for, Blueprint, jsonify
# from app.models
from app import db
from app.utils import db_connect, serialize
from flask_login import login_required

stockControl = Blueprint('stockControl', __name__, template_folder='templates')






@stockControl.route("/stock", methods=["GET", "POST"])
@login_required
def viewAllStock():

    """ View all stock on inital stock page """

    con = db_connect()
    cur = con.cursor()
    cur.execute("SELECT product_code, name FROM ingredients")
    ingredients = cur.fetchall()
    cur.execute("SELECT *, ROUND(site_1_stock+site_2_stock, 2) AS totalStock FROM stock")
    stock_level = cur.fetchall()
    
    return render_template("stockcontrol.html", stock_level=stock_level, ingredients=ingredients)


@stockControl.route("/stock/<string:product_code>", methods=["GET", "POST"])
@login_required
def stockOverview(product_code):

    """ View individual stock information """
    con = db_connect()
    cur = con.cursor()
    cur.execute("""SELECT *, round(site_1_stock+site_2_stock, 2) AS stock_level,
                                    (select SUM(site_1_stock+site_2_stock) from stock WHERE product_code =:product_code) AS total_stock, 
                                    (select SUM(site_1_stock) from stock WHERE product_code =:product_code) AS site_1,
                                    (select SUM(site_2_stock) from stock WHERE product_code =:product_code) AS site_2
                                    FROM stock WHERE product_code =:product_code""", {'product_code': product_code})
    stockDetails = cur.fetchall()

    # if not stock created, flash message
    if not stockDetails:
        flash("You haven't setup stock configuration for this item")
        return redirect(url_for('ingredients.showIngredients'))
    
    # else show stock information
    return render_template("/stockinfo.html", stock=stockDetails)


    

@stockControl.route("/stock/add", methods=["GET", "POST"])
@login_required
def addStock():

    """ To Do """

    return None
