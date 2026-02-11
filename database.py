import sqlite3
import hashlib

def create_database():
    # Conecta ao arquivo (ele será criado se não existir)
    conn = sqlite3.connect('siveauto.db')
    cursor = conn.cursor()

    print("--- INICIANDO CONFIGURAÇÃO DO BANCO DE DADOS SIVEAUTO ---")

    # 1. TABELA DE USUÁRIOS
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
    print("✅ Tabela 'usuarios' verificada.")

    # 2. TABELA DE VEÍCULOS (ATUALIZADA COM VERSÃO)
    # Nota: Apagamos a versão antiga se necessário para garantir a nova coluna
    cursor.execute("DROP TABLE IF EXISTS veiculos;") 
    cursor.execute("""
    CREATE TABLE veiculos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        marca TEXT NOT NULL,
        modelo TEXT NOT NULL,
        versao TEXT NOT NULL,
        ano INTEGER NOT NULL,
        preco_referencia REAL NOT NULL,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    print("✅ Tabela 'veiculos' criada com o campo 'versao'.")

    # 3. TABELA DE COLETAS (PARA O PESQUISADOR)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS coletas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        veiculo_id INTEGER NOT NULL,
        usuario_id INTEGER NOT NULL,
        valor_encontrado REAL NOT NULL,
        local_loja TEXT NOT NULL,
        foto_url TEXT,
        data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (veiculo_id) REFERENCES veiculos (id),
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
    );
    """)
    print("✅ Tabela 'coletas' verificada.")

    # --- SEED: DADOS INICIAIS ---

    # Criar Usuário Admin Padrão
    senha_admin = hashlib.sha256("admin123".encode()).hexdigest()
    try:
        cursor.execute("""
            INSERT INTO usuarios (nome, email, senha_hash, perfil) 
            VALUES (?, ?, ?, ?)
        """, ('Gabriel Admin', 'admin@siveauto.com', senha_admin, 'ADMIN'))
        print("👤 Usuário ADMIN criado: admin@siveauto.com / admin123")
    except sqlite3.IntegrityError:
        print("ℹ️ Usuário ADMIN já existe no sistema.")

    # Criar Veículos de Exemplo com Versões
    veiculos_seed = [
        ('Fiat', 'Mobi', 'Like 1.0', 2024, 69990.00),
        ('Fiat', 'Mobi', 'Trekking 1.0', 2024, 73500.00),
        ('Toyota', 'Corolla', 'XEi 2.0', 2023, 145000.00),
        ('Toyota', 'Corolla', 'Altis Hybrid', 2023, 182000.00),
        ('Volkswagen', 'Polo', 'Track', 2024, 87990.00),
        ('Volkswagen', 'Polo', 'Highline TSI', 2024, 115000.00)
    ]
    
    for v in veiculos_seed:
        cursor.execute("""
            INSERT INTO veiculos (marca, modelo, versao, ano, preco_referencia) 
            VALUES (?, ?, ?, ?, ?)
        """, v)
        print(f"🚗 Veículo inserido: {v[0]} {v[1]} {v[2]} ({v[3]})")

    conn.commit()
    conn.close()
    print("--- BANCO DE DADOS PRONTO PARA USO! ---")

if __name__ == "__main__":
    create_database()