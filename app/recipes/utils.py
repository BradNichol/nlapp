from app.models import Ingredient



def ingredient_name_to_id(ingredient_name):

    """ function takes a list of ingredient names and converts them to their ids """
    
    ingredient_id = []
    for i in ingredient_name:
        ingredient = Ingredient.query.filter_by(name = i).first()
        ingredient_id.append(ingredient.id)
    
    return ingredient_id