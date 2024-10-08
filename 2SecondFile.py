import os
import telebot

bot = telebot.TeleBot('8133482651:AAF24DMJ6OFaPSrHuhUeHGQqI6Y-eIqx1wU', parse_mode=None)

films = 'movie.txt'


def load_movies(filename):
    movies_dict = {}
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line:
                    parts = line.split('|')
                    if len(parts) == 3:
                        name, description, image_file = parts
                        movies_dict[name.strip()] = {
                            'description': description.strip(),
                            'image': image_file.strip()
                        }
                    elif len(parts) == 2:
                        # Якщо зображення відсутнє
                        name, description = parts
                        movies_dict[name.strip()] = {
                            'description': description.strip(),
                            'image': None
                        }
        return movies_dict
    except FileNotFoundError:
        print(f"Файл {filename} не знайдено.")
        return {}


user_states = {}
MOVIES = load_movies(films)
IMAGES_DIR = 'photos'


def add_film_to_file(filename, name, description, image_file=None):
    with open(filename, 'a', encoding='utf-8') as file:
        if image_file:
            file.write(f"{name}|{description}|{image_file}\n")
            print("фільм успішно додано")
        else:
            file.write(f"{name}|{description}\n")


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "🎬 <b>Ласкаво просимо до бота-кіноафіші!</b>\n\n"
        "Ви можете виконати наступні команди:\n"
        "➡️ /movies - Показати список фільмів\n"
        "➕ /add_movie - Додати новий фільм('title' ~ 'description')\n"
        "ℹ️ Просто введіть назву фільму, щоб отримати його опис."
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode='HTML')


@bot.message_handler(commands=['movies'])
def list_movies(message):
    movies = ''
    for x, y in MOVIES.items():
        movies += (f"movie list: {x}\n\n "
                   f"enter movie title to check description")
    bot.reply_to(message, movies)


@bot.message_handler(commands=['add_movie'])
def add_movie_step1(message):
    bot.send_message(message.chat.id, "Введіть назву фільму, який ви хочете додати:")
    bot.register_next_step_handler(message, add_movie_step2)


def add_movie_step2(message):
    movie_name = message.text.strip()

    if not movie_name:
        bot.send_message(message.chat.id, "⚠️ Назва фільму не може бути порожньою. Спробуйте ще раз.")
        return
    if movie_name in films:
        bot.send_message(message.chat.id, "❗️ Такий фільм вже є у списку.")
        return
    else:
        user_states[message.chat.id] = {'movie_name': movie_name}
        bot.send_message(message.chat.id, "✏️ Введіть опис фільму:")
        bot.register_next_step_handler(message, add_movie_step3)


def add_movie_step3(message):
    movie_description = message.text.strip()
    if not movie_description:
        bot.send_message(message.chat.id, "⚠️ Опис фільму не може бути порожнім. Спробуйте ще раз.")
        return
    user_states[message.chat.id]['movie_description'] = movie_description
    bot.send_message(message.chat.id, "📷 Відправте зображення фільму або введіть 'пропустити':")
    bot.register_next_step_handler(message, add_movie_step4)


def add_movie_step4(message):
    movie_name = user_states[message.chat.id]['movie_name']
    movie_description = user_states[message.chat.id]['movie_description']

    if message.content_type == 'photo':

        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        image_filename = f"{movie_name.replace(' ', '_')}.jpg"
        image_path = os.path.join(IMAGES_DIR, image_filename)
        with open(image_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        image_file = image_filename
    elif message.text.lower() == 'пропустити':
        image_file = None
    else:
        bot.send_message(message.chat.id, "⚠️ Будь ласка, відправте зображення або введіть 'пропустити'.")
        return

    add_film_to_file(films, movie_name, movie_description, image_file)
    MOVIES[movie_name] = {
        'description': movie_description,
        'image': image_file
    }

    bot.send_message(message.chat.id, f"✅ Фільм '<b>{movie_name}</b>' було успішно додано до списку!",
                     parse_mode='HTML')
    del user_states[message.chat.id]


# def add_film_to_file(movies, movie_name, movie_description, message):
#     movies[movie_name] = {
#         'description': movie_description,
#     }
#     bot.send_message(message.chat.id, f"✅ Фільм '<b>{movie_name}</b>' було успішно додано до списку!",
#                      parse_mode='HTML')
#     del user_states[message.chat.id]


bot.infinity_polling()
