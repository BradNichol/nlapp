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
    
    protein = db.Column(db.Integer, unique=False, nullable=False)
    carbohydrates = db.Column(db.Integer, unique=False, nullable=False)
    sugars = db.Column(db.Integer, unique=False, nullable=False)
    fats = db.Column(db.Integer, unique=False, nullable=False)
    saturates = db.Column(db.Integer, unique=False, nullable=False)
    fibre = db.Column(db.Integer, unique=False, nullable=False)
    salt = db.Column(db.Integer, unique=False, nullable=False)
    sodium = db.Column(db.Integer, unique=False, nullable=False)



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
    
    recipes = db.relationship('Recipes', backref='customer')
    #orders = db.relationship('Orders', backref='customer')



class Recipes(db.Model, UserMixin):

    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    rname = db.Column(db.String(30), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), unique=False, nullable=False)
    ingredient_id = db.Column(db.String(30), db.ForeignKey('Ingredient.product_code'), unique=False, nullable=False)
    ingredient_amount = db.Column(db.Float, unique=False, nullable=False)
    bar_weight = db.Column(db.Integer, unique=False, nullable=False)
    flavour = db.Column(db.String(30), unique=False, nullable=False)
    version_number = db.Column(db.Integer, unique=False, nullable=False)
    bar_weight = db.Column(db.Integer, unique=False, nullable=False)
    approved = db.Column(db.Integer, unique=False, nullable=False, default='0')

    orders = db.relationship('Orders', backref='recipe')


class Orders(db.Model, UserMixin):

    __tablename__ ='orders'
    
    order_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), unique=False, nullable=False)
    order_date = db.Column(db.DateTime, nullable=False, default='')
    rname = db.Column(db.String(30), db.ForeignKey('recipes.rname'), unique=False, nullable=False)
    recipe_version_number = db.Column(db.Integer, unique=False, nullable=False)
    status = db.Column(db.String(20), unique=False, nullable=False, default='New')
    units = db.Column(db.Integer, unique=False, nullable=False, default=0)
    batch_size = db.Column(db.Integer, unique=False, nullable=False)

    customers = db.relationship('Customer', backref='customers')


class OEEtbl(db.Model, UserMixin):

    __tablename__='OEE'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), unique=False, nullable=False)
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=False, nullable=False)
    line_num = db.Column(db.Integer, unique=False, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    speed = db.Column(db.Integer, unique=False, nullable=False)
    actual_operators = db.Column(db.Integer, unique=False, nullable=False)



class OEEcalc:
    def __init__(self, totalLostMinutes, totalUnitCount, totalRejects):
        self.shiftLength = 480
        self.maxCPM = 60
        self.totalLostMinutes = totalLostMinutes
        self.totalUnitCount = totalUnitCount
        self.totalRejects = totalRejects
        self.runtime = self.shiftLength - self.totalLostMinutes


    def availability(self):
        return round(((self.runtime) / self.shiftLength),2)

    def performance(self):
        return round(((self.totalUnitCount / self.runtime) / self.maxCPM),2)

    def quality(self):
        if self.totalRejects == 0:
            return 1
        else:
            return round(((self.totalUnitCount - self.totalRejects) / self.totalUnitCount),2)

    
    """ calculate OEE score """

    def OEEscore(self):
        score = round((self.availability() * self.performance() * self.quality()),2)
        if score == 0:
            return 1
        else:
            return score




    






