import requests
import pandas as pd
import time
import mysql.connector
from mysql.connector import errorcode
from dotenv import load_dotenv
import os
from pathlib import Path

## to call data from env
# Get the path to the current file (script.py)
# Path(__file__).parent points to the directory that contains the env file
main_path = Path(__file__).parent.parent.parent
# Construct the relative path to the .env file
dotenv_path = main_path / 'dev' / '.env'
# Load the environment variables from the specified .env file
load_dotenv(dotenv_path)

# # certificate for MYSQL docker
ssl_ca = f'{main_path}/dev/mysql_pem/ca.pem'         
ssl_cert = f'{main_path}/dev/mysql_pem/server-cert.pem'    
ssl_key = f'{main_path}/dev/mysql_pem/server-key.pem'

# MySQL connection configuration
config = {
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'host': os.getenv('MYSQL_LOCAL_HOST'),  # Use the container's IP or hostname if accessing MySQL container from another container
    'database': os.getenv('MYSQL_DB_NAME'),
    # 'client_flags': [mysql.connector.ClientFlag.SSL],
    'ssl_ca': ssl_ca,
    'ssl_cert': ssl_cert,
    'ssl_key': ssl_key
}

location = requests.get("https://api.mouse.rip/relic-hunter").json()
location_df = pd.json_normalize(location)
location_df['date'] = time.strftime('%Y%m%d', time.gmtime())
if(location_df.loc[0, "id"] == "unknown"):
    location_df = location_df.loc[:,["date","id", "name"]]
    location_df["article"] = "unknown"
    location_df["region"] = "unknown"
    location_df["title"] = "unknown"
location_df = location_df.loc[:,["date","id", "name", "article", "region", "title"]]
location_list =list( location_df.iloc[0])

try:
    cnx = mysql.connector.connect(**config)
    print(cnx)
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)
else:
  cursor = cnx.cursor()
  add_relic = ("INSERT IGNORE INTO relic_hunter "
               "(date_utc0,id, name, article, region, title)"
               "VALUES (%s, %s, %s, %s, %s, %s)")
  cursor.execute(add_relic, location_list)
  cnx.commit()
  
  cursor.close()
  cnx.close()