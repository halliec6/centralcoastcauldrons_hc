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
        num_red_ml = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory"))
        num_red_potions = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory"))
        gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))

    first_row = num_red_ml.first()
    num_red_ml = first_row.num_red_ml

    first_row = num_red_potions.first()
    num_red_potions = first_row.num_red_potions

    first_row = gold.first()
    gold = first_row.gold

    return {"number_of_potions": num_red_potions, "ml_in_barrels": num_red_ml, "gold": gold}

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
