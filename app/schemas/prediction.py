from pydantic import BaseModel
from app.models import AlgorithmEnum
from typing import Optional
from typing import Tuple
from typing import List
from app.services.s3_service import S3Service


# class ModelOpinion(BaseModel):
#     disease: str
#     confidence: float
#     box: Tuple[int, int, int, int]  # x1, y1, x2, y2
#     model_name: str
#     class Config:
#         orm_mode = True


# class ModelOpinionOut(BaseModel):
#     disease: str
#     confidence: float
#     box: Tuple[int, int, int, int]
#     model_name: str

#     model_config = {
#         "from_attributes": True
#     }

