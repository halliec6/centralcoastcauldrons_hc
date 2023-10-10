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
        num_green_potions = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory"))
        num_green_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory"))
        num_blue_potions = connection.execute(sqlalchemy.text("SELECT num_blue_potions FROM global_inventory"))
        num_blue_ml = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory"))

    first_row = num_red_ml.first()
    num_red_ml = first_row.num_red_ml

    first_row = num_green_ml.first()
    num_green_ml = first_row.num_green_ml

    first_row = num_blue_ml.first()
    num_blue_ml = first_row.num_blue_ml

    first_row = num_red_potions.first()
    num_red_potions = first_row.num_red_potions

    first_row = num_green_potions.first()
    num_green_potions = first_row.num_green_potions

    first_row = num_blue_potions.first()
    num_blue_potions = first_row.num_blue_potions

    first_row = gold.first()
    gold = first_row.gold

    potions = num_blue_potions + num_red_potions + num_green_potions
    ml = num_green_ml + num_red_ml + num_blue_ml
    #need to add up all the ml, gold and potions
    return {"number_of_potions": potions, "ml_in_barrels": ml, "gold": gold}

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
