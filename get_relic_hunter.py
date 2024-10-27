import requests
import pandas as pd
import time
import mysql.connector
from mysql.connector import errorcode
from dotenv import load_dotenv
import os

## to call data from env
# Get the path to the current file (script.py)
current_path = Path(__file__).parent
# Construct the relative path to the .env file
dotenv_path = current_path / 'dev' / '.env'
# Load the environment variables from the specified .env file
load_dotenv(dotenv_path)

location = requests.get("https://api.mouse.rip/relic-hunter").json()
location_df = pd.json_normalize(location)
location_df['date'] = time.strftime('%Y%m%d', time.gmtime())
location_df = location_df.loc[:,["date","id", "name", "article", "region", "title"]]
location_list =list( location_df.iloc[0])

try:
    cnx = mysql.connector.connect(user=os.getenv('MYSQL_USER'), password=os.getenv('123456'), host=os.getenv('MYSQL_LOCAL_HOST'), database=os.getenv('MYSQL_DB_NAME'))
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