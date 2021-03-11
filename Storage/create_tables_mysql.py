import mysql.connector
db_conn = mysql.connector.connect(host="<Insert>", user="<Insert>", password="<Insert>", database="<Insert>")

db_cursor = db_conn.cursor()
db_cursor.execute('''
                  CREATE TABLE weather
                  (id INT NOT NULL AUTO_INCREMENT, 
                   plot_id VARCHAR(250) NOT NULL,
                   tracker_id VARCHAR(250) NOT NULL,
                   relative_humidity INTEGER NOT NULL,
                   low NUMERIC NOT NULL,
                   high NUMERIC NOT NULL,
                   avg NUMERIC NOT NULL,
                   notation VARCHAR(50) NOT NULL,
                   timestamp VARCHAR(100) NOT NULL,
                   date_created VARCHAR(100) NOT NULL,
                   CONSTRAINT weather_pk PRIMARY KEY(id))
                  ''')

db_cursor.execute('''
                  CREATE TABLE soil
                  (id INT NOT NULL AUTO_INCREMENT, 
                   plot_id VARCHAR(250) NOT NULL,
                   tracker_id VARCHAR(250) NOT NULL,
                   ph_level INTEGER NOT NULL,
                   phosphorus INTEGER NOT NULL,
                   saturation INTEGER NOT NULL,
                   timestamp VARCHAR(100) NOT NULL,
                   date_created VARCHAR(100) NOT NULL,
                   CONSTRAINT weather_pk PRIMARY KEY(id))
                  ''')


db_conn.commit()
db_conn.close()
