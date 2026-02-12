import streamlit as st
from src.services.DatabaseService import DatabaseService
import pandas as pd
import time

class LojistaView:
    @staticmethod
    def render(usuario):
        # 1. CONTROLE DE NAVEGAÇÃO (Igual Admin/Pesquisador)
        if 'aba_lojista' not in st.session_state:
            st.session_state['aba_lojista'] = 'cadastro'

        inicial = usuario.nome[0].upper() if usuario.nome else "L"

        # 2. CSS PADRÃO (Layout Fixo + Cores)
        st.markdown("""
            <style>
                .block-container { padding: 1rem !important; max-width: 100%; }
                #MainMenu, header, footer { display: none !important; }
                [data-testid="collapsedControl"] { display: none !important; }
                [data-testid="stAppViewContainer"] { background-color: #C0C0C0 !important; }
                body { zoom: 0.75; overflow-x: hidden; }
                
                /* Sidebar Customizada */
                [data-testid="stVerticalBlock"] > [style*="flex-direction: row"] > [data-testid="stColumn"]:first-child {
                    background-color: #D3D3D3 !important; border-right: 1px solid #999;
                    padding: 20px !important; min-height: 100vh !important;
                }
                .avatar-circle {
                    width: 80px; height: 80px; background-color: #FF8C00; color: white;
                    border-radius: 50%; text-align: center; line-height: 80px; font-size: 32px;
                    font-weight: bold; margin: 0 auto 15px auto; border: 4px solid white;
                }
                [data-testid="stForm"], .stDataFrame {
                    background-color: #FFFFFF; border-radius: 12px; padding: 20px;
                    border: 1px solid #aaa; box-shadow: 0 4px 15px rgba(0,0,0,0.08);
                }
                /* Inputs */
                div[data-baseweb="input"] > div, input { background-color: #FFFFFF !important; color: #333 !important; }
                .stButton button { width: 100%; border-radius: 8px; font-weight: bold; }
            </style>
        """, unsafe_allow_html=True)

        col_sidebar, col_content = st.columns([1, 5], gap="small")

        # --- BARRA LATERAL (MENU) ---
        with col_sidebar:
            st.markdown(f"<div class='avatar-circle'>{inicial}</div>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align:center; margin:0; color:#333;'>{usuario.nome}</h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; color:#555; font-size:0.9rem;'>LOJISTA</p>", unsafe_allow_html=True)
            st.markdown("---")
            
            # Botões de Navegação
            if st.button("📝 Nova Loja", use_container_width=True): 
                st.session_state['aba_lojista'] = 'cadastro'
                st.rerun()
                
            if st.button("📋 Meus Status", use_container_width=True): 
                st.session_state['aba_lojista'] = 'status'
                st.rerun()
            
            st.markdown("<br>"*5, unsafe_allow_html=True)
            if st.button("🚪 Sair", type="primary", use_container_width=True): 
                st.session_state.clear()
                st.rerun()

        # --- CONTEÚDO PRINCIPAL ---
        with col_content:
            if st.session_state['aba_lojista'] == 'cadastro':
                LojistaView.render_cadastro(usuario)
            else:
                LojistaView.render_status(usuario)

    @staticmethod
    def render_cadastro(usuario):
        st.markdown("### 📝 Solicitar Cadastro de Loja")
        
        conn = DatabaseService.get_connection()
        
        with st.form("form_loja", clear_on_submit=True):
            st.write("Preencha os dados da loja para análise da Coordenação:")
            
            nome = st.text_input("Nome Fantasia")
            end = st.text_input("Endereço Completo")
            tel = st.text_input("Telefone")
            
            if st.form_submit_button("Enviar para Aprovação", type="primary"):
                if nome and end:
                    # Trava de Duplicidade
                    duplicado = conn.execute(
                        "SELECT id FROM lojas WHERE nome = ? AND endereco = ?", 
                        (nome, end)
                    ).fetchone()
                    
                    if duplicado:
                        st.error("⚠️ Esta loja já foi cadastrada anteriormente!")
                    else:
                        try:
                            conn.execute("""
                                INSERT INTO lojas (nome, endereco, telefone, responsavel_id, status)
                                VALUES (?, ?, ?, ?, 'PENDENTE')
                            """, (nome, end, tel, usuario.id))
                            conn.commit()
                            
                            st.success("✅ Solicitação enviada com sucesso! Aguarde aprovação.")
                            time.sleep(1.5)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao salvar: {e}")
                else:
                    st.warning("⚠️ Preencha pelo menos Nome e Endereço.")
        conn.close()

    @staticmethod
    def render_status(usuario):
        st.markdown("### 📋 Status das Solicitações")
        
        conn = DatabaseService.get_connection()
        df = pd.read_sql("""
            SELECT nome, endereco, telefone, status, criado_em 
            FROM lojas 
            WHERE responsavel_id = ? 
            ORDER BY id DESC
        """, conn, params=(usuario.id,))
        
        if not df.empty:
            st.dataframe(
                df, 
                use_container_width=True,
                hide_index=True,
                column_config={
                    "nome": "Loja",
                    "endereco": "Endereço",
                    "status": st.column_config.TextColumn("Status", help="Situação da aprovação"),
                    "criado_em": st.column_config.DatetimeColumn("Data", format="DD/MM/YYYY")
                }
            )
        else:
            st.info("Você ainda não cadastrou nenhuma loja.")
        conn.close()