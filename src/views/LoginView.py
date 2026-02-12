import streamlit as st
from src.controllers.AuthController import AuthController
from src.controllers.ColetaController import ColetaController
from src.services.DatabaseService import DatabaseService
import pandas as pd

class LoginView:
    @staticmethod
    def render():
        # --- CSS MANTIDO (Identidade Visual Validada) ---
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
                    padding: 25px !important; min-height: 100vh !important;
                    box-shadow: 2px 0 10px rgba(0,0,0,0.1);
                }
                .main-title {
                    text-align: center; color: #0F52BA; font-size: 4rem; font-weight: bold; margin-bottom: 0;
                    text-shadow: 1px 1px 2px rgba(255,255,255,0.5);
                }
                .result-card {
                    background-color: #fff3cd; border-left: 8px solid #ffc107;
                    padding: 25px; margin-top: 20px; border-radius: 12px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                }
                .stButton button { width: 100%; height: 45px; border-radius: 8px; font-weight: bold; }
                
                div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
                    background-color: #FFFFFF !important; border-color: #CCCCCC !important; color: #333 !important;
                }
                input, div[data-baseweb="select"] span { color: #333 !important; }
            </style>
        """, unsafe_allow_html=True)

        col_sidebar, col_content = st.columns([1.2, 4], gap="large")

        # --- 1. LOGIN ---
        with col_sidebar:
            st.markdown("<br><h2 style='text-align:center; color:#333;'>🔐 Acesso</h2>", unsafe_allow_html=True)
            st.caption("Área restrita para administradores, coordenadores e pesquisadores.")
            with st.form("login_form"):
                email = st.text_input("Usuário", placeholder="ex@siveauto.com")
                senha = st.text_input("Senha", type="password")
                if st.form_submit_button("ENTRAR NO SISTEMA"):
                    usuario = AuthController.validar_login(email, senha)
                    if usuario: st.session_state['usuario_ativo'] = usuario; st.rerun()
                    else: st.error("Credenciais inválidas.")
            st.markdown("<br>"*5, unsafe_allow_html=True)
            st.info("Utilize a busca ao lado para consultas públicas de preços.")

        # --- 2. BUSCA PÚBLICA ---
        with col_content:
            st.markdown("<br><div class='main-title'>🚗 SIVEAUTO</div>", unsafe_allow_html=True)
            st.markdown("<p style='text-align:center; color:#333; font-size:1.2rem;'>Sistema Integrado de Auditoria e Cotação</p>", unsafe_allow_html=True)

            _, central_col, _ = st.columns([0.5, 4, 0.5])
            with central_col:
                st.markdown("### 🔎 Pesquisa Rápida de Mercado")
                conn = DatabaseService.get_connection()
                try:
                    df_v = pd.read_sql("SELECT marca, modelo, versao, ano FROM veiculos", conn)
                    with st.container(border=True):
                        f1, f2 = st.columns(2)
                        marca = f1.selectbox("Marca", options=sorted(df_v['marca'].unique()), index=None, placeholder="Selecione...")
                        modelo = f2.selectbox("Modelo", options=sorted(df_v[df_v['marca']==marca]['modelo'].unique()) if marca else [], index=None, placeholder="...")
                        f3, f4 = st.columns(2)
                        versao = f3.selectbox("Versão", options=sorted(df_v[(df_v['marca']==marca)&(df_v['modelo']==modelo)]['versao'].unique()) if modelo else [], index=None, placeholder="...")
                        ano = f4.selectbox("Ano", options=sorted(df_v[(df_v['marca']==marca)&(df_v['modelo']==modelo)&(df_v['versao']==versao)]['ano'].unique()) if versao else [], index=None, placeholder="...")

                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("🔍 CONSULTAR PREÇO ATUALIZADO", type="primary", use_container_width=True):
                            if not ano:
                                st.warning("Por favor, selecione todos os filtros para uma busca precisa.")
                            else:
                                resultado = ColetaController.obter_estatisticas_publicas(marca, modelo, versao, ano)
                                
                                if resultado and resultado['status'] == 'ok':
                                    ColetaController.registrar_busca(marca, modelo, versao, ano)

                                    st.markdown(f"""
                                        <div class="result-card">
                                            <h2 style="margin:0; color:#333;">✅ {marca} {modelo}</h2>
                                            <p style="color:#666;">{versao} • Ano {ano}</p>
                                            <hr style="border-top: 1px solid #d4a017;">
                                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
                                                <span style="font-size:1.2rem; font-weight:bold;">Média de Mercado:</span>
                                                <span style="font-size:1.8rem; font-weight:bold; color:#333;">R$ {resultado['media']:,.2f}</span>
                                            </div>
                                            <div style="background-color:#e8f5e9; padding:15px; border-radius:8px; border:1px solid #28a745;">
                                                <b style="color:#28a745; font-size:1.1rem;">🏆 Melhor Oferta Validada:</b>
                                                <span style="float:right; font-weight:bold; font-size:1.4rem; color:#28a745;">R$ {resultado['melhor_preco']:,.2f}</span>
                                                <div style="clear:both;"></div>
                                                <small style="color:#555;">Disponível em: <b>{resultado['loja_barata']}</b></small>
                                            </div>
                                            <p style="margin-top:10px; font-size:0.8rem; color:#888;">Baseado em {resultado['total_amostras']} amostras de mercado verificadas.</p>
                                        </div>
                                    """, unsafe_allow_html=True)
                                elif resultado and resultado['status'] == 'empty':
                                    st.error("Nenhuma coleta realizada para este veículo ainda.")
                                    ColetaController.registrar_busca(marca, modelo, versao, ano)
                                else:
                                    st.error("Veículo não encontrado ou dados insuficientes.")
                finally:
                    conn.close()