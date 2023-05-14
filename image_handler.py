import replicate
import streamlit as st
from typing import BinaryIO
import base64
from PIL import Image
from io import BytesIO


class ImageHandler:
    def __init__(self, image_file: BinaryIO) -> None:
        self.model = "pharmapsychotic/clip-interrogator:a4a8bafd6089e1716b06057c42b19378250d008b80fe87caa5cd36d40c1eda90"
        self.api_key = st.secrets["REPLICATE_API_KEY"]
        self.image_file = image_file

    def resize_and_convert(self, image):
        im = Image.open(image)
        # drop alpha channel to make jpeg
        new_image = im.convert("RGB").resize((300, 300))
        buffered = BytesIO()
        new_image.save(buffered, format="JPEG")
        return buffered

    def describe(self):
        # description = "a cartoon snail with a colorful shell on its back, snail, elon musk as slimy mollusk, nacre, art of angrysnail, snail shell, transparent goo, nacre colors, colourful slime, gary, snail in the style of nfl logo, inkscape, it's name is greeny, slimy, cell shaded cartoon, turbo"

        print("Ingested image. Generating description...")
        description = replicate.run(
            self.model, input={"image": self.image_file, "mode": "fast"}
        )
        print("Description:", description)
        return description

    @property
    def image_b64(self):
        """Return the image as an encoded 64bit string"""
        if self.image_file is not None:
            resized = self.resize_and_convert(self.image_file)
            return base64.b64encode(resized.getvalue())
