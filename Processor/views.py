import pandas as pd
from wordcloud import WordCloud
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
from collections import Counter
from .text_processor import main
from .text_generator import text_generator
import datetime
from .forms import UploadFileForm, LoginForm
from django.core.exceptions import ValidationError
import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import UserRegistrationForm

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('upload_file')
    else:
        form = UserRegistrationForm()
    return render(request, 'Processor/registration/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('upload_file')
    else:
        form = LoginForm()
    return render(request, 'Processor/registration/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('upload_file')

def download_files(request):
    media_root = settings.MEDIA_ROOT  # Получаем корневую папку медиа
    files = os.listdir(media_root)  # Получаем список файлов в папке медиа
    if not files:  # Проверяем, что список файлов пустой
        return render(request, 'Processor/empty_folder.html')  # Отображаем страницу для пустой папки
    # Создаем абсолютные пути к файлам и их метки времени последней модификации
    file_paths_and_mtime = [
        (file, os.path.join(settings.MEDIA_URL, file), os.path.getmtime(os.path.join(media_root, file)))
        for file in files
    ]
    # Сортировка файлов по времени последней модификации (по убыванию)
    file_paths_and_mtime.sort(key=lambda x: x[2], reverse=True)
    # Разделяем список на отдельные списки файлов, меток времени и абсолютных путей
    sorted_files, sorted_file_paths, sorted_mtimes = zip(*file_paths_and_mtime)

    return render(request, 'Processor/download_files.html', {'files': zip(sorted_files, sorted_file_paths)})

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                uploaded_file = form.cleaned_data['file']  # Получаем объект UploadedFile
                main(uploaded_file)
                processed_data = "Файл успешно отправлен на обработку."
                return render(request, 'Processor/upload_success.html', {'processed_data': processed_data})

            except ValidationError as e:
                error_message = "Ошибка валидации файла: {}".format(e)
                return render(request, 'Processor/error.html', {'error_message': error_message})
            except Exception as e:
                error_message = "Произошла ошибка: {}".format(e)
                return render(request, 'Processor/error.html', {'error_message': error_message})
    else:
        form = UploadFileForm()

        return render(request, 'Processor/upload_file.html', {'form': form})
#
# def process_texts_parallel(process_func, df, csv_file, batch_size, num_cores):
#     result_freq = Counter()
#     with Pool(num_cores) as pool, tqdm(total=len(df)//batch_size) as pbar:
#         for lemmas in pool.imap_unordered(process_func, text_generator(csv_file, batch_size)):
#             result_freq.update(lemmas)
#             pbar.update(1)
#     return result_freq
#
# def save_wordcloud_to_file(wordcloud, output_directory, filename):
#     wordcloud.to_file(os.path.join(output_directory, filename))
#
# def save_frequency_to_csv(freq_data, output_directory, filename):
#     # Преобразуем словарь в объект Counter
#     freq_counter = Counter(freq_data)
#     df = pd.DataFrame(freq_counter.most_common(), columns=["Word", "Frequency"])
#     df.to_csv(os.path.join(output_directory, filename), index=False)
#
# def main(uploaded_file):
#     # Создаем папку с текущей датой и временем
#     output_directory = settings.MEDIA_ROOT
#
#     df = pd.read_csv(uploaded_file.temporary_file_path(), sep=";", encoding="utf-8", skiprows=4)
#
#     # Обработка текстов параллельно для каждой части речи
#     batch_size = 1024
#     num_cores = cpu_count()
#
#     def filter_low_frequency_words(word_freq, min_frequency=40):
#         filtered_word_freq = {word: freq for word, freq in word_freq.items() if freq >= min_frequency}
#         return filtered_word_freq
#
#     def save_wordcloud_and_frequency(word_freq, filename_prefix):
#         # Получаем название родительского файла без расширения
#         parent_filename = os.path.splitext(os.path.basename(uploaded_file.name))[0]
#
#         # Получаем текущую дату и время
#         current_datetime = datetime.datetime.now().strftime("%d.%m.%Y-%H:%M")
#
#         # Формируем название файла с родительским файлом и временем создания
#         wordcloud_filename = f"{parent_filename}_{current_datetime}_{filename_prefix}_wordcloud.png"
#         frequency_filename = f"{parent_filename}_{current_datetime}_{filename_prefix}_frequency.csv"
#
#         # Сохраняем облако слов в файл
#         save_wordcloud_to_file(
#             WordCloud(width=800, height=400, background_color="white").generate_from_frequencies(word_freq),
#             output_directory, wordcloud_filename)
#
#         # Сохраняем частоту слов в CSV
#         save_frequency_to_csv(word_freq, output_directory, frequency_filename)
#
#     # Обработка существительных
#     noun_freq = process_texts_parallel(process_nouns, df, uploaded_file.temporary_file_path(), batch_size, num_cores)
#     noun_freq = filter_low_frequency_words(noun_freq, min_frequency=40)
#     save_wordcloud_and_frequency(noun_freq, "Существительные")
#
#     # Обработка прилагательных
#     adj_freq = process_texts_parallel(process_adjectives, df, uploaded_file.temporary_file_path(), batch_size, num_cores)
#     adj_freq = filter_low_frequency_words(adj_freq, min_frequency=40)
#     save_wordcloud_and_frequency(adj_freq, "Прилагательные")
#
#     # Обработка глаголов
#     verb_freq = process_texts_parallel(process_verbs, df, uploaded_file.temporary_file_path(), batch_size, num_cores)
#     verb_freq = filter_low_frequency_words(verb_freq, min_frequency=40)
#     save_wordcloud_and_frequency(verb_freq, "Глаголы")

# if __name__ == "__main__":
#     main()