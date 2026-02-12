import sqlite3
import hashlib

def create_database():
    conn = sqlite3.connect('siveauto.db')
    cursor = conn.cursor()

    print("--- RECONFIGURANDO BANCO DE DADOS SIVEAUTO (INTEGRADO) ---")

    # 1. TABELA DE USUÁRIOS
    # Mantendo a estrutura padrão para todos os perfis
    cursor.execute("DROP TABLE IF EXISTS usuarios")
    cursor.execute("""
    CREATE TABLE usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha_hash TEXT NOT NULL,
        perfil TEXT NOT NULL, 
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. TABELA DE LOJAS
    # Fluxo: Lojista cadastra -> Coordenador aprova/rejeita
    cursor.execute("DROP TABLE IF EXISTS lojas")
    cursor.execute("""
    CREATE TABLE lojas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        endereco TEXT NOT NULL,
        telefone TEXT,
        responsavel_id INTEGER,
        status TEXT DEFAULT 'PENDENTE',
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (responsavel_id) REFERENCES usuarios(id)
    );
    """)

    # 3. TABELA DE VEÍCULOS (CATÁLOGO MESTRE)
    # CORREÇÃO 4.3: Removido 'preco_referencia'. Esta tabela é apenas para cadastro do modelo.
    cursor.execute("DROP TABLE IF EXISTS veiculos")
    cursor.execute("""
    CREATE TABLE veiculos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        marca TEXT NOT NULL,
        modelo TEXT NOT NULL,
        versao TEXT NOT NULL,
        ano INTEGER NOT NULL,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 4. TABELA DE COLETAS (PESQUISA DE CAMPO)
    # Onde o preço real de mercado é registrado pelo pesquisador em uma loja
    cursor.execute("DROP TABLE IF EXISTS coletas")
    cursor.execute("""
    CREATE TABLE coletas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        veiculo_id INTEGER NOT NULL,
        usuario_id INTEGER NOT NULL,
        loja_id INTEGER,
        valor_encontrado REAL NOT NULL,
        local_loja TEXT NOT NULL,
        foto_url TEXT,
        data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (veiculo_id) REFERENCES veiculos (id),
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
        FOREIGN KEY (loja_id) REFERENCES lojas (id)
    );
    """)

    # 5. TABELA DE BUSCAS (AUDITORIA)
    cursor.execute("DROP TABLE IF EXISTS buscas")
    cursor.execute("""
    CREATE TABLE buscas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        marca_buscada TEXT,
        modelo_buscado TEXT,
        versao_buscada TEXT,
        ano_buscado INTEGER,
        data_busca TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # --- SEED DE USUÁRIOS (Senha padrão: 123) ---
    senha = hashlib.sha256("123".encode()).hexdigest()
    
    perfis = [
        ('Gabriel Admin', 'admin@siveauto.com', 'ADMIN'),
        ('Carlos Gerente', 'gerente@siveauto.com', 'GERENTE'), # Adicionado perfil Gerente
        ('Ana Coord', 'coord@siveauto.com', 'COORDENADOR'),
        ('Lucas Lojista', 'lojista@siveauto.com', 'LOJISTA'),
        ('Pedro Pesq', 'pesq@siveauto.com', 'PESQUISADOR')
    ]
    
    for nome, email, perfil in perfis:
        try:
            cursor.execute("INSERT INTO usuarios (nome, email, senha_hash, perfil) VALUES (?,?,?,?)", 
                           (nome, email, senha, perfil))
        except: pass

    # --- SEED DE VEÍCULOS (Exemplos para o Catálogo) ---
    veiculos_seed = [
        ('Fiat', 'Mobi', 'Like 1.0', 2024),
        ('Toyota', 'Corolla', 'XEi 2.0', 2023),
        ('Volkswagen', 'Polo', 'Track', 2024)
    ]
    for v in veiculos_seed:
        cursor.execute("INSERT INTO veiculos (marca, modelo, versao, ano) VALUES (?,?,?,?)", v)

    conn.commit()
    conn.close()
    print("✅ Banco de dados INTEGRADO criado com sucesso!")

if __name__ == "__main__":
    create_database()