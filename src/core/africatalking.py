import africastalking
from django.conf import settings

class ATClient:
    def __init__(self):
        username = settings.AFRICA_TALKING_USERNAME
        api_key = settings.AFRICA_TALKING_APIKEY
        if not username or not api_key:
            self.client = None
            self.sms = None
        else:
            africastalking.initialize(username, api_key)
            self.sms = africastalking.SMS

    def send_sms(self, to, message):
        if not self.sms:
            # sandbox/mock fallback
            print(f"[AT MOCK] SMS to={to} message={message}")
            return {'status': 'mocked'}

        try:
            response = self.sms.send(
                message,
                to if isinstance(to, list) else [to],
                sender_id=settings.AFRICA_TALKING_CODE
            )
            return response
        except Exception as e:
            print("Error sending SMS:", e)
            return {'status': 'failed', 'error': str(e)}

africastalking_client = ATClient()
