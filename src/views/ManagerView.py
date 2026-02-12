import streamlit as st
from src.services.DatabaseService import DatabaseService
import pandas as pd
import time

class ManagerView:
    @staticmethod
    def render(usuario):
        # 1. ESTADO DE NAVEGAÇÃO
        if 'manager_aba' not in st.session_state: st.session_state['manager_aba'] = 'Veiculos'
        if 'veiculo_to_edit' not in st.session_state: st.session_state['veiculo_to_edit'] = None

        nome_display = usuario.nome if usuario else "Gerente"
        inicial = nome_display[0].upper()

        # 2. CSS PADRÃO (SIDEBAR CINZA + ZOOM 0.75)
        st.markdown("""
            <style>
                .block-container { padding-top: 3rem !important; max-width: 100%; }
                #MainMenu, header, footer { display: none !important; }
                [data-testid="collapsedControl"] { display: none !important; }
                [data-testid="stAppViewContainer"] { background-color: #C0C0C0 !important; }
                body { zoom: 0.75; overflow-x: hidden; }
                [data-testid="stVerticalBlock"] > [style*="flex-direction: row"] > [data-testid="stColumn"]:first-child {
                    background-color: #D3D3D3 !important; border-right: 1px solid #999;
                    padding: 20px !important; min-height: 100vh !important;
                }
                .avatar-circle {
                    width: 80px; height: 80px; background-color: #FF8C00; color: white;
                    border-radius: 50%; text-align: center; line-height: 80px; font-size: 32px;
                    font-weight: bold; margin: 0 auto 15px auto; border: 4px solid white;
                }
                div[data-testid="stForm"], .row-card {
                    background-color: #FFFFFF; border-radius: 12px; padding: 20px;
                    border: 1px solid #aaa; box-shadow: 0 4px 15px rgba(0,0,0,0.08);
                    margin-bottom: 10px;
                }
                .stButton button { width: 100%; border-radius: 8px; font-weight: bold; }
                input { background-color: white !important; color: #333 !important; }
            </style>
        """, unsafe_allow_html=True)

        col_sidebar, col_content = st.columns([1, 5], gap="small")

        with col_sidebar:
            st.markdown(f"<div class='avatar-circle'>{inicial}</div>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align:center;'>{nome_display}</h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; color:#555;'>GERÊNCIA</p><hr>", unsafe_allow_html=True)
            
            if st.button("🚗 Catálogo Veículos", use_container_width=True):
                st.session_state['manager_aba'] = 'Veiculos'; st.rerun()
            
            st.markdown("<br>"*5, unsafe_allow_html=True)
            if st.button("🚪 Sair", type="primary", use_container_width=True):
                st.session_state.clear(); st.rerun()

        with col_content:
            ManagerView.render_veiculos()

    @staticmethod
    def render_veiculos():
        st.markdown("### 🚗 Gestão do Catálogo Mestre")
        st.caption("Cadastre marca e modelo. O preço será capturado pelos pesquisadores.")
        
        conn = DatabaseService.get_connection()
        c1, c2 = st.columns([2.5, 1.2])

        with c1:
            # CORREÇÃO: SQL sem 'preco_referencia' para evitar o erro do print image_e0f579.png
            df = pd.read_sql("SELECT id, marca, modelo, versao, ano FROM veiculos ORDER BY id DESC", conn)
            
            # Tabela Manual com Botões
            h1, h2, h3, h4, h5 = st.columns([0.4, 1.2, 1.5, 0.6, 0.8])
            h1.markdown("**ID**"); h2.markdown("**Marca**"); h3.markdown("**Modelo**"); h4.markdown("**Ano**"); h5.markdown("**Ações**")
            st.markdown("<hr style='margin:0 0 10px 0;'>", unsafe_allow_html=True)

            for _, row in df.iterrows():
                with st.container():
                    l1, l2, l3, l4, l5 = st.columns([0.4, 1.2, 1.5, 0.6, 0.8])
                    l1.write(f"#{row['id']}")
                    l2.write(row['marca'])
                    l3.write(f"{row['modelo']} {row['versao']}")
                    l4.write(str(row['ano']))
                    btn_ed, btn_del = l5.columns(2)
                    if btn_ed.button("✏️", key=f"ed_v_{row['id']}"):
                        st.session_state['veiculo_to_edit'] = row.to_dict(); st.rerun()
                    if btn_del.button("🗑️", key=f"del_v_{row['id']}"):
                        conn.execute("DELETE FROM veiculos WHERE id=?", (row['id'],)); conn.commit(); st.rerun()
                st.markdown("<hr style='margin:5px 0; opacity:0.1;'>", unsafe_allow_html=True)

        with c2:
            data = st.session_state['veiculo_to_edit']
            is_edit = data is not None
            # clear_on_submit garante a limpeza dos campos
            with st.form("frm_veic_mgr", clear_on_submit=True):
                st.write(f"#### {'Editar' if is_edit else 'Novo'} Modelo")
                ma = st.text_input("Marca", value=data['marca'] if is_edit else "")
                mo = st.text_input("Modelo", value=data['modelo'] if is_edit else "")
                ve = st.text_input("Versão", value=data['versao'] if is_edit else "")
                an = st.number_input("Ano", value=int(data['ano']) if is_edit else 2025, step=1)
                
                if st.form_submit_button("Salvar no Catálogo", type="primary"):
                    if ma and mo:
                        if is_edit:
                            conn.execute("UPDATE veiculos SET marca=?, modelo=?, versao=?, ano=? WHERE id=?", (ma, mo, ve, an, data['id']))
                        else:
                            conn.execute("INSERT INTO veiculos (marca, modelo, versao, ano) VALUES (?,?,?,?)", (ma, mo, ve, an))
                        conn.commit()
                        st.session_state['veiculo_to_edit'] = None
                        st.success("✅ Sucesso!"); time.sleep(0.5); st.rerun()
                    else: st.error("Marca e Modelo obrigatórios.")
                
                if is_edit and st.form_submit_button("Cancelar"):
                    st.session_state['veiculo_to_edit'] = None; st.rerun()
        conn.close()