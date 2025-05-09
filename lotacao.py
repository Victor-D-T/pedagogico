import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

print("Iniciando o script...")  # Adicione esta linha

try:
    print("Lendo o arquivo Excel...")  # Adicione esta linha
    data = pd.read_excel('lotacao.xls')
    print("Arquivo Excel lido com sucesso!")  # Adicione esta linha

    df = pd.DataFrame(data)
    df['Unidade'] = df['SALA'].str.split('-').str[0].str.strip()
    df_sorted = df.sort_values(['Unidade', 'Quantidade_Atual'], ascending=[True, False])

    # Definir cores para cada unidade
    cores_unidades = {'Unid. 1': 'skyblue', 'Unid. 2': 'lightgreen', 'Unid. 3': 'salmon'}

    # Gráfico 1: Ocupação vs Capacidade por Turma
    print("Gerando o gráfico 1...")  # Adicione esta linha
    fig, ax = plt.subplots(figsize=(15, 10))
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

    # Adicionar linhas e textos separando as unidades
    current_pos = 0
    for unidade in df_sorted['Unidade'].unique():
        next_pos = current_pos + len(df_sorted[df_sorted['Unidade'] == unidade])
        if current_pos > 0:
            plt.axvline(x=current_pos - 0.5, color='gray', linestyle='--', alpha=0.5)

        plt.text((current_pos + next_pos) / 2,
                 plt.ylim()[1] * 0.85,
                 unidade,
                 horizontalalignment='center',
                 fontsize=12,
                 fontweight='bold',
                 bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

        current_pos = next_pos

    plt.xticks(x, df_sorted['TURMA'], rotation=45, ha='right')
    plt.ylabel('Número de Alunos')
    plt.title('Ocupação vs Capacidade por Turma e Unidade', pad=20)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)  # Use st.pyplot() para exibir o gráfico no Streamlit
    print("Gráfico 1 gerado com sucesso!")  # Adicione esta linha

except Exception as e:
    print(f"Ocorreu um erro: {e}")  # Adicione esta linha