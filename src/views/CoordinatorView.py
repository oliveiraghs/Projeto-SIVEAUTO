import streamlit as st
from src.services.DatabaseService import DatabaseService
import pandas as pd
import time

class CoordinatorView:
    @staticmethod
    def render(usuario):
        if 'aba_coord' not in st.session_state:
            st.session_state['aba_coord'] = 'pendentes'

        inicial = usuario.nome[0].upper() if usuario.nome else "C"

        st.markdown("""
            <style>
                .block-container { padding-top: 3rem !important; }
                [data-testid="stAppViewContainer"] { background-color: #C0C0C0 !important; }
                body { zoom: 0.75; }
                [data-testid="stVerticalBlock"] > [style*="flex-direction: row"] > [data-testid="stColumn"]:first-child {
                    background-color: #D3D3D3 !important; border-right: 1px solid #999;
                    padding: 20px !important; min-height: 100vh !important;
                }
                .avatar-circle {
                    width: 80px; height: 80px; background-color: #FF8C00; color: white;
                    border-radius: 50%; text-align: center; line-height: 80px; font-size: 32px;
                    font-weight: bold; margin: 0 auto 15px auto; border: 4px solid white;
                }
                [data-testid="stForm"], .stDataFrame, .stExpander {
                    background-color: #FFFFFF; border-radius: 12px;
                    border: 1px solid #aaa; box-shadow: 0 4px 15px rgba(0,0,0,0.08);
                }
            </style>
        """, unsafe_allow_html=True)

        col_sidebar, col_content = st.columns([1, 5], gap="small")

        with col_sidebar:
            st.markdown(f"<div class='avatar-circle'>{inicial}</div>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align:center;'>{usuario.nome}</h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;'>COORDENAÇÃO</p><hr>", unsafe_allow_html=True)
            if st.button("🚦 Aprovações", use_container_width=True): 
                st.session_state['aba_coord'] = 'pendentes'; st.rerun()
            if st.button("🏪 Rede Ativa", use_container_width=True): 
                st.session_state['aba_coord'] = 'rede'; st.rerun()
            st.markdown("<br>"*5, unsafe_allow_html=True)
            if st.button("🚪 Sair", type="primary", use_container_width=True): 
                st.session_state.clear(); st.rerun()

        with col_content:
            conn = DatabaseService.get_connection()
            if st.session_state['aba_coord'] == 'pendentes':
                st.markdown("### 🚦 Aprovações Pendentes")
                pendentes = pd.read_sql("SELECT id, nome, endereco, telefone FROM lojas WHERE status='PENDENTE'", conn)
                if pendentes.empty: st.success("✅ Nenhuma solicitação pendente.")
                else:
                    for _, row in pendentes.iterrows():
                        with st.expander(f"📌 {row['nome']}", expanded=True):
                            st.write(f"Endereço: {row['endereco']} | Tel: {row['telefone']}")
                            c1, c2 = st.columns(2)
                            if c1.button("✅ Aprovar", key=f"ap_{row['id']}", use_container_width=True):
                                conn.execute("UPDATE lojas SET status='APROVADA' WHERE id=?", (row['id'],))
                                conn.commit(); st.rerun()
                            if c2.button("❌ Rejeitar", key=f"rj_{row['id']}", use_container_width=True):
                                conn.execute("UPDATE lojas SET status='REJEITADA' WHERE id=?", (row['id'],))
                                conn.commit(); st.rerun()
            else:
                st.markdown("### 🏪 Rede de Lojas Ativas")
                df = pd.read_sql("SELECT nome, endereco, status FROM lojas WHERE status='APROVADA'", conn)
                st.dataframe(df, use_container_width=True, hide_index=True)
            conn.close()