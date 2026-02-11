import sqlite3
import hashlib

def resetar_senha_admin():
    # 1. Gera a hash SHA256 da senha "admin123"
    senha_nova = "admin123"
    senha_hash = hashlib.sha256(senha_nova.encode()).hexdigest()
    
    # 2. Conecta no banco
    conn = sqlite3.connect('siveauto.db')
    cursor = conn.cursor()
    
    print(f"🔄 Atualizando senha do admin para: {senha_nova}...")
    
    # 3. Tenta atualizar o usuário existente
    cursor.execute("""
        UPDATE usuarios 
        SET senha_hash = ?, perfil = 'ADMIN' 
        WHERE email = 'admin@siveauto.com'
    """, (senha_hash,))
    
    # 4. Se não existia ninguém com esse email, cria do zero
    if cursor.rowcount == 0:
        print("⚠️ Usuário não encontrado, criando novo...")
        cursor.execute("""
            INSERT INTO usuarios (nome, email, senha_hash, perfil) 
            VALUES (?, ?, ?, ?)
        """, ('Gabriel Admin', 'admin@siveauto.com', senha_hash, 'ADMIN'))
    else:
        print("✅ Usuário encontrado e atualizado.")

    conn.commit()
    conn.close()
    print("🚀 Sucesso! Tente logar agora.")

if __name__ == "__main__":
    resetar_senha_admin()