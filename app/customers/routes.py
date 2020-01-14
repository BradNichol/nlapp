from flask import flash, redirect, render_template, request, url_for, Blueprint, jsonify
from app import db
from app.models import Customer
from flask_login import login_required
from app.utils import db_connect, serialize


customers = Blueprint('customers', __name__, template_folder='templates')


@customers.route("/customer", methods=["GET", "POST"])
@login_required
def customer():

    if request.form.get('cname'):
        
        # get customer details
        cname = request.form.get('cname')
        cnumber = request.form.get('cnumber')
        fname = request.form.get('fname')
        sname = request.form.get('sname')
        email = request.form.get('email')

        #enter customer into database
        newCustomer = Customer(cname=cname, cnumber=cnumber, fname=fname, sname=sname, email=email)
        db.session.add(newCustomer)
        db.session.commit()

        flash('New customer has been added')
        return redirect(url_for('customers.customer'))

    else: # on page enter

        customers = Customer.query.all()
        return render_template("customer.html", customers=customers)



@customers.route("/customer/edit", methods=["GET", "POST"])
@login_required
def editcustomer():

    if request.method == "GET":
        # on page enter, no id will be available so display table
        customer_id = request.args.get("customer_id")
        if not customer_id:
            customers = Customer.query.all()
            return render_template('customer.html', customers=customers)
        else:
            con = db_connect()
            cur = con.cursor()
            cur.execute("SELECT id, cname, cnumber, fname, sname, email FROM customers WHERE id = :customer_id", {'customer_id': customer_id})
            result = cur.fetchall()

            return jsonify(serialize(cur, result))

    if request.method == "POST":
        cid = request.form.get('cid')
        customer = Customer.query.filter_by(id=cid).first()

        customer.cname = request.form.get('cname')
        customer.cnumber = request.form.get('cnumber')
        customer.fname = request.form.get('fname')
        customer.sname = request.form.get('sname')
        customer.email = request.form.get('email')
        db.session.commit()

        flash('Edits successful')
        return redirect(url_for('customers.customer'))
