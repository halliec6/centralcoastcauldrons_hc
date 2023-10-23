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

    # with db.engine.begin() as connection:
    #     result = connection.execute(
    #         sqlalchemy.text(
    #             "SELECT gold FROM global_inventory"))
       
    # first_row = result.first()
    # num_gold = first_row.gold

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(
            """
            SELECT sum(charge)
            FROM gold_ledger
            """
        ))
        #gold = result.fetchone()[0]
        num_gold = result.first()[0]
        #gold = first_row.result

    print("Total gold:", num_gold)
   
    red_purchase = 0
    green_purchase = 0
    blue_purchase = 0 

    print("data pulled from server:")
    print("gold: ", num_gold)
   
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
            if red_purchase >= 1:
                red_purchase = 1
                
                #needs to change once buying more than one barrel
                num_gold = num_gold - barrel.price        
        elif barrel.sku == 'SMALL_GREEN_BARREL':
            
            available = barrel.quantity

            green_purchase = num_gold//barrel.price 
            
            #can only buy what is available
            if green_purchase>available:
                green_purchase = available 

            if green_purchase >=1:
                green_purchase = 1            
                num_gold = num_gold - barrel.price

        elif barrel.sku == 'SMALL_BLUE_BARREL':
            available = barrel.quantity

            blue_purchase = num_gold//barrel.price 
            
            #can only buy what is available
            if blue_purchase>available:
                blue_purchase = available 

            if blue_purchase >=1:
                blue_purchase = 1
                num_gold = num_gold - barrel.price

    print("\nreturn values:")
    print("- sku: SMALL_RED_BARREL    Quantity: ", red_purchase)
    print("- sku: SMALL_GREEN_BARREL  Quantity: ", green_purchase)
    print("- sku: SMALL_BLUE_BARREL   Quantity: ", blue_purchase)


    ans = []

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
    print("return value of bbarrels plan: ", ans)
    return ans

@router.post("/deliver")
def post_deliver_barrels(barrels_delivered: list[Barrel]):
    """ """
    print("\nin barrels deliver: planning to buy")
    print(barrels_delivered)
    gold_paid, red_ml, blue_ml, green_ml, dark_ml = 0, 0, 0, 0, 0

    for barrel_delivered in barrels_delivered:
        gold_paid+= barrel_delivered.price*barrel_delivered.quantity
        if barrel_delivered.sku == "SMALL_RED_BARREL":
            red_ml += barrel_delivered.ml_per_barrel *barrel_delivered.quantity
        elif barrel_delivered.sku == "SMALL_GREEN_BARREL":
            green_ml += barrel_delivered.ml_per_barrel *barrel_delivered.quantity
        elif barrel_delivered.sku == "SMALL_BLUE_BARREL":
            blue_ml += barrel_delivered.ml_per_barrel * barrel_delivered.quantity
        elif barrel_delivered.potion_type == [0, 0, 0, 100]:
            dark_ml += barrel_delivered.ml_per_barrel * barrel_delivered.quantity
        else:
            raise Exception("Invalid potion type")
        
    print("gold_paid: ", gold_paid, "red_ml: ", red_ml, "green_ml: ", green_ml, "blue_ml: ", blue_ml, "dark_ml: ", dark_ml)
    
    # with db.engine.begin() as connection:
    #     connection.execute(
    #         sqlalchemy.text("""
    #             UPDATE global_inventory SET 
    #             gold = gold-:gold_paid,
    #             num_red_ml = num_red_ml + :red_ml,
    #             num_green_ml = num_green_ml + :green_ml,
    #             num_blue_ml = num_blue_ml + :blue_ml
    #             """),
    #         [{"gold_paid": gold_paid, "red_ml": red_ml, "green_ml": green_ml, "blue_ml": blue_ml}]
    #     )


    
    #is this too much hard coding???
    with db.engine.begin() as connection:
        transaction_id = connection.execute(
            #add the transaction statement first and track the transaction ID ---> need to
            sqlalchemy.text(
                """
                INSERT INTO transactions (description, tag)
                VALUES('spent :gold_paid on :red_ml redml, :green_ml greenml, :blue_ml blueml', 'BARRELS')
                RETURNING id
                """
            ),
            [{"gold_paid": gold_paid, "red_ml": red_ml, "green_ml": green_ml, "blue_ml": blue_ml}]).scalar_one()
        

        connection.execute(
            #add this to both insert statements
            sqlalchemy.text(
                """
                INSERT INTO gold_ledger(transaction_id, charge)
                VALUES (:transaction_id, :gold_paid )
                """
            ),
            [{"transaction_id": transaction_id, "gold_paid": -gold_paid}],
        )
        connection.execute(   
            sqlalchemy.text("""
                INSERT INTO ml_ledger(transaction_id, red_ml, green_ml, blue_ml)
                VALUES (:transaction_id, :red_ml, :green_ml, :blue_ml)
                """),
            [{"red_ml": red_ml, "green_ml": green_ml, "blue_ml": blue_ml, "transaction_id": transaction_id}]
        )
    return "OK"

