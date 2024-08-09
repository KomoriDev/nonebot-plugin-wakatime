from nonebot.exception import NoneBotException


class UserUnboundException(NoneBotException):
    """User Not Bound"""


class BindUserException(NoneBotException):
    """Bind User Api Failed"""
