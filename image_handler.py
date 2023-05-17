from typing import BinaryIO
import base64
from PIL import Image
from io import BytesIO
import streamlit as st
import replicate
import openai

openai.api_key = st.secrets["OPENAI_API_KEY"]


class ImageHandler:
    def __init__(self, image_file: BinaryIO) -> None:
        self.openai_engine = "text-davinci-003"
        self.summary_prompt = "Rewrite this description of an image. Focus on specific emotions, aesthetics, and genres"
        self.openai_temperature = 0.9
        self.model = "pharmapsychotic/clip-interrogator:a4a8bafd6089e1716b06057c42b19378250d008b80fe87caa5cd36d40c1eda90"
        self.image_file = image_file

    def get_summary(self, description):
        response = openai.Completion.create(
            engine=self.openai_engine,
            prompt=f"{self.summary_prompt}: '{description}'",
            temperature=self.openai_temperature,
            max_tokens=60,
        )
        return response.choices[0].text.strip()

    def describe(self, postprocess=False):
        """Describe the full image."""
        print("Ingested image. Generating description...")
        client = replicate.Client(api_token=st.secrets["REPLICATE_API_KEY"])
        description = client.run(
            self.model, input={"image": self.image_file, "mode": "fast"}
        )
        print("Raw description:", description)

        if postprocess:
            # Post-process the description using GPT-3
            description = self.get_summary(description)
            print("Processed description:", description)

        return description

    def resize_and_convert(self, image, small=False):
        dimensions = 768
        if small:
            dimensions = 500

        im = Image.open(image)
        w, h = im.size
        # Thumbnail only works when the images are bigger than the final size
        dimensions = min(dimensions, w, h)
        dimensions = (dimensions, dimensions)

        # drop alpha channel to make jpeg
        new_image = im.convert("RGB")
        new_image.thumbnail(dimensions, Image.Resampling.LANCZOS)
        buffered = BytesIO()
        new_image.save(buffered, format="JPEG")
        print(f"THUMBNAIL SIZE: {buffered.tell()}")
        return buffered

    @property
    def image_b64(self):
        """Return the image as an encoded 64bit string"""
        if self.image_file is not None:
            resized = self.resize_and_convert(self.image_file)
            return base64.b64encode(resized.getvalue())
