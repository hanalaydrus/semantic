import requests

class Model(object):
    def request_data(self, camera_id):
        # cnx = mysql.connector.connect(user='root', password='root',
        #                             host='127.0.0.1',
        #                             database='camera')
        # cursor = cnx.cursor()

        # query = ("SELECT url, street_name, latitude, longitude FROM camera WHERE camera_id=%s")

        # cursor.execute(query, (id,))

        # for (url, street_name, latitude, longitude) in cursor:
        #     response = {'url' : url, 'street_name': street_name, 'latitude': latitude, 'longitude': longitude}

        # cursor.close()
        # cnx.close()

        response = {'url' : '', 'street_name': '', 'latitude': '', 'longitude': ''}

        try:
            cameraData = requests.get('http://camera-service:50052/camera/'+ str(camera_id))
        except Exception:
            print("Request Failed, problem with connection")

        if cameraData.status_code == 200:
            responseCameraData = cameraData.json()
            if responseCameraData['status'] == 'success':
                print("status success")
                response = {'url' : responseCameraData['url'], 'street_name': responseCameraData['street_name'], 'latitude': responseCameraData['latitude'], 'longitude': responseCameraData['longitude']}
            else:
                print("status failed")
        else:
            print("failed")
        
        return response