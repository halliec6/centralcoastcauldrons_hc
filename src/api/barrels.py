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
    
    
    
    red_purchase = 0
    green_purchase = 0
    blue_purchase = 0 

    print("data pulled from server:")
    print("gold: ", num_gold)
    print("red_ml: ", num_red_ml)
    print("green_ml: ", num_green_ml)
    print("blue_ml: ", num_blue_ml)
    
    hashmap = {}
    
    hashmap["SMALL_RED_BARREL"]={"quantity": 0} 
    hashmap["SMALL_GREEN_BARREL"]={"quantity": 0} 
    hashmap["SMALL_BLUE_BARREL"]={"quantity": 0} 
    hashmap["MEDIUM_RED_BARREL"]={"quantity": 0} 
    hashmap["MEDIUM_GREEN_BARREL"]={"quantity": 0} 
    hashmap["MEDIUM_BLUE_BARREL"]={"quantity": 0} 

    bought = True
    total_gold = num_gold
    
    #num_gold = num_gold//2

    if num_gold >3000:
         num_gold = 3000

    if num_red_ml + num_blue_ml + num_green_ml >(100*300)/2:
         num_gold = 0
    #need to update this logic to be more efficient
    while num_gold >=250 and bought == True:    
        bought = False
        for barrel in wholesale_catalog:
            if barrel.sku == 'MEDIUM_RED_BARREL':
                available = barrel.quantity

                red_purchase = num_gold//barrel.price
                if red_purchase>available:
                        red_purchase = available 
                if red_purchase>0: 
                    red_purchase = 1   
                    num_gold = num_gold - (barrel.price * red_purchase)
                    barrel.quantity = barrel.quantity - red_purchase
                    bought = True
                    hashmap["MEDIUM_RED_BARREL"]["quantity"] = hashmap["MEDIUM_RED_BARREL"]["quantity"] + red_purchase
                
            elif barrel.sku == 'MEDIUM_GREEN_BARREL':
                
                available = barrel.quantity

                green_purchase = num_gold//barrel.price 
                
                if green_purchase>available:
                        green_purchase = available 
                
                
                if green_purchase>0: 
                    green_purchase = 1
                    num_gold = num_gold - (barrel.price * green_purchase)
                    barrel.quantity = barrel.quantity - green_purchase
                    bought = True
                    hashmap["MEDIUM_GREEN_BARREL"]["quantity"] = hashmap["MEDIUM_GREEN_BARREL"]["quantity"] + green_purchase


            elif barrel.sku == 'MEDIUM_BLUE_BARREL':
                available = barrel.quantity

                blue_purchase = num_gold//barrel.price 
                
                if blue_purchase>available:
                        blue_purchase = available 
                
                if blue_purchase>0: 
                    blue_purchase = 1                       
                    num_gold = num_gold - (barrel.price * blue_purchase)
                    barrel.quantity = barrel.quantity - blue_purchase
                    bought = True
                    hashmap["MEDIUM_BLUE_BARREL"]["quantity"] = hashmap["MEDIUM_BLUE_BARREL"]["quantity"] + blue_purchase

    bought = True       
    while num_gold >=100 and bought == True:    
        bought = False        
        for barrel in wholesale_catalog:
            if barrel.sku == 'SMALL_RED_BARREL':
                available = barrel.quantity

                red_purchase = num_gold//barrel.price
                if red_purchase>available:
                        red_purchase = available 
                if red_purchase>0: 
                    red_purchase = 1   
                    num_gold = num_gold - (barrel.price * red_purchase)
                    barrel.quantity = barrel.quantity - red_purchase
                    bought = True
                    hashmap["SMALL_RED_BARREL"]["quantity"] = hashmap["SMALL_RED_BARREL"]["quantity"] + red_purchase
                
            elif barrel.sku == 'SMALL_GREEN_BARREL':
                
                available = barrel.quantity

                green_purchase = num_gold//barrel.price 
                
                if green_purchase>available:
                        green_purchase = available 

                if green_purchase>0: 
                    green_purchase = 1
                    num_gold = num_gold - (barrel.price * green_purchase)
                    barrel.quantity = barrel.quantity - green_purchase
                    bought = True
                    hashmap["SMALL_GREEN_BARREL"]["quantity"] = hashmap["SMALL_GREEN_BARREL"]["quantity"] + green_purchase


            elif barrel.sku == 'SMALL_BLUE_BARREL':
                available = barrel.quantity

                blue_purchase = num_gold//barrel.price 
                
                if blue_purchase>available:
                        blue_purchase = available 
                
                if blue_purchase>0: 
                    blue_purchase = 1                       
                    num_gold = num_gold - (barrel.price * blue_purchase)
                    barrel.quantity = barrel.quantity - blue_purchase
                    bought = True
                    hashmap["SMALL_BLUE_BARREL"]["quantity"] = hashmap["SMALL_BLUE_BARREL"]["quantity"] + blue_purchase

                

    print("\nreturn values:")

    print("- sku: MEDIUM_RED_BARREL    Quantity: ", hashmap["MEDIUM_RED_BARREL"]["quantity"])
    print("- sku: MEDIUM_GREEN_BARREL  Quantity: ", hashmap["MEDIUM_GREEN_BARREL"]["quantity"])
    print("- sku: MEDIUM_BLUE_BARREL   Quantity: ", hashmap["MEDIUM_BLUE_BARREL"]["quantity"])
    print("- sku: SMALL_RED_BARREL    Quantity: ", hashmap["SMALL_RED_BARREL"]["quantity"])
    print("- sku: SMALL_GREEN_BARREL  Quantity: ", hashmap["SMALL_GREEN_BARREL"]["quantity"])
    print("- sku: SMALL_BLUE_BARREL   Quantity: ", hashmap["SMALL_BLUE_BARREL"]["quantity"])
    print("gold remaining: ", total_gold - num_gold)

    ans = []

    if hashmap["SMALL_RED_BARREL"]["quantity"]>0:
        ans.append({
            "sku": "SMALL_RED_BARREL",
            "quantity": hashmap["SMALL_RED_BARREL"]["quantity"],
        })
    if hashmap["SMALL_GREEN_BARREL"]["quantity"]>0:
        ans.append({
            "sku": "SMALL_GREEN_BARREL",
            "quantity": hashmap["SMALL_GREEN_BARREL"]["quantity"]
        })
    if hashmap["SMALL_BLUE_BARREL"]["quantity"]>0:
        ans.append(
        {
            "sku": "SMALL_BLUE_BARREL",
            "quantity": hashmap["SMALL_BLUE_BARREL"]["quantity"]
        }
        )

    if hashmap["MEDIUM_RED_BARREL"]["quantity"]>0:
        ans.append({
            "sku": "MEDIUM_RED_BARREL",
            "quantity": hashmap["MEDIUM_RED_BARREL"]["quantity"],
        })
    if hashmap["MEDIUM_GREEN_BARREL"]["quantity"]>0:
        ans.append({
            "sku": "MEDIUM_GREEN_BARREL",
            "quantity": hashmap["MEDIUM_GREEN_BARREL"]["quantity"]
        })
    if hashmap["MEDIUM_BLUE_BARREL"]["quantity"]>0:
        ans.append(
        {
            "sku": "MEDIUM_BLUE_BARREL",
            "quantity": hashmap["MEDIUM_BLUE_BARREL"]["quantity"]
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
        if barrel_delivered.sku == "SMALL_RED_BARREL" or barrel_delivered.sku == "MEDIUM_RED_BARREL":
            red_ml += barrel_delivered.ml_per_barrel *barrel_delivered.quantity
        elif barrel_delivered.sku == "SMALL_GREEN_BARREL" or barrel_delivered.sku == "MEDIUM_GREEN_BARREL":
            green_ml += barrel_delivered.ml_per_barrel *barrel_delivered.quantity
        elif barrel_delivered.sku == "SMALL_BLUE_BARREL" or barrel_delivered.sku == "MEDIUM_BLUE_BARREL":
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

