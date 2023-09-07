import requests
import json

SERVER_TOKEN = 'AAAA6japnAg:APA91bFRhS17WJembrSYRlZD9jexClyA8uZg0in5Ch1045G4uzkNT1BTqXHnVB6wXMa2SpH6nvKITUrSnlE8h2odNIuYodFci85_h4Bkf6Wwz0ajPRsnh7pKfbQR6G6hiNK4MkmC9ay4'
class Firebase:
    def __init__(self):
        pass

    def send(self,registrations_ids, message):
        fields = {
            # 'registration_ids' : registrations_ids,
            'to' : registrations_ids,
            'data' : message,
        }
        return self.send_push_notification(fields)

    def send_push_notification(self,fields):
        # firebase server url to send the curl request
        url = 'https://fcm.googleapis.com/fcm/send'

        # building headers for the request
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'key=' + SERVER_TOKEN,
        }

        # body = {
        #         'notification': {'title': 'Sending push form python script',
        #                             'body': 'New Message'
        #                             },
        #         'to':
        #             deviceToken,
        #         'priority': 'high',
        #         #   'data': dataPayLoad,
        #         }
        # data = {
        #     "registration_ids": "dQDHpqOsS-SSl7Ry8x4C5d:APA91bEVk38hVSWpl3k9iIQCMb732lW_VRo0ji9NU_0cIdW5MbzUZUP-bXsmpCe21LPW2eUeZAUk18bF-twmUJx0RJ3tCvgqg0La7ArCXDP8iWV7AXhzELsEdWFwz19C7KrquLbPrCc9", 
        #     "data": 'nothing'}

        data = json.dumps(fields)
        response = requests.post(url,headers=headers, data=data,)

        print(response)

        # print(response)
        # print(response.status_code)

        return True