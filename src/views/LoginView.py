import streamlit as st
from src.controllers.AuthController import AuthController
from src.services.DatabaseService import DatabaseService
import pandas as pd
import time
import random

class LoginView:
    @staticmethod
    def render():
        # --- CSS GERAL E LAYOUT (Zoom 0.75) ---
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
                
                /* Fundo da Área Principal (Direita) - Cinza Escuro */
                [data-testid="stAppViewContainer"] {
                    background-color: #C0C0C0 !important; 
                    overflow-x: hidden !important;
                }

                /* ZOOM FIXO */
                body { zoom: 0.75; }

                /* --- SIDEBAR FIXA (ESQUERDA) - Onde ficará o LOGIN --- */
                [data-testid="stVerticalBlock"] > [style*="flex-direction: row"] > [data-testid="stColumn"]:first-child {
                    background-color: #D3D3D3 !important; /* Cinza Claro */
                    border-right: 1px solid #999;
                    padding: 25px !important;
                    min-height: 100vh !important;
                    box-shadow: 2px 0 10px rgba(0,0,0,0.1);
                }

                /* Título Principal (SIVEAUTO) na Área Central */
                .main-title {
                    text-align: center; color: #0F52BA; font-size: 4rem; font-weight: bold; margin-bottom: 0;
                    text-shadow: 1px 1px 2px rgba(255,255,255,0.5);
                }
                .main-subtitle {
                    text-align: center; color: #333; font-size: 1.2rem; margin-bottom: 40px;
                }

                /* Cards (Formulários) */
                div[data-testid="stForm"] {
                    background-color: white;
                    border-radius: 10px;
                    padding: 20px;
                    border: 1px solid #bbb;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                }
                
                /* Botões */
                .stButton button { width: 100%; height: 45px; border-radius: 8px; font-weight: bold; }
                
                /* Botão Login (Azul) */
                div[data-testid="stColumn"]:first-child button {
                    background-color: #0F52BA !important; color: white !important;
                }
                
                /* Botão Busca (Verde) */
                div[data-testid="stColumn"]:last-child button {
                    background-color: #28a745 !important; color: white !important;
                }

                /* Inputs compactos */
                .stTextInput, .stSelectbox { margin-bottom: -10px !important; }
                
                /* Resultado da Busca */
                .result-card {
                    background-color: #fff3cd; border-left: 6px solid #ffc107;
                    padding: 15px; margin-top: 20px; border-radius: 8px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                }
                .price-tag {
                    color: #28a745; font-weight: bold; font-size: 1.8rem; float: right; 
                }
            </style>
        """, unsafe_allow_html=True)

        # --- ESTRUTURA: SIDEBAR (1) | CONTEÚDO (4) ---
        col_sidebar, col_content = st.columns([1.2, 4], gap="large")

        # --- 1. SIDEBAR (ÁREA DE LOGIN) ---
        with col_sidebar:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<h2 style='text-align:center; color:#333;'>🔐 Acesso Restrito</h2>", unsafe_allow_html=True)
            st.caption("Faça login para acessar o painel administrativo.")
            
            with st.form("login_form"):
                email = st.text_input("Usuário", placeholder="admin@siveauto.com")
                st.markdown("<br>", unsafe_allow_html=True)
                senha = st.text_input("Senha", type="password", placeholder="••••••")
                st.markdown("<br>", unsafe_allow_html=True)
                
                submitted = st.form_submit_button("ENTRAR ACESSO")
                if submitted:
                    if not email or not senha:
                        st.warning("Preencha todos os campos.")
                    else:
                        usuario = AuthController.validar_login(email, senha)
                        if usuario:
                            st.session_state['usuario_ativo'] = usuario
                            st.rerun()
                        else:
                            st.error("Dados inválidos.")
            
            st.markdown("<br>"*5, unsafe_allow_html=True)
            st.info("Caso não tenha acesso, utilize a busca ao lado para consultas públicas.")

        # --- 2. CONTEÚDO PRINCIPAL (BUSCA PÚBLICA) ---
        with col_content:
            # Espaçador superior para centralizar verticalmente
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Título SIVEAUTO Gigante
            st.markdown("""
                <div class="main-title">🚗 SIVEAUTO</div>
                <div class="main-subtitle">Sistema Integrado de Auditoria e Cotação Veicular</div>
            """, unsafe_allow_html=True)

            # Centralizar o formulário de busca usando colunas internas
            c_left, c_form_busca, c_right = st.columns([1, 4, 1])
            
            with c_form_busca:
                st.markdown("### 🔎 Pesquisa Rápida de Mercado")
                
                conn = DatabaseService.get_connection()
                try:
                    df = pd.read_sql_query("SELECT marca, modelo, versao, ano, preco_referencia FROM veiculos", conn)
                    
                    # Container Branco para a Busca
                    with st.container(border=True):
                        # Filtros lado a lado para economizar espaço vertical
                        f1, f2 = st.columns(2)
                        with f1:
                            marcas = sorted(df['marca'].unique())
                            marca = st.selectbox("Marca", options=marcas, index=None, placeholder="Selecione...")
                            
                            versao_opts = sorted(df[(df['marca'] == marca) & (df['modelo'] == modelo)]['versao'].unique()) if 'modelo' in locals() and modelo else []
                            # Ajuste lógico para filtros
                        
                        # Recalculando filtros corretamente
                        modelos = sorted(df[df['marca'] == marca]['modelo'].unique()) if marca else []
                        
                        with f2:
                            modelo = st.selectbox("Modelo", options=modelos, index=None, disabled=not marca, placeholder="...")
                        
                        f3, f4 = st.columns(2)
                        with f3:
                            versoes = sorted(df[(df['marca'] == marca) & (df['modelo'] == modelo)]['versao'].unique()) if modelo else []
                            versao = st.selectbox("Versão", options=versoes, index=None, disabled=not modelo, placeholder="...")
                        
                        with f4:
                            anos = sorted(df[(df['marca'] == marca) & (df['modelo'] == modelo) & (df['versao'] == versao)]['ano'].unique()) if versao else []
                            ano = st.selectbox("Ano", options=anos, index=None, disabled=not versao, placeholder="...")

                        st.markdown("<br>", unsafe_allow_html=True)
                        buscar = st.button("🔍 CONSULTAR PREÇO DE REFERÊNCIA", use_container_width=True)

                    # Resultado
                    if buscar:
                        if not ano:
                            st.warning("Por favor, selecione todos os filtros acima.")
                        else:
                            res = df[(df['marca']==marca) & (df['modelo']==modelo) & (df['versao']==versao) & (df['ano']==ano)]
                            
                            if not res.empty:
                                row = res.iloc[0]
                                preco = row['preco_referencia']
                                local = random.choice(["Matriz São Paulo", "Filial Campinas", "Unidade Sul"])
                                preco_fmt = f"R$ {preco:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                                
                                st.markdown(f"""
                                    <div class="result-card">
                                        <span class="price-tag">{preco_fmt}</span>
                                        <h3 style="margin:0; color:#333;">✅ {row['marca']} {row['modelo']}</h3>
                                        <p style="margin:5px 0; color:#555;">{row['versao']} - {row['ano']}</p>
                                        <hr style="margin:10px 0; border-top:1px solid #e0c070;">
                                        <small>📍 Disponível para auditoria em: <b>{local}</b></small>
                                    </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.error("Veículo não encontrado na base.")

                except Exception as e:
                    st.error(f"Erro de conexão: {e}")
                finally:
                    conn.close()
