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
    
    print("\nIn barrels plan") 
    print(wholesale_catalog)

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_red_potions, num_blue_potions, num_green_potions, gold FROM global_inventory"))
       
    first_row = result.first()
    red_potions = first_row.num_red_potions
    green_potions = first_row.num_green_potions
    blue_potions = first_row.num_blue_potions
    num_gold = first_row.gold

   
    red_purchase = 0
    green_purchase = 0
    blue_purchase = 0 

    print("data pulled from server:")
    print("gold: ", num_gold)
    print("num_red_potions: ", red_potions)
    print("num_gree_potions: ", green_potions)
    print("num blue potions: ", blue_potions)
    
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
                
                #needs to change once buying more than one barrel
                num_gold = num_gold - barrel.price        
        elif barrel.sku == 'SMALL_GREEN_BARREL':
            
            available = barrel.quantity

            green_purchase = num_gold//barrel.price 
            
            #can only buy what is available
            if green_purchase>available:
                green_purchase = available 

            if green_purchase >1:
                green_purchase = 1            
                num_gold = num_gold - barrel.price

        elif barrel.sku == 'SMALL_BLUE_BARREL':
            available = barrel.quantity

            blue_purchase = num_gold//barrel.price 
            
            #can only buy what is available
            if blue_purchase>available:
                blue_purchase = available 

            if blue_purchase >1:
                blue_purchase = 1
                num_gold = num_gold - barrel.price

    print("\nreturn values:")
    print("- sku: SMALL_RED_BARREL    Quantity: ", red_purchase)
    print("- sku: SMALL_GREEN_BARREL  Quantity: ", green_purchase)
    print("- sku: SMALL_BLUE_BARREL   Quantity: ", blue_purchase)


    ans = []

    #probably should add the array [0,0,...]
    if red_purchase>0:
        ans.append({
            "sku": "SMALL_RED_BARREL",
            "quantity": red_purchase,
        })
    if green_purchase>0:
        ans.append({
            "sku": "SMALL_GREEN_BARREL",
            "quantity": green_purchase
        })
    if blue_purchase>0:
        ans.append(
        {
            "sku": "SMALL_BLUE_BARREL",
            "quantity": blue_purchase
        }
        )

    return ans

@router.post("/deliver")
def post_deliver_barrels(barrels_delivered: list[Barrel]):
    """ """
    print("\nin barrels deliver: planning to buy")
    print(barrels_delivered)
    
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_red_ml, num_green_ml, num_blue_ml, gold FROM global_inventory"))
       
    first_row = result.first()
    num_red_ml = first_row.num_red_ml
    num_green_ml = first_row.num_green_ml
    num_blue_ml = first_row.num_blue_ml
    num_gold = first_row.gold
    
    print("Initial database values:")
    print("num_gold: ", num_gold)
    print("num_red_ml: ", num_red_ml)
    print("num_green_ml: ", num_green_ml)
    print("num_blue_ml: ", num_blue_ml)
    
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
    
    print("\nwhat was purchased in barrels delivered:")
    print("num gold spent ", num_gold)
    print("num_red_ml bought: ", new_red_ml)
    print("num_green_ml bought: ", new_green_ml)
    print("num_blue_ml bought: ", new_blue_ml)  
    
    #make final calculations
    num_gold = num_gold - spent_gold
    num_red_ml = num_red_ml + new_red_ml
    num_green_ml = num_green_ml + new_green_ml
    num_blue_ml = num_blue_ml+ new_blue_ml

    print("\ncalculations to upload to database:")
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

