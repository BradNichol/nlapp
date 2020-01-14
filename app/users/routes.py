from flask import flash, redirect, render_template, request, url_for, Blueprint, jsonify
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import User
from app import db
from app.utils import db_connect, serialize, send_reset_email
from flask_login import login_user, current_user, logout_user, login_required

users = Blueprint('users', __name__, template_folder='templates')



"""
----------------------------------

Registration & Login

----------------------------------
"""

@users.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == "POST":
        
        #store user details
        fname = request.form.get("firstname")
        sname = request.form.get("surname")
        email = request.form.get("email")

        duplicate_check = User.query.filter_by(email=email).first()
        if duplicate_check:
            flash('That email is already registered. Please use an alternative email, or reset your password.')
            return redirect(url_for('users.login'))

        
        # check password length
        pass_length = len(request.form.get('password'))
        if pass_length < 6:
            flash('Password must be at least 6 characters.')
            return redirect(url_for('users.register'))
    
             
        #hash password for protection
        hashed_password = generate_password_hash(request.form.get("password"))
        
        #enter user into database
        user = User(first_name=fname, surname=sname, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        flash('Thank you for registering. Your account is now waiting for administrator approval')
        return redirect(url_for('users.login'))


    return render_template('register.html')


@users.route("/login", methods=["GET", "POST"])
def login():
    """Log user in """

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == "POST":

        email = request.form.get("username")
        password = request.form.get("password")

        # query database
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('You need to register an account first')
            return redirect(url_for('users.register'))
        if user.approved == 'NO':
            flash ('Your account has not been approved. Please contact the administrator.')
            return redirect(url_for('users.login'))
        elif user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            flash("Login unsuccessful. Email or password incorrect")
    

    return render_template("login.html")


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('users.login'))



"""
----------------------------------

User and admin accounts 

----------------------------------
"""
@users.route("/account")
@login_required
def account():
    return render_template("account.html")


@users.route("/users", methods=["GET", "POST"])
@login_required
def showusers():

    if request.method == "GET":
        # on page enter, no id will be available so display table
        user_id = request.args.get("user_id")
        if not user_id:
            users = User.query.all()
            return render_template('users.html', users=users)
        else:
            con = db_connect()
            cur = con.cursor()
            cur.execute("SELECT id, first_name, surname, access_level, approved FROM users WHERE id = :user_id", {'user_id': user_id})
            result = cur.fetchall()

            return jsonify(serialize(cur, result))
    
    # update user
    if request.method == "POST":

        id = request.form.get('id')
        first_name = request.form.get('first_name')
        surname = request.form.get('surname')
        access_level = request.form.get('access_level')
        approved = request.form.get('approved')

        con = db_connect('update')
        cur = con.cursor()
        sql = """UPDATE users SET first_name=?, surname=?, access_level=?, approved=? WHERE id=?"""

        cur.execute(sql, (first_name, surname, access_level, approved, id))
        con.commit()
        con.close()

        flash('User updated')
        return redirect(url_for('users.showusers'))




@users.route("/password/reset", methods=["GET", "POST"])
def reset_request():
    """ Password reset request """

    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == "POST":
        email = request.form.get('email')

        user = User.query.filter_by(email=email).first()
        if user is None:
            flash('There is no account with that email. Please register first.')
            return redirect(url_for('users.passwordreset'))
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.')
        return redirect(url_for('users.login'))

    return render_template('reset_request.html')

@users.route("/password/<token>", methods=["GET", "POST"])
def reset_token(token):
    """ Enter new password """
    
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    user = User.verify_reset_token(token)
    if user is None:
        flash('Your token is invalid or has expired.')
        return redirect(url_for('users.reset_request'))
    
    if request.form.get('password'):          
        # update new password
        hashed_password = generate_password_hash(request.form.get("password"))
        user.password = hashed_password
        db.session.commit()

        flash('Your password has been updated. You can now login.')
        return redirect(url_for('users.login'))

    return render_template('reset_token.html')



