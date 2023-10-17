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

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_red_ml, num_green_ml, num_blue_ml FROM global_inventory"))
    
    #read from database red potion amount
    first_row = result.first()
    num_red_ml = first_row.num_red_ml
    num_blue_ml = first_row.num_blue_ml
    num_green_ml = first_row.num_green_ml

    print("\nBottler - Plan")
    print("red_ml: ", num_red_ml)
    print("green_ml: ", num_green_ml)
    print("blue_ml: ", num_blue_ml)

    ans = [] 
    with db.engine.begin() as connection:
        catalog  = connection.execute(sqlalchemy.text(
            """
            SELECT quantity, potion_type
            FROM catalog
            """
        ))
    
        for potion in catalog:
            if potion.potion_type[0]<=num_red_ml and potion.potion_type[1]<=num_green_ml and potion.potion_type[2]<=num_blue_ml:
                num_red_ml -= potion.potion_type[0]
                num_green_ml -= potion.potion_type[1]
                num_blue_ml -= potion.potion_type[2]

                ans.append({
                    "potion_type": potion.potion_type,
                    "quantity": 1
                })
    print("out of loop in plan")
    print("red_ml: ", num_red_ml)
    print("green_ml: ", num_green_ml)
    print("blue_ml: ", num_blue_ml)

    
    return ans

@router.post("/deliver")
def post_deliver_bottles(potions_delivered: list[PotionInventory]):
    """ """
    print("\nBottle - Delivered")
    print(potions_delivered)

    with db.engine.begin() as connection:
        additional_potions = sum(p.quantity for p in potions_delivered)
        red_ml = sum(p.quantity * p.potion_type[0] for p in potions_delivered)
        green_ml = sum(p.quantity *p.potion_type[1] for p in potions_delivered)
        blue_ml = sum(p.quantity*p.potion_type[2] for p in potions_delivered)
        dark_ml = sum(p.quantity * p.potion_type[3] for p in potions_delivered)

        for potion_delivered in potions_delivered:
            connection.execute(
                sqlalchemy.text(
                    """
                    UPDATE catalog 
                    SET quantity = quantity+ :additional_potions
                    WHERE potion_type = :potion_type
                    """
                ),
                [{"additional_potions": potion_delivered.quantity,
                  "potion_type": potion_delivered.potion_type}])
        
        connection.execute(
            sqlalchemy.text(
                """
                UPDATE global_inventory SET
                num_red_ml = num_red_ml - :red_ml,
                num_green_ml = num_green_ml - :green_ml,
                num_blue_ml = num_blue_ml - :blue_ml
                """
            ),
            [{"red_ml": red_ml, "green_ml": green_ml, "blue_ml": blue_ml}])
    
    return "OK"

