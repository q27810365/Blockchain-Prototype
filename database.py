import json
import os

BASEDBPATH = 'data'
ACCOUNTFILE = 'account'


class BaseDB():
    filepath = ''

    def __init__(self):
        self.set_path()
        self.filepath = '/'.join((BASEDBPATH, self.filepath))

    def set_path(self):
        pass

    def find_all(self):
        return self.read()

    def insert(self, item):
        self.write(item)

    def read(self):
        raw = ''
        if not os.path.exists(self.filepath):
            return []
        with open(self.filepath, 'r+') as f:
            raw = f.readline()
        if len(raw) > 0:
            data = json.loads(raw)
        else:
            data = []
        return data

    def write(self, item):
        data = self.read()
        if isinstance(item, list):
            data = data + item
        else:
            data.append(item)
        with open(self.filepath, 'w+') as f:
            f.write(json.dumps(data))
        return True

    def clear(self):
        with open(self.filepath, 'w+') as f:
            f.write('')

    def hash_insert(self, item):
        exists = False
        for i in self.find_all():
            if item['hash'] == i['hash']:
                exists = True
                break
        if not exists:
            self.write(item)


class AccountDB(BaseDB):
    def set_path(self):
        self.filepath = ACCOUNTFILE

    def find_one(self):
        ac = self.read()
        return ac[0]

