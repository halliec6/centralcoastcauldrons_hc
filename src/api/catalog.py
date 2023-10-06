from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])

def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
   
    with db.engine.begin() as connection:
        #no idea what this part should do 
        result = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory"))
    
    first_row = result.first()
    num_red_potions = first_row.num_red_potions


    # Can return a max of 20 items.
    if num_red_potions > 20:
        num_red_potions = 20
    
    if num_red_potions == 0:
        num_red_potions = []
    
    return [
            {
                "sku": "RED_POTION_0",
                "name": "red potion",
                "quantity": num_red_potions,
                "price": 50,
                "potion_type": [100, 0, 0, 0],
            }
        ]
