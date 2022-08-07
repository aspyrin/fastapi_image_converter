from fastapi import FastAPI, File
# from fastapi import UploadFile
from pydantic import BaseModel, AnyHttpUrl, ValidationError, validator
from urllib.request import urlopen
from fastapi.responses import StreamingResponse
from PIL import Image
from io import BytesIO

app = FastAPI()

ALLOWED_EXTENSIONS = {'svg', 'png', 'jpg', 'jpeg', 'gif'}
ROOT_MESSAGE = {
        "app_name": "Image converter",
        "allowed extensions": ALLOWED_EXTENSIONS,
        "paths": {
            "convert_to_grayscale": "/convert-to-grayscale",
            "convert_to_grayscale_from_url": "/convert-to-grayscale-from-url",
        }
    }


class Message(BaseModel):
    url: AnyHttpUrl

    @validator('url')
    def url_has_allowed_ext(cls, value=str):
        link_has_extension = False
        for ext in ALLOWED_EXTENSIONS:
            if f'.{ext}' in value.lower():
                link_has_extension = True
        if not link_has_extension:
            raise ValueError('link not look at image')
        return value


@app.get("/")
async def root():
    return ROOT_MESSAGE


@app.post("/convert-to-grayscale")
async def convert_to_grayscale(file: bytes = File()):
    """
    POST, function receives file, check filename, check extension,
    convert image to grayscale and return it as image/png
    :param file:
    :return: edited image in initial format
    """

    # file size validation
    if len(file) > 0:

        # create PIL object and define it format
        image_source = Image.open(BytesIO(file))
        image_format = image_source.format

        # convert image greyscale
        image_edited = image_source.convert("L")

        # create binary object from edited image
        with BytesIO() as output:
            image_edited.save(output, format=image_format)
            img_bytes_object = output.getvalue()
            img_io_object = BytesIO(img_bytes_object)
            bytes_count = img_bytes_object.__sizeof__()

        # create response
        response: StreamingResponse = StreamingResponse(img_io_object, media_type=f"image/{image_format}")
        response.headers['content-type'] = f"image/{image_format}"
        response.headers['content-length'] = str(bytes_count)
        response.headers['Transfer-Encoding'] = "chunked"

        # send qr-code as attachment for download
        # response.headers["Content-Disposition"] = f"attachment; filename=edited_image.{image_format}"

        return response

    else:
        return "File size 0"


@app.post("/convert-to-grayscale-from-url")
async def convert_to_grayscale_from_url(parameters: Message):
    """
    POST, function receives url, check url, get file from url, check extension,
    convert image to grayscale and return it as image/png
    :param url in JSON:
    :return: edited image in initial format
    """

    # get url from parameters
    try:
        url = parameters.url
    except ValidationError as e:
        return {"Exception": e.json()}

    # get file from url
    try:
        with urlopen(url) as url:
            image_source = Image.open(url)
            image_format = image_source.format

    except Exception as e:
        if e.code == 403:
            return {"Exception": '403 HTTP Error, This Link is forbidden'}
        else:
            return {"Exception": e}

    # convert image greyscale
    image_edited = image_source.convert("L")

    # create binary object from edited image
    with BytesIO() as output:
        image_edited.save(output, format=image_format)
        img_bytes_object = output.getvalue()

    img_io_object = BytesIO(img_bytes_object)
    bytes_count = img_bytes_object.__sizeof__()

    # create response
    response: StreamingResponse = StreamingResponse(img_io_object, media_type=f"image/{image_format}")
    response.headers['content-type'] = f"image/{image_format}"
    response.headers['content-length'] = str(bytes_count)
    response.headers['Transfer-Encoding'] = "chunked"

    # send image_edited as attachment for download
    # response.headers["Content-Disposition"] = f"attachment; filename=edited_image.{image_format}"

    return response
