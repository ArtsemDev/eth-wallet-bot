from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters.command import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BufferedInputFile, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from bot.src.keyboards.reply import main_panel_kb
from bot.src.keyboards.inline import WalletCallbackData, wallet_panel_ikb, wallet_create_ikb
from bot.src.models import session_maker, User
from bot.src.settings import web3
from bot.src.states import SendETHStatesGroup
from bot.src.utils import create_qrcode

__all__ = ["router"]


router = Router()


@router.message(CommandStart())
async def start(message: Message):
    user = User(id=message.from_user.id)
    with session_maker() as session:  # type: Session
        session.add(instance=user)
        try:
            session.commit()
        except IntegrityError:
            text = "Привет! Давно не виделись!"
        else:
            text = "Привет! Я Бот - Эфириум Кошелек!"
        finally:
            await message.answer(
                text=text,
                reply_markup=main_panel_kb
            )


@router.message(F.text == "⁉️ ПОДДЕРЖКА")
async def support(message: Message):
    await message.delete()
    await message.answer(
        text='<a href="https://t.me/thommyserpentes">Поддержка</a>'
    )


@router.message(F.text == "💳 МОЙ КОШЕЛЕК")
async def wallet(message: Message):
    with session_maker() as session:  # type: Session
        user = session.get(User, message.from_user.id)

    if user.wallet_address is None:
        await message.answer(
            text="Чтобы создать кошелек, нажмите кнопку ниже 👇",
            reply_markup=wallet_create_ikb
        )
    else:
        account = web3.eth.account.from_key(user.wallet_key)
        balance = web3.eth.get_balance(account.address)
        await message.answer_photo(
            photo=BufferedInputFile(
                file=create_qrcode(payload=account.address),
                filename=f"{account.address}.png"
            ),
            caption=f"`{account.address}`\n\n{web3.from_wei(balance, 'ether')}",
            reply_markup=wallet_panel_ikb,
            parse_mode=ParseMode.MARKDOWN
        )


@router.callback_query(WalletCallbackData.filter(F.action == "create"))
async def create_wallet(callback: CallbackQuery):
    await callback.message.delete()
    account, mnemonic = web3.eth.account.create_with_mnemonic()
    with session_maker() as session:  # type: Session
        session.execute(
            update(User)
            .filter_by(id=callback.from_user.id)
            .values(wallet_address=account.address, wallet_key=account.key)
        )
        session.commit()
    balance = web3.eth.get_balance(account.address)
    await callback.message.answer_photo(
        photo=BufferedInputFile(
            file=create_qrcode(payload=account.address),
            filename=f"{account.address}.png"
        ),
        caption=f"`{account.address}`\n\n"
                f"{web3.from_wei(balance, 'ether')}\n\n"
                f"Запиши Вашу мнемоническую фразу, для возможности восстановления кошелька:\n\n"
                f"`{mnemonic}`",
        reply_markup=wallet_panel_ikb,
        parse_mode=ParseMode.MARKDOWN
    )


@router.callback_query(WalletCallbackData.filter(F.action == "reject"))
async def reject_send_eth(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    with session_maker() as session:  # type: Session
        user = session.get(User, callback.from_user.id)

    account = web3.eth.account.from_key(user.wallet_key)
    balance = web3.eth.get_balance(account.address)
    if callback.message.photo:
        await callback.message.edit_caption(
            caption=f"`{account.address}`\n\n"
                    f"{web3.from_wei(balance, 'ether')}\n\n",
            reply_markup=wallet_panel_ikb,
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await callback.message.answer_photo(
            photo=BufferedInputFile(
                file=create_qrcode(payload=account.address),
                filename=f"{account.address}.png"
            ),
            caption=f"`{account.address}`\n\n"
                    f"{web3.from_wei(balance, 'ether')}\n\n",
            reply_markup=wallet_panel_ikb,
            parse_mode=ParseMode.MARKDOWN
        )


@router.callback_query(WalletCallbackData.filter(F.action == "send"))
async def send_eth(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(state=SendETHStatesGroup.address)
    await callback.message.edit_caption(
        caption="Введите кошелек получателя:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="ОТМЕНИТЬ", callback_data=WalletCallbackData(action="reject").pack())]]
        )
    )


@router.message(SendETHStatesGroup.address)
async def get_recipient_address(message: Message, state: FSMContext):
    await message.delete()
    await state.update_data(recipient_address=message.text)
    await state.set_state(state=SendETHStatesGroup.amount)
    await message.answer(
        text="Введите количество:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="ОТМЕНИТЬ", callback_data=WalletCallbackData(action="reject").pack())]]
        )
    )


@router.message(SendETHStatesGroup.amount)
async def send_transaction(message: Message, state: FSMContext):
    await message.delete()
    state_data = await state.get_data()
    if message.text.isdigit():
        with session_maker() as session:  # type: Session
            user = session.get(User, message.from_user.id)
        amount = web3.to_wei(float(message.text), "ether")
        try:
            hash = web3.eth.send_transaction(transaction={
                "from": user.wallet_address,
                "to": state_data.get("recipient_address"),
                "value": amount
            })
        except ValueError:
            await message.answer(
                text="Недостаточно средств, укажите сумму меньше:",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text="ОТМЕНИТЬ",
                                              callback_data=WalletCallbackData(action="reject").pack())]]
                )
            )
        else:
            await state.clear()
            account = web3.eth.account.from_key(user.wallet_key)
            balance = web3.eth.get_balance(account.address)
            await message.answer_photo(
                photo=BufferedInputFile(
                    file=create_qrcode(payload=account.address),
                    filename=f"{account.address}.png"
                ),
                caption=f"Транзакция успешно отправлена!\n\n`{account.address}`\n\n{web3.from_wei(balance, 'ether')}",
                reply_markup=wallet_panel_ikb,
                parse_mode=ParseMode.MARKDOWN
            )
    else:
        await message.answer(
            text="Неверные данные, проверьте правильность и повторите ввод:",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="ОТМЕНИТЬ", callback_data=WalletCallbackData(action="reject").pack())]]
            )
        )
