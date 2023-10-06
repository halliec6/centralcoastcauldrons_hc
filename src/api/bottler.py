from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

# Gets called 4 times a day
@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.
    
    #every potion is 100mL

    #pull data from the Supabase
    with db.engine.begin() as connection:
        num_red_ml = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory"))

    #read from database red potion amount
    first_row = num_red_ml.first()
    num_red_ml = first_row.num_red_ml

    red_potions = num_red_ml//100

    return [
            {
                "potion_type": [100, 0, 0, 0],
                "quantity": red_potions,
            }
        ]

@router.post("/deliver")
def post_deliver_bottles(potions_delivered: list[PotionInventory]):
    """ """
    print(potions_delivered)
    #not totally sure how to deal with potion type
    
    new_num_red_potions = 0

    for potion in potions_delivered:
        if potion.potion_type == [100,0,0,0]:
            new_num_red_potions = new_num_red_potions + potion.quantity
    
    with db.engine.begin() as connection:
        num_red_potions = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory"))
        num_red_ml = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory"))
    
    #read from database red potion amaount
    first_row = num_red_potions.first()
    num_red_potions = first_row.num_red_potions

    #read from database the red ml ammount
    first_row = num_red_ml.first()
    num_red_ml = first_row.num_red_ml

    #old plus new and update
    new_num_red_potions = new_num_red_potions + num_red_potions
    new_num_red_ml = num_red_ml - (100 * num_red_potions)
    ####FIX add in subtracting mL based on what you made


    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = :new_num_red_potion"), [{"new_num_red_potion": new_num_red_potions}])
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = :new_num_red_ml"), [{"new_num_red_ml": new_num_red_ml}])

    return "OK"

