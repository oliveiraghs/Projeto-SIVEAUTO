import streamlit as st
from src.services.DatabaseService import DatabaseService
import pandas as pd
import time

class ManagerView:
    @staticmethod
    def render(usuario):
        # Pega a inicial para o avatar
        inicial = usuario.nome[0].upper() if usuario.nome else "G"

        # --- CSS IDENTICO AO ADMIN (Layout Estático e Sem Scroll) ---
        st.markdown(f"""
            <style>
                /* 1. CONFIGURAÇÕES GERAIS */
                body {{ zoom: 0.8; overflow: hidden; }}
                #MainMenu, footer, header {{ display: none !important; }}
                
                .block-container {{
                    padding-top: 1.5rem !important;
                    padding-bottom: 0rem !important;
                    max-width: 100%;
                }}

                /* 2. SIDEBAR (CINZA E FIXA) */
                [data-testid="stSidebar"] {{
                    background-color: #D3D3D3 !important;
                    min-width: 220px !important;
                }}
                [data-testid="stSidebar"] ::-webkit-scrollbar {{ display: none !important; }}

                /* 3. AVATAR */
                .avatar-circle {{
                    width: 70px; height: 70px;
                    background-color: #4B0082; /* Roxo para diferenciar Gerente do Admin */
                    color: white;
                    border-radius: 50%;
                    text-align: center; line-height: 70px;
                    font-size: 28px; font-weight: bold;
                    margin: 20px auto 10px auto;
                    border: 3px solid white;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }}

                /* 4. FORMULÁRIO (DIREITA) */
                [data-testid="stForm"] {{
                    background-color: #F8F9FA;
                    border-radius: 15px;
                    padding: 20px !important;
                    border: 1px solid #CCC;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
                }}
                .stTextInput, .stNumberInput {{ margin-bottom: -15px !important; }}
            </style>
        """, unsafe_allow_html=True)

        # --- BARRA LATERAL ---
        with st.sidebar:
            st.markdown(f"<div class='avatar-circle'>{inicial}</div>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align:center; color:#333; margin:0;'>{usuario.nome}</h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; color:#666; font-size:0.9rem;'>GERENTE DE FROTA</p>", unsafe_allow_html=True)
            st.write("---")
            
            st.button("🏠 Dashboard", use_container_width=True)
            st.button("🚗 Gestão de Veículos", use_container_width=True)
            st.button("📈 Relatórios", use_container_width=True)
            
            st.markdown("<div style='height: 30vh;'></div>", unsafe_allow_html=True)
            if st.button("🚪 Sair do Sistema", type="primary", use_container_width=True):
                del st.session_state['usuario_ativo']
                st.rerun()

        # --- LAYOUT PRINCIPAL (Lista Esquerda | Form Direita) ---
        col_lista, col_cadastro = st.columns([2, 1.2])

        # --- COLUNA 1: LISTA DE VEÍCULOS ---
        with col_lista:
            st.markdown("### 🚗 Base de Veículos (Referência)")
            
            conn = DatabaseService.get_connection()
            try:
                # Busca Veículos
                df = pd.read_sql_query("SELECT id, marca, modelo, ano, preco_referencia FROM veiculos ORDER BY id DESC", conn)
                
                # Cabeçalhos Ajustados para Veículos
                h1, h2, h3, h4, h5 = st.columns([0.5, 1.5, 2, 1.2, 1.5])
                h1.markdown("**ID**")
                h2.markdown("**Marca**")
                h3.markdown("**Modelo**")
                h4.markdown("**Preço Ref.**")
                h5.markdown("**Ações**")
                st.markdown("---")

                # Linhas
                for _, row in df.iterrows():
                    c1, c2, c3, c4, c5 = st.columns([0.5, 1.5, 2, 1.2, 1.5])
                    c1.write(f"#{row['id']}")
                    c2.write(row['marca'])
                    c3.write(f"{row['modelo']} ({row['ano']})")
                    c4.write(f"R$ {row['preco_referencia']:,.0f}")
                    
                    btn_col1, btn_col2 = c5.columns(2)
                    # Botão Editar
                    if btn_col1.button("✏️", key=f"edit_v_{row['id']}"):
                        st.session_state['veiculo_to_edit'] = row.to_dict()
                        st.rerun()
                    
                    # Botão Excluir
                    if btn_col2.button("🗑️", key=f"del_v_{row['id']}"):
                        ManagerView.excluir_veiculo(row['id'])
                        time.sleep(0.5)
                        st.rerun()
                    
                    st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Erro: {e}")
            finally:
                conn.close()

        # --- COLUNA 2: FORMULÁRIO DE VEÍCULO ---
        with col_cadastro:
            is_editing = 'veiculo_to_edit' in st.session_state
            v_data = st.session_state.get('veiculo_to_edit', {"marca": "", "modelo": "", "ano": 2024, "preco_referencia": 0.0, "id": None})
            
            titulo = "📝 Editar Veículo" if is_editing else "➕ Novo Veículo"
            
            with st.form("form_veiculo", clear_on_submit=not is_editing):
                st.markdown(f"### {titulo}")
                
                marca = st.text_input("Marca:", value=v_data['marca'], placeholder="Ex: Toyota")
                modelo = st.text_input("Modelo:", value=v_data['modelo'], placeholder="Ex: Corolla XEi")
                ano = st.number_input("Ano Fabricação:", min_value=1950, max_value=2030, value=int(v_data['ano']))
                preco = st.number_input("Preço de Referência (R$):", min_value=0.0, value=float(v_data['preco_referencia']), step=100.0)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                if is_editing:
                    c1, c2 = st.columns(2)
                    if c1.form_submit_button("Salvar", type="primary"):
                        ManagerView.atualizar_veiculo(v_data['id'], marca, modelo, ano, preco)
                        del st.session_state['veiculo_to_edit']
                        st.rerun()
                    if c2.form_submit_button("Cancelar"):
                        del st.session_state['veiculo_to_edit']
                        st.rerun()
                else:
                    if st.form_submit_button("Cadastrar Veículo", type="primary"):
                        if marca and modelo and preco > 0:
                            ManagerView.salvar_veiculo(marca, modelo, ano, preco)
                            st.success("Veículo Salvo!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.warning("Preencha Marca, Modelo e Preço.")

    # --- BANCO DE DADOS (VEÍCULOS) ---
    @staticmethod
    def salvar_veiculo(marca, modelo, ano, preco):
        conn = DatabaseService.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO veiculos (marca, modelo, ano, preco_referencia) VALUES (?, ?, ?, ?)", 
                       (marca, modelo, ano, preco))
        conn.commit()
        conn.close()

    @staticmethod
    def atualizar_veiculo(id_vec, marca, modelo, ano, preco):
        conn = DatabaseService.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE veiculos SET marca=?, modelo=?, ano=?, preco_referencia=? WHERE id=?", 
                       (marca, modelo, ano, preco, id_vec))
        conn.commit()
        conn.close()

    @staticmethod
    def excluir_veiculo(id_vec):
        conn = DatabaseService.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM veiculos WHERE id = ?", (id_vec,))
        conn.commit()
        conn.close()