import streamlit as st
from src.controllers.AuthController import AuthController
from src.models.Veiculo import Veiculo
import time
import random

class LoginView:
    @staticmethod
    def render():
        # --- CSS "ZERO SCROLL" (Versão Definitiva) ---
        st.markdown("""
            <style>
                /* 1. FORÇA BRUTA: Esconder a barra de rolagem visualmente */
                ::-webkit-scrollbar {
                    display: none !important;
                }
                
                /* 2. Travar a rolagem no container principal do Streamlit */
                [data-testid="stAppViewContainer"] {
                    overflow: hidden !important;
                }
                
                /* 3. Remover espaços mortos do cabeçalho e rodapé */
                header, footer, #MainMenu {
                    display: none !important;
                    height: 0 !important;
                }
                
                /* 4. Ajuste do Zoom e Espaçamento */
                body {
                    zoom: 0.75;
                }
                
                /* Zera o padding inferior que causa o espaço branco */
                .block-container {
                    padding-top: 2rem !important;
                    padding-bottom: 0rem !important;
                    max-width: 1100px;
                }

                /* 5. Título Principal */
                .header-container {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-bottom: 10px;
                }
                .header-icon { font-size: 3rem; margin-right: 15px; }
                .header-title h1 { color: #0F52BA; margin: 0; font-size: 2.5rem; line-height: 1.2; }
                .header-title p { color: #666; margin: 0; font-size: 1rem; }

                /* 6. Estilo dos Cartões */
                div[data-testid="column"] > div {
                    padding: 20px !important;
                    border-radius: 12px;
                }
                
                /* Cores de Fundo */
                div[data-testid="column"]:nth-of-type(1) > div {
                    background-color: white;
                    border: 1px solid #ddd;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
                }
                div[data-testid="column"]:nth-of-type(3) > div {
                    background-color: #f8f9fa;
                    border: 1px solid #e0e0e0;
                }

                /* 7. Inputs e Botões */
                .stTextInput, .stSelectbox { margin-bottom: -15px !important; }
                div[data-testid="stMarkdownContainer"] h3 { font-size: 1.3rem !important; margin-bottom: 10px !important; }
                
                button { height: 42px !important; margin-top: 10px !important; }

                /* Cores dos Botões */
                div[data-testid="column"]:nth-of-type(1) button {
                    background-color: #0F52BA !important;
                    color: white !important;
                    border: none !important;
                }
                div[data-testid="column"]:nth-of-type(3) button {
                    background-color: #28a745 !important;
                    color: white !important;
                    border: none !important;
                }

                /* 8. Resultado Compacto e HTML Seguro */
                .result-card {
                    background-color: #fff3cd;
                    border-left: 6px solid #ffc107;
                    padding: 12px 15px;
                    margin-top: 15px;
                    border-radius: 8px;
                    font-size: 0.95rem;
                }
                .price-tag {
                    color: #28a745;
                    font-weight: bold;
                    font-size: 1.4rem;
                    float: right; 
                }
            </style>
        """, unsafe_allow_html=True)

        # --- CABEÇALHO ---
        st.markdown("""
            <div class="header-container">
                <div class="header-icon">🚗</div>
                <div class="header-title">
                    <h1>SIVEAUTO</h1>
                    <p>Sistema Integrado de Auditoria e Cotação</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        col_login, col_gap, col_busca = st.columns([1, 0.1, 1.3])

        # --- LOGIN ---
        with col_login:
            st.markdown("<h3>🔐 Acesso Restrito</h3>", unsafe_allow_html=True)
            st.caption("Área exclusiva para gestão")
            
            email = st.text_input("Usuário:", placeholder="admin@siveauto.com")
            senha = st.text_input("Senha:", type="password", placeholder="••••••")
            
            if st.button("ENTRAR", use_container_width=True):
                if not email or not senha:
                    st.warning("Preencha os campos.")
                else:
                    usuario = AuthController.validar_login(email, senha)
                    if usuario:
                        st.session_state['usuario_ativo'] = usuario
                        st.rerun()
                    else:
                        st.error("Inválido.")

        # --- BUSCA ---
        with col_busca:
            st.markdown("<h3>🔎 Pesquisa de Mercado</h3>", unsafe_allow_html=True)
            
            # Filtros
            marcas = Veiculo.get_todas_marcas()
            marca = st.selectbox("Marca:", ["Selecione..."] + marcas)
            
            modelos = []
            if marca != "Selecione...":
                modelos = Veiculo.get_modelos_por_marca(marca)
            modelo = st.selectbox("Modelo:", ["Selecione..."] + modelos)
            
            anos = []
            if modelo != "Selecione...":
                anos = Veiculo.get_anos_por_modelo(modelo)
            ano = st.selectbox("Ano:", ["Selecione..."] + [str(x) for x in anos])

            # Botão
            buscar = st.button("BUSCAR VEÍCULO 🔍", use_container_width=True)
            
            # Resultado
            if buscar:
                if "Selecione..." in [marca, modelo, ano]:
                    st.warning("Selecione todos os dados.")
                else:
                    veic = Veiculo.buscar_veiculo_exato(marca, modelo, int(ano))
                    
                    if veic:
                        local = random.choice(["Loja Matriz - SP", "Filial Campinas", "AutoCenter Sul"])
                        # HTML Compacto (Sem indentação para evitar erro)
                        st.markdown(f"""<div class="result-card"><span class="price-tag">R$ {veic.preco_referencia:,.2f}</span><div style="font-weight:bold; color:#333;">✅ {veic.marca} {veic.modelo}</div><div style="margin-top:2px;">📅 Ano: {veic.ano}</div><div style="margin-top:2px; font-size:0.85rem;">📍 Local: <b>{local}</b></div></div>""", unsafe_allow_html=True)
                    else:
                        st.error("Não encontrado.")
            else:
                # Espaço vazio mínimo
                st.write("")