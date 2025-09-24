import re
import time
import json
from openai import OpenAI
from typing import Union
from typing import List
from typing import Tuple

class LLMProvider():

    MAX_TOKENS = 50000

    def __init__(self, provider_secret_key, provider_url, provider_submodel):
        self.provider_secret_key = provider_secret_key
        self.provider_url = provider_url
        self.provider_submodel = provider_submodel

    async def predict(self, image_url: str, image_size: Tuple[int, int]):
        client = OpenAI(
            api_key=self.provider_secret_key,
            base_url=self.provider_url,
        )
        
        photo_result = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Ты дендролог. Тебе нужно посмотреть на фото, и найти на нём дерево или кустарник, или несколько деревьев, которые хотел сфотографировать лесник.
Если ты нашёл, то тебе нужно вернуть мне json в формате (массив для каждого дерева/кустарника):
[
    {
        coord: [x1, y1, x2, y2],
        type: "дерево"/"кустарник",
        breed: "не определено"/"дуб"/"ясень"/"тополь"/"сосна"/"берёза"/", // маленькими русскими буквами, один наиболее вероятный вариант, постарайся предположить
        condition: "нормальное"/"заваливающееся"/"упавшее"/"авариайное"/"пенёк",
        is_dry: true/false, // Засохшее или нет
        percentage_dried: 0...100, // Процент засохших веток. Если зима и/или определить не возможно, то null
        artifacts: ["трещина", "дупло", "грибы", "гниль", "повреждение ствола", "повреждение кроны", "обломанные ветки", "сломанный ствол"], // Возможно несколько вариантов
        description: "..." // понятное свободное описание состояние дерева в 1-2 предложения.
        season: "зима","весна","лето","осень" // один наиболее верояный вариант
    }
]
Если деревьев не найдено, или они далеко, чтобы рассмотреть, то массив будет пустым [].
Не обращай внимания на деревья на заднем плане, если ты видишь, что на переднем доминирует то, которое хотел сфотографировать лесник.
Будь осторожен с тем, чтобы называть деревья берёзой, смотри на нижнюю часть ствола.
coord: [x1, y1, x2, y2] - координаты прямоугольника в пикселях, в которые помещается рассматриваемые дерево или кустарник.
Размер всего изображения в пикселях: """ + f'ширина: {image_size[0]}, высота: {image_size[1]}' + """
Не надо давать больше никаких текстовых пояснений, только чистая json."""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url,
                            "detail": "auto"
                        }}
                ]
            }],
            model=self.provider_submodel,
            max_tokens=LLMProvider.MAX_TOKENS,
        )
        # В прошлый раз с этой api были баги, если не поставить задержку
        # TODO: разобраться в чём была проблема
        time.sleep(0.1)
        results = []
        try:
            response_message = photo_result.choices[0].message.content
            print('response_message', response_message)
            results = LLMProvider.extract_json_from_llm_output(response_message)
            if not isinstance(results, list):
                raise ValueError("Ожидался массив результатов")
        except Exception as e:
            print(f"Ошибка при выполнении запроса к GPT: {e}")

        return results

    @staticmethod
    def extract_json_from_llm_output(text: str) -> Union[dict, list]:
        text = text.replace('```json', '').replace('```', '')
        try:
            return json.loads(text)
        except (AttributeError, json.JSONDecodeError):
            print('Не удалось просто получить json')
        try:
            # Попробуем найти JSON-блок в тексте
            json_str = re.search(r'({.*?}|\[.*?\])', text, re.DOTALL).group(1)
            return json.loads(json_str)
        except (AttributeError, json.JSONDecodeError):
            raise ValueError("Не удалось извлечь корректный JSON из ответа модели.")