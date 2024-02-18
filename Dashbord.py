import streamlit as st
import requests 
import pandas as pd
import plotly.express as px
from PIL import Image

st.set_page_config(layout= 'wide',page_icon= 'jabuti-05.png', page_title= 'Facilitador')

st.title('Tratamentos de Dados')

Jabuti = Image.open('jabuti-05.png')
Minerva = Image.open('Minerva.png')

coluna1,coluna2,coluna3 = st.columns([250,250,250])


with coluna1:
    st.image(Jabuti,width = 350) 

with coluna2:
    st.write('Olá!!, Seja muito bem vindo!')
    st.write('Ao lado esquerdo existe uma barra de seleção onde vc encontrará todos os softwares que te ajudam a economizar um tempinho do seu dia!')
    st.write('Podem aparecer algumas janelas de erro caso você ainda nao tenha subido os arquivos, apenas ignore!')
    st.write('Este aplicativo foi feito por Miguel Ortega em seu tempo nem tão livre.')

with coluna3:
    st.image(Minerva,width= 350)
