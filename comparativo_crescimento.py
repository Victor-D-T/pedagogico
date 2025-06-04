import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from utils.styles import THEME

class ComparativoCrescimento:
    def __init__(self, df_fluxo):
        self.df = df_fluxo
        self.meses = [
            'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]
        self.meses_df = [col for col in self.df.columns if col in self.meses]
        self.prepare_data()

    def prepare_data(self):
        """Prepara os dados de receitas e despesas por categoria"""
        
        # Filtrar receitas (código começando com 1, excluindo totalizadores)
        self.receitas = self.df[
            (self.df['Código'].astype(str).str.startswith('1')) &
            (~self.df['Descrição'].str.contains('RECEITAS', na=False, case=False))
        ].copy()
        
        # Filtrar despesas (código começando com 2, excluindo totalizadores)
        self.despesas = self.df[
            (self.df['Código'].astype(str).str.startswith('2')) &
            (~self.df['Descrição'].str.contains('DESPESAS', na=False, case=False))
        ].copy()

    def calcular_crescimento_por_categoria(self, df, tipo='receita'):
        """Calcula o crescimento/queda por categoria"""
        resultados = []
        
        for _, row in df.iterrows():
            categoria = row['Descrição']
            valores_mensais = row[self.meses_df].fillna(0)
            
            # Remover meses com valores zero para cálculo mais preciso
            valores_nao_zero = valores_mensais[valores_mensais != 0]
            
            if len(valores_nao_zero) >= 2:
                # Calcular crescimento percentual mensal médio
                crescimentos = valores_nao_zero.pct_change().dropna()
                crescimento_medio = crescimentos.mean() * 100
                
                # Calcular crescimento absoluto (primeiro vs último valor não-zero)
                primeiro_valor = valores_nao_zero.iloc[0]
                ultimo_valor = valores_nao_zero.iloc[-1]
                crescimento_absoluto = ((ultimo_valor - primeiro_valor) / abs(primeiro_valor)) * 100
                
                # Variabilidade (desvio padrão dos crescimentos)
                volatilidade = crescimentos.std() * 100
                
                # Tendência geral (regressão linear simples)
                x = np.arange(len(valores_nao_zero))
                y = valores_nao_zero.values
                if len(x) > 1:
                    coef = np.polyfit(x, y, 1)[0]  # coeficiente angular
                    tendencia = 'Crescente' if coef > 0 else 'Decrescente'
                else:
                    tendencia = 'Estável'
                
                resultados.append({
                    'Categoria': categoria,
                    'Tipo': tipo.capitalize(),
                    'Crescimento_Medio_Mensal_%': round(crescimento_medio, 2),
                    'Crescimento_Absoluto_%': round(crescimento_absoluto, 2),
                    'Volatilidade_%': round(volatilidade, 2),
                    'Tendencia': tendencia,
                    'Valor_Inicial': primeiro_valor,
                    'Valor_Final': ultimo_valor,
                    'Meses_Ativos': len(valores_nao_zero)
                })
        
        return pd.DataFrame(resultados)

    def gerar_relatorio_comparativo(self):
        """Gera o relatório comparativo completo"""
        
        # Calcular crescimentos
        df_receitas_crescimento = self.calcular_crescimento_por_categoria(self.receitas, 'receita')
        df_despesas_crescimento = self.calcular_crescimento_por_categoria(self.despesas, 'despesa')
        
        # Combinar os dados
        df_completo = pd.concat([df_receitas_crescimento, df_despesas_crescimento], ignore_index=True)
        
        return df_completo, df_receitas_crescimento, df_despesas_crescimento

    def plot_comparativo_barras(self, df_completo):
        """Gráfico de barras comparativo do crescimento absoluto"""
        
        fig = go.Figure()
        
        # Separar receitas e despesas
        receitas_data = df_completo[df_completo['Tipo'] == 'Receita']
        despesas_data = df_completo[df_completo['Tipo'] == 'Despesa']
        
        # Barras de receitas
        fig.add_trace(go.Bar(
            name='Receitas',
            x=receitas_data['Categoria'],
            y=receitas_data['Crescimento_Absoluto_%'],
            marker_color=THEME['RECEITA_COLOR'],
            text=receitas_data['Crescimento_Absoluto_%'].apply(lambda x: f'{x:.1f}%'),
            textposition='outside'
        ))
        
        # Barras de despesas
        fig.add_trace(go.Bar(
            name='Despesas',
            x=despesas_data['Categoria'],
            y=despesas_data['Crescimento_Absoluto_%'],
            marker_color=THEME['DESPESA_COLOR'],
            text=despesas_data['Crescimento_Absoluto_%'].apply(lambda x: f'{x:.1f}%'),
            textposition='outside'
        ))
        
        fig.update_layout(
            title='Comparativo de Crescimento/Queda por Categoria',
            xaxis_title='Categorias',
            yaxis_title='Crescimento/Queda (%)',
            barmode='group',
            paper_bgcolor=THEME['BG_COLOR'],
            plot_bgcolor=THEME['BG_COLOR'],
            font=dict(color=THEME['TEXT_COLOR']),
            xaxis=dict(tickangle=45),
            legend=dict(
                bgcolor=THEME['CARD_COLOR'],
                font=dict(color=THEME['TEXT_COLOR'])
            )
        )
        
        # Adicionar linha de referência no zero
        fig.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.5)
        
        return fig

    def plot_volatilidade_scatter(self, df_completo):
        """Gráfico de dispersão: Crescimento vs Volatilidade"""
        
        fig = px.scatter(
            df_completo, 
            x='Crescimento_Absoluto_%', 
            y='Volatilidade_%',
            color='Tipo',
            # size='Valor_Final',
            hover_data=['Categoria', 'Tendencia'],
            title='Crescimento vs Volatilidade por Categoria',
            color_discrete_map={'Receita': THEME['RECEITA_COLOR'], 'Despesa': THEME['DESPESA_COLOR']}
        )
        
        fig.update_layout(
            paper_bgcolor=THEME['BG_COLOR'],
            plot_bgcolor=THEME['BG_COLOR'],
            font=dict(color=THEME['TEXT_COLOR']),
            legend=dict(
                bgcolor=THEME['CARD_COLOR'],
                font=dict(color=THEME['TEXT_COLOR'])
            )
        )
        
        # Adicionar linhas de referência
        fig.add_vline(x=0, line_dash="dash", line_color="white", opacity=0.3)
        fig.add_hline(y=df_completo['Volatilidade_%'].mean(), line_dash="dash", line_color="orange", opacity=0.5)
        
        return fig

    
    def plot_evolucao_por_categoria(self):
        """Gráfico de evolução por categoria, com possibilidade de múltiplos filtros"""

        st.markdown(f"<h3 style='color:{THEME['TEXT_COLOR']};'>📈 Evolução por Categoria</h3>", unsafe_allow_html=True)

        # Unificar receitas e despesas para permitir seleção conjunta
        df_concat = pd.concat([self.receitas.assign(Tipo='Receita'), self.despesas.assign(Tipo='Despesa')], ignore_index=True)

        # Seleção de categorias
        categorias_disponiveis = df_concat['Descrição'].unique()
        categorias_selecionadas = st.multiselect(
            "Selecione as categorias para visualizar a evolução:",
            options=categorias_disponiveis,
            default=categorias_disponiveis[:1]  # seleciona a primeira como padrão
        )

        if not categorias_selecionadas:
            st.warning("Selecione pelo menos uma categoria.")
            return

        # Filtrar apenas as categorias selecionadas
        df_filtrado = df_concat[df_concat['Descrição'].isin(categorias_selecionadas)]

        # Plotar gráfico
        fig = go.Figure()

        for _, row in df_filtrado.iterrows():
            fig.add_trace(go.Scatter(
                x=self.meses_df,
                y=row[self.meses_df].fillna(0),
                mode='lines+markers',
                name=f"{row['Descrição']} ({row['Tipo']})"
            ))

        fig.update_layout(
            title='Evolução Mensal por Categoria',
            xaxis_title='Meses',
            yaxis_title='Valor (R$)',
            paper_bgcolor=THEME['BG_COLOR'],
            plot_bgcolor=THEME['BG_COLOR'],
            font=dict(color=THEME['TEXT_COLOR']),
            legend=dict(
                bgcolor=THEME['CARD_COLOR'],
                font=dict(color=THEME['TEXT_COLOR'])
            )
        )

        st.plotly_chart(fig, use_container_width=True)


    def render(self):
        """Renderiza a análise comparativa completa"""
        
        st.markdown(f"<h2 style='color:{THEME['TEXT_COLOR']};'>Análise Comparativa de Crescimento</h2>", unsafe_allow_html=True)
        
        # Gerar dados
        df_completo, df_receitas, df_despesas = self.gerar_relatorio_comparativo()
        
        if df_completo.empty:
            st.warning("Não há dados suficientes para análise de crescimento.")
            return  

        # Tabs para diferentes visualizações
        tab1, = st.tabs(["Evolução"])

        with tab1:
            self.plot_evolucao_por_categoria()
