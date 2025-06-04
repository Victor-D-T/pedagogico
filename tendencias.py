class TendenciasFinanceiras:
    def __init__(self, df_fluxo):
        self.df = df_fluxo
        self.meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                     'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    
    def calcular_tendencias(self):
        """Calcula tendências de crescimento"""
        receitas_mensais = self.df[self.df['Código'].astype(str).str.startswith('1')][self.meses].sum()
        despesas_mensais = self.df[self.df['Código'].astype(str).str.startswith('2')][self.meses].sum()
        
        # Calcular taxa de crescimento
        receitas_growth = receitas_mensais.pct_change().dropna()
        despesas_growth = despesas_mensais.pct_change().dropna()
        
        return {
            'receitas_trend': receitas_growth.mean(),
            'despesas_trend': despesas_growth.mean(),
            'melhor_mes': receitas_mensais.idxmax(),
            'pior_mes': receitas_mensais.idxmin()
        }
    
    def plot_tendencias(self):
        """Gráfico de tendências com projeções"""
        trends = self.calcular_tendencias()
        
        fig = go.Figure()
        
        # Dados históricos
        receitas = self.df[self.df['Código'].astype(str).str.startswith('1')][self.meses].sum()
        
        fig.add_trace(go.Scatter(
            x=self.meses,
            y=receitas,
            name='Receitas Históricas',
            line=dict(color='#1976D2', width=3)
        ))
        
        # Linha de tendência
        from scipy import stats
        x_numeric = list(range(len(receitas)))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_numeric, receitas)
        trend_line = [slope * x + intercept for x in x_numeric]
        
        fig.add_trace(go.Scatter(
            x=self.meses,
            y=trend_line,
            name=f'Tendência (R²={r_value**2:.3f})',
            line=dict(color='#FF9800', dash='dash')
        ))
        
        fig.update_layout(
            title="Análise de Tendências - Receitas",
            xaxis_title="Meses",
            yaxis_title="Valor (R$)",
            template="plotly_dark"
        )
        
        return fig