import os
import psycopg2

DATABASE_URL = os.popen('heroku config:get DATABASE_URL -a chatbot-ccclub').read()[:-1]
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()

#創開團表單 activity
create_table =  '''CREATE TABLE activity(
           id serial PRIMARY KEY,
           activity_type VARCHAR (50),
           activity_name VARCHAR (50),
           activity_date DATE ,
           activity_time TIME ,
           location_title VARCHAR (50),
           location_latitude NUMERIC (9, 6) ,
           location_longitude NUMERIC (9, 6),
           people INTEGER ,
           cost INTEGER ,
           due_date DATE ,
           description TEXT,
           photo TEXT,
           attendee INTEGER ,
           condition VARCHAR (50),
           user_id INTEGER,
           created_at VARCHAR (50),
           updated_at VARCHAR (50)
        );'''

cursor.execute(create_table)
conn.commit()

#創報名表單 registration
create_table =  '''CREATE TABLE registration(
           id serial PRIMARY KEY,
           activity_id INTEGER,
           condition VARCHAR (50),
           user_id INTEGER,
           created_at VARCHAR (50),
           updated_at VARCHAR (50)
        );'''

cursor.execute(create_table)
conn.commit()


#創用戶表單 users
create_table =  '''CREATE TABLE users(
           id serial PRIMARY KEY,
           name VARCHAR (50),
           phone VARCHAR (50),
           line_id VARCHAR (50),
           created_at VARCHAR (50),
           updated_at VARCHAR (50)
        );'''

cursor.execute(create_table)
conn.commit()



cursor.close()
conn.close()
