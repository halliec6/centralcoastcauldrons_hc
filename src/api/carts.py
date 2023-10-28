from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from enum import Enum

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)
class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """

    return {
        "previous": "",
        "next": "",
        "results": [
            {
                "line_item_id": 1,
                "item_sku": "1 oblivion potion",
                "customer_name": "Scaramouche",
                "line_item_total": 50,
                "timestamp": "2021-01-01T00:00:00Z",
            }
        ],
    }

class NewCart(BaseModel):
    customer: str

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
    return {"cart_id": id}

@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """
    
    
    return -1


class CartItem(BaseModel):
    quantity: int

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

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    print("\nIn checkout")
    print("cart_id: ", cart_id, "cart_checkout: ", cart_checkout)
        
    with db.engine.begin() as connection:
        transaction_id = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO transactions (description, tag)
                VALUES('cart id - :cart_id', 'CHECKOUT')
                RETURNING id
                """
            ),
            [{"cart_id": cart_id}])
        transaction_id = transaction_id.first()[0]

        results = connection.execute(
            sqlalchemy.text(
                """
                SELECT *
                FROM cart_items
                LEFT JOIN catalog ON cart_items.catalog_id = catalog.catalog_id
                WHERE cart_id = :cart_id
                """
            ),
            [{"cart_id": cart_id}]
        )

        
        #change this
        # connection.execute(
        #     sqlalchemy.text(
        #         """
        #         UPDATE catalog
        #         SET quantity = catalog.quantity - cart_items.quantity
        #         FROM cart_items
        #         WHERE catalog.catalog_id = cart_items.catalog_id and cart_items.cart_id = :cart_id
                
        #         """
        #     ),
        #     [{"cart_id": cart_id}]
        # )
        

        #also need to update gold amount and return total_potions bought
        #leave this
        # result = connection.execute(
        #     sqlalchemy.text(
        #         """
        #         SELECT cart_items.quantity AS cart_quantity, price
        #         FROM catalog
        #         JOIN cart_items ON cart_items.catalog_id = catalog.catalog_id
        #         WHERE cart_id = :cart_id

        #         """
        #     ),
        #     [{"cart_id": cart_id}])
        
        gold_spent, total_potions = 0, 0

        for item in results:
            connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO potion_ledger (transaction_id, quantity, catalog_id)
                    VALUES (:transaction_id, :quantity, :catalog_id)
                    """
                ),
                [{"transaction_id": transaction_id, "quantity": -(item.quantity), "catalog_id": item.catalog_id}]
            )
            gold_spent = item.quantity * item.price
            total_potions += item.quantity
        
        #change this
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO gold_ledger(transaction_id, charge)
                VALUES (:transaction_id, :gold_spent)
                """
            ),
            [{"transaction_id": transaction_id, "gold_spent": gold_spent}]
        )
        print("gold_spent: ", gold_spent)
        print("total_potinos: ", total_potions)
    

    return {"total_potions_bought": total_potions, "total_gold_paid": gold_spent}
    