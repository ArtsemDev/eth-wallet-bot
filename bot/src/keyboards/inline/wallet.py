from typing import Literal

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

__all__ = [
    "WalletCallbackData",
    "wallet_panel_ikb",
    "wallet_create_ikb",
]


class WalletCallbackData(CallbackData, prefix="wallet"):
    action: Literal["create", "send", "reject"]


wallet_panel_ikb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="ОТПРАВИТЬ ETH",
                callback_data=WalletCallbackData(action="send").pack()
            )
        ]
    ]
)

wallet_create_ikb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="СОЗДАТЬ КОШЕЛЕК",
                callback_data=WalletCallbackData(action="create").pack()
            )
        ]
    ]
)
