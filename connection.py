import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='.env')

MYSQL_CONFIG = {
    'host': os.getenv('host'),
    'user': os.getenv('user'),
    'password': os.getenv('AIVEN_MYSQL_PASS'),
    'database': os.getenv('data'),
    'port': int(os.getenv('port'))
}
