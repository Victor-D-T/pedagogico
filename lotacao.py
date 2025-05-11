import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils.styles import THEME

class RelatorioLotacao:
    def __init__(self):
        self.cores_unidades = {
            'Unid. 1': '#1976D2',
            'Unid. 2': '#43A047',
            'Unid. 3': '#E53935'
        }
        self.load_data()

    def load_data(self):
        """Carrega e processa os dados iniciais"""
        try:
            data = pd.read_excel('lotacao.xls')
            self.df = pd.DataFrame(data)
            self.df['Unidade'] = self.df['SALA'].str.split('-').str[0].str.strip()
            self.df_sorted = self.df.sort_values(['Unidade', 'Quantidade_Atual'], ascending=[True, False])
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")

    def show_header(self):
        """Mostra o cabeçalho da página"""
        st.markdown(f"""
            <h1 style='
                text-align: left;
                color: {THEME['TEXT_COLOR']};
                font-size: 36px;
                margin-bottom: 10px;
                font-family: Arial, sans-serif;
                font-weight: bold;
                text-transform: uppercase;
            '>Análise de Lotação das Turmas</h1>
            <p style='font-size:18px; color:{THEME['TEXT_COLOR']};'>
                Este painel apresenta a ocupação das turmas por unidade escolar e alguns dados estatísticos.
            </p>
        """, unsafe_allow_html=True)
        st.divider()

    def show_estatisticas(self):
        """Mostra as estatísticas por unidade"""
        st.markdown(f"""
            <h2 style='
                text-align: left;
                color: {THEME['TEXT_COLOR']};
                font-size: 28px;
                margin-top: 30px;
                margin-bottom: 10px;
            '>Estatísticas por Unidade</h2>
        """, unsafe_allow_html=True)

        for unidade in self.df['Unidade'].unique():
            self._mostrar_estatisticas_unidade(unidade)

    def _mostrar_estatisticas_unidade(self, unidade):
        """Mostra estatísticas para uma unidade específica"""
        st.markdown(self._get_unidade_header_style(unidade), unsafe_allow_html=True)

        dados_unidade = self.df[self.df['Unidade'] == unidade]
        total_capacidade = dados_unidade['Capacidade'].sum()
        total_atual = dados_unidade['Quantidade_Atual'].sum()
        taxa_ocupacao = (total_atual / total_capacidade) * 100 if total_capacidade > 0 else 0

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Capacidade Total", f"{total_capacidade}")
        with col2:
            st.metric("Ocupação Total", f"{total_atual}")
        with col3:
            st.metric("Taxa de Ocupação", f"{taxa_ocupacao:.1f}%")

    def plot_ocupacao_capacidade(self):
        """Plota o gráfico de ocupação vs capacidade"""
        st.markdown(self._get_section_header("Ocupação vs Capacidade por Turma"), unsafe_allow_html=True)

        fig = go.Figure()

        for unidade in self.cores_unidades:
            mask = self.df_sorted['Unidade'] == unidade
            if any(mask):
                # Barras de Capacidade
                fig.add_trace(go.Bar(
                    name=f'Capacidade ({unidade})',
                    x=self.df_sorted[mask]['TURMA'],
                    y=self.df_sorted[mask]['Capacidade'],
                    marker_color=self.cores_unidades[unidade],
                    opacity=0.25,
                    offsetgroup=unidade
                ))
                # Barras de Quantidade Atual
                fig.add_trace(go.Bar(
                    name=f'Quantidade Atual ({unidade})',
                    x=self.df_sorted[mask]['TURMA'],
                    y=self.df_sorted[mask]['Quantidade_Atual'],
                    marker_color=self.cores_unidades[unidade],
                    opacity=0.85,
                    offsetgroup=unidade
                ))

        fig.update_layout(
            barmode='group',
            paper_bgcolor=THEME['BG_COLOR'],
            plot_bgcolor=THEME['BG_COLOR'],
            font=dict(color=THEME['TEXT_COLOR']),
            legend=dict(
                bgcolor=THEME['CARD_COLOR'],
                font=dict(color=THEME['TEXT_COLOR'])
            ),
            xaxis=dict(
                showgrid=True,
                gridcolor=THEME['CARD_COLOR'],
                gridwidth=0.1,
                tickfont=dict(color=THEME['TEXT_COLOR']),
                tickangle=45
            ),
            yaxis=dict(
                title='Número de Alunos',
                showgrid=True,
                gridcolor=THEME['CARD_COLOR'],
                gridwidth=0.1,
                tickfont=dict(color=THEME['TEXT_COLOR'])
            ),
            margin=dict(l=20, r=20, t=40, b=100),
            hovermode='x unified'
        )

        st.plotly_chart(fig, use_container_width=True)

    def plot_taxa_ocupacao(self):
            """Plota o gráfico de taxa de ocupação"""
            st.markdown(self._get_section_header("Taxa de Ocupação por Turma", size=22), unsafe_allow_html=True)

            taxa_ocupacao = (self.df_sorted['Quantidade_Atual'] / self.df_sorted['Capacidade'] * 100)
            
            fig = go.Figure()

            for unidade in self.cores_unidades:
                mask = self.df_sorted['Unidade'] == unidade
                if any(mask):
                    fig.add_trace(go.Bar(
                        name=unidade,
                        x=self.df_sorted[mask]['TURMA'],
                        y=taxa_ocupacao[mask],
                        marker_color=self.cores_unidades[unidade],
                        opacity=0.85
                    ))

            # Linha de capacidade máxima
            fig.add_trace(go.Scatter(
                x=self.df_sorted['TURMA'],
                y=[100] * len(self.df_sorted),
                mode='lines',
                name='Capacidade Máxima',
                line=dict(color=THEME['ACCENT2'], dash='dash')
            ))

            fig.update_layout(
                paper_bgcolor=THEME['BG_COLOR'],
                plot_bgcolor=THEME['BG_COLOR'],
                font=dict(color=THEME['TEXT_COLOR']),
                legend=dict(
                    bgcolor=THEME['CARD_COLOR'],
                    font=dict(color=THEME['TEXT_COLOR'])
                ),
                xaxis=dict(
                    showgrid=True,
                    gridcolor=THEME['CARD_COLOR'],
                    gridwidth=0.1,
                    tickfont=dict(color=THEME['TEXT_COLOR']),
                    tickangle=45
                ),
                yaxis=dict(
                    title='Taxa de Ocupação (%)',
                    showgrid=True,
                    gridcolor=THEME['CARD_COLOR'],
                    gridwidth=0.1,
                    tickfont=dict(color=THEME['TEXT_COLOR'])
                ),
                margin=dict(l=20, r=20, t=40, b=100),
                hovermode='x unified'
            )

            st.plotly_chart(fig, use_container_width=True)

    def plot_comparativo_medias(self):
        """Plota o gráfico comparativo de médias"""
        st.markdown(self._get_section_header("Comparativo de Médias por Unidade", size=22), unsafe_allow_html=True)

        media_ocupacao = self.df.groupby('Unidade')['Quantidade_Atual'].mean()
        media_capacidade = self.df.groupby('Unidade')['Capacidade'].mean()
        total_ocupacao = self.df.groupby('Unidade')['Quantidade_Atual'].sum()
        total_capacidade = self.df.groupby('Unidade')['Capacidade'].sum()

        fig = go.Figure()

        for i, unidade in enumerate(self.cores_unidades):
            if unidade in media_capacidade.index:
                # Barra de Capacidade Média
                fig.add_trace(go.Bar(
                    name='Capacidade Média' if i == 0 else None,
                    x=[unidade],
                    y=[media_capacidade[unidade]],
                    marker_color=self.cores_unidades[unidade],
                    opacity=0.25,
                    offsetgroup=unidade
                ))
                # Barra de Ocupação Média
                fig.add_trace(go.Bar(
                    name='Ocupação Média' if i == 0 else None,
                    x=[unidade],
                    y=[media_ocupacao[unidade]],
                    marker_color=self.cores_unidades[unidade],
                    opacity=0.85,
                    offsetgroup=unidade,
                    text=f'Total: {total_ocupacao[unidade]}/{total_capacidade[unidade]}',
                    textposition='outside'
                ))

        fig.update_layout(
            barmode='group',
            paper_bgcolor=THEME['BG_COLOR'],
            plot_bgcolor=THEME['BG_COLOR'],
            font=dict(color=THEME['TEXT_COLOR']),
            legend=dict(
                bgcolor=THEME['CARD_COLOR'],
                font=dict(color=THEME['TEXT_COLOR'])
            ),
            xaxis=dict(
                showgrid=True,
                gridcolor=THEME['CARD_COLOR'],
                gridwidth=0.1,
                tickfont=dict(color=THEME['TEXT_COLOR'])
            ),
            yaxis=dict(
                title='Número de Alunos',
                showgrid=True,
                gridcolor=THEME['CARD_COLOR'],
                gridwidth=0.1,
                tickfont=dict(color=THEME['TEXT_COLOR'])
            ),
            margin=dict(l=20, r=20, t=40, b=20),
            hovermode='x unified'
        )

        st.plotly_chart(fig, use_container_width=True)

    def render(self, filtros=None):
        """Renderiza todo o relatório de lotação"""
        self.show_header()
        if filtros and "unidade" in filtros and filtros["unidade"] != "Todas":
            self.df = self.df[self.df['Unidade'] == filtros["unidade"]]
            self.df_sorted = self.df_sorted[self.df_sorted['Unidade'] == filtros["unidade"]]
        self.show_estatisticas()
        st.divider()
        self.plot_ocupacao_capacidade()
        st.divider()
        colA, colB = st.columns(2)
        with colA:
            self.plot_taxa_ocupacao()
        with colB:
            self.plot_comparativo_medias()

    @staticmethod
    def _get_section_header(texto, size=26):
        return f"""
            <h2 style='
                text-align: left;
                color: {THEME['TEXT_COLOR']};
                font-size: {size}px;
                margin-top: 30px;
                margin-bottom: 10px;
            '>{texto}</h2>
        """

    @staticmethod
    def _get_unidade_header_style(unidade):
        return f"""
            <div style='
                text-align: center;
                color: {THEME['TEXT_COLOR']};
                font-size: 22px;
                padding: 8px;
                margin-top: 10px;
                background-color: {THEME['CARD_COLOR']};
                border-radius: 8px;
                font-weight: bold;
                box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            '>{unidade}</div>
        """