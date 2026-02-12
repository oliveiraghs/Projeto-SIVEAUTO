import unittest
import hashlib

class TesteSegurancaAuth(unittest.TestCase):

    def gerar_hash(self, senha):
        """Simula a função de hash usada no AuthController/AdminView"""
        return hashlib.sha256(senha.encode()).hexdigest()

    def test_hash_consistencia(self):
        """Teste 1: A mesma senha deve gerar sempre o mesmo hash."""
        senha = "senha123"
        hash1 = self.gerar_hash(senha)
        hash2 = self.gerar_hash(senha)
        
        self.assertEqual(hash1, hash2, "Erro: O sistema de hash está instável.")

    def test_senha_incorreta(self):
        """Teste 2: Uma senha errada JAMAIS deve gerar o mesmo hash da correta."""
        senha_correta = "admin123"
        senha_errada = "admin124"
        
        hash_correto = self.gerar_hash(senha_correta)
        hash_errado = self.gerar_hash(senha_errada)
        
        self.assertNotEqual(hash_correto, hash_errado, "PERIGO: Senhas diferentes geraram o mesmo hash!")

    def test_validacao_admin(self):
        """Teste 3: Simula o processo de login (Comparação Banco vs Input)."""
        # Hash correto da senha 'siveauto2026' (SHA-256)
        hash_banco = "dcccb4ae2a44a2ba2a3cc4da7f9a00346b79d99bad92d08258e97c02d5ae7341"
        
        # O usuário digitou a senha correta
        input_usuario = "siveauto2026"
        hash_input = self.gerar_hash(input_usuario)
        
        self.assertEqual(hash_banco, hash_input, "Erro: Login falhou mesmo com a senha correta.")

if __name__ == '__main__':
    unittest.main()