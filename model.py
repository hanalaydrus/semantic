import requests

class Model(object):
    def request_data(self, camera_id):

        response = {"url" : "", "street_name": "", "latitude": "", "longitude": ""}

        try:
            cameraData = requests.get("http://camera-service:50052/camera/"+ str(camera_id))
        except Exception:
            print("Request Failed, problem with connection")
        else:
            if cameraData.status_code == 200:
                responseCameraData = cameraData.json()
                if responseCameraData["status"] == "success":
                    response = {"url" : responseCameraData["url"], "street_name": responseCameraData["street_name"], "latitude": responseCameraData["latitude"], "longitude": responseCameraData["longitude"]}
                else:
                    print("status request camera data failed")
            else:
                print("request camera data failed")
        
        return response

    def request_data_all(self):

        response = {"url" : "", "street_name": "", "latitude": "", "longitude": ""}

        try:
            cameraData = requests.get("http://camera-service:50052/camera")
        except Exception:
            print("Request Failed, problem with connection")
        else:
            if cameraData.status_code == 200:
                responseCameraData = cameraData.json()
                if responseCameraData["status"] == "success":
                    # response = {"url" : responseCameraData["url"], "street_name": responseCameraData["street_name"], "latitude": responseCameraData["latitude"], "longitude": responseCameraData["longitude"]}
                    response = responseCameraData["data"]
                else:
                    print("status request camera data failed")
            else:
                print("request camera data failed")
        
        return response