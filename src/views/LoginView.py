import streamlit as st
from src.controllers.AuthController import AuthController
from src.services.DatabaseService import DatabaseService
import pandas as pd
import time
import random

class LoginView:
    @staticmethod
    def render():
        # --- CSS "ZERO SCROLL" (Mantido Estável) ---
        st.markdown("""
            <style>
                /* 1. FORÇA BRUTA: Esconder a barra de rolagem visualmente */
                ::-webkit-scrollbar { display: none !important; }
                
                /* 2. Travar a rolagem no container principal do Streamlit */
                [data-testid="stAppViewContainer"] { overflow: hidden !important; }
                
                /* 3. Remover espaços mortos do cabeçalho e rodapé */
                header, footer, #MainMenu { display: none !important; height: 0 !important; }
                
                /* 4. Ajuste do Zoom e Espaçamento */
                body { zoom: 0.75; }
                
                /* Zera o padding inferior que causa o espaço branco */
                .block-container {
                    padding-top: 2rem !important;
                    padding-bottom: 0rem !important;
                    max-width: 1100px;
                }

                /* 5. Título Principal */
                .header-container {
                    display: flex; align-items: center; justify-content: center; margin-bottom: 10px;
                }
                .header-icon { font-size: 3rem; margin-right: 15px; }
                .header-title h1 { color: #0F52BA; margin: 0; font-size: 2.5rem; line-height: 1.2; }
                .header-title p { color: #666; margin: 0; font-size: 1rem; }

                /* 6. Estilo dos Cartões */
                div[data-testid="column"] > div {
                    padding: 20px !important; border-radius: 12px;
                }
                
                /* Cores de Fundo */
                div[data-testid="column"]:nth-of-type(1) > div {
                    background-color: white; border: 1px solid #ddd; box-shadow: 0 4px 10px rgba(0,0,0,0.05);
                }
                div[data-testid="column"]:nth-of-type(3) > div {
                    background-color: #f8f9fa; border: 1px solid #e0e0e0;
                }

                /* 7. Inputs e Botões */
                .stTextInput, .stSelectbox { margin-bottom: -15px !important; }
                div[data-testid="stMarkdownContainer"] h3 { font-size: 1.3rem !important; margin-bottom: 10px !important; }
                
                button { height: 42px !important; margin-top: 10px !important; }

                /* Cores dos Botões */
                div[data-testid="column"]:nth-of-type(1) button {
                    background-color: #0F52BA !important; color: white !important; border: none !important;
                }
                div[data-testid="column"]:nth-of-type(3) button {
                    background-color: #28a745 !important; color: white !important; border: none !important;
                }

                /* 8. Resultado Compacto e HTML Seguro */
                .result-card {
                    background-color: #fff3cd; border-left: 6px solid #ffc107;
                    padding: 12px 15px; margin-top: 15px; border-radius: 8px; font-size: 0.95rem;
                }
                .price-tag {
                    color: #28a745; font-weight: bold; font-size: 1.4rem; float: right; 
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

        # --- LOGIN (Esquerda - Mantido Original) ---
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

        # --- BUSCA (Direita - Atualizado com Versão) ---
        with col_busca:
            st.markdown("<h3>🔎 Pesquisa de Mercado</h3>", unsafe_allow_html=True)
            
            # Conexão direta para garantir filtros dinâmicos rápidos
            conn = DatabaseService.get_connection()
            # Carregamos apenas o necessário para os combos
            df = pd.read_sql_query("SELECT marca, modelo, versao, ano, preco_referencia FROM veiculos", conn)
            conn.close()
            
            # 1. Filtro Marca
            marcas = sorted(df['marca'].unique())
            marca = st.selectbox("Marca:", options=marcas, index=None, placeholder="Selecione...")
            
            # 2. Filtro Modelo (Depende da Marca)
            modelos = []
            if marca:
                modelos = sorted(df[df['marca'] == marca]['modelo'].unique())
            modelo = st.selectbox("Modelo:", options=modelos, index=None, placeholder="Selecione...", disabled=not marca)
            
            # 3. Filtro Versão (Depende do Modelo) --> NOVO CAMPO
            versoes = []
            if modelo:
                versoes = sorted(df[(df['marca'] == marca) & (df['modelo'] == modelo)]['versao'].unique())
            versao = st.selectbox("Versão:", options=versoes, index=None, placeholder="Selecione...", disabled=not modelo)

            # 4. Filtro Ano (Depende da Versão)
            anos = []
            if versao:
                anos = sorted(df[(df['marca'] == marca) & (df['modelo'] == modelo) & (df['versao'] == versao)]['ano'].unique())
            ano = st.selectbox("Ano:", options=anos, index=None, placeholder="Selecione...", disabled=not versao)

            # Botão
            buscar = st.button("BUSCAR VEÍCULO 🔍", use_container_width=True)
            
            # Resultado
            if buscar:
                if not ano:
                    st.warning("Selecione todos os dados (Marca, Modelo, Versão e Ano).")
                else:
                    # Busca exata no DataFrame filtrado
                    resultado = df[
                        (df['marca'] == marca) & 
                        (df['modelo'] == modelo) & 
                        (df['versao'] == versao) & 
                        (df['ano'] == ano)
                    ]
                    
                    if not resultado.empty:
                        row = resultado.iloc[0]
                        preco = row['preco_referencia']
                        local = random.choice(["Loja Matriz - SP", "Filial Campinas", "AutoCenter Sul"])
                        
                        # Formatação de Moeda Visual
                        preco_fmt = f"R$ {preco:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                        
                        st.markdown(f"""
                            <div class="result-card">
                                <span class="price-tag">{preco_fmt}</span>
                                <div style="font-weight:bold; color:#333;">✅ {row['marca']} {row['modelo']}</div>
                                <div style="margin-top:2px; font-size:0.9rem; color:#555;">Versão: {row['versao']}</div>
                                <div style="margin-top:2px;">📅 Ano: {row['ano']}</div>
                                <div style="margin-top:2px; font-size:0.85rem;">📍 Local: <b>{local}</b></div>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error("Veículo não encontrado na base de referência.")