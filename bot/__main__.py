from typing import Callable

from aiohttp.web import Application, RouteTableDef, run_app, Request, json_response, middleware
from aiohttp.web_response import Response

from bot.src.settings import bot, dp, settings
from bot.src.models import engine
from bot.src.models.models import SQLModel
from bot.handlers import echo


@middleware
async def check_telegram_secret_token(request: Request, handler: Callable):
    token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if token is None or token != settings.TELEGRAM_SECRET_TOKEN.get_secret_value():
        return Response(body="incorrect token", status=400)
    return await handler(request)


async def on_startup(app) -> None:  # noqa
    SQLModel.metadata.create_all(bind=engine)
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(
        url=settings.DOMAIN.unicode_string() + "webhook",
        allowed_updates=["message", "callback_query"],
        secret_token=settings.TELEGRAM_SECRET_TOKEN.get_secret_value()
    )
    dp.include_router(router=echo.router)


async def on_shutdown(app) -> None:  # noqa
    await bot.delete_webhook(drop_pending_updates=True)


app = Application(middlewares=[check_telegram_secret_token])
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)


router = RouteTableDef()


@router.post(path="/webhook")
async def get_webhook(request: Request):
    try:
        await dp.feed_raw_update(bot=bot, update=await request.json())
    except Exception as e:
        print(e)
    return json_response(data={"status": "OK"})


app.add_routes(routes=router)


if __name__ == '__main__':
    run_app(
        app=app,
        host="0.0.0.0",
        port=8000
    )
