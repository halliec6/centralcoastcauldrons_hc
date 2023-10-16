from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)


class NewCart(BaseModel):
    customer: str


@router.post("/")
def create_cart(new_cart: NewCart):
    """ """
    return {"cart_id": 1}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """

    return {}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """

    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """

    return {"total_potions_bought": 1, "total_gold_paid": 50}
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

# #store given data, return ID
# @router.post("/")
# def create_cart(new_cart: NewCart):
#     """ """
#     print("\nIN CREATE CART")
#     global num_carts

#     num_carts +=1

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
#     print("cart_id: ", cart_id, "item_sku: ", item_sku, "ammount: ", cart_item.quantity)
    
#     global cart_dict
#     #this is the customer saying what they want? then check database to see if available and add to CartItem
    
#     cart_dict[cart_id][item_sku] = cart_item.quantity

#     return {"Success": True}

# class CartCheckout(BaseModel):
#     payment: str

# #update database, have to have enough for customer, transaction is all or nothing (check what payment looks like in logs?)
# @router.post("/{cart_id}/checkout")
# def checkout(cart_id: int, cart_checkout: CartCheckout):
#     """ """
#     global cart_dict
    
#     current_cart = cart_dict[cart_id]
#     print("in checkout, current cart: ", current_cart, "cart id: ", cart_id)
#     for sku in current_cart:
        
#         with db.engine.begin() as connection:
#             result = connection.execute(sqlalchemy.text("SELECT num_red_potions, num_green_potions, num_blue_potions, gold FROM global_inventory"))
        
#         first_row = result.first()
#         red_potions = first_row.num_red_potions
#         green_potions = first_row.num_green_potions
#         blue_potions = first_row.num_blue_potions
#         gold = first_row.gold

#         total_potions, gold_spent = 0, 0
#         #check if enough red
#         if sku == "SMALL_RED_POTION":
#             #calculate if they have enough money and gold
#             if red_potions>=current_cart[sku]:
#                 red_potions = red_potions - current_cart[sku]
#                 total_potions = total_potions + current_cart[sku]
#                 gold_spent = 50* current_cart[sku]
#             else:
#                 return{
#                     "success": "False"
#                 }
#         elif sku == "SMALL_GREEN_POTION":
#             #calculate if they have enough money and gold
#             if green_potions>=current_cart[sku]:
#                 green_potions = green_potions - current_cart[sku]
#                 total_potions = total_potions + current_cart[sku]
#                 gold_spent = 50* current_cart[sku]
#             else:
#                 return{
#                     "success": "False"
#                 }
#         elif sku == "SMALL_BLUE_POTION":
#             if blue_potions>=current_cart[sku]:
#                 blue_potions = blue_potions - current_cart[sku]
#                 total_potions = total_potions + current_cart[sku]
#                 gold_spent = 50* current_cart[sku]
#             else:
#                 return{
#                     "success": "False"
#                 }

#     gold = gold+gold_spent 
#     #update database
    
#     with db.engine.begin() as connection: 
#         connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = :gold"), [{"gold": gold}])   
#         connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = :red_potions"), [{"red_potions": red_potions}])
#         connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = :green_potions"), [{"green_potions": green_potions}])
#         connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_potions = :blue_potions"), [{"blue_potions": blue_potions}])

#     print("cart_id: ", cart_id, "total_potions_bought: ", total_potions, "total_gold_paid: ", gold_spent)
    
#     return {"total_potions_bought": total_potions, "total_gold_paid": gold_spent}
    