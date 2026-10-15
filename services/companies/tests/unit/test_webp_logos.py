import base64
import io

from PIL import Image

from tests.unit.test_logos import COMPANY_ID, company, sign_in  # noqa: F401 (fixture)

URL = f"/companies/{COMPANY_ID}/logo"


def webp(mode="RGBA") -> bytes:
    out = io.BytesIO()
    Image.new(mode, (4, 4), (200, 30, 30, 128) if mode == "RGBA" else (200, 30, 30)).save(
        out, "WEBP", lossless=True
    )

    return out.getvalue()


def test_a_webp_logo_is_kept_as_png_with_its_transparency(client, company):  # noqa: F811
    _, saved = company
    sign_in("bob")

    response = client.put(URL, json={"image": base64.b64encode(webp()).decode()})

    assert response.status_code == 200
    content, media_type = saved["logo"]
    assert media_type == "image/png"
    stored = Image.open(io.BytesIO(content))
    assert (stored.format, stored.mode) == ("PNG", "RGBA")
    assert stored.getpixel((0, 0)) == (200, 30, 30, 128)


def test_a_webp_that_cant_be_read_is_refused(client, company):  # noqa: F811
    _, saved = company
    sign_in("bob")
    broken = base64.b64encode(b"RIFF\x00\x00\x00\x00WEBPVP8 broken").decode()

    assert client.put(URL, json={"image": broken}).status_code == 422
    assert saved == {}
