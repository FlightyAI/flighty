import datetime
import json
import os
import random
import snowflake.connector

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'config.txt')) as f:
  for line in f.readlines():
    parsed = line.split(' = ')
    if (parsed[0] == 'ORGANIZATION'):
      organization_name = parsed[1].rstrip().lower()
    elif (parsed[0] == 'SNOWFLAKE_USER'):
      snowflake_user = parsed[1].rstrip().lower()
    elif (parsed[0] == 'SNOWFLAKE_PASSWORD'):
      snowflake_password = parsed[1].rstrip()
    elif (parsed[0] == 'SNOWFLAKE_ACCOUNT'):
      snowflake_account = parsed[1].rstrip().lower()   

ctx = snowflake.connector.connect(account=snowflake_account, 
        user=snowflake_user, password=snowflake_password)
cs = ctx.cursor() 
cs.execute("USE DATABASE flighty")

def log_to_snowflake(input, prod, endpoint, model_name, output):

  statement = ("insert into model_data.model_data"
  f" select to_timestamp('{datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}'), "
  f"'{endpoint}', '{model_name}', {json.dumps(input)}, {json.dumps(output)}, {'true' if prod else 'false'}, "
  f" {random.randint(1,5)};")
  statement = statement.replace('"', "'") # Snowflake expects single quotes even in JSON
  cs.execute(statement)

