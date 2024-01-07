from datetime import datetime

from session import Session


class Message:
    def __init__(self, session_id):
        self.message_id = None
        self.session_id = session_id
        self.timestamp = datetime.now()
        self.role = None
        self.content = None
        self.type = "text"

