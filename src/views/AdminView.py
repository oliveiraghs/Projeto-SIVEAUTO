import streamlit as st
from src.services.DatabaseService import DatabaseService
import pandas as pd
import hashlib
import time

class AdminView:
    @staticmethod
    def render(usuario):
        # 1. Gerenciamento de Navegação e Estados
        if 'admin_aba' not in st.session_state:
            st.session_state['admin_aba'] = 'Usuarios'
        
        # Inicializa o estado de edição se não existir
        if 'user_to_edit' not in st.session_state:
            st.session_state['user_to_edit'] = None

        inicial = usuario.nome[0].upper() if usuario.nome else "A"

        # --- CSS PADRONIZADO (Zoom 0.75) ---
        st.markdown(f"""
            <style>
                body {{ zoom: 0.75; overflow: hidden; }}
                #MainMenu, footer, header {{ display: none !important; }}
                .block-container {{ padding-top: 1.5rem !important; max-width: 100%; }}
                [data-testid="stSidebar"] {{ background-color: #D3D3D3 !important; }}
                .avatar-circle {{
                    width: 70px; height: 70px; background-color: #FF8C00; color: white;
                    border-radius: 50%; text-align: center; line-height: 70px; font-size: 28px;
                    font-weight: bold; margin: 20px auto 10px auto; border: 3px solid white;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }}
                [data-testid="stForm"] {{ background-color: #F8F9FA; border-radius: 15px; border: 1px solid #CCC; }}
                .stTextInput, .stSelectbox, .stNumberInput {{ margin-bottom: -15px !important; }}
            </style>
        """, unsafe_allow_html=True)

        # --- SIDEBAR ---
        with st.sidebar:
            st.markdown(f"<div class='avatar-circle'>{inicial}</div>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align:center;'>{usuario.nome}</h3>", unsafe_allow_html=True)
            st.write("---")
            if st.button("🏠 Dashboard", use_container_width=True): 
                st.session_state['admin_aba'] = 'Dashboard'; st.rerun()
            if st.button("👥 Usuários", use_container_width=True): 
                st.session_state['admin_aba'] = 'Usuarios'; st.rerun()
            if st.button("🚗 Veículos", use_container_width=True): 
                st.session_state['admin_aba'] = 'Veiculos'; st.rerun()
            
            st.markdown("<div style='height: 35vh;'></div>", unsafe_allow_html=True)
            if st.button("🚪 Sair", type="primary", use_container_width=True):
                st.session_state.clear() # Limpa tudo ao sair
                st.rerun()

        # --- ROTEAMENTO ---
        aba = st.session_state['admin_aba']
        if aba == 'Usuarios':
            AdminView.render_usuarios()
        elif aba == 'Veiculos':
            AdminView.render_veiculos()
        else:
            st.info("Área de Dashboard")

    @staticmethod
    def render_usuarios():
        st.markdown("### 👥 Gestão de Usuários")
        col_lista, col_form = st.columns([2, 1.2])

        # --- LISTA DE USUÁRIOS ---
        with col_lista:
            conn = DatabaseService.get_connection()
            df = pd.read_sql_query("SELECT id, nome, email, perfil FROM usuarios ORDER BY id DESC", conn)
            
            h1, h2, h3, h4 = st.columns([0.5, 2, 2, 1.2])
            h1.caption("**ID**"); h2.caption("**Nome**"); h3.caption("**E-mail**"); h4.caption("**Ações**")
            st.markdown("---")

            for _, row in df.iterrows():
                c1, c2, c3, c4 = st.columns([0.5, 2, 2, 1.2])
                c1.write(f"#{row['id']}")
                c2.write(row['nome'])
                c3.write(row['email'])
                
                b1, b2 = c4.columns(2)
                # BOTÃO EDITAR (O Segredo está em passar o dicionário da linha)
                if b1.button("✏️", key=f"btn_ed_{row['id']}"):
                    st.session_state['user_to_edit'] = row.to_dict()
                    st.rerun() # Força o formulário a ler o novo estado

                if b2.button("🗑️", key=f"btn_del_{row['id']}"):
                    AdminView.excluir_usuario(row['id'])
                    st.rerun()
                st.markdown("<hr style='margin: 5px 0; opacity: 0.2;'>", unsafe_allow_html=True)
            conn.close()

        # --- FORMULÁRIO (CADASTRO / EDIÇÃO) ---
        with col_form:
            user_data = st.session_state['user_to_edit']
            is_editing = user_data is not None
            
            # Define valores padrão baseados no estado (Edição ou Novo)
            default_nome = user_data['nome'] if is_editing else ""
            default_email = user_data['email'] if is_editing else ""
            default_perfil = user_data['perfil'] if is_editing else "PESQUISADOR"
            
            titulo = "📝 Editar Usuário" if is_editing else "➕ Novo Usuário"
            
            # IMPORTANTE: clear_on_submit só deve ser True se NÃO estiver editando
            with st.form("form_usuarios_admin", clear_on_submit=not is_editing):
                st.markdown(f"#### {titulo}")
                
                novo_nome = st.text_input("Nome:", value=default_nome)
                novo_email = st.text_input("E-mail:", value=default_email)
                nova_senha = st.text_input("Senha:", type="password", placeholder="Deixe em branco para não alterar" if is_editing else "Senha de acesso")
                
                lista_perfis = ["ADMIN", "GERENTE", "COORDENADOR", "LOJISTA", "PESQUISADOR"]
                idx_perfil = lista_perfis.index(default_perfil) if default_perfil in lista_perfis else 4
                
                novo_perfil = st.selectbox("Perfil:", options=lista_perfis, index=idx_perfil)

                st.markdown("<br>", unsafe_allow_html=True)
                
                if is_editing:
                    c_b1, c_b2 = st.columns(2)
                    if c_b1.form_submit_button("Atualizar", type="primary", use_container_width=True):
                        AdminView.atualizar_usuario(user_data['id'], novo_nome, novo_email, nova_senha, novo_perfil)
                        st.session_state['user_to_edit'] = None # Limpa após salvar
                        st.success("Atualizado!")
                        time.sleep(1)
                        st.rerun()
                    
                    if c_b2.form_submit_button("Cancelar", use_container_width=True):
                        st.session_state['user_to_edit'] = None
                        st.rerun()
                else:
                    if st.form_submit_button("Cadastrar Usuário", type="primary", use_container_width=True):
                        if novo_nome and novo_email and nova_senha:
                            AdminView.salvar_usuario(novo_nome, novo_email, nova_senha, novo_perfil)
                            st.success("Criado com sucesso!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Preencha todos os campos.")

    # =========================================================
    # ÁREA DE VEÍCULOS (Padronizada)
    # =========================================================
    @staticmethod
    def render_veiculos():
        st.markdown("### 🚗 Gestão de Veículos")
        col_list, col_form = st.columns([1.8, 1])
        conn = DatabaseService.get_connection()
        with col_list:
            df_v = pd.read_sql_query("SELECT id, marca, modelo, versao, ano, preco_referencia FROM veiculos ORDER BY id DESC", conn)
            st.dataframe(df_v, use_container_width=True, hide_index=True)
        with col_form:
            with st.form("form_veic_admin", clear_on_submit=True):
                st.markdown("#### Adicionar Novo")
                ma = st.text_input("Marca:"); mo = st.text_input("Modelo"); ve = st.text_input("Versão")
                an = st.number_input("Ano", value=2024); pr = st.number_input("Preço Ref.")
                if st.form_submit_button("Salvar Veículo", use_container_width=True):
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO veiculos (marca, modelo, versao, ano, preco_referencia) VALUES (?,?,?,?,?)", (ma,mo,ve,an,pr))
                    conn.commit()
                    st.rerun()
        conn.close()

    # =========================================================
    # MÉTODOS DE APOIO (DB)
    # =========================================================
    @staticmethod
    def salvar_usuario(n, e, s, p):
        h = hashlib.sha256(s.encode()).hexdigest()
        conn = DatabaseService.get_connection()
        conn.execute("INSERT INTO usuarios (nome, email, senha_hash, perfil) VALUES (?,?,?,?)", (n,e,h,p))
        conn.commit(); conn.close()

    @staticmethod
    def atualizar_usuario(id_u, n, e, s, p):
        conn = DatabaseService.get_connection()
        if s: # Se digitou senha nova
            h = hashlib.sha256(s.encode()).hexdigest()
            conn.execute("UPDATE usuarios SET nome=?, email=?, senha_hash=?, perfil=? WHERE id=?", (n,e,h,p,id_u))
        else: # Mantém a antiga
            conn.execute("UPDATE usuarios SET nome=?, email=?, perfil=? WHERE id=?", (n,e,p,id_u))
        conn.commit(); conn.close()

    @staticmethod
    def excluir_usuario(id_u):
        conn = DatabaseService.get_connection()
        conn.execute("DELETE FROM usuarios WHERE id=?", (id_u,))
        conn.commit(); conn.close()