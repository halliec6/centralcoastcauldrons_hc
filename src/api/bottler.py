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
        #num_red_ml = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory"))
        #num_green_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory"))
        #num_blue_ml = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory"))
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
    
    #make purple mix!!!
    if num_red_ml-50>=0 and num_blue_ml-50>=0:
        num_red_ml = num_red_ml - 50
        num_blue_ml = num_blue_ml - 50
        ans.append({
                "potion_type": [50, 0, 50, 0],
                "quantity": 1,
        })
    
    #make yellow
    if num_red_ml-50>=0 and num_green_ml-50>=0:
        num_red_ml = num_red_ml - 50
        num_green_ml = num_green_ml - 50
        ans.append({
                "potion_type": [50, 50, 0, 0],
                "quantity": 1,
        })
    
    if num_red_ml//100>0:
        ans.append({
                "potion_type": [100, 0, 0, 0],
                "quantity": num_red_ml//100,
            })
    if num_green_ml//100>0:
        ans.append( {
                "potion_type": [0, 100, 0, 0],
                "quantity": num_green_ml//100,
            })
    if num_blue_ml//100>0:
        ans.append(
            {
                "potion_type": [0, 0, 100, 0],
                "quantity": num_blue_ml//100,
            }
        )
    print("after subtraction ml:")
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

# @router.post("/deliver")
# def post_deliver_bottles(potions_delivered: list[PotionInventory]):
#     """ """
#     print("\nBottle - Delivered")
#     print(potions_delivered)
#     #not totally sure how to deal with potion type
    
#     new_num_red_potions, new_num_green_potions, new_num_blue_potions, new_num_yellow_potions, new_num_purple_potions = 0, 0, 0, 0, 0
#     num_red_potions, num_green_potions, num_blue_potions, num_purple_potions, num_yellow_potions = 0,0,0,0,0
#     for potion in potions_delivered:
#         if potion.potion_type == [100, 0,0,0]:
#             new_num_red_potions = new_num_red_potions + potion.quantity
#         elif potion.potion_type == [0, 100, 0, 0]:
#             new_num_green_potions = new_num_green_potions + potion.quantity
#         elif potion.potion_type == [0, 0, 100, 0]:
#             new_num_blue_potions = new_num_blue_potions + potion.quantity
#         elif potion.potion_type == [50, 0, 50, 0]:
#             new_num_purple_potions = new_num_purple_potions + potion.quantity
#         elif potion.potion_type == [50, 50, 0, 0]:
#             new_num_yellow_potions = new_num_yellow_potions+ potion.quantity
#         else: 
#             raise Exception("Invalid potion type")

    
#     with db.engine.begin() as connection:
#         result = connection.execute(
#             sqlalchemy.text(
#                 """
#                 SELECT *
#                 FROM CATALOG
#                 """
#             )
#         )
#         for row in result:
#             if row.sku == "SMALL_RED_POTION":
#                 num_red_potions = row.quantity
#             elif row.sku == "SMALL_BLUE_POTION":
#                 num_blue_potions = row.quantity
#             elif row.sku == "SMALL_GREEN_POTION":
#                 num_green_potions = row.quantity
#             elif row.sku == "SMALL_YELLOW_POTION":
#                 num_yellow_potions = row.quantity
#             elif row.sku == "SMALL_PURPLE_POTION":
#                 num_purple_potions = row.quantity
        
#     with db.engine.begin() as connection:
#         result = connection.execute(sqlalchemy.text
#             ("SELECT num_red_ml, num_green_ml, num_blue_ml FROM global_inventory"))
    
#     #read from database red potion amount
#     first_row = result.first()
#     num_red_ml = first_row.num_red_ml
#     num_green_ml = first_row.num_green_ml
#     num_blue_ml = first_row.num_blue_ml
        
#     #old plus new and update
#     new_num_red_ml = num_red_ml - ((100 * new_num_red_potions)+(50*(new_num_green_potions+new_num_purple_potions)))
#     new_num_green_ml = num_green_ml - ((100 * new_num_green_potions)+(50*new_num_yellow_potions)) 
#     new_num_blue_ml = num_blue_ml - ((100 * new_num_blue_potions) +(50*new_num_purple_potions))
    
#     new_num_red_potions = new_num_red_potions + num_red_potions    
#     new_num_green_potions = new_num_green_potions + num_green_potions
#     new_num_blue_potions = new_num_blue_potions + num_blue_potions
#     new_num_yellow_potions = new_num_yellow_potions + num_yellow_potions 
#     new_num_purple_potions = new_num_purple_potions + num_purple_potions 

#     print("new ml ammounts")
#     print("red_ml: ", new_num_red_ml)
#     print("red_ml: ", new_num_green_ml)
#     print("red_ml: ", new_num_blue_ml)

#     print("\nnew potion ammounts")
#     print("red potions: ", new_num_red_potions)
#     print("green potions: ", new_num_green_potions)
#     print("blue potions: ", new_num_blue_potions)
#     print("yellow potions: ", new_num_yellow_potions)
#     print("purple potions: ", new_num_purple_potions)





#     with db.engine.begin() as connection:
#         connection.execute(
#             sqlalchemy.text(
#                 """
#                 UPDATE catalog 
#                 SET quantity = :new_num_red_potion
#                 WHERE sku = 'SMALL_RED_POTION'
#                 """
#                 ), 
#             [{"new_num_red_potion": new_num_red_potions}])
        
#         connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = :new_num_red_ml"), [{"new_num_red_ml": new_num_red_ml}])
        
#         #connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = :new_num_green_potion"), [{"new_num_green_potion": new_num_green_potions}])
#         #connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = :new_num_green_ml"), [{"new_num_green_ml": new_num_green_ml}])

#         #connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_potions = :new_num_blue_potion"), [{"new_num_blue_potion": new_num_blue_potions}])
#         #connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_ml = :new_num_blue_ml"), [{"new_num_blue_ml": new_num_blue_ml}])
#     return "OK"


