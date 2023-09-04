import spacy
import pandas as pd
from wordcloud import WordCloud
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
from collections import Counter
from .text_generator import text_generator
import datetime
from django.conf import settings
import os

# Загрузка модели для русского языка
nlp = spacy.load("ru_core_news_sm")

# Функция для проверки, что лемма соответствует условиям
def is_valid_lemma(token):
    return (
        (3 <= len(token.lemma_) <= 20) and
        not any('a' <= char <= 'z' or 'A' <= char <= 'Z' for char in token.lemma_) and
        not token.lemma_.isdigit()
    )
# Функции для обработки текста и получения списка лемм (начальных форм слов) по каждой части речи
def process_nouns(text):
    doc = nlp(text)
    lemmatized_nouns = [
        token.lemma_ for token in doc
        if (token.pos_ == "NOUN" or token.pos_ == "PROPN") and
        token.lemma_ not in stop_words and
        is_valid_lemma(token)
    ]
    return lemmatized_nouns

def process_adjectives(text):
    doc = nlp(text)
    lemmatized_adjectives = [
        token.lemma_ for token in doc
        if token.pos_ == "ADJ" and
        token.lemma_ not in stop_words and
        is_valid_lemma(token)
    ]
    return lemmatized_adjectives

def process_verbs(text):
    doc = nlp(text)
    lemmatized_verbs = [
        token.lemma_ for token in doc
        if token.pos_ == "VERB" and
        token.lemma_ not in stop_words and
        is_valid_lemma(token)
    ]
    return lemmatized_verbs

stop_words = spacy.lang.ru.stop_words.STOP_WORDS.union("-")


def process_texts_parallel(process_func, df, csv_file, batch_size, num_cores):
    result_freq = Counter()
    with Pool(num_cores) as pool, tqdm(total=len(df)//batch_size) as pbar:
        for lemmas in pool.imap_unordered(process_func, text_generator(csv_file, batch_size)):
            result_freq.update(lemmas)
            pbar.update(1)
    return result_freq

def save_wordcloud_to_file(wordcloud, output_directory, filename):
    wordcloud.to_file(os.path.join(output_directory, filename))

def save_frequency_to_csv(freq_data, output_directory, filename):
    # Преобразуем словарь в объект Counter
    freq_counter = Counter(freq_data)
    df = pd.DataFrame(freq_counter.most_common(), columns=["Word", "Frequency"])
    df.to_csv(os.path.join(output_directory, filename), index=False)

def main(uploaded_file):
    # Создаем папку с текущей датой и временем
    output_directory = settings.MEDIA_ROOT

    df = pd.read_csv(uploaded_file.temporary_file_path(), sep=";", encoding="utf-8", skiprows=4)

    # Обработка текстов параллельно для каждой части речи
    batch_size = 1024
    num_cores = cpu_count()

    def filter_low_frequency_words(word_freq, min_frequency=40):
        filtered_word_freq = {word: freq for word, freq in word_freq.items() if freq >= min_frequency}
        return filtered_word_freq

    def save_wordcloud_and_frequency(word_freq, filename_prefix):
        # Получаем название родительского файла без расширения
        parent_filename = os.path.splitext(os.path.basename(uploaded_file.name))[0]

        # Получаем текущую дату и время
        current_datetime = datetime.datetime.now().strftime("%d.%m.%Y-%H:%M")

        # Формируем название файла с родительским файлом и временем создания
        wordcloud_filename = f"{parent_filename}_{current_datetime}_{filename_prefix}_wordcloud.png"
        frequency_filename = f"{parent_filename}_{current_datetime}_{filename_prefix}_frequency.csv"

        # Сохраняем облако слов в файл
        save_wordcloud_to_file(
            WordCloud(width=800, height=400, background_color="white").generate_from_frequencies(word_freq),
            output_directory, wordcloud_filename)

        # Сохраняем частоту слов в CSV
        save_frequency_to_csv(word_freq, output_directory, frequency_filename)

    # Обработка существительных
    noun_freq = process_texts_parallel(process_nouns, df, uploaded_file.temporary_file_path(), batch_size, num_cores)
    noun_freq = filter_low_frequency_words(noun_freq, min_frequency=40)
    save_wordcloud_and_frequency(noun_freq, "Существительные")

    # Обработка прилагательных
    adj_freq = process_texts_parallel(process_adjectives, df, uploaded_file.temporary_file_path(), batch_size, num_cores)
    adj_freq = filter_low_frequency_words(adj_freq, min_frequency=40)
    save_wordcloud_and_frequency(adj_freq, "Прилагательные")

    # Обработка глаголов
    verb_freq = process_texts_parallel(process_verbs, df, uploaded_file.temporary_file_path(), batch_size, num_cores)
    verb_freq = filter_low_frequency_words(verb_freq, min_frequency=40)
    save_wordcloud_and_frequency(verb_freq, "Глаголы")

if __name__ == "__main__":
    main()


