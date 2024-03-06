class StoreDB:
    """
    A simple key-value store that persists data to a JSON file.

    This class provides methods to add, fetch, update, and delete key-value pairs.
    The data is stored in a dictionary and persisted to a JSON file after each operation.
    If the JSON file does not exist, it is created upon initialization.
    If the JSON file exists, it is loaded upon initialization.

    Methods:
        add(key, value): Adds a new key-value pair to the store.
        fetch(key): Fetches the value associated with a key from the store.
        update(key, value): Updates the value associated with a key in the store.
        delete(key): Deletes a key-value pair from the store.
    """
    def __init__(self, db_file = './db_file.json'):
        import json
        import os
        self.db_file = db_file
        if os.path.exists(db_file):
            with open(db_file, 'r') as f:
                self.db = json.load(f)
        else:
            self.db = {}

    def add(self, key, value):
        if key in self.db:
            raise Exception('Key already exists')
        self.db[key] = value
        self._persist()

    def fetch(self, key):
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


"""
Usage:
store = StoreDB()
store.add('key1', 'value1')
store.add('key2', 'value2')
store.add('key3', 'value3')
print(store.fetch('key1'))  # Outputs: value1
# Update a value
store.update('key1', 'updatedValue1')
# Fetch and print the updated value
print(store.fetch('key1'))  # Outputs: updatedValue1
# Delete a key-value pair
store.delete('key1')
"""
