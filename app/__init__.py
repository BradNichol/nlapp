from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail


app = Flask(__name__)

app.config['SECRET_KEY'] = 'dev'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nldata.db'


db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'users.login'
app.config['MAIL_SERVER'] = ''
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = ''
mail = Mail(app)


from app.users.routes import users
from app.main.routes import main
from app.ingredients.routes import ingredients
from app.stock_control.routes import stockControl
from app.customers.routes import customers
from app.recipes.routes import recipes
from app.orders.routes import orders
from app.oee.routes import oee
from app.advice.routes import advice
from app.schedule.routes import schedule
from app.errors.handlers import errors
from app.products.routes import products
from app.reports.routes import reports


app.register_blueprint(users)
app.register_blueprint(main)
app.register_blueprint(ingredients)
app.register_blueprint(stockControl)
app.register_blueprint(customers)
app.register_blueprint(recipes)
app.register_blueprint(orders)
app.register_blueprint(oee)
app.register_blueprint(errors)
app.register_blueprint(advice)
app.register_blueprint(schedule)
app.register_blueprint(products)
app.register_blueprint(reports)


