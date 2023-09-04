import pandas as pd

# Функция для генерации текстов из файла в определенных пакетах
def text_generator(filename, batch_size):
    for chunk in pd.read_csv(filename, sep=";", encoding="utf-8", chunksize=batch_size, skiprows=4):
        texts = chunk["Текст"].dropna()
        for text in texts:
            yield text
