

def convert(l):
    res = str(l.difficulty).split(".")[-1].lower()
    diff = res.capitalize().replace("_", " ")
    
    if "_" in res:
        res = res.split("_")[::-1]
        res = "-".join(res)

    if l.is_epic():
        res+="-epic"
    elif l.is_featured():
        res+="-featured"
    else:
        pass

    return res, diff

def convert_length(l):
    return str(l).split(".")[-1].lower()