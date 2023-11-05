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
        result = connection.execute(sqlalchemy.text(
            """
            SELECT sum(red_ml)
            FROM ml_ledger
            """
        ))
        num_red_ml = result.first()[0]
        
        result = connection.execute(sqlalchemy.text(
            """
            SELECT sum(green_ml)
            FROM ml_ledger
            """
        ))
        num_green_ml = result.first()[0]

        result = connection.execute(sqlalchemy.text(
            """
            SELECT sum(blue_ml)
            FROM ml_ledger
            """
        ))
        num_blue_ml= result.first()[0]


    print("\nBottler - Plan")
    print("red_ml: ", num_red_ml)
    print("green_ml: ", num_green_ml)
    print("blue_ml: ", num_blue_ml)

    #change this!!!
    ans = []
    hashmap = {} 
    with db.engine.begin() as connection:
        catalog  = connection.execute(sqlalchemy.text(
            """
            SELECT sku, name, COALESCE(SUM(potion_ledger.quantity), 0), price, potion_type
            FROM catalog
            LEFT JOIN potion_ledger ON catalog.catalog_id = potion_ledger.catalog_id
            GROUP BY sku, name, price, potion_type
            """
        ))

        potion_catalog = []
        for potion in catalog:
            potion_catalog.append(potion)
        
        #can access the potion quantity with potion.coalesce
        #add sorting in descending order 
        potion_catalog = sorted(potion_catalog, key = lambda item: item.coalesce)

        total_potions = connection.execute(sqlalchemy.text(
            """
            select sum(coalesce(potion_ledger.quantity, 0)) as total_potion_sum
            from catalog
            left join potion_ledger on catalog.catalog_id = potion_ledger.catalog_id
            """
        ))
        total_potions = total_potions.first()[0]
        
        print("total potions: ", total_potions)
        #potion_catalog = sorted(potion_catalog, key = qu)
        while(num_red_ml + num_green_ml + num_blue_ml >=100) and total_potions<300:    
            for potion in potion_catalog:
                if potion.potion_type[0]<=num_red_ml and potion.potion_type[1]<=num_green_ml and potion.potion_type[2]<=num_blue_ml and total_potions<300 :
                    num_red_ml -= potion.potion_type[0]
                    num_green_ml -= potion.potion_type[1]
                    num_blue_ml -= potion.potion_type[2]
                    total_potions = total_potions+1

                    value = hashmap.get(potion.name)
                    if value is not None:
                        hashmap[potion.name]["quantity"] = hashmap[potion.name]["quantity"]+1
                    else:
                        hashmap[potion.name]= {
                            "potion_type": potion.potion_type,
                            "quantity": 1
                        }
                    # ans.append({
                    #     "potion_type": potion.potion_type,
                    #     "quantity": 1
                    # })
        keys = hashmap.keys()
        for val in keys:

            ans.append({
                "potion_type": hashmap[val]["potion_type"],
                "quantity": hashmap[val]["quantity"]
            })
        print("out of loop in plan")
        print("red_ml: ", num_red_ml)
        print("green_ml: ", num_green_ml)
        print("blue_ml: ", num_blue_ml)
        print("total_potions: ", total_potions)

        print(ans)
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
        
        transaction_id = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO transactions (description, tag)
                VALUES('MADE POTIONS used :red_ml redml, :green_ml greenml, :blue_ml blueml', 'BOTTLER')
                RETURNING id
                """
            ),
            [{"red_ml": -red_ml, "green_ml": -green_ml, "blue_ml": -blue_ml}]).scalar_one()
        
        connection.execute(
            sqlalchemy.text(
                """
                INSERT into ml_ledger (transaction_id, red_ml, green_ml, blue_ml)
                VALUES(:transaction_id, :red_ml, :green_ml, :blue_ml)
                """
            ),
            [{"transaction_id": transaction_id, "red_ml": -red_ml, "green_ml": -green_ml, "blue_ml": -blue_ml}]
        )
        
        for potion_delivered in potions_delivered:
            catalog_id = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT catalog_id from catalog
                    WHERE potion_type = :potion_type
                    """
                ),
                [{"potion_type": potion_delivered.potion_type}]
            )
            
            #print(catalog_id.first()[0])
            catalog_id = catalog_id.first()[0]
            connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO potion_ledger(transaction_id, quantity, catalog_id)
                    VALUES (:transaction_id, :quantity, :catalog_id)
                    """
                ),
                [{"transaction_id": transaction_id, "quantity": potion_delivered.quantity, "catalog_id": catalog_id}]
            )
        return "OK"

