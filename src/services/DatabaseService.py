import sqlite3

class DatabaseService:
    @staticmethod
    def get_connection():
        # Conecta ao arquivo criado na raiz
        return sqlite3.connect("siveauto.db")