import requests, os, time, iconkit, math, gd, asyncio, diffs
from threading import Thread
from pprint import pprint

forms = ['cube', 'ship', 'ball', 'ufo', 'wave', 'robot', 'spider']
client = gd.Client()

async def parse(search_term, page = 0):
    try:
        print(f"Searching: {search_term}. Page: {page + 1}")
        levels = await client.search_levels_on_page(page=page, query=search_term)
        search_result = f'{search_term}:\n'
        i = 1
        for item in levels:
            search_result += f"{i}: \"{item.name}\" by {item.creator}\n"
            i += 1
        return search_result, levels
    except Exception as e:
        print(e)
        return False

async def get_level(id:int):
    sl = ''
    try:
        print(f"Getting level: {id}")
        level = await client.get_level(id)
    
        raw_sl = False
        if level.song.dl_link:
            raw_sl = level.song.dl_link

        level_diff, diff = diffs.convert(level)
        s = ''
        if level.stars != 0:
            s = f"(rated: {level.stars}*)"
        result = f"ID: {level.id}\n\nName: {level.name}\nCreator: {level.creator}\n\nDifficulty: {diff} {s}\nDownloads: {level.downloads}\nLikes: {level.rating}\nLength: {diffs.convert_length(level.length)}\n\nMusic:\nName: {level.song.name}\nAuthor: {level.song.author}"
        
        if raw_sl:
            sl = '/'.join(raw_sl.split('/')[3:len(raw_sl.split('/'))])
            if "https://audio.ngfiles.com" in raw_sl:
                sl = '0' + sl
            elif "http://audio.ngfiles.com" in raw_sl:
                sl = '1' + sl
            elif "geometrydashcontent" in raw_sl:
                sl = '2' + sl
        else:
            sl = ''
        #print("sl : " + sl)
        return result, f"{level_diff}.png", sl, level
    except LookupError:
        return False

def get_song(link:str):
    print(f"Downloading: {link}")
    if not os.path.exists(f"songs/{link.split('/')[-1]}.mp3"):
        if link.startswith("0"):
            link = "https://audio.ngfiles.com/" + link[1:] 
        elif link.startswith("1"):
            link = "http://audio.ngfiles.com/" + link[1:]
        else:
            link = "http://geometrydashcontent.com/" + link[1:]
        song = requests.get(link).content
        filename = str(link.split('/')[-1]).replace("?", '') + ".mp3"
        with open(f"songs/{filename}", "wb") as f:
            f.write(song)

async def get_account(accid:str, by_nick:bool = False):
    print(f"Getting account: {accid}")
    try:
        if not by_nick:
            user = await client.get_user(accid)
        else:
            user = await client.search_user(accid)

        uname = str(user.name)

        while uname.endswith(" "):
            uname = uname[:len(uname)-1]

        if not os.path.exists(f"icons/{uname}"):
            os.mkdir(f"icons/{uname}")

        await get_icon(user.account_id, uname)
        iconkit.generate_ic(uname)

        result = f'Username: {user.name}\nRank: {user.rank}\nStars: {user.stars}\nDiamonds: {user.diamonds}\nCoins: {user.coins}\nUser coins: {user.user_coins}\nDemons: {user.demons}\nCreator points: {user.cp}\n\nAccount ID: {user.account_id}\nPlayer ID: {user.id}'
        return result, user, uname
    except Exception as e:
        print(e)
        return False

async def get_icon(id, uname):
    ic = await client.get_user(id)
    ic = ic.icon_set
    generated_ic = await gd.IconSet.generate_full(ic)

    with open(f"icons/{uname}/generated_ic.png", "wb") as f:
        f.write(generated_ic)
