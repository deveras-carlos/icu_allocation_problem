from app.database import database
from app.database import ItemNotFoundError, DatabaseError

class BaseRepository:
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.database = database

    def get_all(self):
        try:
            return self.database.read(self.collection_name)
        except DatabaseError as e:
            raise DatabaseError(f"Error getting all items from {self.collection_name}: {e}")

    def get(self, identifier: str, value):
        try:
            data = self.database.read(self.collection_name)
            return [item for item in data if item.get(identifier) == value]
        except DatabaseError as e:
            raise DatabaseError(f"Error getting items by {identifier} from {self.collection_name}: {e}")

    def add(self, item: dict):
        try:
            self.database.append(self.collection_name, item)
        except DatabaseError as e:
            raise DatabaseError(f"Error adding item to {self.collection_name}: {e}")

    def update(self, item: dict, identifier: str):
        try:
            self.database.update(self.collection_name, item, identifier)
        except ItemNotFoundError as e:
            raise ItemNotFoundError(f"Error updating item in {self.collection_name}: {e}")
        except DatabaseError as e:
            raise DatabaseError(f"Error updating item in {self.collection_name}: {e}")

    def delete(self, identifier: str, value):
        try:
            self.database.delete(self.collection_name, identifier, value)
        except ItemNotFoundError as e:
            raise ItemNotFoundError(f"Error deleting item from {self.collection_name}: {e}")
        except DatabaseError as e:
            raise DatabaseError(f"Error deleting item from {self.collection_name}: {e}")

    def get_by_id(self, id: int):
        try:
            data = self.database.read(self.collection_name)
            for item in data:
                if item.get('id') == id:
                    return item
            raise ItemNotFoundError(f"Item with id {id} not found in {self.collection_name}")
        except DatabaseError as e:
            raise DatabaseError(f"Error retrieving item by id from {self.collection_name}: {e}")
