from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    #does this print statement stay? 
    #what is its purpose?
    print(wholesale_catalog)

    with db.engine.begin() as connection:
        num_red_potions = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory"))
        num_gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))


    #no idea about this stuff need to test a bunch but sleep time now
    #read from database red potion amount
    first_row = num_red_potions.first()
    num_red_potions = first_row.num_red_potions

    #read from database gold amount
    first_row = num_gold.first()
    num_gold = first_row.gold

    quantity_purchase = 0
    
    #make calculations on how many we buy
    if num_red_potions>10:
        quantity_purchase = 0
    else:

        #modify later when adding multiple colors
        for barrel in wholesale_catalog:
            if barrel.sku == 'SMALL_RED_BARREL':
                #then calculate how many to purchase
                available = barrel.quantity

                quantity_purchase = num_gold//barrel.price
                
                #can only buy what is available
                if quantity_purchase>available:
                    quantity_purchase = available    

    return [
        {
            "sku": "SMALL_RED_BARREL",
            "quantity": quantity_purchase,
        }
    ]

@router.post("/deliver")
def post_deliver_barrels(barrels_delivered: list[Barrel]):
    """ """
    print(barrels_delivered)
    
    with db.engine.begin() as connection:
        num_red_ml = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory"))
        num_gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))


    #read from database red ml amount
    first_row = num_red_ml.first()
    num_red_ml = first_row.num_red_ml

    #read from database gold amount
    first_row = num_gold.first()
    num_gold = first_row.gold

    spent_gold= 0
    new_ml = 0

    #iterate through list and calculate money spent and mL gained
    for barrel in barrels_delivered:
        spent_gold = spent_gold + (barrel.price * barrel.quantity)
        new_ml = new_ml + (barrel.ml_per_barrel * barrel.quantity) #not sure if 10 is the right mL or not
    
    #make final calculations
    num_gold = num_gold - spent_gold
    num_red_ml = num_red_ml + new_ml

    #do this at the end once you know the updated values
    with db.engine.begin() as connection: 
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = :num_gold"), [{"num_gold": num_gold}])   
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = :num_red_ml"), [{"num_red_ml": num_red_ml}])

    #does this stay as the return value?
    return "OK"

