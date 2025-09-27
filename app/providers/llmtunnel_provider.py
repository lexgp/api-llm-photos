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
                        "text": """Ты дендролог. На фото нужно найти одно дерево или кустарник, которое хотел сфотографировать лесник.
Выбирай по строгому приоритету:
1. В первую очередь выбери наиболее проблемное (сухое, повреждённое, упавшее, пенёк, сухостой)
2. Если несколько, выбери тот, что в фокусе и ближе к наблюдателю.
3. Если их несколько, дерево в центре кадра..
Важно:
- ЕСЛИ ты не видишь достоверного дерева/кустарника НА ПЕРЕДНЕМ ПЛАНЕ, то ответ = null. Никаких других ответов. 
- Игнорируй задний план.
- Если дерева/кустарника нет или объект слишком далеко — верни null.

Координаты bbox: [x1, y1, x2, y2] должны описывать ствол целиком (вытянутый вертикально прямоугольник). Не включай крону, соседние деревья или фон.
Формат ответа строго JSON, без пояснений:
```json
{
  "bbox": [x1, y1, x2, y2],
  "type": "дерево" | "кустарник",
  "breed": "не определено" | "дуб" | "ясень" | "тополь" | "сосна" | "берёза" | "вяз" | "клён" | "ель",
  "condition": "нормальное" | "заваливающееся" | "упавшее" | "авариайное" | "не удовлетворительное" | "пенёк",
  "is_dry": true | false,
  "percentage_dried": 0–100,
  "artifacts": ["трещина", "дупло", "содранная кора", "обнажены корни", "грибы", "гниль", "повреждение ствола", "повреждение кроны", "обломанные ветки", "сломанный ствол"],
  "description": "Краткое описание состояния дерева (1–2 предложения).",
  "season": "вегетативный" | "не вегетативный"
}
```
Если сезон не вегетативный, то выводы о сухости должны быть крайне осторожными, скорее нет чем да.
Не выдумывай повреждения, если не уверен, трудно рассмотреть, значит не фиксируй повреждения. Важна уверенность.
Размер изображения: ширина {image_size[0]}, высота {image_size[1]}.
Координаты: x — слева направо, y — сверху вниз. (0,0) — верхний левый угол.
bbox: [x1, y1, x2, y2] — x1,y1 = верхний левый, x2,y2 = нижний правый.
Требования: все значения — целые числа, x1 < x2, y1 < y2, 0 ≤ x1 < {image_size[0]}, 0 ≤ y1 < {image_size[1]}, 0 < x2 ≤ {image_size[0]}, 0 < y2 ≤ {image_size[1]}.

Перед выводом JSON выполни внутреннюю проверку согласованности:
1) Убедись, что bbox действительно содержит ствол того объекта, который описываешь.
2) Вычисли центр bbox = ((x1+x2)/2, (y1+y2)/2). Если центр bbox не попадает в центральную зону (см. ниже) и рядом есть другой кандидат ближе к центру — выбери его.
3) Если не можешь однозначно сопоставить описание и bbox — верни null.

bbox должен охватывать ствол целиком: обычно вертикальный прямоугольник (высота >> ширина).
Минимум: высота bbox ≥ 15% высоты изображения и ширина bbox ≤ 60% ширины изображения.
Не включай в bbox окружающую крону и соседние деревья.

ЕСЛИ ты не видишь достоверного дерева/кустарника НА ПЕРЕДНЕМ ПЛАНЕ, то ответ = null. Никаких других ответов. 
Ещё раз - игнорируй задний план фото, игнорируй деревья в далеке. Если спереди в близи деревьев нет, верни null

"""
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
            temperature=0,
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