from abc import ABC, abstractmethod

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
            usage="Uses the gmail API to send an email and returns success/failure"
        )
    
    def run(self, recipient_email: str, subject: str, body: str) -> str:
        print("running email tool")
        return str(True)
    
    def get_usage(self) -> str:
        return super().get_usage()