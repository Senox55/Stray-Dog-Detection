import json
import aiogram
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile, InputMediaPhoto
from aiogram import F

from dataset import Dataset, Decomposition
from model import Model

BOT_TOKEN = '7348573908:AAGCRzkrpRYPmFocrRBTnXVkes_rZ_-HspI'

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

model = Model()
embeddings = []
filelist = []
with open('dataset', 'r') as file:
    line = json.load(file)

    for image in line['filelist']:
        embeddings.append(model.extract_features(image))
        filelist.append(image)


decomposition = Decomposition(embeddings)
pca_embeddings = decomposition.do_decomposition(embeddings)

@dp.message(Command(commands=["start"]))
async def process_start_command(message: Message):
    await message.answer(
        'Привет, скинь фото своего питомца, а я поищу его в базе потерявшихся')


@dp.message(F.photo)
async def handle_photo(message: Message):

    user_id = message.from_user.id

    photo = message.photo[-1]

    file_info = await bot.get_file(photo.file_id)

    photo_path = f"photos.png"
    await bot.download_file(file_info.file_path, photo_path)
    features = model.extract_features(photo_path)
    features = features.reshape(1, -1)
    pca_features = decomposition.do_decomposition(features)
    photo_paths = model.find_similar(pca_features.flatten(), pca_embeddings, filelist)
    media = []
    for path in photo_paths:
        media.append(InputMediaPhoto(media=FSInputFile(path)))

    # Отправляем фото в одном сообщении
    for url in media:
        print("Media URL:", url)
    try:
        await bot.send_media_group(chat_id=user_id, media=media)
    except aiogram.exceptions.TelegramBadRequest as e:
        print(f"Error sending media group: {e}")


@dp.message()
async def send_back(message: Message):
    input_text = message.text
    print(input_text)


if __name__ == '__main__':
    dp.run_polling(bot)