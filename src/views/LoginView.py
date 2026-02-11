import streamlit as st
from src.controllers.AuthController import AuthController
import time

class LoginView:
    @staticmethod
    def render():
        # --- Cabeçalho (Header) ---
        st.markdown("<h1 style='text-align: center;'>SIVEAUTO 🚗</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Sistema Integrado de Consulta de Veículos Automotores</p>", unsafe_allow_html=True)
        st.markdown("---")

        # Criação das duas colunas (Esquerda: Login | Direita: Consulta)
        col_login, col_consulta = st.columns([1, 1.2], gap="large")

        # --- LADO ESQUERDO: LOGIN ---
        with col_login:
            with st.container(border=True):
                st.subheader("Login")
                
                email = st.text_input("Usuário:", placeholder="Digite seu user")
                senha = st.text_input("Senha:", type="password", placeholder="Digite sua senha")
                
                # Espaço para alinhar o botão
                st.markdown("###") 
                
                if st.button("Entrar", type="primary", use_container_width=True):
                    if not email or not senha:
                        st.warning("Preencha todos os campos!")
                    else:
                        usuario = AuthController.validar_login(email, senha)
                        if usuario:
                            st.success(f"Olá, {usuario.nome}!")
                            st.session_state['usuario_ativo'] = usuario
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Credenciais inválidas.")

        # --- LADO DIREITO: CONSULTA RÁPIDA (Pública) ---
        with col_consulta:
            with st.container(border=True):
                st.markdown("<h3 style='color: green;'>Consulta rápida</h3>", unsafe_allow_html=True)
                
                # Campos simulando a busca pública
                c1, c2 = st.columns(2)
                with c1:
                    marca = st.selectbox("Marca:", ["Selecione a marca", "Fiat", "Honda", "Toyota", "Volkswagen"])
                    ano = st.selectbox("Ano:", ["Selecione o ano", "2024", "2023", "2022", "2021"])
                with c2:
                    modelo = st.selectbox("Modelo:", ["Selecione o modelo", "Uno", "Civic", "Corolla", "Polo"])
                    opcionais = st.selectbox("Opcionais:", ["Padrão", "Completo", "Blindado"])

                if st.button("Buscar 🔍", use_container_width=True):
                    # Lógica simples para mostrar que funciona (sem conectar no banco ainda)
                    st.info("🔎 Buscando preço médio na tabela FIPE...")
                    time.sleep(1.5)
                    
                    # Simulação de Resultado (Card Amarelo da imagem)
                    st.warning(f"""
                        **Resultado da Pesquisa:**
                        \n🚗 Veículo: {marca} {modelo} ({ano})
                        \n💰 Preço Médio de Mercado: **R$ 85.490,00**
                        \n📅 Referência: Fev/2026
                    """)