import pytest
from PIL import Image
from io import BytesIO
from synesthesai.handler.image import ImageHandler


@pytest.fixture
def processor():
    test_image_file = open("tests/data/cartoon_snail.png", "rb")
    handler = ImageHandler(test_image_file)
    test_image_file.close()
    return handler

def test_resize_and_convert(processor):
    # Test resizing a large image
    large_image = Image.new('RGB', (1000, 1000))
    large_image_bytes = BytesIO()
    large_image.save(large_image_bytes, format='JPEG')
    large_image_bytes.seek(0)
    resized_image = processor.resize_and_convert(large_image_bytes)
    assert isinstance(resized_image, BytesIO)

    # Test resizing a small image
    small_image = Image.new('RGB', (100, 100))
    small_image_bytes = BytesIO()
    small_image.save(small_image_bytes, format='JPEG')
    small_image_bytes.seek(0)
    resized_image = processor.resize_and_convert(small_image_bytes, small=True)
    assert isinstance(resized_image, BytesIO)

def test_image_b64(processor):
    # Test encoding a large image
    large_image = Image.new('RGB', (1000, 1000))
    large_image_bytes = BytesIO()
    large_image.save(large_image_bytes, format='JPEG')
    large_image_bytes.seek(0)
    processor.image_file = large_image_bytes
    encoded_image = processor.image_b64
    assert isinstance(encoded_image, bytes)

    # Test encoding a small image
    small_image = Image.new('RGB', (100, 100))
    small_image_bytes = BytesIO()
    small_image.save(small_image_bytes, format='JPEG')
    small_image_bytes.seek(0)
    processor.image_file = small_image_bytes
    encoded_image = processor.image_b64
    assert isinstance(encoded_image, bytes)