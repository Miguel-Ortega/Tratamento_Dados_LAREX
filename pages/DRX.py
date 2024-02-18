import seaborn as sns 
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import os
import io

st.set_page_config(page_icon= 'jabuti-05.png', page_title= 'Facilitador')


local, arquivos = dados()
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
sns.scatterplot(data=df_picos, x='2-theta(deg)', y='Height(cps)', hue='Chemical formula', s=15)
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

