from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])

def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    ans = []
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(
            """
            SELECT sku, name, COALESCE(SUM(potion_ledger.quantity), 0), price, potion_type
            FROM catalog
            LEFT JOIN potion_ledger ON catalog.catalog_id = potion_ledger.catalog_id
            GROUP BY sku, name, price, potion_type
            """
        ))
        for item in result:
            if item.coalesce != 0:
                catalog_item = {
                    "sku": item.sku,
                    "name": item.name,
                    "quantity": item.coalesce,
                    "price": item.price,
                    "potion_type": item.potion_type,
                }
                ans.append(catalog_item)
    
    print("in catalog: ", ans)

    return ans

# def get_catalog():
#     """
#     Each unique item combination must have only a single price.
#     """
   
#     with db.engine.begin() as connection:
#         #no idea what this part should do 
#         red_result = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory"))
#         green_result = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory"))
#         blue_result = connection.execute(sqlalchemy.text("SELECT num_blue_potions FROM global_inventory"))

#     #red 
#     first_row = red_result.first()
#     num_red_potions = first_row.num_red_potions

#     #green
#     first_row = green_result.first()
#     num_green_potions = first_row.num_green_potions

#     #blue
#     first_row = blue_result.first()
#     num_blue_potions = first_row.num_blue_potions

    
#     # Can return a max of 20 items --> is this 20 total? or 20 of each potion??.
#     if num_red_potions > 8:
#         num_red_potions = 8
#     # elif num_red_potions == 0:
#     #     num_red_potions = []
    
#     if num_green_potions >6:
#         num_green_potions = 6
#     # elif num_green_potions == 0:
#     #     num_green_potions = []

#     if num_blue_potions >6:
#         num_blue_potions = 6
#     # elif num_blue_potions == 0:
#     #     num_blue_potions = []
    
#     ans = []

#     if num_red_potions>0:
#         ans.append({
#                 "sku": "SMALL_RED_POTION",
#                 "name": "red potion",
#                 "quantity": num_red_potions,
#                 "price": 50,
#                 "potion_type": [100, 0, 0, 0],
#             })
#     if num_green_potions>0:
#         ans.append({
#                 "sku": "SMALL_GREEN_POTION",
#                 "name": "green potion",
#                 "quantity": num_green_potions,
#                 "price": 50,
#                 "potion_type": [0, 100, 0, 0],
#             })
#     if num_blue_potions>0:
#         ans.append( {   
#                 "sku": "SMALL_BLUE_POTION",
#                 "name": "blue potion",
#                 "quantity": num_blue_potions,
#                 "price": 50,
#                 "potion_type": [0, 0, 100, 0],
#             })


#     #create an answer list

#     return ans