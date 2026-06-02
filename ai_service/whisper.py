import tempfile
from .openai_client import client


def transcribe_audio(audio_file):
    with tempfile.NamedTemporaryFile(
        suffix='.webm',
        delete=False
    ) as temp_audio:

        for chunk in audio_file.chunks():
            temp_audio.write(chunk)

        temp_audio_path = temp_audio.name

    with open(temp_audio_path, 'rb') as file:
        transcription = client.audio.transcriptions.create(
            model='whisper-1',
            file=file,
            language='ru',
            prompt='Расшифруй только произнесённую речь. Тебе КАТЕГОРИЧЕСКИ запрещено добавлять пояснения, комментарии, заголовки или лишний текст! Ты должен расшифровывать только произнесённую речь, без всяких дополнительных слов. Если ты не уверен в том, что было сказано, то просто пропусти эти слова и не добавляй ничего лишнего! Ты должен строго следовать этим инструкциям и не добавлять ничего, кроме расшифровки произнесённой речи!'
        )

    return transcription.text