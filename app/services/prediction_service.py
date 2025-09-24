import os

from app.providers.llmtunnel_provider import LLMProvider
from typing import List

from typing import List, Dict

from typing import Tuple
from dotenv import load_dotenv
load_dotenv()

PROVIDER_SECRET_KEY = os.getenv("PROVIDER_SECRET_KEY")
PROVIDER_URL = os.getenv("PROVIDER_URL")
PROVIDER_SUBMODEL = os.getenv("PROVIDER_SUBMODEL")


async def run_prediction(prediction_in_url: str, image_size: Tuple[int, int]) -> List[Dict]:

    provider = LLMProvider(
        provider_secret_key=PROVIDER_SECRET_KEY,
        provider_url=PROVIDER_URL,
        provider_submodel=PROVIDER_SUBMODEL
    )
    return await provider.predict(prediction_in_url, image_size)

