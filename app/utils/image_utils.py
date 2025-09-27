import io
import os
import base64

from uuid import uuid4
from pathlib import Path
from PIL import Image
from fastapi import UploadFile
from typing import Tuple
from io import BytesIO

TARGET_SIZE = (640, 640)

def get_image_size(file: BytesIO) -> Tuple[int, int]:
    image = Image.open(file)
    width, height = image.size
    file.seek(0)
    return width, height

def get_file_s3name(file: UploadFile) -> str:
    ext = Path(file.filename).suffix or ".jpg"
    filename = f"{uuid4().hex}{ext}"
    return filename

def save_to_media(file: UploadFile, subdirectory) -> Path:
    MEDIA_DIR = Path("media/" + subdirectory)
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    # TODO: есть смысл по дате раскидывать
    ext = Path(file.filename).suffix or ".jpg"
    filename = f"{uuid4().hex}{ext}"
    file_path = MEDIA_DIR / filename

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    return file_path


def resize_image(image_path: Path, size: Tuple[int, int] = TARGET_SIZE) -> Path:
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        img.thumbnail(size, Image.LANCZOS)

        # Создание нового холста с белым фоном
        new_img = Image.new("RGB", size, (255, 255, 255))
        offset = (
            (size[0] - img.width) // 2,
            (size[1] - img.height) // 2
        )
        new_img.paste(img, offset)

        # Сохраняем с суффиксом
        resized_path = image_path.with_stem(image_path.stem + "_resized")
        new_img.save(resized_path, format="JPEG")

    return resized_path

def resize_to_square(image: Image.Image, size: int = 1024) -> Image.Image:
    # масштабируем картинку с сохранением пропорций
    image.thumbnail((size, size), Image.Resampling.LANCZOS)
    # создаём квадратный холст
    new_img = Image.new("RGB", (size, size), (0, 0, 0))
    # вставляем в центр
    offset = ((size - image.width) // 2, (size - image.height) // 2)
    new_img.paste(image, offset)
    return new_img

async def get_base64_image(file: UploadFile):
        # читаем байты
    file_bytes = await file.read()

    # открываем картинку
    try:
        image = Image.open(io.BytesIO(file_bytes))
    except Exception:
        raise Exception("Некорректный формат изображения")

    # приводим к 1024×1024 с паддингами
    image_resized = resize_to_square(image, 1024)

    # сохраняем в JPEG в память
    buffer = io.BytesIO()
    image_resized.save(buffer, format="JPEG", quality=95)
    buffer.seek(0)

    # кодируем в base64
    b64_str = base64.b64encode(buffer.read()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64_str}"
