from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

num_carts = 0
cart_dict = {}

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)


#how is this useful?? - this is not useful to me right now, will be useful later
class NewCart(BaseModel):
    customer: str

"""
cart_dict = {
    "cart_id": {
        "sku": str,
        
    }
}
"""

#store given data, return ID
@router.post("/")
def create_cart(new_cart: NewCart):
    """ """
    print("\nIN CREATE CART")
    global num_carts

    num_carts +=1

    #add cart id to the dictionary
    global cart_dict

    
    cart_dict[num_carts]= {}

    return {"cart_id": num_carts}


#return the cart information
@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """
    # look up ID in dictionary to access info from there?
    # What form is info returned in?
    # where is this called/used? pretty sure called in 
    # set_item_quantity, what info is helpful to return if cart
    # must be accessed with ID? maybe create an object from the info and return that?
    global cart_dict

    
    return cart_dict.get(cart_id)


class CartItem(BaseModel):
    quantity: int

#get cart, add item to cart if it is available in the database
@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    print("\nIN set item quantity")
    print("cart_id: ", cart_id, "item_sku: ", item_sku, "amount: ", cart_item.quantity)
    
    global cart_dict
    #this is the customer saying what they want? then check database to see if available and add to CartItem
    
    # num_red_potions = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory"))
    #  connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = :num_gold"), [{"num_gold": num_gold}])   
    
    #check the database for available items, if it is available 
    if item_sku == "SMALL_RED_POTION":
        with db.engine.begin() as connection:
            num_red_potions = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory"))
        first_row = num_red_potions.first()
        num_red_potions = first_row.num_red_potions
        
        #if I have enough of what the customer wants, add it to their cart dict
        if num_red_potions>= cart_item.quantity:
            cart_dict[cart_id] = {
                "sku": item_sku,
                "quantity": cart_item.quantity
            }
            return {"Success": True}
        else:
            return {"Success": False}
    
    elif item_sku == "SMALL_GREEN_POTION":
        with db.engine.begin() as connection:
            num_green_potions = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory"))
        first_row = num_green_potions.first()
        num_green_potions = first_row.num_green_potions
        
        #if I have enough of what the customer wants, add it to their cart dict
        if num_green_potions>= cart_item.quantity:
            cart_dict[cart_id] = {
                "sku": item_sku,
                "quantity": cart_item.quantity
            }
            return {"Success": True}
        else:
            return {"Success": False}
        
    elif item_sku == "SMALL_BLUE_POTION":
        
        with db.engine.begin() as connection:
            num_blue_potions = connection.execute(sqlalchemy.text("SELECT num_blue_potions FROM global_inventory"))
        first_row = num_blue_potions.first()
        num_blue_potions = first_row.num_blue_potions
        
        #if I have enough of what the customer wants, add it to their cart dict
        if num_blue_potions>= cart_item.quantity:
            cart_dict[cart_id] = {
                "sku": item_sku,
                "quantity": cart_item.quantity
            }
            return {"Success": True}
        else:
            return {"Success": False}
    
    
    return "OK"


class CartCheckout(BaseModel):
    payment: str

#update database, have to have enough for customer, transaction is all or nothing (check what payment looks like in logs?)
@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    global cart_dict
    #cartID once again accesses through get cart
    #cart_info = get_cart(cart_id)
    
    
    #modify database

    #subtract potion
    #subtract gold
    potions_bought = cart_dict[cart_id]["quantity"]
    potion_sku = cart_dict[cart_id]["sku"]
    cost = potions_bought*50
    
    print("\nin checkout")
    print("cart_id: ", cart_id, "cart_checkout: ", cart_checkout, "sku: ", potion_sku)
    
    #update the database, subtract potions bought and quantity
    if potion_sku == "SMALL_RED_POTION":
        with db.engine.begin() as connection:
            num_red_potions = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory"))
            num_gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))

        first_row = num_red_potions.first()
        num_red_potions = first_row.num_red_potions
        
        first_row = num_gold.first()
        num_gold = first_row.gold

        new_gold = num_gold + cost
        new_red_potions = num_red_potions - potions_bought
        
        with db.engine.begin() as connection: 
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = :new_gold"), [{"new_gold": new_gold}])   
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = :new_red_potions"), [{"new_red_potions": new_red_potions}])

    elif potion_sku == "SMALL_GREEN_POTION":
        with db.engine.begin() as connection:
            num_green_potions = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory"))
            num_gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))

        first_row = num_green_potions.first()
        num_green_potions = first_row.num_green_potions
        
        first_row = num_gold.first()
        num_gold = first_row.gold

        new_gold = num_gold + cost
        new_green_potions = num_green_potions - potions_bought
        
        with db.engine.begin() as connection: 
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = :new_gold"), [{"new_gold": new_gold}])   
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = :new_green_potions"), [{"new_green_potions": new_green_potions}])
    
    elif potion_sku == "SMALL_BLUE_POTION":
        with db.engine.begin() as connection:
            num_blue_potions = connection.execute(sqlalchemy.text("SELECT num_blue_potions FROM global_inventory"))
            num_gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))

        first_row = num_blue_potions.first()
        num_blue_potions = first_row.num_blue_potions
        
        first_row = num_gold.first()
        num_gold = first_row.gold

        new_gold = num_gold + cost
        new_blue_potions = num_blue_potions - potions_bought
        
        with db.engine.begin() as connection: 
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = :new_gold"), [{"new_gold": new_gold}])   
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_potions = :new_blue_potions"), [{"new_blue_potions": new_blue_potions}])


    return {"total_potions_bought": potions_bought, "total_gold_paid": cost}

# from fastapi import APIRouter, Depends, Request
# from pydantic import BaseModel
# from src.api import auth
# import sqlalchemy
# from src import database as db

# num_carts = 0
# cart_dict = {}

# router = APIRouter(
#     prefix="/carts",
#     tags=["cart"],
#     dependencies=[Depends(auth.get_api_key)],
# )


# #how is this useful?? - this is not useful to me right now, will be useful later
# class NewCart(BaseModel):
#     customer: str

# """
# cart_dict = {
#     "cart_id": {
#         "sku": str,
        
