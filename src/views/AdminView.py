import streamlit as st
from src.services.DatabaseService import DatabaseService
import pandas as pd
import time

class AdminView:
    @staticmethod
    def render(usuario):
        inicial = usuario.nome[0].upper() if usuario.nome else "U"

        # --- CSS CORRIGIDO (Barra Lateral Visível) ---
        st.markdown(f"""
            <style>
                /* 1. CONFIGURAÇÕES GERAIS */
                body {{
                    zoom: 0.8; 
                    overflow: hidden; 
                }}
                
                /* Esconde APENAS o rodapé e menu de hambúrguer, mas mantém a área da sidebar */
                #MainMenu, footer {{
                    display: none !important;
                }}

                /* Ajuste do container principal */
                .block-container {{
                    padding-top: 1.5rem !important; /* Espaço para não colar no topo */
                    padding-bottom: 0rem !important;
                    max-width: 100%;
                }}

                /* 2. SIDEBAR (CINZA E FIXA) */
                [data-testid="stSidebar"] {{
                    background-color: #D3D3D3 !important;
                    min-width: 220px !important;
                    max-width: 220px !important;
                }}
                
                /* Remove rolagem interna da sidebar */
                [data-testid="stSidebar"] ::-webkit-scrollbar {{
                    display: none !important;
                }}

                /* 3. AVATAR DE PERFIL */
                .avatar-circle {{
                    width: 70px;
                    height: 70px;
                    background-color: #FF8C00;
                    color: white;
                    border-radius: 50%;
                    text-align: center;
                    line-height: 70px; /* Centraliza verticalmente */
                    font-size: 28px;
                    font-weight: bold;
                    margin: 20px auto 10px auto;
                    border: 3px solid white;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }}

                /* 4. ESTILO DO FORMULÁRIO (DIREITA) */
                [data-testid="stForm"] {{
                    background-color: #F8F9FA;
                    border-radius: 15px;
                    padding: 20px !important;
                    border: 1px solid #CCC;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
                }}
                
                /* Títulos e Inputs compactos */
                .stTextInput, .stSelectbox {{
                    margin-bottom: -10px !important;
                }}
            </style>
        """, unsafe_allow_html=True)

        # --- BARRA LATERAL (SIDEBAR) ---
        with st.sidebar:
            # Avatar
            st.markdown(f"<div class='avatar-circle'>{inicial}</div>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align:center; color:#333; margin:0;'>{usuario.nome}</h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; color:#666; font-size:0.9rem;'>{usuario.perfil}</p>", unsafe_allow_html=True)
            st.write("---")
            
            # Botões de Navegação
            st.button("🏠 Dashboard", use_container_width=True)
            st.button("👥 Usuários", use_container_width=True)
            st.button("🚗 Veículos", use_container_width=True)
            
            # Espaçador e Botão Sair
            st.markdown("<div style='height: 30vh;'></div>", unsafe_allow_html=True)
            if st.button("🚪 Sair do Sistema", type="primary", use_container_width=True):
                del st.session_state['usuario_ativo']
                st.rerun()

        # --- LAYOUT PRINCIPAL (DIVISÃO 2 COLUNAS) ---
        col_lista, col_cadastro = st.columns([2, 1.2])

        # --- COLUNA 1: LISTA (ESQUERDA) ---
        with col_lista:
            st.markdown("### 👥 Gestão de Usuários")
            
            conn = DatabaseService.get_connection()
            try:
                df = pd.read_sql_query("SELECT id, nome, email, perfil FROM usuarios", conn)
                
                # Cabeçalhos
                h1, h2, h3, h4 = st.columns([0.5, 2, 2, 1.5])
                h1.markdown("**ID**")
                h2.markdown("**Nome**")
                h3.markdown("**E-mail**")
                h4.markdown("**Ações**")
                st.markdown("---")

                # Linhas
                for _, row in df.iterrows():
                    c1, c2, c3, c4 = st.columns([0.5, 2, 2, 1.5])
                    c1.write(f"#{row['id']}")
                    c2.write(row['nome'])
                    c3.write(row['email'])
                    
                    btn_col1, btn_col2 = c4.columns(2)
                    if btn_col1.button("✏️", key=f"edit_{row['id']}"):
                        st.session_state['user_to_edit'] = row.to_dict()
                        st.rerun()
                    
                    if btn_col2.button("🗑️", key=f"del_{row['id']}"):
                        AdminView.excluir_usuario(row['id'])
                        time.sleep(0.5)
                        st.rerun()
                    
                    st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Erro ao carregar: {e}")
            finally:
                conn.close()

        # --- COLUNA 2: FORMULÁRIO (DIREITA) ---
        with col_cadastro:
            is_editing = 'user_to_edit' in st.session_state
            # Recupera senha_hash apenas se estiver editando, senão vazio
            user_data = st.session_state.get('user_to_edit', {"nome": "", "email": "", "senha_hash": "", "perfil": "PESQUISADOR", "id": None})
            
            # Título
            titulo = "📝 Editar Usuário" if is_editing else "➕ Novo Usuário"
            
            with st.form("form_usuario", clear_on_submit=not is_editing):
                st.markdown(f"### {titulo}")
                
                nome = st.text_input("Nome Completo:", value=user_data['nome'])
                email = st.text_input("E-mail:", value=user_data['email'])
                senha = st.text_input("Senha:", type="password", value=user_data.get('senha_hash', ''))
                perfil = st.selectbox("Perfil:", 
                                    ["ADMIN", "GERENTE", "COORDENADOR", "LOJISTA", "PESQUISADOR"], 
                                    index=["ADMIN", "GERENTE", "COORDENADOR", "LOJISTA", "PESQUISADOR"].index(user_data['perfil']))
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                if is_editing:
                    c1, c2 = st.columns(2)
                    if c1.form_submit_button("Salvar", type="primary"):
                        AdminView.atualizar_usuario(user_data['id'], nome, email, senha, perfil)
                        del st.session_state['user_to_edit']
                        st.rerun()
                    if c2.form_submit_button("Cancelar"):
                        del st.session_state['user_to_edit']
                        st.rerun()
                else:
                    if st.form_submit_button("Cadastrar Usuário", type="primary"):
                        if nome and email and senha:
                            AdminView.salvar_usuario(nome, email, senha, perfil)
                            st.success("Cadastrado!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.warning("Preencha todos os campos.")

    # --- MÉTODOS DE BANCO DE DADOS ---
    @staticmethod
    def salvar_usuario(nome, email, senha, perfil):
        conn = DatabaseService.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (nome, email, senha_hash, perfil) VALUES (?, ?, ?, ?)", (nome, email, senha, perfil))
        conn.commit()
        conn.close()

    @staticmethod
    def atualizar_usuario(id_user, nome, email, senha, perfil):
        conn = DatabaseService.get_connection()
        cursor = conn.cursor()
        # Nota: Idealmente faríamos hash da senha aqui se ela mudou
        cursor.execute("UPDATE usuarios SET nome=?, email=?, senha_hash=?, perfil=? WHERE id=?", (nome, email, senha, perfil, id_user))
        conn.commit()
        conn.close()

    @staticmethod
    def excluir_usuario(id_user):
        conn = DatabaseService.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id = ?", (id_user,))
        conn.commit()
        conn.close()