import hashlib
import sqlite3
from src.models.Usuario import Usuario
from src.services.DatabaseService import DatabaseService

class AuthController:
    @staticmethod
    def validar_login(email, senha):
        # 1. Transforma a senha digitada em código secreto (Hash)
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        
        conn = DatabaseService.get_connection()
        cursor = conn.cursor()
        
        # 2. Busca no banco se existe esse email com essa senha
        # Nota: Não trazemos a senha de volta, apenas ID, Nome, Email e Perfil
        cursor.execute("SELECT id, nome, email, perfil FROM usuarios WHERE email = ? AND senha_hash = ?", (email, senha_hash))
        resultado = cursor.fetchone()
        
        conn.close()
        
        if resultado:
            # 3. Cria o usuário exatamente com os 4 campos que definimos no Passo 1
            # id, nome, email, perfil
            return Usuario(resultado[0], resultado[1], resultado[2], resultado[3])
        else:
            return None