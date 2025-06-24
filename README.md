# 🎧 Питомец — звукорежиссёр

Графическая утилита для автоматического удаления тишины из `.wav`-аудиофайлов. Программа обрабатывает аудио в выбранной папке, удаляет тишину, сохраняет результат в отдельную папку и автоматически архивирует его.

## 🖥 Основные возможности

- Удаление тишины с помощью библиотеки `librosa`.
- Поддержка `.wav`-файлов.
- Удобный графический интерфейс на `tkinter`.
- Информативный статус обработки и прогресс.
- Автоматическое логирование работы в `logs/translation_file.log`.
- Уведомление в Telegram о результатах обработки и ошибках.
- Создание `.zip`-архива с обработанными файлами.

## 📦 Установка зависимостей

Создай и активируй виртуальное окружение, затем установи зависимости:

```bash
pip install -r requirements.txt
```
---

## 📦 Сбор exe-файла
- Необходимо в интерфейсе auto-py-to-exe добавить ряд библиотек:
   - --hidden-import=tkinter.font
   - --hidden-import=PIL.Image
   - --hidden-import=PIL.ImageTk
   - --hidden-import=logging.handlers
   - --hidden-import=librosa
   - --hidden-import=soundfile
   - --hidden-import=requests
   - --hidden-import=scipy._lib
   - --hidden-import=scipy._lib._util
   - --hidden-import=scipy._cython_utils
   - --hidden-import=scipy._cython_utils._cyutility
   - --collect-submodules=librosa
   - --collect-submodules=soundfile
   - --collect-submodules=scipy

## 👨‍💻 Автор

Разработал: Кузьмин Ярослав

---

## 📧 Контакты

- **Telegram**: [@ProsvetovYaroslav](https://t.me/ProsvetovYaroslav)
- **Email**: [ykuzmin@fromtech.ru](mailto:ykuzmin@fromtech.ru)
