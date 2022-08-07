from fastapi import FastAPI, File
from fastapi.responses import StreamingResponse
from PIL import Image
from io import BytesIO

app = FastAPI()


@app.get("/")
async def root():
    message = {
        "app_name": "Image converter",
    }
    return message


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
