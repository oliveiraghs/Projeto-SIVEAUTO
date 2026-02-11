import streamlit as st
from src.views.LoginView import LoginView
from src.views.AdminView import AdminView
from src.views.ManagerView import ManagerView  # <--- 1. NOVO IMPORT

st.set_page_config(
    page_title="SIVEAUTO - Gestão", 
    page_icon="🚗", 
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    if 'usuario_ativo' not in st.session_state:
        LoginView.render()
    else:
        usuario = st.session_state['usuario_ativo']
        
        # Roteamento por Perfil
        if usuario.perfil == 'ADMIN':
            AdminView.render(usuario)
            
        elif usuario.perfil == 'GERENTE': # <--- 2. NOVA ROTA
            ManagerView.render(usuario)
            
        else:
            # Placeholder para Pesquisadores
            with st.sidebar:
                st.title("SIVEAUTO")
                if st.button("Sair"):
                    del st.session_state['usuario_ativo']
                    st.rerun()
            st.info(f"Painel de {usuario.perfil} em construção.")

if __name__ == "__main__":
    main()