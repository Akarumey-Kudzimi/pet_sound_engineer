import tkinter.font as tkFont
import soundfile as sf
import tkinter as tk
import numpy as np
import requests
import librosa
import zipfile
import logging
import glob
import time
import sys
import os

from logging.handlers import RotatingFileHandler
from tkinter import filedialog as fd
from PIL import Image, ImageTk


############ Раздел конфигурации ############

# Название файла логирования
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)
LOGGER_NAME_FILE = os.path.join(LOGS_DIR, f'translation_file.log')

# Настройки логирования
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
HANDLER = RotatingFileHandler(LOGGER_NAME_FILE, maxBytes=2 * 1024 * 1024, backupCount=2)
HANDLER.setFormatter(logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s :: %(filename)s :: %(lineno)d'))
LOGGER.addHandler(HANDLER)

# ID адреса Telegram ответственных лиц в случае ошибок
TG_ADRESSES = [
    '1459561428',  # Кузьмин
    '5876518955'   # Карима
]


def send_tg(message):
    """Функция отправки уведомлений в Telegram."""
    tg_adresses = TG_ADRESSES
    for dev_id in tg_adresses:
        token = '7454366026:AAGvVcsEJWQGWaKV6D08ytYtUk-MfuSNA5w'
        url = ('https://api.telegram.org/'
            f'bot{token}/'
            f'sendMessage?chat_id={dev_id}&text=Автоматизатор по удалению тишины из промтов: {message}')
        payloads: dict = {}
        headers: dict = {}
        try:
            try:
                requests.get(url=url, headers=headers, data=payloads, timeout=10)
            except Exception as send_tg_reponse_error:
                LOGGER.exception(f"Произошла ошибка: {send_tg_reponse_error}")
                LOGGER.info('Повторная попытка отправки сообщения в Telegram')
                requests.get(url=url, headers=headers, data=payloads, timeout=10)
        except Exception as send_tg_second_reponse_error:
            LOGGER.exception(f"Произошла ошибка: {send_tg_second_reponse_error}")
            return 'error'
    return 'success'


############ Основной функционал ############

def resource_path(relative_path):
    """Возвращает абсолютный путь к ресурсу, работает и в .exe и в .py"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def trim_silence(y, top_db=35):
    non_silent_intervals = librosa.effects.split(y, top_db=35, frame_length=512, hop_length=128)
    trimmed = np.concatenate([y[start:end] for start, end in non_silent_intervals])
    return trimmed


def cut_silence(path, status_label, progress_label):
    folder_name = os.path.basename(os.path.normpath(path))
    time_stamp = time.strftime('%d_%m_%H-%M', time.localtime())
    output_folder = f'{folder_name}_{time_stamp}'
    processed = 0
    failed = 0
    failed_files = []

    wav_files = [f for f in os.listdir(path) if f.lower().endswith(".wav")]
    total = len(wav_files)
    if not wav_files:
        LOGGER.warning(f"В папке {path} не найдено .wav-файлов. Папка Output не создаётся.")
        status_label.config(text="Нет .wav файлов для обработки", fg="red")
        return

    os.makedirs(output_folder, exist_ok=True)
    for i, filename in enumerate(wav_files, 1):
        full_path = os.path.join(path, filename)
        try:
            LOGGER.info(f"Загрузка файла: {filename}")
            y, sr = librosa.load(full_path, sr=None)
            LOGGER.info(f"Обрезка тишины: {filename}")
            trimmed_audio = trim_silence(y, top_db=35)
            output_path = os.path.join(output_folder, filename)
            sf.write(output_path, trimmed_audio, sr)
            LOGGER.info(f"Успешно сохранён: {output_path}")
            processed += 1
        except Exception as e:
            LOGGER.error(f"Ошибка при обработке {filename}: {e}")
            failed += 1
            failed_files.append(filename)
        # Обновляем прогресс
        progress_label.config(text=f"Идёт обработка промтов. Не закрывайте программу: {i} из {total}")
        progress_label.update_idletasks()

    try:
        with zipfile.ZipFile(f'{output_folder}.zip', 'w') as output_zip:
            for root, dirs, files in os.walk(output_folder):
                for f in files:
                    output_zip.write(os.path.join(root, f), arcname=f)
        LOGGER.info(f"Архив успешно создан: {output_folder}.zip")
    except Exception as e:
        LOGGER.error(f"Ошибка при создании архива: {e}")

    LOGGER.info(f"Готово. Обработано: {processed} файлов, не удалось: {failed}")
    if failed_files:
        LOGGER.error(f"Список промтов с ошибками: {', '.join(failed_files)}")
        send_tg(f"Список промтов с ошибками: {', '.join(failed_files)}")

    progress_label.config(text="")
    status_label.config(
        text=f"Готово. Загружено: {total}, обработано: {processed}, не удалось: {failed}",
        fg="lime" if failed == 0 else "orange"
    )
    send_tg(f"Готово. Загружено: {total}, обработано: {processed}, не удалось: {failed}")


def insert_file(status_label, progress_label):
    file_name = fd.askdirectory()
    LOGGER.info(f"Выбрана папка: {file_name}")
    status_label.config(text="Начинается обработка...", fg="lime")
    root.update_idletasks()
    cut_silence(file_name, status_label, progress_label)


if __name__ == '__main__':
    root = tk.Tk()
    root.title("Питомец - звукорежиссёр")

    window_width = 450
    window_height = 300
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    position_top = int(screen_height / 2 - window_height / 2)
    position_left = int(screen_width / 2 - window_width / 2)
    root.geometry(f'{window_width}x{window_height}+{position_left}+{position_top}')
    root.resizable(True, True)
    root.configure(bg="#050a14")

    fontStyle = tkFont.Font(family="Lucida Grande", size=10)

    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)

    try:
        image_path = None
        for ext in ('png', 'jpg', 'jpeg'):
            possible_path = f'pet_sound_engineer_image.{ext}'
            if os.path.exists(resource_path(possible_path)):
                image_path = resource_path(possible_path)
                break
        if not image_path and os.path.exists(resource_path("pet_sound_engineer_image")):
            image_path = resource_path("pet_sound_engineer_image")

        if image_path:
            img = Image.open(image_path)
            img.thumbnail((240, 190), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            image_label = tk.Label(root, image=photo, bg="#1e1e1e", borderwidth=0, highlightthickness=0)
            image_label.image = photo
            image_label.grid(row=0, column=0, padx=20, pady=10)
        else:
            LOGGER.warning("Изображение pet_sound_engineer_image не найдено")
    except Exception as e:
        LOGGER.error(f"Ошибка загрузки изображения: {e}")

    b1 = tk.Button(
        text="Выбрать папку с аудио",
        height=3,
        width=25,
        command=lambda: insert_file(status_label, progress_label),
        bg='#3c3f41',
        fg='#ffffff',
        activebackground='#555',
        activeforeground='#fff',
        font=fontStyle
    )
    b1.grid(row=0, column=1, padx=10, pady=10, sticky="e")

    progress_label = tk.Label(
        root,
        text="",
        bg="#050a14",
        fg="lime",
        font=("Arial", 10)
    )
    progress_label.grid(row=2, column=0, columnspan=2)

    status_label = tk.Label(
        root,
        text="",
        bg="#050a14",
        fg="lime",
        font=("Arial", 10)
    )
    status_label.grid(row=1, column=0, columnspan=2, pady=(5, 10))

    root.mainloop()
