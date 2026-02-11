from src.services.DatabaseService import DatabaseService

class Usuario:
    def __init__(self, id, nome, email, senha_hash, perfil):
        self.id = id
        self.nome = nome
        self.email = email
        self.senha_hash = senha_hash
        self.perfil = perfil

    @staticmethod
    def buscar_por_email(email):
        conn = DatabaseService.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT id, nome, email, senha_hash, perfil FROM usuarios WHERE email = ?", (email,))
            row = cursor.fetchone()
            
            if row:
                # Cria e retorna o objeto Usuario com os dados do banco
                return Usuario(id=row[0], nome=row[1], email=row[2], senha_hash=row[3], perfil=row[4])
            return None
        finally:
            conn.close()