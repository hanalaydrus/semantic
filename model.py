import datetime
import mysql.connector

class Model():
    def run(id):
        cnx = mysql.connector.connect(user='root', password='root',
                                    host='127.0.0.1',
                                    database='camera')
        cursor = cnx.cursor()

        query = ("SELECT url, street_name, latitude, longitude FROM camera WHERE camera_id=%s")

        cursor.execute(query, (id,))

        for (url, street_name, latitude, longitude) in cursor:
            response = {'url' : url, 'street_name': street_name, 'latitude': latitude, 'longitude': longitude}

        cursor.close()
        cnx.close()
        
        return response