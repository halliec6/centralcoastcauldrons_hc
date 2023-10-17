from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db


router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

#how is this useful?? - this is not useful to me right now, will be useful later
class NewCart(BaseModel):
    customer: str

#store given data, return ID
@router.post("/")
def create_cart(new_cart: NewCart):
    """ """
    print("\nIN CREATE CART")
    
    with db.engine.begin() as connection:
        id = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO cart
                (str)
                VALUES(:new_cart_str)
                RETURNING cart_id
                """
            ),
            [{"new_cart_str": new_cart.customer}])
    first_row = id.first()
    id = first_row.cart_id
    #print(id)
    return {"cart_id": id}


#return the cart information
@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """
    
    
    return -1


class CartItem(BaseModel):
    quantity: int

#get cart, add item to cart if it is available in the database
@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    print("\nIN set item quantity")
    print("cart_id: ", cart_id, "item_sku: ", item_sku, "ammount: ", cart_item.quantity)
    
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(
            """
            INSERT INTO cart_items (cart_id, quantity, catalog_id)
            SELECT :cart_id, :quantity, catalog_id
            FROM catalog WHERE catalog.sku = :item_sku
            """
        ),
        [{"cart_id": cart_id, "quantity": cart_item.quantity, "item_sku": item_sku}]
        )

    return {"Success": True}

class CartCheckout(BaseModel):
    payment: str

#update database, have to have enough for customer, transaction is all or nothing (check what payment looks like in logs?)
@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    print("\nIn checkout")
    print("cart_id: ", cart_id, "cart_checkout: ", cart_checkout)
        
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                UPDATE catalog
                SET quantity = catalog.quantity - cart_items.quantity
                FROM cart_items
                WHERE catalog.catalog_id = cart_items.catalog_id and cart_items.cart_id = :cart_id
                
                """
            ),
            [{"cart_id": cart_id}]
        )
        #also need to update gold amount and return total_potions bought
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT cart_items.quantity AS cart_quantity, price
                FROM catalog
                JOIN cart_items ON cart_items.catalog_id = catalog.catalog_id
                WHERE cart_id = :cart_id

                """
            ),
            [{"cart_id": cart_id}])
        
        gold_spent, total_potions = 0, 0
        for item in result:
            gold_spent = item.cart_quantity * item.price
            total_potions += item.cart_quantity
        
        connection.execute(
            sqlalchemy.text(
                """
                UPDATE global_inventory
                SET gold = gold + :gold_spent
                """
            ),
            [{"gold_spent": gold_spent}]
        )
        print("gold_spent: ", gold_spent)
        print("total_potinos: ", total_potions)
    
    #add logic for potions bought and gold spent
   # return("made it")
    return {"total_potions_bought": total_potions, "total_gold_paid": gold_spent}
    