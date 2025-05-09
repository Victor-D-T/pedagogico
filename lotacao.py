import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Configurar a página
st.set_page_config(page_title="Análise de Lotação", layout="wide")

# Paleta de cores do tema
DARK_BLUE = "#16213E"
CARD_BLUE = "#22304A"
PRIMARY_BLUE = "#1976D2"
TEXT_COLOR = "#F5F6FA"
ACCENT1 = "#00B4D8"
ACCENT2 = "#FFD166"
ACCENT3 = "#EF476F"

# Título principal estilizado
st.markdown(f"""
    <h1 style='
        text-align: left;
        color: {PRIMARY_BLUE};
        font-size: 36px;
        margin-bottom: 10px;
        font-family: Arial, sans-serif;
        font-weight: bold;
        text-transform: uppercase;
    '>Análise de Lotação das Turmas</h1>
    <p style='font-size:18px; color:{TEXT_COLOR};'>
        Este painel apresenta a ocupação das turmas por unidade escolar e alguns dados estatísticos.
    </p>
""", unsafe_allow_html=True)

st.divider()

try:
    data = pd.read_excel('lotacao.xls')
    df = pd.DataFrame(data)
    df['Unidade'] = df['SALA'].str.split('-').str[0].str.strip()
    df_sorted = df.sort_values(['Unidade', 'Quantidade_Atual'], ascending=[True, False])

    # Sidebar filter
    unidade_options = ['Todas'] + list(df['Unidade'].unique())
    unidade_selecionada = st.sidebar.selectbox("Filtrar por Unidade", unidade_options)
    if unidade_selecionada != 'Todas':
        df = df[df['Unidade'] == unidade_selecionada]
        df_sorted = df_sorted[df_sorted['Unidade'] == unidade_selecionada]

    # Definir cores para cada unidade (mais sóbrias para o tema escuro)
    cores_unidades = {
        'Unid. 1': PRIMARY_BLUE,
        'Unid. 2': ACCENT1,
        'Unid. 3': ACCENT3
    }

    # Estatísticas
    st.markdown(f"""
        <h2 style='
            text-align: left;
            color: {PRIMARY_BLUE};
            font-size: 28px;
            margin-top: 30px;
            margin-bottom: 10px;
        '>Estatísticas por Unidade</h2>
    """, unsafe_allow_html=True)

    for unidade in df['Unidade'].unique():
        st.markdown(f"""
            <div style='
                text-align: center;
                color: {TEXT_COLOR};
                font-size: 22px;
                padding: 8px;
                margin-top: 10px;
                background-color: {CARD_BLUE};
                border-radius: 8px;
                font-weight: bold;
                box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            '>{unidade}</div>
        """, unsafe_allow_html=True)

        dados_unidade = df[df['Unidade'] == unidade]
        total_capacidade = dados_unidade['Capacidade'].sum()
        total_atual = dados_unidade['Quantidade_Atual'].sum()
        taxa_ocupacao = (total_atual / total_capacidade) * 100

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Capacidade Total", f"{total_capacidade}")
        with col2:
            st.metric("Ocupação Total", f"{total_atual}")
        with col3:
            st.metric("Taxa de Ocupação", f"{taxa_ocupacao:.1f}%")

    st.divider()

    # Gráfico 1: Ocupação vs Capacidade por Turma
    st.markdown(f"""
        <h2 style='
            text-align: left;
            color: {PRIMARY_BLUE};
            font-size: 26px;
            margin-top: 30px;
            margin-bottom: 10px;
        '>Ocupação vs Capacidade por Turma</h2>
    """, unsafe_allow_html=True)
    fig1, ax1 = plt.subplots(figsize=(15, 5), dpi=200)
    x = np.arange(len(df_sorted['TURMA']))
    width = 0.35

    for unidade in cores_unidades:
        mask = df_sorted['Unidade'] == unidade
        x_unit = x[mask]
        ax1.bar(x_unit + width/2,
                df_sorted[mask]['Capacidade'],
                width,
                label=f'Capacidade ({unidade})',
                color=cores_unidades[unidade],
                alpha=0.25)
        ax1.bar(x_unit - width/2,
                df_sorted[mask]['Quantidade_Atual'],
                width,
                label=f'Quantidade Atual ({unidade})',
                color=cores_unidades[unidade],
                alpha=0.85)

    current_pos = 0
    for unidade in df_sorted['Unidade'].unique():
        next_pos = current_pos + len(df_sorted[df_sorted['Unidade'] == unidade])
        if current_pos > 0:
            ax1.axvline(x=current_pos - 0.5, color='#22304A', linestyle='--', alpha=0.5)
        ax1.text((current_pos + next_pos) / 2,
                 ax1.get_ylim()[1] * 0.9,
                 unidade,
                 horizontalalignment='center',
                 fontsize=12,
                 fontweight='bold',
                 color=TEXT_COLOR,
                 bbox=dict(facecolor=CARD_BLUE, alpha=0.8, edgecolor='none'))
        current_pos = next_pos

    ax1.set_facecolor(DARK_BLUE)
    fig1.patch.set_facecolor(DARK_BLUE)
    ax1.set_xticks(x)
    ax1.set_xticklabels(df_sorted['TURMA'], rotation=45, ha='right', color=TEXT_COLOR)
    ax1.set_ylabel('Número de Alunos', color=TEXT_COLOR)
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', facecolor=CARD_BLUE, labelcolor=TEXT_COLOR)
    ax1.grid(True, alpha=0.3, color='#22304A')
    ax1.tick_params(colors=TEXT_COLOR)
    fig1.tight_layout()
    st.pyplot(fig1)

    st.divider()

    # Gráficos 2 e 3 lado a lado
    colA, colB = st.columns(2)

    # Gráfico 2: Taxa de Ocupação por Turma
    with colA:
        st.markdown(f"""
            <h3 style='
                text-align: left;
                color: {PRIMARY_BLUE};
                font-size: 22px;
                margin-bottom: 10px;
            '>Taxa de Ocupação por Turma</h3>
        """, unsafe_allow_html=True)
        fig2, ax2 = plt.subplots(figsize=(8, 5), dpi=200)
        taxa_ocupacao = (df_sorted['Quantidade_Atual'] / df_sorted['Capacidade'] * 100)
        for unidade in cores_unidades:
            mask = df_sorted['Unidade'] == unidade
            ax2.bar(df_sorted[mask]['TURMA'],
                    taxa_ocupacao[mask],
                    color=cores_unidades[unidade],
                    label=unidade,
                    alpha=0.85)
        ax2.axhline(y=100, color=ACCENT2, linestyle='--', label='Capacidade Máxima')
        current_pos = 0
        for unidade in df_sorted['Unidade'].unique():
            next_pos = current_pos + len(df_sorted[df_sorted['Unidade'] == unidade])
            if current_pos > 0:
                ax2.axvline(x=current_pos - 0.5, color='#22304A', linestyle='--', alpha=0.5)
            ax2.text((current_pos + next_pos) / 2,
                     ax2.get_ylim()[1] * 0.9,
                     unidade,
                     horizontalalignment='center',
                     fontsize=12,
                     fontweight='bold',
                     color=TEXT_COLOR,
                     bbox=dict(facecolor=CARD_BLUE, alpha=0.8, edgecolor='none'))
            current_pos = next_pos
        ax2.set_facecolor(DARK_BLUE)
        fig2.patch.set_facecolor(DARK_BLUE)
        ax2.set_xticklabels(df_sorted['TURMA'], rotation=45, ha='right', color=TEXT_COLOR)
        ax2.set_ylabel('Taxa de Ocupação (%)', color=TEXT_COLOR)
        ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left', facecolor=CARD_BLUE, labelcolor=TEXT_COLOR)
        ax2.grid(True, alpha=0.3, color='#22304A')
        ax2.tick_params(colors=TEXT_COLOR)
        fig2.tight_layout()
        st.pyplot(fig2)

    # Gráfico 3: Comparativo de Médias por Unidade
    with colB:
        st.markdown(f"""
            <h3 style='
                text-align: left;
                color: {PRIMARY_BLUE};
                font-size: 22px;
                margin-bottom: 10px;
            '>Comparativo de Médias por Unidade</h3>
        """, unsafe_allow_html=True)
        fig3, ax3 = plt.subplots(figsize=(8, 5), dpi=200)
        media_ocupacao = df.groupby('Unidade')['Quantidade_Atual'].mean()
        media_capacidade = df.groupby('Unidade')['Capacidade'].mean()
        total_ocupacao = df.groupby('Unidade')['Quantidade_Atual'].sum()
        total_capacidade = df.groupby('Unidade')['Capacidade'].sum()
        x = np.arange(len(media_ocupacao))
        width = 0.35
        for i, unidade in enumerate(cores_unidades):
            if unidade in media_capacidade.index:
                ax3.bar(i - width/2, media_capacidade[unidade], width,
                        label='Capacidade Média' if i == 0 else "",
                        color=cores_unidades[unidade],
                        alpha=0.25)
                ax3.bar(i + width/2, media_ocupacao[unidade], width,
                        label='Ocupação Média' if i == 0 else "",
                        color=cores_unidades[unidade],
                        alpha=0.85)
        max_altura = max(media_capacidade.max(), media_ocupacao.max())
        for i, unidade in enumerate(cores_unidades):
            if unidade in total_ocupacao.index:
                ax3.text(i, max_altura * 1.1,
                         f'Total: {total_ocupacao[unidade]}/{total_capacidade[unidade]}',
                         ha='center', va='bottom',
                         color=TEXT_COLOR,
                         bbox=dict(facecolor=CARD_BLUE, alpha=0.8, edgecolor='none'))
        ax3.set_facecolor(DARK_BLUE)
        fig3.patch.set_facecolor(DARK_BLUE)
        ax3.set_xticks(x)
        ax3.set_xticklabels(media_ocupacao.index, color=TEXT_COLOR)
        ax3.set_ylabel('Número de Alunos', color=TEXT_COLOR)
        ax3.legend(facecolor=CARD_BLUE, labelcolor=TEXT_COLOR)
        ax3.grid(True, alpha=0.3, color='#22304A')
        ax3.set_ylim(0, max_altura * 1.3)
        ax3.tick_params(colors=TEXT_COLOR)
        fig3.tight_layout()
        st.pyplot(fig3)

except Exception as e:
    st.error(f"Erro ao carregar os dados: {str(e)}")