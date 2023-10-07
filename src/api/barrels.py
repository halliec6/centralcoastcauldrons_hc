from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

#status: functions with all colors, seems to be working fully, need to push to girhub
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
        num_green_potions = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory"))
        num_blue_potions = connection.execute(sqlalchemy.text("SELECT num_blue_potions FROM global_inventory"))

        num_gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))

    

    #no idea about this stuff need to test a bunch but sleep time now
    #read from database red potion amount
    first_row = num_red_potions.first()
    num_red_potions = first_row.num_red_potions

    first_row = num_green_potions.first()
    num_green_potions = first_row.num_green_potions

    first_row = num_blue_potions.first()
    num_blue_potions = first_row.num_blue_potions

    #read from database gold amount
    first_row = num_gold.first()
    num_gold = first_row.gold

    red_purchase = 0
    green_purchase = 0
    blue_purchase = 0 


    #turn part w/in the if into a func
    
    for barrel in wholesale_catalog:
        if barrel.sku == 'SMALL_RED_BARREL':
            #then calculate how many to purchase
            available = barrel.quantity

            red_purchase = num_gold//barrel.price
            
            #can only buy what is available
            if red_purchase>available:
                red_purchase = available 
                
            #want to buy one of ea so I don't blow my money all in one place
            if red_purchase > 1:
                red_purchase = 1
            
            num_gold = (num_gold - barrel.price) * available
        
        elif barrel.sku == 'SMALL_GREEN_BARREL':
            
            available = barrel.quantity

            green_purchase = num_gold//barrel.price 
            
            #can only buy what is available
            if green_purchase>available:
                green_purchase = available 

            if green_purchase >1:
                green_purchase = 1
            
            num_gold = (num_gold - barrel.price) * available

        elif barrel.sku == 'SMALL_BLUE_BARREL':
            available = barrel.quantity

            blue_purchase = num_gold//barrel.price 
            
            #can only buy what is available
            if blue_purchase>available:
                blue_purchase = available 

            if blue_purchase >1:
                blue_purchase = 1
            num_gold = (num_gold - barrel.price) * available

        print("\nin barrels plan:")
        print("- sku: SMALL_RED_BARREL    Quantity: ", red_purchase)
        print("- sku: SMALL_GREEN_BARREL  Quantity: ", green_purchase)
        print("- sku: SMALL_BLUE_BARREL   Quantity: ", blue_purchase)


    return [
        {
            "sku": "SMALL_RED_BARREL",
            "quantity": red_purchase,
        },
        {
            "sku": "SMALL_GREEN_BARREL",
            "quantity": green_purchase
        },
        {
            "sku": "SMALL_BLUE_BARREL",
            "quantity": blue_purchase
        }
    ]

@router.post("/deliver")
def post_deliver_barrels(barrels_delivered: list[Barrel]):
    """ """
    print(barrels_delivered)
    
    with db.engine.begin() as connection:
        num_red_ml = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory"))
        num_green_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory"))
        num_blue_ml = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory"))

        num_gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))


    #read from database red ml amount
    first_row = num_red_ml.first()
    num_red_ml = first_row.num_red_ml

    #read from database greem ml amount
    first_row = num_green_ml.first()
    num_green_ml = first_row.num_green_ml

    #read from database greem ml amount
    first_row = num_blue_ml.first()
    num_blue_ml = first_row.num_blue_ml
    
    #read from database gold amount
    first_row = num_gold.first()
    num_gold = first_row.gold

    spent_gold= 0
    new_red_ml = 0
    new_green_ml = 0
    new_blue_ml = 0

    #iterate through list and calculate money spent and mL gained
    for barrel in barrels_delivered:
        
        spent_gold = spent_gold + (barrel.price * barrel.quantity)

        if barrel.sku == "SMALL_RED_BARREL":
            new_red_ml = new_red_ml + (barrel.ml_per_barrel * barrel.quantity) #not sure if 10 is the right mL or not
        elif barrel.sku == "SMALL_GREEN_BARREL":
            new_green_ml = new_green_ml + (barrel.ml_per_barrel * barrel.quantity)
        elif barrel.sku == "SMALL_BLUE_BARREL":
            new_blue_ml = new_blue_ml + (barrel.ml_per_barrel * barrel.quantity)
           
    #make final calculations
    num_gold = num_gold - spent_gold
    num_red_ml = num_red_ml + new_red_ml
    num_green_ml = num_green_ml + new_green_ml
    num_blue_ml = num_blue_ml+ new_blue_ml

    print("\nin barrels deliver")
    print("- num_gold: ", num_gold)
    print("- num_red_ml: ", num_red_ml)
    print("- num_green_ml: ", num_green_ml)
    print("- num_blue_ml: ", num_blue_ml)
    #do this at the end once you know the updated values
    with db.engine.begin() as connection: 
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = :num_gold"), [{"num_gold": num_gold}])   
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = :num_red_ml"), [{"num_red_ml": num_red_ml}])
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = :num_green_ml"), [{"num_green_ml": num_green_ml}])
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_ml = :num_blue_ml"), [{"num_blue_ml": num_blue_ml}])

    #does this stay as the return value?
    return "OK"


"""
    if num_red_potions>10:
        red_purchase = 0
    else:

        #modify later when adding multiple colors
        for barrel in wholesale_catalog:
            if barrel.sku == 'SMALL_RED_BARREL':
                #then calculate how many to purchase
                available = barrel.quantity

                red_purchase = num_gold//barrel.price
                
                #can only buy what is available
                if red_purchase>available:
                    red_purchase = available   
    """ 