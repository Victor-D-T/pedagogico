import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils.styles import THEME
from comparativo_crescimento import ComparativoCrescimento



class RelatorioFinanceiro:
    def __init__(self):
        self.meses = [
            'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]
        self.load_data()
        self.process_data()

    def load_data(self):
        """Carrega os dados do arquivo Excel"""
        try:
            self.df_fluxo = pd.read_excel('fluxo_de_caixa.xlsx', skiprows=3)
            self.df_fluxo.columns = [c.strip() for c in self.df_fluxo.columns]
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")
        

    def process_data(self, selected_month=None):
        """Processa os dados para análise"""
        # Identificar colunas de meses
        self.meses_df = [col for col in self.df_fluxo.columns if col in self.meses]

        # Se um mês específico for selecionado, usar apenas essa coluna
        if selected_month and selected_month in self.meses_df:
            self.meses_df = [selected_month]

        # Filtrar receitas e despesas
        self.receitas = self.df_fluxo[
            (self.df_fluxo['Código'].astype(str).str.startswith('1')) &
            (~self.df_fluxo['Descrição'].str.contains('RECEITAS', na=False))
        ]
        self.despesas = self.df_fluxo[
            (self.df_fluxo['Código'].astype(str).str.startswith('2')) &
            (~self.df_fluxo['Descrição'].str.contains('DESPESAS', na=False))
        ]

        # Preparar dados para gráficos
        self.prepare_pie_chart_data()
        self.prepare_monthly_data()

    def agrupar_outros(self, labels, sizes, threshold=0.01):
        """Agrupa pequenas fatias em 'Outros'"""
        total = sizes.sum()
        new_labels = []
        new_sizes = []
        outros = 0

        for label, size in zip(labels, sizes):
            if size / total < threshold:
                outros += size
            else:
                new_labels.append(label)
                new_sizes.append(size)

        if outros > 0:
            new_labels.append("Outros")
            new_sizes.append(outros)

        return new_labels, new_sizes

    def prepare_pie_chart_data(self):
        """Prepara dados para os gráficos de pizza"""
        # Dados de receitas
        self.labels_receitas = self.receitas['Descrição']
        self.sizes_receitas = self.receitas[self.meses_df].sum(axis=1)
        self.labels_receitas, self.sizes_receitas = self.agrupar_outros(
            self.labels_receitas, self.sizes_receitas
        )

        # Dados de despesas
        self.labels_despesas = self.despesas['Descrição']
        self.sizes_despesas = self.despesas[self.meses_df].sum(axis=1).abs()
        self.labels_despesas, self.sizes_despesas = self.agrupar_outros(
            self.labels_despesas, self.sizes_despesas
        )

    def prepare_monthly_data(self):
        """Prepara dados para o gráfico de evolução mensal"""
        self.receitas_mensais = self.receitas[self.meses_df].sum()
        self.despesas_mensais = self.despesas[self.meses_df].sum()
        self.lucro_mensal = self.receitas_mensais + self.despesas_mensais

    def plot_pie_chart(self, sizes, labels, title):
        """Plota um gráfico de pizza interativo"""
        fig = go.Figure(
            data=[go.Pie(
                labels=labels,
                values=sizes,
                textinfo='percent+label',
                textposition='outside',
                pull=[0.1 if v/sum(sizes) > 0.10 else 0 for v in sizes],
                marker=dict(colors=THEME['PIE_COLORS'][:len(labels)]),
                showlegend=True
            )]
        )

        fig.update_traces(
            textfont=dict(size=14, color=THEME['TEXT_COLOR']),
            hoverinfo='label+percent+value',
            texttemplate='%{percent}'
        )

        fig.update_layout(
            title=dict(
                text=title,
                font=dict(color=THEME['TEXT_COLOR'], size=20),
                x=0.5
            ),
            paper_bgcolor=THEME['BG_COLOR'],
            plot_bgcolor=THEME['BG_COLOR'],
            margin=dict(t=50, l=20, r=20, b=20),
            showlegend=True,
            legend=dict(
                font=dict(color=THEME['TEXT_COLOR']),
                bgcolor=THEME['CARD_COLOR']
            )
        )

        return fig

    def plot_receitas_despesas(self):
        """Plota os gráficos de pizza de receitas e despesas"""
        col1, col2 = st.columns(2)

        with col1:
            fig_receitas = self.plot_pie_chart(
                self.sizes_receitas,
                self.labels_receitas,
                "Receitas por Categoria"
            )
            st.plotly_chart(fig_receitas, use_container_width=True)

        with col2:
            fig_despesas = self.plot_pie_chart(
                self.sizes_despesas,
                self.labels_despesas,
                "Despesas por Categoria"
            )
            st.plotly_chart(fig_despesas, use_container_width=True)

    def plot_evolucao_mensal(self):
        """Plota o gráfico de evolução mensal interativo"""
        st.markdown(
            f"<h3 style='color:{THEME['TEXT_COLOR']};'>Evolução Mensal: Receitas, Despesas e Lucro</h3>",
            unsafe_allow_html=True
        )

        fig = go.Figure()

        # Adicionar barras de receitas
        fig.add_trace(go.Bar(
            x=self.meses_df,
            y=self.receitas_mensais,
            name='Receitas',
            marker_color=THEME['RECEITA_COLOR']
        ))

        # Adicionar barras de despesas
        fig.add_trace(go.Bar(
            x=self.meses_df,
            y=self.despesas_mensais,
            name='Despesas',
            marker_color=THEME['DESPESA_COLOR']
        ))

        # Adicionar linha de lucro
        fig.add_trace(go.Scatter(
            x=self.meses_df,   
            y=self.lucro_mensal,
            name='Lucro',
            line=dict(color=THEME['LUCRO_COLOR'], width=3),
            mode='lines+markers'
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
                showgrid=True,
                gridcolor=THEME['CARD_COLOR'],
                gridwidth=0.1,
                tickfont=dict(color=THEME['TEXT_COLOR']),
                title='R$'
            ),
            margin=dict(l=20, r=20, t=40, b=20),
            hovermode='x unified'
        )

        st.plotly_chart(fig, use_container_width=True)
    def render_comparativo_crescimento(self):
        """Renderiza a análise comparativa de crescimento"""
        comparativo = ComparativoCrescimento(self.df_fluxo)
        comparativo.render()
    
    def render(self):
        """Renderiza todo o relatório financeiro"""
        # Código existente...
        st.markdown(f"<h2 style='color:{THEME['TEXT_COLOR']};'>Relatório Financeiro</h2>", unsafe_allow_html=True)

        # Criar abas
        tab1, tab2 = st.tabs(["📊 Visão Geral", "📈 Análise de Crescimento"])
        
        with tab1:
            # Código existente do relatório (seletor de mês, métricas, gráficos)
            meses_opcoes = ['Todos os meses'] + self.meses_df
            selected_month = st.selectbox('Selecione o mês:', meses_opcoes)

            if selected_month == 'Todos os meses':
                self.process_data()
            else:
                self.process_data(selected_month)

            # Mostrar totais do período selecionado
            col1, col2, col3 = st.columns(3)
            with col1:
                total_receitas = self.receitas[self.meses_df].sum().sum()
                st.metric("Total Receitas", f"R$ {total_receitas:,.2f}")
            with col2:
                total_despesas = self.despesas[self.meses_df].sum().sum()
                st.metric("Total Despesas", f"R$ {total_despesas:,.2f}")
            with col3:
                lucro_total = total_receitas + total_despesas
                st.metric("Lucro Total", f"R$ {lucro_total:,.2f}")

            self.plot_receitas_despesas()

            if selected_month == 'Todos os meses':
                self.plot_evolucao_mensal()
        
        with tab2:
            # Nova funcionalidade de análise comparativa
            self.render_comparativo_crescimento()
