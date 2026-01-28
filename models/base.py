from datetime import datetime , UTC
from bson import ObjectId

class BaseModel:
    
    def __init__(self):
        self._id = ObjectId()
        self.created_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)
        self.deleted_at = None
        
    def to_dict(self):
        return {
            "_id" : str(self._id),
            "created_at" : self.created_at,
            "updated_at" : self.updated_at,
            "deleted_at" : self.deleted_at
        }