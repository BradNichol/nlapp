from app import db, login_manager, app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



""""
---------------
Database Models
--------------
"""

class User(db.Model, UserMixin):

    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30), unique=False, nullable=False)
    surname = db.Column(db.String(30), unique=False, nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    access_level = db.Column(db.String(20), unique=False, nullable=False, default='USER')
    approved = db.Column(db.String(3), unique=False, nullable=False, default='NO')

    oee = db.relationship('OEEtbl', backref='operator')

    def reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    
    
    def __repr__(self):
        return f"User('{self.id}', '{self.first_name}', '{self.surname}')"

    @property
    def serialize(self):
        """Return object data in serializeable format"""
        return {
            'id': self.id,
            'first_name': self.first_name
        }


class Ingredient(db.Model, UserMixin):

    __tablename__ = 'ingredients'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=False, nullable=False)
    group = db.Column(db.String(30), unique=False, nullable=False)
    product_code = db.Column(db.String(20), unique=True, nullable=False)
    protein = db.Column(db.Integer, unique=False, nullable=False, default=0)
    carbohydrates = db.Column(db.Integer, unique=False, nullable=False, default=0)
    sugars = db.Column(db.Integer, unique=False, nullable=False, default=0)
    fats = db.Column(db.Integer, unique=False, nullable=False, default=0)
    saturates = db.Column(db.Integer, unique=False, nullable=False, default=0)
    fibre = db.Column(db.Integer, unique=False, nullable=False, default=0)
    salt = db.Column(db.Integer, unique=False, nullable=False, default=0)
    sodium = db.Column(db.Integer, unique=False, nullable=False, default=0)



class Stock(db.Model, UserMixin):

    __tablename__ = 'stock'

    id = db.Column(db.Integer, primary_key=True)
    ingredient_name = db.Column(db.String(30), unique=False, nullable=False)
    product_code = db.Column(db.String(20), unique=False, nullable=False)
    supplier_name = db.Column(db.String(50), unique=False, nullable=False)
    batch_code = db.Column(db.String(20), unique=False, nullable=False)
    best_before = db.Column(db.String(20), unique=False, nullable=False)
    site_1_stock = db.Column(db.Integer, unique=False, nullable=False)
    site_2_stock = db.Column(db.Integer, unique=False, nullable=False)


class Customer(db.Model, UserMixin):

    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    cname = db.Column(db.String(30), unique=True, nullable=False)
    cnumber = db.Column(db.String(30), unique=True, nullable=True)
    fname = db.Column(db.String(30), unique=False, nullable=True)
    sname = db.Column(db.String(30), unique=False, nullable=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    
    recipes = db.relationship('Recipe', backref='customer')
    
    products = db.relationship('Product', backref='customer')



class Recipe(db.Model, UserMixin):

    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    rname = db.Column(db.String(30), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), unique=False, nullable=False)
    bar_weight = db.Column(db.Integer, unique=False, nullable=False)
    flavour = db.Column(db.String(30), unique=False, nullable=False)
    version_number = db.Column(db.Integer, unique=False, nullable=False)
    approved = db.Column(db.Integer, unique=False, nullable=False, default='0')

    orders = db.relationship('Orders', backref='recipe')

    product = db.relationship('Product', backref='recipe')

class RecipeDetails(db.Model, UserMixin):

    __tablename__ = 'recipe_details'

    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), unique=False, nullable=False)
    ingredient_id = db.Column(db.String(30), db.ForeignKey('ingredients.id'), unique=False, nullable=False)
    ingredient_amount = db.Column(db.Float, unique=False, nullable=False)
    ingredient_location = db.Column(db.String(30), unique=False, nullable=False)




