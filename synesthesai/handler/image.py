from typing import BinaryIO
import base64
from PIL import Image
from io import BytesIO
import streamlit as st
import replicate
from LLM.openai import OpenAI
from LLM.palm import PaLM




class ImageHandler:

    def __init__(self, image_file: BinaryIO) -> None:
        self.clip_interrogator = "pharmapsychotic/clip-interrogator:a4a8bafd6089e1716b06057c42b19378250d008b80fe87caa5cd36d40c1eda90"
        self.image_file = image_file
        
        self.LLM = PaLM(model="models/text-bison-001")
        self.temperature = 0.7
        # self.LLM = OpenAI(model="text-curie-001")
        # self.temperature = 1.2
        # self.LLM = OpenAI(model="text-davinci-003")
        # self.temperature = 0.9
        self.max_tokens = 60
        self.summary_prompt = """Rewrite this description of this piece of art. Focus on specific emotions, aesthetics, and genres. No more than two sentences.
    ```{description}```
    Summary: """

    def get_summary(self, description):
        prompt = self.summary_prompt.format(description=description)
        print("THIS IS THE PROMPT")
        print(prompt)
        response = self.LLM.complete(
            prompt=prompt,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        return response

    def describe(self, postprocess=True):
        """Describe the full image."""
        print("Ingested image. Generating description...")
        client = replicate.Client(api_token=st.secrets["REPLICATE_API_KEY"])
        # description = client.run(
        #     self.clip_interrogator, input={"image": self.image_file, "mode": "fast"}
        # )
        description = "a tattooed man and a naked woman on the ground, yakuza tattoo on body, hans bellmer and nadav kander, nobuyoshi araki, shunga style, of taiwanese girl with tattoos, by Li Shida, hans bellmer and wlop, sorayama, tattooed man, yakuza slim girl, daido moriyama, ryan mcginley"
        
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
        new_image.save(buffered, format="JPEG", quality=85)
        print(f"THUMBNAIL SIZE: {buffered.tell()}")
        return buffered

    @property
    def image_b64(self):
        """Return the image as an encoded 64bit string"""
        if self.image_file is not None:
            resized = self.resize_and_convert(self.image_file)
            return base64.b64encode(resized.getvalue())