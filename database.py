import sqlite3
import hashlib

def create_database():
    conn = sqlite3.connect('siveauto.db')
    cursor = conn.cursor()

    print("--- INICIANDO CRIAÇÃO DO BANCO DE DADOS ---")

    # 1. Tabela de Usuários (COM PERFIL GERENTE LIBERADO)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha_hash TEXT NOT NULL,
        perfil TEXT NOT NULL CHECK(perfil IN ('ADMIN', 'GERENTE', 'COORDENADOR', 'LOJISTA', 'PESQUISADOR')),
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    print("✅ Tabela 'usuarios' criada/verificada.")

    # 2. Tabela de Veículos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS veiculos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        marca TEXT NOT NULL,
        modelo TEXT NOT NULL,
        ano INTEGER NOT NULL,
        preco_referencia REAL NOT NULL,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    print("✅ Tabela 'veiculos' criada/verificada.")

    # 3. CRIAR USUÁRIO ADMIN PADRÃO (O SEED)
    senha_admin = hashlib.sha256("admin123".encode()).hexdigest()
    try:
        cursor.execute("INSERT INTO usuarios (nome, email, senha_hash, perfil) VALUES (?, ?, ?, ?)",
                       ('Gabriel Admin', 'admin@siveauto.com', senha_admin, 'ADMIN'))
        print("👤 Usuário ADMIN criado: admin@siveauto.com / admin123")
    except sqlite3.IntegrityError:
        print("ℹ️ Usuário ADMIN já existe.")

    # 4. CRIAR VEÍCULOS DE EXEMPLO
    veiculos_seed = [
        ('Fiat', 'Mobi Like 1.0', 2024, 69990.00),
        ('Toyota', 'Corolla XEi', 2023, 145000.00),
        ('Volkswagen', 'Polo Track', 2024, 87990.00)
    ]
    
    for v in veiculos_seed:
        cursor.execute("SELECT id FROM veiculos WHERE modelo = ?", (v[1],))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO veiculos (marca, modelo, ano, preco_referencia) VALUES (?, ?, ?, ?)", v)
            print(f"🚗 Veículo inserido: {v[1]}")

    conn.commit()
    conn.close()
    print("--- CONCLUÍDO COM SUCESSO! ---")

if __name__ == "__main__":
    create_database()