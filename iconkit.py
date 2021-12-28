from PIL import Image
from os import remove

def generate_ic(username):
    back = Image.open("template.png")
    f = Image.open(f"icons/{username}/generated_ic.png")

    back.copy()
    back.paste(f, mask=f)
    f.close()

    back.save(f"icons/{username}/iconkit.png")
    remove(f"icons/{username}/generated_ic.png")