#     }
# }
# """

# #store given data, return ID
# @router.post("/")
# def create_cart(new_cart: NewCart):
#     """ """
#     global num_carts

#     num_carts +=1

#     #add cart id to the dictionary
#     global cart_dict

    
#     cart_dict[num_carts]= {}

#     return {"cart_id": num_carts}


# #return the cart information
# @router.get("/{cart_id}")
# def get_cart(cart_id: int):
#     """ """
#     # look up ID in dictionary to access info from there?
#     # What form is info returned in?
#     # where is this called/used? pretty sure called in 
#     # set_item_quantity, what info is helpful to return if cart
#     # must be accessed with ID? maybe create an object from the info and return that?
#     global cart_dict

    
#     return cart_dict.get(cart_id)


# class CartItem(BaseModel):
#     quantity: int

# #get cart, add item to cart if it is available in the database
# @router.post("/{cart_id}/items/{item_sku}")
# def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
#     """ """
#     print("\nIN set item quantity")
#     print("cart_id: ", cart_id, "item_sku: ", item_sku, "amount: ", cart_item.quantity)
    
#     global cart_dict
#     #this is the customer saying what they want? then check database to see if available and add to CartItem
    
#     # num_red_potions = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory"))
#     #  connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = :num_gold"), [{"num_gold": num_gold}])   
    
#     #check the database for available items, if it is available 
#     if item_sku == "SMALL_RED_POTION":
#         with db.engine.begin() as connection:
#             num_red_potions = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory"))
#         first_row = num_red_potions.first()
#         num_red_potions = first_row.num_red_potions
        
#         #if I have enough of what the customer wants, add it to their cart dict
#         if num_red_potions>= cart_item.quantity:
#             cart_dict[id] = {
#                 "sku": item_sku,
#                 "quantity": cart_item.quantity
#             }
#             return {"Success": True}
#         else:
#             return {"Success": False}
#     return "OK"


# class CartCheckout(BaseModel):
#     payment: str

# #update database, have to have enough for customer, transaction is all or nothing (check what payment looks like in logs?)
# @router.post("/{cart_id}/checkout")
# def checkout(cart_id: int, cart_checkout: CartCheckout):
#     """ """
#     global cart_dict
#     #cartID once again accesses through get cart
#     #cart_info = get_cart(cart_id)

#     #modify database

#     #subtract potion
#     #subtract gold
#     cost = cart_dict[id].quantity
#     if cost>cart_checkout.quantity:
#         return {"success: ", False}
#     else:
#         return {"success: ", True}

#     return {"total_potions_bought": 1, "total_gold_paid": 50}
