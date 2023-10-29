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
    
    
    if sort_col is search_sort_options.customer_name:
        order_by = db.cart.c.str
    elif sort_col is search_sort_options.item_sku:
        order_by = db.catalog.c.sku
    elif sort_col is search_sort_options.line_item_total:
        order_by = db.gold_ledger.c.charge
    else:
        order_by = db.transactions.c.created_at
    
    if sort_order == search_sort_order.desc:
        order_by = order_by.desc()
    else:
        order_by = order_by.asc()
    
    stmt = (
        sqlalchemy.select(
            db.transactions.c.id,
            db.cart.c.str.label("customer"),
            db.catalog.c.sku.label("item"),
            db.cart_items.c.quantity,
            db.gold_ledger.c.charge.label("gold"),
            db.transactions.c.created_at.label("time")
        )
        .select_from(db.transactions
            .join(db.gold_ledger, db.transactions.c.id == db.gold_ledger.c.transaction_id)
            .join(db.cart, db.transactions.c.cart_id == db.cart.c.cart_id)
            .join(db.potion_ledger, db.transactions.c.id == db.potion_ledger.c.transaction_id)
            .join(db.catalog, db.potion_ledger.c.catalog_id == db.catalog.c.catalog_id)
            .join(db.cart_items, db.cart.c.cart_id == db.cart_items.c.cart_id)
        )
        .where(db.transactions.c.tag == 'CHECKOUT')
        .order_by(order_by)
    )

    # filter only if name parameter is passed
    if customer_name != "":
        #need to change to not be case sensitive
        stmt = stmt.where(db.cart.c.str.ilike(f"%{customer_name}%"))
    if potion_sku != "":
        stmt = stmt.where(db.catalog.c.sku.ilike(f"%{potion_sku}%"))
    #need to add typing in potion
    
    with db.engine.connect() as conn:
        result = conn.execute(stmt)
        json = []
        i = 0
       
        for row in result:
            quantity = row.quantity
            name = row.item
            item_sku = str(quantity)+ " " +name
            
            json.append(
                {
                    "line_item_id": i,
                    "item_sku": item_sku,
                    "customer_name": row.customer,
                    "line_item_total": row.gold,
                    "timestamp": row.time
                }
            )
            i = i+1
    return json


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
                INSERT INTO transactions (description, tag, cart_id)
                VALUES('cart id - :cart_id', 'CHECKOUT', :cart_id)
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
    