from aiogram.fsm.state import State, StatesGroup

__all__ = [
    "SendETHStatesGroup",
]


class SendETHStatesGroup(StatesGroup):
    address = State()
    amount = State()
