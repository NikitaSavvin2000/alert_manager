import logging
import os
from dotenv import load_dotenv

load_dotenv()

public_or_local = os.getenv("PUBLIC_OR_LOCAL", "LOCAL")


logging.basicConfig(
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s", datefmt="%H:%M:%S", level=logging.ERROR,
)
logger = logging.getLogger("microservice indicators")


API_TOKEN = os.getenv("API_TOKEN", "LOCAL")
sender_email = os.getenv("sender_email", "LOCAL")
password = os.getenv("password", "LOCAL")
password_db = os.getenv("password_db", "LOCAL")
host = os.getenv("host", "LOCAL")
port = os.getenv("port", 0)
dbname = os.getenv("dbname", "mydb")
user = os.getenv("user", "user")


DB_PARAMS = {
    "dbname": dbname,
    "user": user,
    "password": password_db,
    "host": host,
    "port": port
}
