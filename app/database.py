from typing import Any
import firebase_admin
from firebase_admin import credentials, db

class FireBaseDB:

    def __init__(self, credentials_path: str, database_url: str) -> None:
        cred = credentials.Certificate(credentials_path)
        firebase_admin.initialize_app(cred,{
            "databaseURL": database_url
        })

    def writeRecord(self, path: str, data: dict) -> None:
        ref = db.reference(path)
        ref.set(data)

    def updateRecord(self, path: str, data: dict) -> None:
        ref = db.reference(path)
        ref.update(data)

    def readRecord(self, path: str) -> dict:
        ref = db.reference(path)
        return ref.get()