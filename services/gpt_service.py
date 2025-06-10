from g4f.client import Client
import g4f
import re
import time

def is_russian_text(text: str) -> bool:
    """Проверяет, что в тексте нет китайских иероглифов."""
    return not re.search(r"[\u4e00-\u9fff]", text)

def get_gpt_response(client: Client, prompt: str, text_chunk: str) -> str:
    """Отправляет текст в GPT и проверяет, содержит ли он только русские буквы."""
    max_attempts = 20  # Максимальное количество попыток
    attempt = 0

    while attempt < max_attempts:
        attempt += 1
        print(f"Запрос к GPT, попытка {attempt}...")

        try:
            response = client.chat.completions.create(
                model= g4f.models.default,
                provider=g4f.Provider.Yqcloud,
                messages=[{"role": "user", "content": prompt + text_chunk}],
                stream=True
            )

            chunk_result = ""
            for message in response:
                if message.choices and message.choices[0].delta:
                    content = message.choices[0].delta.content
                    if content:
                        chunk_result += content
                        # print(content, flush=True, end='')

            # Проверяем, состоит ли ответ только из русских символов
            if is_russian_text(chunk_result):
                print("Ответ GPT содержит только русские буквы.")
                return chunk_result.strip()
            else:
                print("Ответ GPT содержит нерусские символы, повторяем запрос...")
                time.sleep(5)  # Небольшая задержка перед повторной попыткой

        except Exception as e:
            print(f"Ошибка при запросе к GPT: {e}")

    print("Не удалось получить корректный ответ от GPT после нескольких попыток.")
    return ""

def generate_text_with_gpt(text: str) -> str:
    """Разбивает текст на части по 500 слов и отправляет в GPT."""
    if not text.strip():
        print("Передан пустой текст.")
        return ""

    client = Client()
    prompt = "Вот распознанный текст, исправь ошибки допущенные при распознавании, сделай читабельно и сделай красивое форматирование текста для pdf формата и не используй Markdown. Результат напиши на русском языке и не дописывай больше ничего лишнего а только результат верни:\n\n"
    words = text.split()
    result = ""

    for i in range(0, len(words), 1000):
        chunk = " ".join(words[i:i + 1000])  # Формируем блок по 1000 слов
        processed_chunk = get_gpt_response(client, prompt, chunk)

        if processed_chunk:
            result += processed_chunk + "\n"

        time.sleep(10)  # Задержка между запросами

    return result.strip()

def generate_text_ideas_with_gpt(text: str, prompt: str) -> str:
    """Разбивает текст на части по 500 слов и отправляет в GPT."""
    if not text.strip():
        print("Передан пустой текст.")
        return ""

    client = Client()
    words = text.split()
    result = ""

    for i in range(0, len(words), 500):
        chunk = " ".join(words[i:i + 500])  # Формируем блок по 500 слов
        processed_chunk = get_gpt_response(client, prompt, chunk)

        if processed_chunk:
            if 'False' not in processed_chunk:
                result += processed_chunk + "\n"

        time.sleep(10)  # Задержка между запросами

    return result.strip()