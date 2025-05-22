



class ChatUser:
    ...


class Chat(ChatUser):

    def __init__(self, user1: User, user2: User, msg: str) -> None:
        self.user1: User = user1
        self.user2: User = user2
        self.msg: str = msg

    