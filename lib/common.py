import json

def cprint(tag,content):
    print("[ %s ]" % (tag,))
    if not isinstance(content, str):
        content = json.dumps(content, indent=4)
    print(' ' * 2 + content)
