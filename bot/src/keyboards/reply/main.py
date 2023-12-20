from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

__all__ = [
    "main_panel_kb",
]


main_panel_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=False,
    keyboard=[
        [
            KeyboardButton(
                text="💳 МОЙ КОШЕЛЕК"
            ),
            KeyboardButton(
                text="⁉️ ПОДДЕРЖКА"
            )
        ]
    ]
)
