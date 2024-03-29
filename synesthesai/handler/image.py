from typing import BinaryIO
import base64
import io
from PIL import Image
from io import BytesIO
from vision.gemini_vision import GeminiVision


class ImageHandler:
    def __init__(self, image_file: BinaryIO) -> None:
        self.image_file = image_file
        
        self.vision_model = GeminiVision(model="models/gemini-pro-vision")
        self.temperature = 1.0
        
        self.max_tokens = 60
        self.description_prompt = """I'm blind, but a friend said I'd love this image. I'm wondering if I could make a playlist that would allow me to experience the same feelings that seeing this image would. What feelings does this image evoke? What kind of genres and which musical artists would be appropriate?"""
        
    def describe(self):
        """Describe the full image."""
        print("Ingested image. Generating description...")
        description = self.vision_model.complete(
            prompt=self.description_prompt, 
            image=self.image_PIL, 
            temperature=self.temperature, 
            max_tokens=self.max_tokens,
        )
        print("Description:", description)
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

    @property
    def image_PIL(self):
        """Return the image as a PIL image."""
        return Image.open(self.image_file)