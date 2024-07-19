import seaborn as sns 
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import os
import io

st.set_page_config(page_icon= 'jabuti-05.png', page_title= 'Facilitador')

st.title('Bem-vindo ao tratamento de DRX!')
st.write('')
st.write('Software desenvolvido por Miguel O.')

coluna1,coluna2 = st.columns(2)

with coluna1:
    Dados = st.file_uploader(label="Faça upload do arquivo com o Grafico", type=['csv'])
    if Dados:
        Dados = pd.read_csv(Dados)
        csv_Dados = io.StringIO()
        Dados.to_csv(csv_Dados, index=False)
        csv_Dados.seek(0)
    #d = st.selectbox('Selecione o arquivo com o grafico:',arquivos)
#while d + '.csv' not in arquivos:
    #d = st.text_input('Arquivo não encontrado. Favor digitar o nome do arquivo novamente:')
with coluna2:
    Picos = st.file_uploader(label="Faça upload do arquivo Picos", type=['csv'])
    if Picos:
        Picos = pd.read_csv(Picos)
        csv_Picos = io.StringIO()
        Picos.to_csv(csv_Picos, index=False)
        csv_Picos.seek(0)
#while p + '.csv' not in arquivos:
    #p = st.text_input('Arquivo não encontrado. Favor digitar o nome do arquivo novamente:')


df_picos = pd.read_csv(csv_Picos)
df_dados = pd.read_csv(csv_Dados)

x = df_dados["#twotheta"]
y = df_dados[' yobs']
plt.plot(x, y, color='black')
df_picos = df_picos[df_picos['Chemical formula'] != 'Unknown']

categorias = df_picos['Chemical formula'].unique()
categoria_dict = {categoria: i+1 for i, categoria in enumerate(categorias)}

df_picos['Numero'] = df_picos['Chemical formula'].map(categoria_dict)
scatter = plt.scatter(df_picos['2-theta(deg)'], df_picos['Height(cps)'], s=0, c=df_picos['Numero'], cmap='viridis')

for index, row in df_picos.iterrows():
    plt.text(row['2-theta(deg)'], row['Height(cps)'], str(row['Numero']), ha='center', va='bottom')
    
    
handles = []
labels = []
for categoria, numero in categoria_dict.items():
    handles.append(plt.Line2D([0], [0], markerfacecolor=scatter.cmap(scatter.norm(numero))))
    labels.append(f'{categoria} ({numero})')

plt.legend(handles, labels, title='Chemical Formula')
plt.title(st.text_input('Escreva o Título:'), loc='center')
plt.xlabel('twotheta')
plt.ylabel('yobs')

with coluna1:
    Xlim_inf = st.number_input('Limite inferior do eixo X:')

with coluna2:
    Xlim_sup = st.number_input('Limite superior do eixo X:')

    if Xlim_sup == 0:
        Xlim_sup = 80
    if Xlim_inf == 0:
        Xlim_inf = 20
    plt.xlim(Xlim_inf,Xlim_sup)

plt.ylim(0)
st.pyplot(plt)

