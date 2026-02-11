import streamlit as st
from src.services.DatabaseService import DatabaseService
import pandas as pd
import hashlib
import time

# Configuração da página (Sempre a primeira linha)
try:
    st.set_page_config(layout="wide", page_title="Admin System")
except:
    pass

class AdminView:
    @staticmethod
    def render(usuario):
        # 1. ESTADO DA NAVEGAÇÃO
        if 'admin_aba' not in st.session_state:
            st.session_state['admin_aba'] = 'Usuarios'
        if 'user_to_edit' not in st.session_state:
            st.session_state['user_to_edit'] = None

        nome_display = usuario.nome if usuario and usuario.nome else "Admin"
        inicial = nome_display[0].upper()

        # 2. CSS GLOBAL
        st.markdown("""
            <style>
                /* Remove margens e oculta elementos padrão */
                .block-container { padding: 1rem !important; max-width: 100%; }
                #MainMenu, header, footer { display: none !important; }
                [data-testid="collapsedControl"] { display: none !important; }
                
                /* Cor de fundo e Zoom */
                [data-testid="stAppViewContainer"] { background-color: #C0C0C0 !important; }
                body { zoom: 0.75; overflow-x: hidden; }

                /* SIDEBAR (Coluna Esquerda) */
                [data-testid="stVerticalBlock"] > [style*="flex-direction: row"] > [data-testid="stColumn"]:first-child {
                    background-color: #D3D3D3 !important;
                    border-right: 1px solid #999;
                    padding: 20px !important;
                    min-height: 100vh !important; /* Altura total */
                    box-shadow: 2px 0 5px rgba(0,0,0,0.15);
                }

                /* Avatar e Botões */
                .avatar-circle {
                    width: 80px; height: 80px; background-color: #FF8C00; color: white;
                    border-radius: 50%; text-align: center; line-height: 80px; font-size: 32px;
                    font-weight: bold; margin: 0 auto 15px auto; border: 4px solid white;
                }
                .stButton button { width: 100%; border-radius: 8px; font-weight: 600; border: 1px solid #bbb; }
                
                /* Cards (Formulários) */
                [data-testid="stForm"] {
                    background-color: #FFFFFF; border-radius: 12px;
                    padding: 20px; border: 1px solid #aaa;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
                }
            </style>
        """, unsafe_allow_html=True)

        # 3. LAYOUT (Sidebar Falsa + Conteúdo)
        col_sidebar, col_content = st.columns([1, 5], gap="small")

        with col_sidebar:
            st.markdown(f"<div class='avatar-circle'>{inicial}</div>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align:center; margin:0;'>{nome_display}</h3>", unsafe_allow_html=True)
            st.markdown("---")
            
            if st.button("🏠 Dashboard", key="nav_d", use_container_width=True):
                st.session_state['admin_aba'] = 'Dashboard'; st.rerun()
            if st.button("👥 Usuários", key="nav_u", use_container_width=True):
                st.session_state['admin_aba'] = 'Usuarios'; st.rerun()
            if st.button("🚗 Veículos", key="nav_v", use_container_width=True):
                st.session_state['admin_aba'] = 'Veiculos'; st.rerun()
            
            st.markdown("<br>"*5, unsafe_allow_html=True)
            if st.button("🚪 Sair", key="nav_s", type="primary", use_container_width=True):
                st.session_state.clear(); st.rerun()

        with col_content:
            aba = st.session_state['admin_aba']
            if aba == 'Usuarios':
                AdminView.render_usuarios()
            elif aba == 'Veiculos':
                AdminView.render_veiculos()
            else:
                st.markdown("### 🏠 Dashboard")
                try:
                    conn = DatabaseService.get_connection()
                    k1, k2, k3 = st.columns(3)
                    tu = pd.read_sql("SELECT count(*) as c FROM usuarios", conn).iloc[0]['c']
                    tv = pd.read_sql("SELECT count(*) as c FROM veiculos", conn).iloc[0]['c']
                    k1.metric("Usuários", tu); k2.metric("Veículos", tv); k3.metric("Status", "OK")
                    conn.close()
                except: pass

    @staticmethod
    def render_usuarios():
        st.markdown("### 👥 Usuários")
        c1, c2 = st.columns([2, 1.2])
        
        # Lista
        with c1:
            try:
                conn = DatabaseService.get_connection()
                df = pd.read_sql_query("SELECT id, nome, email, perfil FROM usuarios ORDER BY id DESC", conn)
                h1, h2, h3, h4 = st.columns([0.5, 1.5, 2, 1])
                h1.caption("ID"); h2.caption("Nome"); h3.caption("Email"); h4.caption("Ação")
                st.markdown("<hr style='margin:5px 0; border-top:1px solid #999'>", unsafe_allow_html=True)

                for _, row in df.iterrows():
                    l1, l2, l3, l4 = st.columns([0.5, 1.5, 2, 1])
                    l1.write(f"#{row['id']}")
                    l2.write(row['nome'])
                    l3.write(row['email'])
                    b1, b2 = l4.columns(2)
                    if b1.button("✏️", key=f"e_{row['id']}"):
                        st.session_state['user_to_edit'] = row.to_dict(); st.rerun()
                    if b2.button("🗑️", key=f"d_{row['id']}"):
                        AdminView.excluir_usuario(row['id']); st.rerun()
                    st.markdown("<hr style='margin:2px 0; opacity:0.2'>", unsafe_allow_html=True)
                conn.close()
            except: pass

        # Formulário
        with c2:
            data = st.session_state['user_to_edit']
            is_edit = data is not None
            tit = "Editar" if is_edit else "Novo"
            
            with st.form("frm_user", clear_on_submit=not is_edit):
                st.write(f"#### {tit}")
                n = st.text_input("Nome", value=data['nome'] if is_edit else "")
                e = st.text_input("Email", value=data['email'] if is_edit else "")
                s = st.text_input("Senha", type="password", placeholder="Vazio = manter" if is_edit else "")
                opts = ["ADMIN", "GERENTE", "COORDENADOR", "LOJISTA", "PESQUISADOR"]
                p = st.selectbox("Perfil", opts, index=opts.index(data['perfil']) if is_edit and data['perfil'] in opts else 4)
                
                c_ok, c_canc = st.columns(2)
                if c_ok.form_submit_button("Salvar", type="primary", use_container_width=True):
                    if is_edit:
                        AdminView.atualizar_usuario(data['id'], n, e, s, p)
                        st.session_state['user_to_edit'] = None
                    else:
                        if n and e and s: AdminView.salvar_usuario(n, e, s, p)
                    st.rerun()
                if is_edit and c_canc.form_submit_button("Cancelar", use_container_width=True):
                    st.session_state['user_to_edit'] = None; st.rerun()

    @staticmethod
    def render_veiculos():
        st.markdown("### 🚗 Veículos")
        c1, c2 = st.columns([2, 1])
        try:
            conn = DatabaseService.get_connection()
            with c1:
                df = pd.read_sql_query("SELECT id, marca, modelo, versao, ano, preco_referencia FROM veiculos ORDER BY id DESC", conn)
                st.dataframe(df, use_container_width=True, hide_index=True)
            with c2:
                with st.form("frm_veic", clear_on_submit=True):
                    st.write("#### Adicionar")
                    ma = st.text_input("Marca"); mo = st.text_input("Modelo"); ve = st.text_input("Versão")
                    an = st.number_input("Ano", value=2024); pr = st.number_input("Preço", value=0.0)
                    if st.form_submit_button("Salvar", type="primary", use_container_width=True):
                        conn.execute("INSERT INTO veiculos (marca, modelo, versao, ano, preco_referencia) VALUES (?,?,?,?,?)", (ma,mo,ve,an,pr))
                        conn.commit(); st.rerun()
            conn.close()
        except: pass

    @staticmethod
    def salvar_usuario(n, e, s, p):
        try:
            h = hashlib.sha256(s.encode()).hexdigest()
            c = DatabaseService.get_connection()
            c.execute("INSERT INTO usuarios (nome, email, senha_hash, perfil) VALUES (?,?,?,?)", (n,e,h,p))
            c.commit(); c.close()
        except: pass

    @staticmethod
    def atualizar_usuario(id, n, e, s, p):
        try:
            c = DatabaseService.get_connection()
            if s: 
                h = hashlib.sha256(s.encode()).hexdigest()
                c.execute("UPDATE usuarios SET nome=?, email=?, senha_hash=?, perfil=? WHERE id=?", (n,e,h,p,id))
            else: 
                c.execute("UPDATE usuarios SET nome=?, email=?, perfil=? WHERE id=?", (n,e,p,id))
            c.commit(); c.close()
        except: pass

    @staticmethod
    def excluir_usuario(id):
        try:
            c = DatabaseService.get_connection()
            c.execute("DELETE FROM usuarios WHERE id=?", (id,))
            c.commit(); c.close()
        except: pass
