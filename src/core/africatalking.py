from africastalking import AfricasTalking
from django.conf import settings

class ATClient:
    def __init__(self):
        username = settings.AT_USERNAME
        api_key = settings.AT_API_KEY
        if not username or not api_key:
            self.client = None
        else:
            self.client = AfricasTalking(username, api_key)
            self.sms = self.client.SMS

    def send_sms(self, to, message):
        if not self.client:
            # sandbox/mock
            print(f"[AT MOCK] SMS to={to} message={message}")
            return {'status':'mocked'}
        resp = self.sms.send(message, to)
        return resp

africastalking_client = ATClient()