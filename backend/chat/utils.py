import os
import resend
from twilio.rest import Client

def send_employer_alert(guest_token, agent_id, text_payload):
    """
    Triggers immediate external notifications so you never miss an employer interaction.
    """
    short_token = str(guest_token)[:8]
    alert_message = f"🚨 Portfolio Alert! Guest [{short_token}] on node [{agent_id}] says: '{text_payload}'"
    
    # Option A: Twilio WhatsApp Push Notification
    twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_auth = os.getenv("TWILIO_AUTH_TOKEN")
    if twilio_sid and twilio_auth:
        try:
            client = Client(twilio_sid, twilio_auth)
            client.messages.create(
                from_=os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886"),
                body=alert_message,
                to=f"whatsapp:{os.getenv('PERSONAL_PHONE_NUMBER')}"
            )
        except Exception as e:
            print(f"Twilio error: {e}")

    # Option B: Resend Free-tier Immediate Email
    resend_api_key = os.getenv("RESEND_API_KEY")
    if resend_api_key:
        try:
            resend.api_key = resend_api_key
            resend.Emails.send({
                "from": "portfolio@resend.dev",
                "to": os.getenv("PERSONAL_EMAIL"),
                "subject": f"🔥 New Lead on Portfolio Dashboard [{short_token}]",
                "html": f"<p><strong>Agent Node:</strong> {agent_id}</p><p><strong>Message:</strong> {text_payload}</p>"
            })
        except Exception as e:
            print(f"Resend error: {e}")
