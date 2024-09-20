import seaborn as sns 
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import io

st.set_page_config(page_icon= 'jabuti-05.png', page_title= 'Facilitador')

def tratar_dados():
    st.title('Bem-vindo ao tratamento de DRX!')
    st.write('')
    st.write('Software desenvolvido por Miguel O.')

    coluna1, coluna2 = st.columns(2)

    with coluna1:
        Dados = st.file_uploader(label="Faça upload do arquivo com o Gráfico", type=['csv'])
    
    with coluna2:
        Picos = st.file_uploader(label="Faça upload do arquivo com os Picos", type=['csv'])

    if Dados and Picos:
        df_dados = pd.read_csv(Dados)
        df_picos = pd.read_csv(Picos)
        
        # Preparando os dados
        x = df_dados["#twotheta"]
        y = df_dados[' yobs']
        
        plt.figure(figsize=(10, 6))
        plt.plot(x, y, color='black')

        # Filtrando picos conhecidos
        df_picos = df_picos[df_picos['Chemical formula'] != 'Unknown']
        df_picos = df_picos.replace(" ", np.nan)
        df_picos = df_picos.dropna(subset=['Chemical formula'])


        # Preparando dados para exibição de picos
        resultados = []
        for index, row in df_picos.iterrows():
            graus = row['2-theta(deg)']
            nomes = row['Chemical formula'].split(',')
            
            if 'Height(cps)' in row and pd.notna(row['Height(cps)']):
                valor_original = row['Height(cps)']
            elif 'Height(counts)' in row:
                valor_original = row['Height(counts)']
            else:
                valor_original = None

            for i, nome in enumerate(nomes):
                if i != 0:
                    valor = valor_original + 75  # Adiciona 5 ao primeiro elemento
                else:
                    valor = valor_original  # Mantém o valor original para os demais elementos
                resultados.append({'Chemical formula': nome, 'Height(cps)': valor, '2-theta(deg)': graus})

        # Criando um DataFrame com os dados processados
        df_picos = pd.DataFrame(resultados)

        df_picos_orginal = df_picos['2-theta(deg)'].copy()

        Altura = df_dados.loc[df_dados['#twotheta'].round(3).isin(df_picos['2-theta(deg)'].round(3)), ' yobs']
        Altura = pd.DataFrame(Altura)
        Altura = Altura.reset_index(drop=True)

        df_picos['Height(cps)'] = df_picos['Height(cps)'].round(-1)
        df_picos['2-theta(deg)'] = df_picos['2-theta(deg)'].round(0)
        df_picos['Height(cps)'] = Altura[' yobs'].copy() + 25

        # Adiciona 10 aos valores duplicados (exceto o primeiro), quando '2-theta(deg)' também é duplicado
        df_picos.loc[df_picos.duplicated(subset=['Height(cps)', '2-theta(deg)'], keep='first'), 'Height(cps)'] += 35

        # Encontra as duplicatas novamente, depois da primeira modificação
        duplicates = df_picos.duplicated(subset=['Height(cps)', '2-theta(deg)'], keep='first')

        # Adiciona 100 ao segundo valor duplicado apenas, quando '2-theta(deg)' também é duplicado
        df_picos.loc[duplicates & ~df_picos.duplicated(subset=['Height(cps)', '2-theta(deg)'], keep='last'), 'Height(cps)'] += 100

        df_picos['2-theta(deg)'] = df_picos_orginal

        # Mapear categorias únicas para números
        categorias = df_picos['Chemical formula'].unique()
        categoria_dict = {categoria: i+1 for i, categoria in enumerate(categorias)}
        df_picos['Numero'] = df_picos['Chemical formula'].map(categoria_dict)

        # Plotagem dos pontos com os números das categorias
        scatter = plt.scatter(df_picos['2-theta(deg)'], df_picos['Height(cps)'], s=0, c=df_picos['Numero'], cmap='viridis')

        for index, row in df_picos.iterrows():
            plt.text(row['2-theta(deg)'], row['Height(cps)'], str(row['Numero']), ha='center', va='bottom')

        # Configurando a legenda
        handles = [plt.Line2D([0], [0], markerfacecolor=scatter.cmap(scatter.norm(numero)), markersize=10) for categoria, numero in categoria_dict.items()]
        labels = [f'{categoria} ({numero})' for categoria, numero in categoria_dict.items()]

        plt.legend(handles, labels, title='Chemical Formula')
        plt.title(st.text_input('Escreva o Título:'), loc='center')
        plt.xlabel('twotheta')
        plt.ylabel('yobs')

        # Limites dos eixos
        with coluna1:
            Xlim_inf = st.number_input('Limite inferior do eixo X:', min_value=0.0, value=20.0)

        with coluna2:
            Xlim_sup = st.number_input('Limite superior do eixo X:', min_value=0.0, value=80.0)

        plt.xlim(Xlim_inf, Xlim_sup)
        plt.ylim(0)

        st.pyplot(plt)
    else:
        st.warning("Por favor, faça o upload de ambos os arquivos.")

if __name__ == "__main__":
    tratar_dados()

