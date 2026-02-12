import streamlit as st
from src.services.DatabaseService import DatabaseService
import pandas as pd
import time

class ResearcherView:
    @staticmethod
    def render(usuario):
        # 1. CONTROLE DE NAVEGAÇÃO E ESTADO
        if 'aba_pesquisador' not in st.session_state:
            st.session_state['aba_pesquisador'] = 'nova_coleta'

        # Nome e inicial para o Avatar
        nome_exibicao = usuario.nome if usuario.nome else "Pesquisador"
        inicial = nome_exibicao[0].upper()

        # 2. CSS COMPLETO E PADRONIZADO (Identidade Visual SIVEAUTO)
        st.markdown("""
            <style>
                /* Layout Global e Zoom */
                .block-container { padding-top: 2rem !important; max-width: 100% !important; }
                [data-testid="stAppViewContainer"] { background-color: #C0C0C0 !important; }
                body { zoom: 0.75; overflow-x: hidden; }
                
                /* Sidebar Cinza Lateral */
                [data-testid="stVerticalBlock"] > [style*="flex-direction: row"] > [data-testid="stColumn"]:first-child {
                    background-color: #D3D3D3 !important; border-right: 1px solid #999;
                    padding: 20px !important; min-height: 100vh !important;
                    box-shadow: 2px 0 5px rgba(0,0,0,0.1);
                }
                
                /* Avatar Circular */
                .avatar-circle {
                    width: 80px; height: 80px; background-color: #FF8C00; color: white;
                    border-radius: 50%; text-align: center; line-height: 80px; font-size: 32px;
                    font-weight: bold; margin: 0 auto 15px auto; border: 4px solid white;
                }
                
                /* Estilização de Forms e Dataframes */
                div[data-testid="stForm"], .stDataFrame {
                    background-color: #FFFFFF; border-radius: 12px; padding: 25px;
                    border: 1px solid #aaa; box-shadow: 0 4px 15px rgba(0,0,0,0.08);
                    margin-bottom: 20px;
                }
                
                /* Ajuste de visibilidade de inputs */
                div[data-baseweb="input"] > div, div[data-baseweb="select"] > div, input {
                    background-color: #FFFFFF !important; color: #333 !important;
                }
                
                /* Botões de Ação */
                .stButton button { width: 100%; border-radius: 8px; font-weight: bold; height: 45px; }
            </style>
        """, unsafe_allow_html=True)

        # 3. DIVISÃO DE COLUNAS (Menu | Conteúdo)
        col_sidebar, col_content = st.columns([1, 5], gap="small")

        with col_sidebar:
            st.markdown(f"<div class='avatar-circle'>{inicial}</div>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align:center; margin:0;'>{nome_exibicao}</h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; color:#555; font-size:0.9rem;'>PESQUISADOR</p><hr>", unsafe_allow_html=True)
            
            if st.button("📋 Nova Coleta", use_container_width=True):
                st.session_state['aba_pesquisador'] = 'nova_coleta'; st.rerun()
                
            if st.button("🕒 Histórico", use_container_width=True):
                st.session_state['aba_pesquisador'] = 'historico'; st.rerun()
            
            st.markdown("<br>"*5, unsafe_allow_html=True)
            if st.button("🚪 Sair", type="primary", use_container_width=True):
                st.session_state.clear(); st.rerun()

        # --- ÁREA DE CONTEÚDO ---
        with col_content:
            conn = DatabaseService.get_connection()
            
            if st.session_state['aba_pesquisador'] == 'nova_coleta':
                st.markdown("### 📝 Registro de Coleta de Campo")
                
                # BUSCA REATIVA DE VEÍCULOS E LOJAS
                df_v = pd.read_sql("SELECT id, marca, modelo, versao, ano FROM veiculos", conn)
                df_v['marca'] = df_v['marca'].astype(str).str.strip()
                
                df_l = pd.read_sql("SELECT id, nome FROM lojas WHERE status = 'APROVADA'", conn)

                if df_v.empty:
                    st.info("ℹ️ O catálogo de veículos está vazio. O Gerente precisa cadastrar modelos primeiro.")
                elif df_l.empty:
                    st.warning("⚠️ Nenhuma loja aprovada disponível. O Coordenador precisa aprovar lojas primeiro.")
                else:
                    # CENTRALIZAÇÃO PROPORCIONAL
                    _, central_col, _ = st.columns([0.1, 4, 0.1])
                    
                    with central_col:
                        # --- PARTE A: SELEÇÃO (Container nativo remove a barra branca) ---
                        with st.container(border=True):
                            st.markdown("##### 🚗 Selecione o Veículo no Catálogo")
                            c1, c2 = st.columns(2)
                            ma = c1.selectbox("Marca", options=sorted(df_v['marca'].unique()), index=None, placeholder="Escolha a Marca...", key='sel_marca')
                            
                            modelos_filt = sorted(df_v[df_v['marca'] == ma]['modelo'].unique()) if ma else []
                            mo = c2.selectbox("Modelo", options=modelos_filt, index=None, placeholder="Selecione o Modelo...", disabled=not ma, key='sel_modelo')
                            
                            c3, c4 = st.columns(2)
                            versoes_filt = sorted(df_v[(df_v['marca'] == ma) & (df_v['modelo'] == mo)]['versao'].unique()) if mo else []
                            ve = c3.selectbox("Versão", options=versoes_filt, index=None, placeholder="Selecione a Versão...", disabled=not mo, key='sel_versao')
                            
                            anos_filt = sorted(df_v[(df_v['marca'] == ma) & (df_v['modelo'] == mo) & (df_v['versao'] == ve)]['ano'].unique(), reverse=True) if ve else []
                            an = c4.selectbox("Ano", options=anos_filt, index=None, placeholder="Ano...", disabled=not ve, key='sel_ano')

                        # --- PARTE B: FORMULÁRIO DE DADOS ---
                        with st.form("form_coleta_final", clear_on_submit=True):
                            st.markdown("##### 💰 Detalhes da Oferta Encontrada")
                            cv, cl = st.columns([1, 1.5])
                            valor = cv.number_input("Preço Encontrado (R$)", min_value=0.0, step=100.0, key='num_preco')
                            loja_nome = cl.selectbox("Loja Visitada (Rede Aprovada)", options=df_l['nome'].unique(), key='sel_loja_coleta')

                            if st.form_submit_button("🚀 GRAVAR COLETA NO BANCO", type="primary"):
                                if ma and mo and ve and an and valor > 0:
                                    # Captura ID
                                    match = df_v[(df_v['marca']==ma)&(df_v['modelo']==mo)&(df_v['versao']==ve)&(df_v['ano']==an)]
                                    v_id = match['id'].values[0]
                                    l_id = df_l[df_l['nome'] == loja_nome]['id'].values[0]
                                    
                                    conn.execute("""
                                        INSERT INTO coletas (veiculo_id, usuario_id, loja_id, valor_encontrado, local_loja)
                                        VALUES (?, ?, ?, ?, ?)
                                    """, (int(v_id), usuario.id, int(l_id), valor, loja_nome))
                                    conn.commit()
                                    
                                    st.success("✅ Coleta registrada com sucesso!")
                                    time.sleep(1)
                                    # A mágica da limpeza: limpa o state e reinicia o script
                                    st.rerun()
                                else:
                                    st.error("⚠️ Por favor, preencha todos os campos antes de gravar.")
            else:
                # HISTÓRICO
                st.markdown("### 🕒 Histórico Recente")
                df_h = pd.read_sql("""
                    SELECT v.marca, v.modelo, v.versao, c.local_loja as loja, c.valor_encontrado as preco, c.data_coleta
                    FROM coletas c JOIN veiculos v ON c.veiculo_id = v.id
                    WHERE c.usuario_id = ? ORDER BY c.data_coleta DESC
                """, conn, params=(usuario.id,))
                st.dataframe(df_h, use_container_width=True, hide_index=True,
                            column_config={"preco": st.column_config.NumberColumn("Valor", format="R$ %.2f")})
            
            conn.close()