class Orders(db.Model, UserMixin):

    __tablename__ ='orders'
    
    order_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), unique=False, nullable=False)
    order_date = db.Column(db.Date, nullable=False, default='')
    rname = db.Column(db.String(30), db.ForeignKey('recipes.rname'), unique=False, nullable=False)
    recipe_version_number = db.Column(db.Integer, unique=False, nullable=False)
    status = db.Column(db.String(20), unique=False, nullable=False, default='New')
    units = db.Column(db.Integer, unique=False, nullable=False, default=0)
    batch_size = db.Column(db.Integer, unique=False, nullable=False)
    batch_code = db.Column(db.Integer, unique=True, nullable=False, default=0)
    customers = db.relationship('Customer', backref='customers')
    oee = db.relationship('OEEtbl', backref='orders')


class OEEtbl(db.Model, UserMixin):

    __tablename__='OEE'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), unique=False, nullable=False)
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=False, nullable=False)
    shift = db.Column(db.String(40), unique=False, nullable=False)
    line_num = db.Column(db.Integer, unique=False, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    speed = db.Column(db.Integer, unique=False, nullable=False)
    actual_operators = db.Column(db.Integer, unique=False, nullable=False)
    planned_output = db.Column(db.Integer, unique=False, nullable=False, default=0)
    product_type = db.Column(db.String(40), unique=False, nullable=False)

class Product(db.Model, UserMixin):

    __tablename__='products'
    
    id = db.Column(db.Integer, primary_key=True)
    product_sku = db.Column(db.String(40), unique=True, nullable=False)
    product_name = db.Column(db.String(40), unique=True, nullable=False, default='')
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), unique=False, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), unique=False, nullable=False)
    run_rate = db.Column(db.Integer, unique=False, nullable=False)

    schedule_details = db.relationship('ScheduleDetails', backref='products')



class Schedule(db.Model, UserMixin):

    __tablename__='schedule'

    id = db.Column(db.Integer, primary_key=True)
    wc_date = db.Column(db.Date, nullable=False)
    format_date = db.Column(db.String(10), nullable=False)

    schedule_details = db.relationship('ScheduleDetails', backref='schedule')


class ScheduleDetails (db.Model, UserMixin):

    __tablename__='schedule_details'
    
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'), unique=False, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), unique=False, nullable=False)
    shift = db.Column(db.String(30), unique=False, nullable=False)
    line_num = db.Column(db.Integer, unique=False, nullable=False)
    monday = db.Column(db.Integer, unique=False, nullable=False, default=0)
    tuesday = db.Column(db.Integer, unique=False, nullable=False, default=0)
    wednesday = db.Column(db.Integer, unique=False, nullable=False, default=0)
    thursday = db.Column(db.Integer, unique=False, nullable=False, default=0)
    friday = db.Column(db.Integer, unique=False, nullable=False, default=0)
    saturday = db.Column(db.Integer, unique=False, nullable=False, default=0)
    sunday = db.Column(db.Integer, unique=False, nullable=False, default=0)
    

class OEEcalc:
    def __init__(self, hourly_count, total_lost_minutes, CPM, total_unit_count, total_rejects):
        self.shift_length = 480
        self.hour_length = 60
        self.hourly_count = hourly_count
        self.shift_run_time = self.hour_length * self.hourly_count
        self.max_cpm = CPM
        self.total_lost_minutes = total_lost_minutes
        self.total_unit_count = total_unit_count
        self.total_rejects = total_rejects
        self.actual_run_time = self.shift_run_time - self.total_lost_minutes
    
        

    def availability(self):
        try:
            return round(((self.actual_run_time) / self.shift_run_time),2)
        except ZeroDivisionError:
            return 0

    def performance(self):
        try:
            return round(((self.total_unit_count / self.actual_run_time) / self.max_cpm),2)
        except ZeroDivisionError:
            return 0
    

    def quality(self):
        if self.total_rejects == 0:
            return 1
        else:
            try:
                return round(((self.total_unit_count - self.total_rejects) / self.total_unit_count),2)
            except ZeroDivisionError:
                return 0

    
    """ calculate OEE score """

    def OEEscore(self):
        score = round((self.availability() * self.performance() * self.quality()),2)
    
        return score




    







