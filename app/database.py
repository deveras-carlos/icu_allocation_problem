import json
import os

class DatabaseError(Exception):
    """General exception for database-related errors."""
    pass

class ItemNotFoundError(DatabaseError):
    """Raised when an item is not found in the database."""
    pass

class FileOperationError(DatabaseError):
    """Raised when a file operation fails (e.g., reading or writing to a file)."""
    pass


class Database:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

    def _get_file_path(self, collection_name: str):
        return os.path.join(self.data_dir, f"{collection_name}.json")

    def read(self, collection_name: str):
        try:
            file_path = self._get_file_path(collection_name)
            if not os.path.exists(file_path):
                return []
            with open(file_path, 'r') as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            raise FileOperationError(f"Error reading file {collection_name}.json: {e}")

    def write(self, collection_name: str, data: list):
        try:
            file_path = self._get_file_path(collection_name)
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
        except OSError as e:
            raise FileOperationError(f"Error writing file {collection_name}.json: {e}")

    def append(self, collection_name: str, item: dict):
        try:
            data = self.read(collection_name)
            data.append(item)
            self.write(collection_name, data)
        except FileOperationError as e:
            raise FileOperationError(f"Error appending to {collection_name}.json: {e}")

    def update(self, collection_name: str, item: dict, identifier: str):
        try:
            data = self.read(collection_name)
            for i, obj in enumerate(data):
                if obj.get(identifier) == item.get(identifier):
                    data[i] = item
                    self.write(collection_name, data)
                    return
            raise ItemNotFoundError(f"Item with {identifier} {item.get(identifier)} not found for update.")
        except (FileOperationError, ItemNotFoundError) as e:
            raise e

    def delete(self, collection_name: str, identifier: str, value):
        try:
            data = self.read(collection_name)
            data = [obj for obj in data if obj.get(identifier) != value]
            if len(data) == len(self.read(collection_name)):  # No item was deleted
                raise ItemNotFoundError(f"Item with {identifier} {value} not found for deletion.")
            self.write(collection_name, data)
        except (FileOperationError, ItemNotFoundError) as e:
            raise e

database = Database( "instances" )