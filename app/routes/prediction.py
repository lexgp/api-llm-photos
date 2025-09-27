from app.utils.image_utils import get_file_s3name, get_image_size, get_base64_image
from app.services.prediction_service import run_prediction
from app.services.s3_service import S3Service
from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File
from fastapi import HTTPException
from typing import List

router = APIRouter()

@router.post("/predict/")
async def predict(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="Файл не загружен")

    prediction_in_url = await get_base64_image(file)
    # image_size = get_image_size(file.file)
    image_size = (1024, 1024)

    # s3_service = S3Service()
    # prediction_in_name = get_file_s3name(file)
    # prediction_in_url = await s3_service.upload_file(file.file, prediction_in_name)
    tree = await run_prediction(prediction_in_url, image_size)

    return {
        'trees': [tree] if tree else [],
        'photo_url': prediction_in_url,
    }
