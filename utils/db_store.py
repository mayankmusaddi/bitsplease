class StoreDB:
    def __init__(self, db_file = './db_file.json'):
        import json
        import os
        self.db_file = db_file
        if os.path.exists(db_file):
            with open(db_file, 'r') as f:
                self.db = json.load(f)
        else:
            self.db = {}

    def create(self, key, value):
        if key in self.db:
            raise Exception('Key already exists')
        self.db[key] = value
        self._persist()

    def read(self, key):
        try:
            return self.db[key]
        except KeyError:
            raise Exception('Key not found')

    def update(self, key, value):
        if key not in self.db:
            raise Exception('Key not found')
        self.db[key] = value
        self._persist()

    def delete(self, key):
        if key not in self.db:
            raise Exception('Key not found')
        del self.db[key]
        self._persist()

    def _persist(self):
        with open(self.db_file, 'w') as f:
            json.dump(self.db, f)
