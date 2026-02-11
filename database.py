import sqlite3
import os

# Nome do arquivo do banco
DB_NAME = "siveauto.db"

def get_connection():
    """Retorna a conexão com o banco de dados"""
    return sqlite3.connect(DB_NAME)

def create_tables():
    """Cria as tabelas do sistema com suporte aos 5 perfis oficiais"""
    conn = get_connection()
    cursor = conn.cursor()

    print("🛠️ Criando tabelas estruturais...")

    # 1. Tabela de Usuários (Atualizada com os 5 perfis do Requisito)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha_hash TEXT NOT NULL,
        perfil TEXT NOT NULL CHECK(perfil IN ('ADMIN', 'GERENTE', 'COORDENADOR', 'LOJISTA', 'PESQUISADOR')),
        data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Tabela de Veículos (Gerenciada pelo GERENTE)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS veiculos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        marca TEXT NOT NULL,
        modelo TEXT NOT NULL,
        ano INTEGER NOT NULL,
        preco_referencia REAL,
        data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 3. Tabela de Lojas (Cadastrada por LOJISTA/PESQUISADOR, Aprovada por COORDENADOR)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lojas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        endereco TEXT,
        id_dono INTEGER, -- Quem cadastrou (Lojista ou Pesquisador)
        situacao TEXT DEFAULT 'PENDENTE' CHECK(situacao IN ('PENDENTE', 'APROVADA', 'REJEITADA')),
        FOREIGN KEY(id_dono) REFERENCES usuarios(id)
    );
    """)

    # 4. Tabela de Cotações (Inserida pelo PESQUISADOR)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cotacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        valor REAL NOT NULL,
        data_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
        id_usuario INTEGER NOT NULL, -- O Pesquisador
        id_veiculo INTEGER NOT NULL,
        id_loja INTEGER NOT NULL,
        obs TEXT,
        FOREIGN KEY(id_usuario) REFERENCES usuarios(id),
        FOREIGN KEY(id_veiculo) REFERENCES veiculos(id),
        FOREIGN KEY(id_loja) REFERENCES lojas(id)
    );
    """)

    # 5. Logs de Busca (Consulta Pública - Sem Login)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs_busca (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        termo_busca TEXT NOT NULL,
        data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
        ip_origem TEXT
    );
    """)

    conn.commit()
    conn.close()
    print("✅ Tabelas criadas com sucesso!")

def seed_data():
    """Insere um usuário de teste para CADA perfil do Requisito"""
    conn = get_connection()
    cursor = conn.cursor()

    print("🌱 Populando banco com usuários de teste...")

    # Lista de usuários baseados na imagem "Desafio 3.2"
    usuarios_seed = [
        ('Gabriel Admin', 'admin@siveauto.com', 'admin123', 'ADMIN'),
        ('Carlos Gerente', 'gerente@siveauto.com', '123456', 'GERENTE'),
        ('Ana Coordenadora', 'coord@siveauto.com', '123456', 'COORDENADOR'),
        ('Lucas Lojista', 'lojista@siveauto.com', '123456', 'LOJISTA'),
        ('João Pesquisador', 'pesq@siveauto.com', '123456', 'PESQUISADOR')
    ]

    try:
        cursor.executemany("""
            INSERT OR IGNORE INTO usuarios (nome, email, senha_hash, perfil) 
            VALUES (?, ?, ?, ?)
        """, usuarios_seed)
        
        # Inserir Veículos (Dados Globais - Responsabilidade do Gerente)
        veiculos_seed = [
            ('Fiat', 'Mobi Like 1.0', 2024, 69990.00),
            ('Volkswagen', 'Polo Track', 2024, 87990.00),
            ('Chevrolet', 'Onix LT', 2023, 89900.00),
            ('Toyota', 'Corolla XEi', 2022, 145000.00)
        ]
        cursor.executemany("""
            INSERT OR IGNORE INTO veiculos (marca, modelo, ano, preco_referencia) 
            VALUES (?, ?, ?, ?)
        """, veiculos_seed)

        print(f"👤 {cursor.rowcount} usuários verificados/inseridos.")
        
    except sqlite3.Error as e:
        print(f"⚠️ Erro ao inserir dados: {e}")

    conn.commit()
    conn.close()
    print("✅ Banco de dados pronto e populado!")

if __name__ == "__main__":
    # Garante que cria do zero se precisar (para testes iniciais)
    # Se quiser resetar o banco, apague o arquivo 'siveauto.db' manualmente antes de rodar
    create_tables()
    seed_data()