from abc import ABC, abstractmethod
from google_services import get_gmail_service
from email.mime.text import MIMEText
import base64

class Tool(ABC):
    @abstractmethod
    def __init__(self, name: str, usage: str):
        self.name = name
        self.usage = usage
    
    @abstractmethod
    def run(self, *args, **kwargs):
        pass
    
    @abstractmethod
    def get_usage(self) -> str:
        return self.usage
    
class EmailTool(Tool):
    def __init__(self):
        super().__init__(
            name="send_email",
            usage="Uses the gmail API to send an email and returns success message or failure error"
        )        
        self.gmail_service = get_gmail_service()
    
    def run(self, recipient_email: str = None, subject: str = None, body: str = None, closing: str = None) -> str:
        if recipient_email is None or subject is None or body is None or closing is None:
            return "Error in send_email, did not receve a recipient email, subject, body, and closing"
        
        message = MIMEText(body + '\n' + closing)
        message['to'] = recipient_email
        message['subject'] = subject
        message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        try:
            message = self.gmail_service.users().messages().send(userId="me", body={'raw': message}).execute()
            return "Email was sent successfully!"
        except Exception as e:
            return f"Error in send_email: {e}"
    
    def get_usage(self) -> str:
        return super().get_usage()