from io import BytesIO

from qrcode import QRCode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import RadialGradiantColorMask
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer

__all__ = [
    "create_qrcode",
]


def create_qrcode(payload: str) -> bytes:
    qr = QRCode()
    qr.add_data(data=payload)
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        color_mask=RadialGradiantColorMask()
    )
    io = BytesIO()
    img.save(io)
    io.seek(0)
    return io.read()
