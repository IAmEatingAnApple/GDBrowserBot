import webreqs, asyncio, logging, json
from pprint import pprint
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputFile

logging.basicConfig(level=logging.INFO)

bot = Bot(token="")
dp = Dispatcher(bot)

def delete_first(text):
    return ' '.join(text.split(' ')[1:len(text.split(' '))])

def is_int(str):
    try:
        int(str)
        return True
    except ValueError:
        return False

def add_buttons1(levels = False, page:int = 1):
    markup = InlineKeyboardMarkup(row_width=3)
    if page >= 1:
        left_arrow = InlineKeyboardButton("⬅️", callback_data="prev_page")
    else:
        left_arrow = InlineKeyboardButton(" ", callback_data="none")
    page_num = InlineKeyboardButton(f"{str(page + 1)}", callback_data='none')
    right_arrow = InlineKeyboardButton("➡️", callback_data="next_page")
    markup.add(left_arrow, page_num, right_arrow)

    if levels:
        i = 1
        for item1 in levels:
            markup.add(InlineKeyboardButton(str(i), callback_data=str(item1.id)))
            i+=1
        i = 1

    return markup

def back_button(bb:bool, start:str = "back", sl:str = '', accid:int = 0, page:int = 0, search_term:str = "", author:bool = True, levelid:int = 0):
    markup = InlineKeyboardMarkup(row_width=1)

    if sl != '':
        markup.add(InlineKeyboardButton("Download song", callback_data=f"sl:{sl}"))
    if accid != 0 and author == True and levelid != 0:
        markup.add(InlineKeyboardButton("Author", callback_data=f"a{accid},{page},{search_term},{levelid}"))
    if bb:
        markup.add(InlineKeyboardButton("Back", callback_data=f"{start},{page},{search_term},{accid},{levelid}"))

    return markup

@dp.message_handler(commands=['start'])
async def start_message(message: types.message):
    await message.answer("This is a bot for finding information in Geometry Dash.")

@dp.message_handler(commands=['search'])
async def search_levels(message: types.message):
    search_term = delete_first(message.text)
    if search_term != '':
        if not is_int(search_term):
            lvls = await webreqs.parse(search_term)
            if lvls:
                await message.answer(lvls[0], reply_markup=add_buttons1(lvls[1], 0))
            else:
                await message.answer("No levels were found")
        else:
            r = await webreqs.get_level(int(search_term))
            if r:
                f = InputFile(f"difficulties/{r[1]}")
                
                await bot.send_photo(message.chat.id, f, r[0], reply_markup=back_button(False, sl=r[2], accid=r[3].creator.account_id, levelid=r[3].id))
            else:
                await message.answer("No levels were found")
    else:
        r = await webreqs.parse("")
        await message.answer(r[0], reply_markup=add_buttons1(r[1], 0))

@dp.message_handler(commands=['profile'])
async def search_profile(message: types.message):
    search_term = delete_first(message.text)
    if search_term != '':
        acc = await webreqs.get_account(search_term, True)
        if acc:
            f = InputFile(f"icons/{search_term.lower()}/iconkit.png")
            await bot.send_photo(message.chat.id, f, acc[0])
        else:
            await message.answer("An account with this nickname was not found")
    else:
        await message.answer("You need to type an account name")


@dp.callback_query_handler(lambda c: c.data)
async def call_handler(callback_query: types.CallbackQuery):
    #pprint(json.loads(str(callback_query)))
    if callback_query.data == "next_page":
        page_num = int(callback_query.message['reply_markup']['inline_keyboard'][0][1]['text']) - 1
        search_term = callback_query.message.text.split(':')[0]

        r = await webreqs.parse(search_term, page_num + 1)
        if r:
            await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=r[0], reply_markup=add_buttons1(r[1], page_num + 1))
        else:
            await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=f"{search_term}:\nNo levels were found", reply_markup=add_buttons1(page=page_num + 1))

    if callback_query.data == "prev_page":
        page_num = int(callback_query.message['reply_markup']['inline_keyboard'][0][1]['text']) - 1
        search_term = callback_query.message.text.split(':')[0]

        r = await webreqs.parse(search_term, page_num - 1)
        if r:
            await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=r[0], reply_markup=add_buttons1(r[1], page_num - 1))
        else:
            await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=f"{search_term}:\nNo levels were found", reply_markup=add_buttons1(page=page_num - 1))

    #level search
    if is_int(callback_query.data):
        page_num = int(callback_query.message['reply_markup']['inline_keyboard'][0][1]['text']) - 1
        search_term = callback_query.message.text.split(':')[0]

        r = await webreqs.get_level(int(callback_query.data))
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
        f = InputFile('difficulties/' + r[1])
        await bot.send_photo(callback_query.message.chat.id, f, r[0], reply_markup=back_button(bb = True, sl=r[2], accid=r[3].creator.account_id, page=page_num, search_term=search_term, levelid=int(callback_query.data)))

    if callback_query.data.startswith("back"):
        pg = int(callback_query.data.split(',')[1])
        st = callback_query.data.split(',')[2]

        r = await webreqs.parse(st, pg)
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
        await bot.send_message(callback_query.message.chat.id, r[0], reply_markup=add_buttons1(r[1], pg))

    if callback_query.data.startswith("sl"):
        sl = callback_query.data[3:]
        await bot.send_message(callback_query.message.chat.id, "Downloading song")

        webreqs.get_song(sl)
        f = InputFile('songs/' + sl.split('/')[-1].replace("?", '') + '.mp3')
        await bot.send_audio(callback_query.message.chat.id, f)

        #account
    if callback_query.data.startswith('a'):
        page_num = int(callback_query.data.split(",")[1])
        st = callback_query.data.split(",")[2]
        levelid = callback_query.data.split(",")[-1]

        r = await webreqs.get_account(callback_query.data[1:])
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
        f = InputFile(f"icons/{r[2]}/iconkit.png")
        if st == "":
            await bot.send_photo(callback_query.message.chat.id, f, r[0], reply_markup=back_button(bb=True, start="tolevel", page=page_num, search_term="prosto lvl", author=False, levelid=levelid))
        else:
            await bot.send_photo(callback_query.message.chat.id, f, r[0], reply_markup=back_button(bb=True, start="tolevel", page=page_num, search_term=st, author=False, levelid=levelid))
        
    if callback_query.data.startswith('tolevel'):
        page_num = int(callback_query.data.split(",")[1])
        st = callback_query.data.split(",")[2]

        r = await webreqs.get_level(int(callback_query.data.split(",")[-1]))
        #print(r)
        bb = False
        if callback_query.data.split(",")[2] != "":
            bb = True
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
        f = InputFile('difficulties/' + r[1])
        if st == "prosto lvl":
            await bot.send_photo(callback_query.message.chat.id, f, r[0], reply_markup=back_button(bb = bb, sl=r[2], accid=r[3].creator.account_id, page=page_num, search_term="", levelid=int(callback_query.data.split(",")[-1])))
        else:
            await bot.send_photo(callback_query.message.chat.id, f, r[0], reply_markup=back_button(bb = bb, sl=r[2], accid=r[3].creator.account_id, page=page_num, search_term=st, levelid=int(callback_query.data.split(",")[-1])))

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
