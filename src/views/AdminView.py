import streamlit as st
from src.services.DatabaseService import DatabaseService
from src.controllers.ColetaController import ColetaController # NOVA IMPORTAÇÃO
import pandas as pd
import hashlib
import time

class AdminView:
    @staticmethod
    def render(usuario):
        # 1. ESTADO DA NAVEGAÇÃO
        if 'admin_aba' not in st.session_state: st.session_state['admin_aba'] = 'Dashboard'
        if 'user_to_edit' not in st.session_state: st.session_state['user_to_edit'] = None
        if 'veiculo_to_edit' not in st.session_state: st.session_state['veiculo_to_edit'] = None
        if 'loja_to_edit' not in st.session_state: st.session_state['loja_to_edit'] = None

        nome_display = usuario.nome if usuario and usuario.nome else "Admin"
        inicial = nome_display[0].upper()

        # 2. CSS GLOBAL PADRONIZADO (Preservando Zoom 0.75 e Sidebar)
        st.markdown("""
            <style>
                .block-container { padding: 1rem !important; max-width: 100% !important; }
                #MainMenu, header, footer { display: none !important; }
                [data-testid="collapsedControl"] { display: none !important; }
                [data-testid="stAppViewContainer"] { background-color: #C0C0C0 !important; }
                body { zoom: 0.75; overflow-x: hidden; }

                /* SIDEBAR */
                [data-testid="stVerticalBlock"] > [style*="flex-direction: row"] > [data-testid="stColumn"]:first-child {
                    background-color: #D3D3D3 !important; border-right: 1px solid #999;
                    padding: 20px !important; min-height: 100vh !important;
                    box-shadow: 2px 0 5px rgba(0,0,0,0.15);
                }
                .avatar-circle {
                    width: 80px; height: 80px; background-color: #FF8C00; color: white;
                    border-radius: 50%; text-align: center; line-height: 80px; font-size: 32px;
                    font-weight: bold; margin: 0 auto 15px auto; border: 4px solid white;
                }
                .stButton button { width: 100%; border-radius: 8px; font-weight: 600; border: 1px solid #bbb; }
                
                /* CARDS E FORMULÁRIOS */
                [data-testid="stForm"], .row-card {
                    background-color: #FFFFFF; border-radius: 12px; padding: 20px;
                    border: 1px solid #aaa; box-shadow: 0 4px 15px rgba(0,0,0,0.08);
                    margin-bottom: 10px;
                }

                /* CORREÇÃO DE INPUTS */
                div[data-baseweb="input"] > div, div[data-baseweb="base-input"], div[data-baseweb="select"] > div {
                    background-color: #FFFFFF !important; border-color: #CCCCCC !important; color: #333 !important;
                }
                input, div[data-baseweb="select"] span, .stMarkdown label, p { color: #333 !important; }
                
                /* Tabelas Manuais */
                .table-header { font-weight: bold; color: #333; padding-bottom: 10px; border-bottom: 2px solid #999; margin-bottom: 15px; }
            </style>
        """, unsafe_allow_html=True)

        col_sidebar, col_content = st.columns([1, 5], gap="small")

        # --- BARRA LATERAL ---
        with col_sidebar:
            st.markdown(f"<div class='avatar-circle'>{inicial}</div>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align:center; margin:0; color:#333;'>{nome_display}</h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; color:#555; font-size:0.8rem;'>SUPER ADMIN</p>", unsafe_allow_html=True)
            st.markdown("---")
            
            if st.button("🏠 Dashboard", use_container_width=True): st.session_state['admin_aba'] = 'Dashboard'; st.rerun()
            if st.button("🔍 Demandas (Buscas)", use_container_width=True): st.session_state['admin_aba'] = 'Demandas'; st.rerun()
            if st.button("👥 Usuários", use_container_width=True): st.session_state['admin_aba'] = 'Usuarios'; st.rerun()
            if st.button("🚗 Veículos", use_container_width=True): st.session_state['admin_aba'] = 'Veiculos'; st.rerun()
            if st.button("🏪 Lojas", use_container_width=True): st.session_state['admin_aba'] = 'Lojas'; st.rerun()
            if st.button("📊 Monitoramento", use_container_width=True): st.session_state['admin_aba'] = 'Coletas'; st.rerun()
            
            st.markdown("<br>"*5, unsafe_allow_html=True)
            if st.button("🚪 Sair", type="primary", use_container_width=True): st.session_state.clear(); st.rerun()

        # --- ÁREA CENTRAL DE CONTEÚDO ---
        with col_content:
            aba = st.session_state['admin_aba']
            if aba == 'Usuarios': AdminView.render_usuarios()
            elif aba == 'Veiculos': AdminView.render_veiculos()
            elif aba == 'Lojas': AdminView.render_lojas()
            elif aba == 'Coletas': AdminView.render_coletas() # ALTERADO AQUI
            elif aba == 'Demandas': AdminView.render_demandas()
            else: AdminView.render_dashboard()

    # --- 1. DASHBOARD ---
    @staticmethod
    def render_dashboard():
        st.markdown("### 📊 Dashboard de Auditoria e Mercado")
        conn = DatabaseService.get_connection()
        try:
            with st.container(border=True):
                k1, k2, k3, k4 = st.columns(4)
                k1.metric("Usuários", pd.read_sql("SELECT count(*) as c FROM usuarios", conn).iloc[0]['c'])
                k2.metric("Base Veículos", pd.read_sql("SELECT count(*) as c FROM veiculos", conn).iloc[0]['c'])
                k3.metric("Lojas Ativas", pd.read_sql("SELECT count(*) as c FROM lojas WHERE status='APROVADA'", conn).iloc[0]['c'])
                k4.metric("Coletas Realizadas", pd.read_sql("SELECT count(*) as c FROM coletas", conn).iloc[0]['c'])
            
            c1, c2 = st.columns(2)
            with c1:
                with st.container(border=True):
                    st.write("**💰 Preço Médio por Marca**")
                    df_p = pd.read_sql("SELECT v.marca, AVG(c.valor_encontrado) as preco FROM coletas c JOIN veiculos v ON c.veiculo_id = v.id GROUP BY v.marca", conn)
                    if not df_p.empty: st.bar_chart(df_p.set_index('marca'))
                    else: st.info("Sem dados.")
            with c2:
                with st.container(border=True):
                    st.write("**📍 Engajamento por Loja**")
                    df_l = pd.read_sql("SELECT local_loja, count(*) as total FROM coletas GROUP BY local_loja", conn)
                    if not df_l.empty: st.bar_chart(df_l.set_index('local_loja'))
                    else: st.info("Sem dados.")

            c3, c4 = st.columns(2)
            with c3:
                with st.container(border=True):
                    st.write("**🚗 Mix de Veículos**")
                    df_m = pd.read_sql("SELECT marca, count(*) as total FROM veiculos GROUP BY marca", conn)
                    if not df_m.empty: st.bar_chart(df_m.set_index('marca'))
            with c4:
                with st.container(border=True):
                    st.write("**👥 Perfis de Usuário**")
                    df_u = pd.read_sql("SELECT perfil, count(*) as total FROM usuarios GROUP BY perfil", conn)
                    if not df_u.empty: st.bar_chart(df_u.set_index('perfil'))
        finally: conn.close()

    # --- 2. DEMANDAS ---
    @staticmethod
    def render_demandas():
        st.markdown("### 🔍 Inteligência de Mercado (Demandas)")
        conn = DatabaseService.get_connection()
        try:
            df_full = pd.read_sql("SELECT data_busca, marca_buscada, modelo_buscado, versao_buscada, ano_buscado FROM buscas ORDER BY id DESC", conn)
            c1, c2 = st.columns([2, 1])
            with c1:
                with st.container(border=True):
                    st.write("**🏆 Veículos Mais Buscados**")
                    df_chart = pd.read_sql("SELECT marca_buscada || ' ' || modelo_buscado as veiculo, count(*) as total FROM buscas GROUP BY veiculo ORDER BY total DESC LIMIT 10", conn)
                    if not df_chart.empty: st.bar_chart(df_chart.set_index('veiculo'))
                    else: st.info("Sem buscas.")
            with c2:
                with st.container(border=True):
                    st.metric("Total de Buscas", len(df_full))
                    st.markdown("---")
                    st.download_button("📥 Baixar CSV", df_full.to_csv(index=False).encode('utf-8'), "demandas.csv", "text/csv", use_container_width=True)
            st.markdown("#### Histórico Recente")
            st.dataframe(df_full, use_container_width=True, hide_index=True)
        finally: conn.close()

    # --- 3. USUÁRIOS ---
    @staticmethod
    def render_usuarios():
        st.markdown("### 👥 Gestão de Usuários")
        c1, c2 = st.columns([2.5, 1.2])
        with c1:
            conn = DatabaseService.get_connection()
            df = pd.read_sql("SELECT id, nome, email, perfil FROM usuarios ORDER BY id DESC", conn)
            h1, h2, h3, h4, h5 = st.columns([0.4, 1.2, 1.8, 1.0, 0.8])
            h1.markdown("**ID**"); h2.markdown("**Nome**"); h3.markdown("**Email**"); h4.markdown("**Perfil**"); h5.markdown("**Ações**")
            st.markdown("<hr style='margin:0 0 15px 0;'>", unsafe_allow_html=True)
            for _, row in df.iterrows():
                with st.container():
                    l1, l2, l3, l4, l5 = st.columns([0.4, 1.2, 1.8, 1.0, 0.8])
                    l1.write(f"#{row['id']}"); l2.write(row['nome']); l3.write(row['email']); l4.write(f"`{row['perfil']}`")
                    btn_ed, btn_del = l5.columns(2)
                    if btn_ed.button("✏️", key=f"ed_u_{row['id']}"): st.session_state['user_to_edit'] = row.to_dict(); st.rerun()
                    if btn_del.button("🗑️", key=f"del_u_{row['id']}"): conn.execute("DELETE FROM usuarios WHERE id=?", (row['id'],)); conn.commit(); st.rerun()
            conn.close()
        with c2:
            data = st.session_state['user_to_edit']
            is_edit = data is not None
            with st.form("frm_user", clear_on_submit=True):
                st.write(f"#### {'Editar' if is_edit else 'Novo'} Usuário")
                n = st.text_input("Nome", value=data['nome'] if is_edit else ""); e = st.text_input("Email", value=data['email'] if is_edit else ""); s = st.text_input("Senha", type="password", placeholder="Vazio = manter atual"); p = st.selectbox("Perfil", ["ADMIN", "GERENTE", "COORDENADOR", "LOJISTA", "PESQUISADOR"], index=0)
                if st.form_submit_button("Salvar Registro", type="primary"):
                    conn = DatabaseService.get_connection()
                    if is_edit:
                        if s: h = hashlib.sha256(s.encode()).hexdigest(); conn.execute("UPDATE usuarios SET nome=?, email=?, senha_hash=?, perfil=? WHERE id=?", (n,e,h,p,data['id']))
                        else: conn.execute("UPDATE usuarios SET nome=?, email=?, perfil=? WHERE id=?", (n,e,p,data['id']))
                    else: h = hashlib.sha256(s.encode()).hexdigest(); conn.execute("INSERT INTO usuarios (nome, email, senha_hash, perfil) VALUES (?,?,?,?)", (n,e,h,p))
                    conn.commit(); conn.close(); st.session_state['user_to_edit'] = None; st.rerun()
                if is_edit and st.form_submit_button("Cancelar"): st.session_state['user_to_edit'] = None; st.rerun()

    # --- 4. VEÍCULOS ---
    @staticmethod
    def render_veiculos():
        st.markdown("### 🚗 Base de Veículos (Catálogo)")
        c1, c2 = st.columns([2.5, 1.2])
        with c1:
            conn = DatabaseService.get_connection()
            df = pd.read_sql("SELECT id, marca, modelo, versao, ano FROM veiculos ORDER BY id DESC", conn)
            h1, h2, h3, h4, h5, h6 = st.columns([0.4, 0.8, 1.0, 1.5, 0.6, 0.8])
            h1.markdown("**ID**"); h2.markdown("**Marca**"); h3.markdown("**Modelo**"); h4.markdown("**Versão**"); h5.markdown("**Ano**"); h6.markdown("**Ações**")
            st.markdown("<hr style='margin:0 0 10px 0;'>", unsafe_allow_html=True)
            for _, row in df.iterrows():
                with st.container():
                    l1, l2, l3, l4, l5, l6 = st.columns([0.4, 0.8, 1.0, 1.5, 0.6, 0.8])
                    l1.write(f"#{row['id']}"); l2.write(row['marca']); l3.write(row['modelo']); l4.write(row['versao']); l5.write(str(row['ano']))
                    btn_ed, btn_del = l6.columns(2)
                    if btn_ed.button("✏️", key=f"ed_v_{row['id']}"): st.session_state['veiculo_to_edit'] = row.to_dict(); st.rerun()
                    if btn_del.button("🗑️", key=f"del_v_{row['id']}"): conn.execute("DELETE FROM veiculos WHERE id=?", (row['id'],)); conn.commit(); st.rerun()
            conn.close()
        with c2:
            data = st.session_state['veiculo_to_edit']
            is_edit = data is not None
            with st.form("frm_veic", clear_on_submit=True):
                st.write(f"#### {'Editar' if is_edit else 'Novo'} Veículo")
                ma = st.text_input("Marca", value=data['marca'] if is_edit else ""); mo = st.text_input("Modelo", value=data['modelo'] if is_edit else ""); ve = st.text_input("Versão", value=data['versao'] if is_edit else ""); an = st.number_input("Ano", value=int(data['ano']) if is_edit else 2024, step=1)
                if st.form_submit_button("Salvar no Catálogo", type="primary"):
                    conn = DatabaseService.get_connection()
                    if is_edit: conn.execute("UPDATE veiculos SET marca=?, modelo=?, versao=?, ano=? WHERE id=?", (ma,mo,ve,an,data['id']))
                    else: conn.execute("INSERT INTO veiculos (marca, modelo, versao, ano) VALUES (?,?,?,?)", (ma,mo,ve,an))
                    conn.commit(); conn.close(); st.session_state['veiculo_to_edit'] = None; st.rerun()
                if is_edit and st.form_submit_button("Cancelar"): st.session_state['veiculo_to_edit'] = None; st.rerun()

    # --- 5. LOJAS ---
    @staticmethod
    def render_lojas():
        st.markdown("### 🏪 Gestão da Rede de Lojas")
        c1, c2 = st.columns([2.5, 1.2])
        with c1:
            conn = DatabaseService.get_connection()
            df = pd.read_sql("SELECT id, nome, endereco, status FROM lojas ORDER BY id DESC", conn)
            h1, h2, h3, h4 = st.columns([1.5, 1.8, 1.0, 0.8])
            h1.markdown("**Nome**"); h2.markdown("**Endereço**"); h3.markdown("**Status**"); h4.markdown("**Ações**")
            st.markdown("<hr style='margin:0 0 10px 0;'>", unsafe_allow_html=True)
            for _, row in df.iterrows():
                with st.container():
                    l1, l2, l3, l4 = st.columns([1.5, 1.8, 1.0, 0.8])
                    l1.write(row['nome']); l2.write(row['endereco']); l3.write(f"`{row['status']}`")
                    btn_ed, btn_del = l4.columns(2)
                    if btn_ed.button("✏️", key=f"ed_l_{row['id']}"): st.session_state['loja_to_edit'] = row.to_dict(); st.rerun()
                    if btn_del.button("🗑️", key=f"del_l_{row['id']}"): conn.execute("DELETE FROM lojas WHERE id=?", (row['id'],)); conn.commit(); st.rerun()
            conn.close()
        with c2:
            data = st.session_state['loja_to_edit']
            is_edit = data is not None
            with st.form("frm_loja", clear_on_submit=True):
                st.write(f"#### {'Editar' if is_edit else 'Novo'} Loja"); nome = st.text_input("Nome", value=data['nome'] if is_edit else ""); end = st.text_input("Endereço", value=data['endereco'] if is_edit else ""); stt = st.selectbox("Status", ["APROVADA", "PENDENTE", "REJEITADA"], index=0)
                if st.form_submit_button("Salvar Loja", type="primary"):
                    conn = DatabaseService.get_connection()
                    if is_edit: conn.execute("UPDATE lojas SET nome=?, endereco=?, status=? WHERE id=?", (nome,end,stt,data['id']))
                    else: conn.execute("INSERT INTO lojas (nome, endereco, status) VALUES (?,?,?)", (nome,end,stt))
                    conn.commit(); conn.close(); st.session_state['loja_to_edit'] = None; st.rerun()
                if is_edit and st.form_submit_button("Cancelar"): st.session_state['loja_to_edit'] = None; st.rerun()

    # --- 6. MONITORAMENTO (COM AUDITORIA VISUAL DE OUTLIERS) ---
    @staticmethod
    def render_coletas():
        st.markdown("### 📊 Monitoramento de Coletas (Auditoria)")
        
        # Chama a lógica inteligente do Controller em vez da query bruta
        df = ColetaController.buscar_coletas_com_auditoria()
        
        col_top, col_down = st.columns([4, 1])
        with col_down:
            st.download_button("📥 Exportar CSV", df.to_csv(index=False).encode('utf-8'), "coletas_auditor.csv", "text/csv", use_container_width=True)
        
        if not df.empty and 'is_outlier' in df.columns:
            # Lógica de Visualização: Pinta de vermelho claro se for outlier
            def highlight_outliers(row):
                if row['is_outlier']:
                    return ['background-color: #ffcccc; color: #900'] * len(row)
                return [''] * len(row)
            
            st.dataframe(df.style.apply(highlight_outliers, axis=1), use_container_width=True, hide_index=True)
            
            # KPI de Alerta
            total_outliers = df['is_outlier'].sum()
            if total_outliers > 0:
                st.error(f"⚠️ Atenção: {total_outliers} coletas detectadas com desvio de preço suspeito (Linhas vermelhas). Verifique!")
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)