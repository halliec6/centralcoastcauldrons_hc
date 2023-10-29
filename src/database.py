import os
import dotenv
from sqlalchemy import create_engine
import sqlalchemy

def database_connection_url():
    dotenv.load_dotenv()

    return os.environ.get("POSTGRES_URI")

engine = create_engine(database_connection_url(), pool_pre_ping=True)


#junk I added
metadata_obj = sqlalchemy.MetaData()
transactions = sqlalchemy.Table("transactions", metadata_obj, autoload_with=engine)
cart = sqlalchemy.Table("cart", metadata_obj, autoload_with=engine)
catalog = sqlalchemy.Table("catalog", metadata_obj, autoload_with=engine)
cart_items = sqlalchemy.Table("cart_items", metadata_obj, autoload_with=engine)
gold_ledger = sqlalchemy.Table("gold_ledger", metadata_obj, autoload_with=engine)
potion_ledger = sqlalchemy.Table("potion_ledger", metadata_obj, autoload_with=engine)