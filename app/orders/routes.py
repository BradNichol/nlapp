from flask import flash, redirect, render_template, request, url_for, Blueprint, jsonify
from app import db
from flask_login import login_required
from app.models import Orders, Customer, Recipe
from app.utils import db_connect, serialize
from datetime import datetime

orders = Blueprint('orders', __name__, template_folder='templates')


@orders.route("/orders")
@login_required
def viewOrders():

    orders = Orders.query.all()
    customers = Customer.query.all()
    recipes = Recipe.query.with_entities(Recipe.rname).distinct().filter_by(approved=1)

    return render_template('orders.html', orders=orders, customers=customers, recipes=recipes)

@orders.route("/orders/add", methods=["POST"])
@login_required
def addOrders():

    if request.method == "POST":

        # store order data from form 
        cid = request.form.get('customer_id')
        order_date = datetime.strptime(request.form.get('order_date'), '%Y-%m-%d')
        rname = request.form.get('recipe')
        units = request.form.get('units')
        batch_code = request.form.get('batch_code')

        
        con = db_connect()
        cur = con.cursor()
        cur.execute('SELECT bar_weight, version_number FROM recipes WHERE rname =:rname AND approved=1', {'rname':rname})
        row = cur.fetchall()
        results = serialize(cur, row)

        # calculate batch size
        unitWeight = results[0]['bar_weight']
        batchSize = unitWeight * int(units)

        # get recipe version number
        version_number = results[0]['version_number']
        
        # add into database
        order = Orders(customer_id=cid, order_date=order_date, rname=rname, recipe_version_number=version_number, units=units, batch_size=batchSize, batch_code=batch_code)
        db.session.add(order)
        db.session.commit()

        return redirect(url_for('orders.viewOrders'))


@orders.route("/orders/<string:order_id>", methods=["GET", "POST"])
@login_required
def orderinfo(order_id):
    
    # Current mix size
    mix_size = 30000
    
    # select order info
    con = db_connect()
    cur = con.cursor()
    cur.execute("""SELECT * FROM orders JOIN customers ON customers.id = orders.customer_id WHERE order_id = :order_id""", {'order_id':order_id})
    order_info = cur.fetchall()
    

    # get recipe name from order
    rname = order_info[0]['rname']
    
    # select all approved recipe names by customer
    cur.execute("""SELECT DISTINCT rname FROM recipes WHERE approved=1 AND customer_id=:customer_id""", {'customer_id':order_info[0]['customer_id']})
    all_recipe = cur.fetchall()

    # select recipe details (changed from approved to version number because user may change approval later and the recipe data for order would be incorrect)
    cur.execute("""SELECT * FROM recipes JOIN ingredients ON 
                            ingredients.product_code = recipes.ingredient_id 
                            WHERE rname=:rname AND version_number =:vn""", {'rname':rname, 'vn':order_info[0]['recipe_version_number']})
    recipe = cur.fetchall()
    
    # select OEE unit data for insights
    cur.execute("""SELECT SUM(_07+_08+_09+_10+_11+_12+_13+_14+_15+_16+_17+_18+_19+_20+_21+_22) AS sum 
                            FROM OEE_details JOIN OEE ON OEE_details.oee_id = OEE.id WHERE type="Product" AND order_id=:order_id""", {'order_id':order_id})
    units_produced = cur.fetchall()

    
    return render_template('/orderdetails.html', order_info=order_info, recipe=recipe, mix_size=mix_size, all_recipe=all_recipe, units_produced=units_produced)


@orders.route("/orders/edit", methods=["GET", "POST"])
@login_required
def editOrders():
    
    """ Edit order details """

    
    if request.method == "POST":

        order_id = request.form.get('order_id')
        rname = request.form.get('recipe')
        units = request.form.get('units')
        status = request.form.get('status')
        

        # get recipe details
        con = db_connect()
        cur = con.cursor()
        cur.execute('SELECT bar_weight, version_number FROM recipes WHERE rname =:rname AND approved=1', {'rname':rname})
        row = cur.fetchall()
        results = serialize(cur, row)

        # re-calculate batch size
        unitWeight = results[0]['bar_weight']
        batchSize = unitWeight * int(units)

        # update the version number
        version_number = results[0]['version_number']

        """ 
        
            Stop edit maybe required, currently unknown.
            Editing allowed for the timebeing to allow user
            to change status to In Progress - useful if job is 
            auto-completed and further production is required 
    
        # stop edit if the job has started or completed
        cur.execute("SELECT status FROM orders WHERE order_id = :order_id", {'order_id':order_id})
        results = cur.fetchall()
        status = results[0]['status']
        if status == 'In Progress':
            flash('Cannot edit once the job has started')
            return redirect(url_for('orders.orderinfo',order_id=order_id))
        elif status == 'Completed':
            flash('Cannot edit once the job has completed')
            return redirect(url_for('orders.orderinfo',order_id=order_id))
        
        """
        

        sql = """UPDATE orders SET rname=?, recipe_version_number=?, units=?, status=?, batch_size=? WHERE order_id=?"""

        cur.execute(sql, (rname, version_number, units, status, batchSize, order_id))
        con.commit()
        con.close()

        return redirect(url_for('orders.orderinfo', order_id=order_id))


    elif request.method == "GET":

        order_id = request.args.get("order_id")

        con = db_connect()
        cur = con.cursor()
        cur.execute("SELECT * FROM orders WHERE order_id = :order_id", {'order_id':order_id})
        row = cur.fetchall()
        result = serialize(cur, row)

        return jsonify(result)

    else:
        return redirect(url_for('orders.viewOrders'))