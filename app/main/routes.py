from app import app, db
from flask import flash, redirect, render_template, request, session, url_for, Blueprint
import sqlite3 as sqlite
from app.models import User
from flask_login import current_user, login_required
from app.utils import db_connect

main = Blueprint('main', __name__)

@main.route("/")
@login_required
def index():

    con = db_connect()
    cur = con.cursor()
    
    cur.execute("SELECT COUNT(cname) FROM customers")
    result1 = cur.fetchone()[0]
    cur.execute("SELECT COUNT(order_id) FROM orders")
    result2 = cur.fetchone()[0]
    cur.execute("SELECT COUNT(id) FROM recipes GROUP BY rname")
    result3 = cur.fetchone()[0]
    

    return render_template('index.html', result1=result1, result2=result2, result3=result3)

    




