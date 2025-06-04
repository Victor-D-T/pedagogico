import streamlit as st
from financeiro import RelatorioFinanceiro
from lotacao import RelatorioLotacao
from utils.styles import THEME

class DashboardEscolar:
    def __init__(self):
        st.set_page_config(
            page_title="Dashboard Escolar",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        self.financeiro = RelatorioFinanceiro()
        self.lotacao = RelatorioLotacao()
        self.sidebar_container = st.sidebar.container()

    def setup_header(self):
        st.markdown(f"""
            <h1 style='
                text-align: center;
                color: {THEME['TEXT_COLOR']};
                padding: 1rem;
                background-color: {THEME['CARD_COLOR']};
                border-radius: 10px;
                margin-bottom: 2rem;
            '>
                Dashboard Escolar
            </h1>
        """, unsafe_allow_html=True)
    def clear_sidebar(self):
        """Limpa a sidebar"""
        with self.sidebar_container:
            st.empty()

    def run(self):
        self.setup_header()
        self.setup_file_upload()
        tab1, tab2 = st.tabs(["📊 Relatório Financeiro", "👥 Relatório de Lotação"])

        with tab1:
            # Não mostra sidebar aqui!
            self.clear_sidebar()
            self.financeiro.render()

        with tab2:
            st.sidebar.title("Filtros")
            # Pegue as unidades dinamicamente se quiser:
            unidades = ["Todas"] + list(self.lotacao.df['Unidade'].unique())
            unidade = st.sidebar.selectbox(
                "Filtrar por Unidade",
                unidades,
                key="unidade_global"
            )
            filtros = {"unidade": unidade}
            self.lotacao.render(filtros)

    def setup_file_upload(self):
        """Sistema de upload de arquivos"""
        st.sidebar.title("📁 Gerenciar Arquivos")
        
        # Upload do arquivo financeiro
        uploaded_finance = st.sidebar.file_uploader(
            "Upload Fluxo de Caixa", 
            type=['xlsx', 'xls'],
            key='finance_file'
        )
        
        if uploaded_finance:
            with open('fluxo_de_caixa.xlsx', 'wb') as f:
                f.write(uploaded_finance.getbuffer())
            st.sidebar.success("✅ Arquivo financeiro carregado!")
        
        # Upload do arquivo de lotação
        uploaded_lotacao = st.sidebar.file_uploader(
            "Upload Dados de Lotação", 
            type=['xlsx', 'xls'],
            key='lotacao_file'
        )
        
        if uploaded_lotacao:
            with open('lotacao.xls', 'wb') as f:
                f.write(uploaded_lotacao.getbuffer())
            st.sidebar.success("✅ Arquivo de lotação carregado!")



if __name__ == "__main__":
    dashboard = DashboardEscolar()
    dashboard.run()