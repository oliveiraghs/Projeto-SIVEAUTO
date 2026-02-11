from src.models.Usuario import Usuario

class AuthController:
    @staticmethod
    def validar_login(email, senha):
        """
        Verifica se o usuário existe e se a senha bate.
        Retorna o objeto Usuario se der certo, ou None se falhar.
        """
        usuario = Usuario.buscar_por_email(email)
        
        if usuario:
            # Como no seed usamos texto puro (ex: 'admin123'), comparamos direto.
            # Em um sistema real, aqui usaríamos bcrypt.checkpw()
            if usuario.senha_hash == senha:
                return usuario
                
        return None