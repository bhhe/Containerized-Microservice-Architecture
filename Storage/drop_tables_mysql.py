import mysql.connector

db_conn = mysql.connector.connect(host="<Insert>", user="<Insert>", password="<Insert>", database="<Insert>")

db_cursor = db_conn.cursor()
db_cursor.execute('''
                  DROP TABLE weather, soil
                  ''')

db_conn.commit()
db_conn.close()
