import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Configurar a página
st.set_page_config(page_title="Análise de Lotação", layout="wide")
st.title("Análise de Lotação das Turmas")

# Criar o DataFrame
try:
    data = pd.read_excel('lotacao.xls')
    df = pd.DataFrame(data)
    df['Unidade'] = df['SALA'].str.split('-').str[0].str.strip()
    df_sorted = df.sort_values(['Unidade', 'Quantidade_Atual'], ascending=[True, False])
    
    # Definir cores para cada unidade
    cores_unidades = {'Unid. 1': 'skyblue', 'Unid. 2': 'lightgreen', 'Unid. 3': 'salmon'}

    # Estatísticas
    st.subheader("Estatísticas por Unidade")
    for unidade in df['Unidade'].unique():
        st.write(f"\n**{unidade}:**")
        dados_unidade = df[df['Unidade'] == unidade]
        total_capacidade = dados_unidade['Capacidade'].sum()
        total_atual = dados_unidade['Quantidade_Atual'].sum()
        taxa_ocupacao = (total_atual / total_capacidade) * 100

        col1, col2, col3 = st.columns(3)
        col1.metric("Capacidade Total", f"{total_capacidade}")
        col2.metric("Ocupação Total", f"{total_atual}")
        col3.metric("Taxa de Ocupação", f"{taxa_ocupacao:.1f}%")


    st.subheader("Ocupação vs Capacidade por Turma")
    fig1, ax1 = plt.subplots(figsize=(25, 10))
    plt.subplots_adjust(top=0.85)

    x = np.arange(len(df_sorted['TURMA']))
    width = 0.35

    for unidade in cores_unidades:
        mask = df_sorted['Unidade'] == unidade
        x_unit = x[mask]

        plt.bar(x_unit + width/2,
                df_sorted[mask]['Capacidade'],
                width,
                label=f'Capacidade ({unidade})',
                color=cores_unidades[unidade],
                alpha=0.3)

        plt.bar(x_unit - width/2,
                df_sorted[mask]['Quantidade_Atual'],
                width,
                label=f'Quantidade Atual ({unidade})',
                color=cores_unidades[unidade],
                alpha=0.7)

    current_pos = 0
    for unidade in df_sorted['Unidade'].unique():
        next_pos = current_pos + len(df_sorted[df_sorted['Unidade'] == unidade])
        if current_pos > 0:
            plt.axvline(x=current_pos - 0.5, color='gray', linestyle='--', alpha=0.5)

        plt.text((current_pos + next_pos) / 2,
                    plt.ylim()[1] * 0.9,
                    unidade,
                    horizontalalignment='center',
                    fontsize=12,
                    fontweight='bold',
                    bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

        current_pos = next_pos

    plt.xticks(x, df_sorted['TURMA'], rotation=45, ha='right')
    plt.ylabel('Número de Alunos')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig1)
    
    # Criar três colunas para os gráficos
    col1, col2 = st.columns(2)

    # Gráfico 1: Ocupação vs Capacidade por Turma
    with col2:
        # Gráfico 3: Comparativo de Médias por Unidade
        st.subheader("Comparativo de Médias por Unidade")
        fig3, ax3 = plt.subplots(figsize=(15, 10))
        media_ocupacao = df.groupby('Unidade')['Quantidade_Atual'].mean()
        media_capacidade = df.groupby('Unidade')['Capacidade'].mean()
        total_ocupacao = df.groupby('Unidade')['Quantidade_Atual'].sum()
        total_capacidade = df.groupby('Unidade')['Capacidade'].sum()

        x = np.arange(len(media_ocupacao))
        width = 0.35

        for i, unidade in enumerate(cores_unidades):
            plt.bar(i - width/2, media_capacidade[unidade], width,
                    label='Capacidade Média',
                    color=cores_unidades[unidade],
                    alpha=0.3)
            plt.bar(i + width/2, media_ocupacao[unidade], width,
                    label='Ocupação Média' if i == 0 else "",
                    color=cores_unidades[unidade],
                    alpha=0.7)

        max_altura = max(media_capacidade.max(), media_ocupacao.max())
        for i, unidade in enumerate(cores_unidades):
            plt.text(i, max_altura * 1.1,
                    f'Total: {total_ocupacao[unidade]}/{total_capacidade[unidade]}',
                    ha='center', va='bottom')

        plt.xticks(x, media_ocupacao.index)
        plt.ylabel('Número de Alunos')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.ylim(0, max_altura * 1.3)
        plt.tight_layout()
        st.pyplot(fig3)
        

    # Gráfico 2: Taxa de Ocupação por Turma
    with col1:
        st.subheader("Taxa de Ocupação por Turma")
        fig2, ax2 = plt.subplots(figsize=(15, 10))
        plt.subplots_adjust(top=0.85)

        taxa_ocupacao = (df_sorted['Quantidade_Atual'] / df_sorted['Capacidade'] * 100)

        for unidade in cores_unidades:
            mask = df_sorted['Unidade'] == unidade
            plt.bar(df_sorted[mask]['TURMA'],
                    taxa_ocupacao[mask],
                    color=cores_unidades[unidade],
                    label=unidade)

        plt.axhline(y=100, color='r', linestyle='--', label='Capacidade Máxima')

        current_pos = 0
        for unidade in df_sorted['Unidade'].unique():
            next_pos = current_pos + len(df_sorted[df_sorted['Unidade'] == unidade])
            if current_pos > 0:
                plt.axvline(x=current_pos - 0.5, color='gray', linestyle='--', alpha=0.5)

            plt.text((current_pos + next_pos) / 2,
                     plt.ylim()[1] * 0.9,
                     unidade,
                     horizontalalignment='center',
                     fontsize=12,
                     fontweight='bold',
                     bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

            current_pos = next_pos

        plt.xticks(rotation=45, ha='right')
        plt.ylabel('Taxa de Ocupação (%)')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig2)

    
except Exception as e:
    st.error(f"Erro ao carregar os dados: {str(e)}")