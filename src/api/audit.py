from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/inventory")
def get_inventory():
    """ """
    with db.engine.begin() as connection:
        ml_result = connection.execute(
            sqlalchemy.text(
                """
                SELECT num_red_ml, num_blue_ml, num_green_ml, gold
                FROM global_inventory
                """
            )
        )
    total_ml = 0
    first_row = ml_result.first()
    total_ml += first_row.num_red_ml
    total_ml += first_row.num_green_ml
    total_ml += first_row.num_blue_ml
    gold = first_row.gold

    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT quantity
                FROM catalog
                WHERE quantity>0
                """
            )
        )
        potions = 0
        for item in result:
            potions += item.quantity
   
    #need to add up all the ml, gold and potions
    return {"number_of_potions": potions, "ml_in_barrels": total_ml, "gold": gold}

class Result(BaseModel):
    gold_match: bool
    barrels_match: bool
    potions_match: bool

# Gets called once a day
@router.post("/results")
def post_audit_results(audit_explanation: Result):
    """ """
    print(audit_explanation)

    return "OK"
