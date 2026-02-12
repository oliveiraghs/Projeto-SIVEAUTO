import streamlit as st
from src.views.LoginView import LoginView
from src.views.AdminView import AdminView
from src.views.ManagerView import ManagerView
from src.views.ResearcherView import ResearcherView
from src.views.CoordinatorView import CoordinatorView
from src.views.LojistaView import LojistaView

try:
    st.set_page_config(layout="wide", page_title="SIVEAUTO", page_icon="🚗")
except:
    pass

def main():
    if 'usuario_ativo' not in st.session_state:
        LoginView.render()
    else:
        usuario = st.session_state['usuario_ativo']
        
        if usuario.perfil == 'ADMIN':
            AdminView.render(usuario)
        elif usuario.perfil == 'GERENTE':
            ManagerView.render(usuario)
        elif usuario.perfil == 'COORDENADOR':
            CoordinatorView.render(usuario)
        elif usuario.perfil == 'LOJISTA':
            LojistaView.render(usuario)
        elif usuario.perfil == 'PESQUISADOR':
            ResearcherView.render(usuario)
        else:
            st.error(f"Perfil desconhecido: {usuario.perfil}")

if __name__ == "__main__":
    main()