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
        num_green_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory"))
        num_blue_ml = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory"))


    #read from database red potion amount
    first_row = num_red_ml.first()
    num_red_ml = first_row.num_red_ml

    first_row = num_green_ml.first()
    num_green_ml = first_row.num_green_ml

    first_row = num_blue_ml.first()
    num_blue_ml = first_row.num_blue_ml

    red_potions = num_red_ml//100
    green_potions = num_green_ml//100
    blue_potions = num_blue_ml//100

    print("\nBottler - Plan")
    print("red_potions to make: ", red_potions)
    print("green_potions to make: ", green_potions)
    print("blue_potions to make: ", blue_potions)
    
    ans = []
    if red_potions>0:
        ans.append({
                "potion_type": [1, 0, 0, 0],
                "quantity": red_potions,
            })
    if green_potions>0:
        ans.append( {
                "potion_type": [0, 1, 0, 0],
                "quantity": green_potions,
            })
    if blue_potions>0:
        ans.append(
            {
                "potion_type": [0, 0, 1, 0],
                "quantity": blue_potions,
            }
        )
    
    return ans

@router.post("/deliver")
def post_deliver_bottles(potions_delivered: list[PotionInventory]):
    """ """
    print("\nBottle - Delivered")
    print(potions_delivered)
    #not totally sure how to deal with potion type
    
    new_num_red_potions, new_num_green_potions, new_num_blue_potions = 0, 0, 0

    for potion in potions_delivered:
        if potion.potion_type == [1, 0,0,0]:
            new_num_red_potions = new_num_red_potions + potion.quantity
        elif potion.potion_type == [0, 1, 0, 0]:
            new_num_green_potions = new_num_green_potions + potion.quantity
        elif potion.potion_type == [0, 0, 1, 0]:
            new_num_blue_potions = new_num_blue_potions + potion.quantity

    
    with db.engine.begin() as connection:
        num_red_potions = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory"))
        num_red_ml = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory"))
        
        #need to add full logic for green and blue potions
        num_green_potions = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory"))
        num_green_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory"))
        
        num_blue_potions = connection.execute(sqlalchemy.text("SELECT num_blue_potions FROM global_inventory"))
        num_blue_ml = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory"))


    
    #read from database red potion amount
    first_row = num_red_potions.first()
    num_red_potions = first_row.num_red_potions

    first_row = num_green_potions.first()
    num_green_potions = first_row.num_green_potions

    first_row = num_blue_potions.first()
    num_blue_potions = first_row.num_blue_potions

    #read from database the red ml ammount
    first_row = num_red_ml.first()
    num_red_ml = first_row.num_red_ml

    #read from database the red ml ammount
    first_row = num_green_ml.first()
    num_green_ml = first_row.num_green_ml

    #read from database the red ml ammount
    first_row = num_blue_ml.first()
    num_blue_ml = first_row.num_blue_ml

    #old plus new and update
    new_num_red_ml = num_red_ml - (100 * new_num_red_potions)
    new_num_red_potions = new_num_red_potions + num_red_potions

    new_num_green_ml = num_green_ml - (100 * new_num_green_potions)
    new_num_green_potions = new_num_green_potions + num_green_potions
    
    new_num_blue_ml = num_blue_ml - (100 * new_num_blue_potions)
    new_num_blue_potions = new_num_blue_potions + num_blue_potions

    print("new ml ammounts")
    print("- new_num_red_potions: ", new_num_red_potions, "new_ml: ", new_num_red_ml)
    print("- new_num_green_potions: ", new_num_green_potions, "new_ml: ", new_num_green_ml)
    print("- new_num_blue_potions: ", new_num_blue_potions, "new_ml: ", new_num_blue_ml)


    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = :new_num_red_potion"), [{"new_num_red_potion": new_num_red_potions}])
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = :new_num_red_ml"), [{"new_num_red_ml": new_num_red_ml}])
        
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = :new_num_green_potion"), [{"new_num_green_potion": new_num_green_potions}])
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = :new_num_green_ml"), [{"new_num_green_ml": new_num_green_ml}])

        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_potions = :new_num_blue_potion"), [{"new_num_blue_potion": new_num_blue_potions}])
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_ml = :new_num_blue_ml"), [{"new_num_blue_ml": new_num_blue_ml}])
    return "OK"

