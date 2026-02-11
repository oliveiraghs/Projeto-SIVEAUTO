import streamlit as st
from src.services.DatabaseService import DatabaseService
import pandas as pd
import time

class ResearcherView:
    @staticmethod
    def render(usuario):
        # Controle de navegação interna
        if 'aba_pesquisador' not in st.session_state:
            st.session_state['aba_pesquisador'] = 'nova_coleta'

        inicial = usuario.nome[0].upper() if usuario.nome else "P"

        # --- CONFIGURAÇÃO VISUAL (CSS PADRÃO) ---
        st.markdown("""
            <style>
                /* Remove margens padrão */
                .block-container {
                    padding-top: 1rem !important;
                    padding-bottom: 0rem !important;
                    max-width: 100% !important;
                }
                #MainMenu, header, footer { display: none !important; }
                [data-testid="collapsedControl"] { display: none !important; }

                /* Fundo Geral - Cinza Escuro */
                [data-testid="stAppViewContainer"] {
                    background-color: #C0C0C0 !important;
                    overflow-x: hidden !important;
                }

                /* Zoom Fixo */
                body { zoom: 0.75; }

                /* --- SIDEBAR FIXA (ESQUERDA) --- */
                [data-testid="stVerticalBlock"] > [style*="flex-direction: row"] > [data-testid="stColumn"]:first-child {
                    background-color: #D3D3D3 !important;
                    border-right: 1px solid #999;
                    padding: 20px !important;
                    min-height: 100vh !important;
                    box-shadow: 2px 0 5px rgba(0,0,0,0.15);
                }

                /* Avatar */
                .avatar-circle {
                    width: 70px; height: 70px; background-color: #FF8C00; color: white;
                    border-radius: 50%; text-align: center; line-height: 70px;
                    font-size: 28px; font-weight: bold; margin: 20px auto 10px auto;
                    border: 3px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }

                /* Botões Laterais */
                .stButton button { 
                    width: 100%; border-radius: 8px; font-weight: bold; 
                    border: 1px solid #bbb;
                }

                /* Formulários Brancos */
                div[data-testid="stForm"], div[data-testid="stVerticalBlock"] > [style*="flex-direction: column"] > div[data-testid="stVerticalBlock"] {
                    background-color: #FFFFFF;
                    border-radius: 12px;
                    padding: 15px;
                    /* border: 1px solid #aaa; removido para evitar bordas duplas em containers internos */
                }
                
                /* Inputs compactos */
                .stSelectbox, .stNumberInput, .stTextInput { margin-bottom: -15px !important; }
            </style>
        """, unsafe_allow_html=True)

        # --- ESTRUTURA: SIDEBAR (1) | CONTEÚDO (5) ---
        col_sidebar, col_content = st.columns([1, 5], gap="medium")

        # --- SIDEBAR FIXA ---
        with col_sidebar:
            st.markdown(f"<div class='avatar-circle'>{inicial}</div>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align:center; margin:0;'>{usuario.nome}</h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; color:#555; font-size:0.9rem;'>PESQUISADOR</p>", unsafe_allow_html=True)
            st.markdown("---")
            
            if st.button("📋 Nova Coleta", use_container_width=True):
                st.session_state['aba_pesquisador'] = 'nova_coleta'
                st.rerun()
                
            if st.button("🕒 Minhas Coletas", use_container_width=True):
                st.session_state['aba_pesquisador'] = 'historico'
                st.rerun()
            
            st.markdown("<br>"*10, unsafe_allow_html=True) # Espaçador inferior
            if st.button("🚪 Sair", type="primary", use_container_width=True):
                del st.session_state['usuario_ativo']
                st.rerun()

        # --- CONTEÚDO PRINCIPAL ---
        with col_content:
            if st.session_state['aba_pesquisador'] == 'nova_coleta':
                ResearcherView.render_formulario(usuario)
            else:
                ResearcherView.render_historico(usuario)


    @staticmethod
    def render_formulario(usuario):
        st.markdown("### 📝 Registro de Preços")
        
        # Centraliza o formulário na área de conteúdo
        _, col_centro, _ = st.columns([0.2, 4, 0.2])

        with col_centro:
            conn = DatabaseService.get_connection()
            try:
                # Query com Versão
                df_v = pd.read_sql_query("SELECT id, marca, modelo, versao, ano FROM veiculos ORDER BY marca", conn)
                
                # Card Branco (Estilizado pelo CSS global ou container)
                with st.container(border=True):
                    st.markdown("##### 🚗 Seleção do Veículo")
                    
                    # Filtros em Cascata
                    c1, c2 = st.columns(2)
                    marcas = sorted(df_v['marca'].unique())
                    marca = c1.selectbox("Marca:", options=marcas, index=None, placeholder="Selecione...")
                    
                    modelos = []
                    if marca:
                        modelos = df_v[df_v['marca'] == marca]['modelo'].unique()
                    modelo = c2.selectbox("Modelo:", options=sorted(modelos), index=None, placeholder="Selecione...", disabled=not marca)

                    c3, c4 = st.columns(2)
                    versoes = []
                    if modelo:
                        versoes = df_v[(df_v['marca'] == marca) & (df_v['modelo'] == modelo)]['versao'].unique()
                    versao = c3.selectbox("Versão:", options=sorted(versoes), index=None, placeholder="Selecione...", disabled=not modelo)

                    v_id_sel = None
                    anos = []
                    if versao:
                        anos = df_v[(df_v['marca'] == marca) & (df_v['modelo'] == modelo) & (df_v['versao'] == versao)]['ano'].unique()
                    ano_sel = c4.selectbox("Ano:", options=sorted(anos, reverse=True), index=None, placeholder="Ano...", disabled=not versao)
                    
                    if ano_sel:
                         v_id_sel = df_v[
                            (df_v['marca'] == marca) & 
                            (df_v['modelo'] == modelo) & 
                            (df_v['versao'] == versao) & 
                            (df_v['ano'] == ano_sel)
                        ]['id'].values[0]

                    st.markdown("---")
                    
                    # Formulário de Coleta
                    with st.form("form_coleta", clear_on_submit=True):
                        st.markdown("##### 💰 Oferta Encontrada")
                        c_p, c_l = st.columns([1, 1.5])
                        
                        valor = c_p.number_input("Valor (R$):", min_value=0.0, step=100.0, format="%.2f")
                        if valor > 0:
                            valor_fmt = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                            st.caption(f"Leitura: **{valor_fmt}**")
                        
                        loja = c_l.text_input("Loja / Concessionária:", placeholder="Ex: Central Veículos")
                        link = st.text_input("Link ou Foto (Opcional):")
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.form_submit_button("🚀 GRAVAR COLETA", type="primary", use_container_width=True):
                            if v_id_sel and valor > 0 and loja:
                                sucesso, msg = ResearcherView.salvar_coleta(v_id_sel, usuario.id, valor, loja, link)
                                if sucesso:
                                    st.success(msg)
                                    time.sleep(1.5)
                                    st.rerun()
                                else:
                                    st.warning(msg)
                            else:
                                st.error("⚠️ Preencha os campos obrigatórios.")
            finally:
                conn.close()

    @staticmethod
    def render_historico(usuario):
        st.markdown("### 🕒 Meu Histórico de Coletas")
        
        # Container Branco para a Tabela
        with st.container(border=True):
            conn = DatabaseService.get_connection()
            try:
                query = """
                    SELECT c.id, v.marca, v.modelo, v.versao, v.ano, c.valor_encontrado, c.local_loja, c.data_coleta
                    FROM coletas c
                    JOIN veiculos v ON c.veiculo_id = v.id
                    WHERE c.usuario_id = ?
                    ORDER BY c.data_coleta DESC
                """
                df = pd.read_sql_query(query, conn, params=(usuario.id,))
                
                if df.empty:
                    st.info("Nenhuma coleta registrada até o momento.")
                else:
                    h1, h2, h3, h4 = st.columns([2.5, 1, 1.5, 1])
                    h1.caption("**Veículo / Versão**")
                    h2.caption("**Valor**")
                    h3.caption("**Loja**")
                    h4.caption("**Data**")
                    st.markdown("---")

                    for _, row in df.iterrows():
                        c1, c2, c3, c4 = st.columns([2.5, 1, 1.5, 1])
                        c1.write(f"{row['marca']} {row['modelo']} {row['versao']} ({row['ano']})")
                        
                        valor_fmt = f"R$ {row['valor_encontrado']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                        c2.write(f"**{valor_fmt}**")
                        c3.write(row['local_loja'])
                        
                        data_br = pd.to_datetime(row['data_coleta']).strftime('%d/%m %H:%M')
                        c4.write(data_br)
                        st.markdown("<hr style='margin: 2px 0; border-top: 1px solid #EEE;'>", unsafe_allow_html=True)
            finally:
                conn.close()

    @staticmethod
    def salvar_coleta(v_id, u_id, valor, loja, foto):
        conn = DatabaseService.get_connection()
        cursor = conn.cursor()
        
        # Trava PS-17 (Duplicidade no dia)
        cursor.execute("""
            SELECT id FROM coletas 
            WHERE veiculo_id = ? 
            AND usuario_id = ? 
            AND local_loja = ? 
            AND date(data_coleta) = date('now')
        """, (v_id, u_id, loja))
        
        if cursor.fetchone():
            conn.close()
            return False, "⚠️ Duplicidade! Este veículo já foi coletado nesta loja hoje."
        
        try:
            cursor.execute("""
                INSERT INTO coletas (veiculo_id, usuario_id, valor_encontrado, local_loja, foto_url) 
                VALUES (?, ?, ?, ?, ?)
            """, (v_id, u_id, valor, loja, foto))
            conn.commit()
            return True, "✅ Coleta realizada com sucesso!"
        except Exception as e:
            return False, f"❌ Erro técnico: {e}"
        finally:
            conn.close()
