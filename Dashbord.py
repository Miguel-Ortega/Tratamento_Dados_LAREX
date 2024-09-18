import streamlit as st
import requests 
import pandas as pd
import plotly.express as px
from PIL import Image

st.set_page_config(layout= 'wide',page_icon= 'jabuti-05.png', page_title= 'Facilitador')

st.title('Tratamentos de Dados')

Jabuti = Image.open('jabuti-05.png')
#Minerva = Image.open('Minerva.png')

coluna1,coluna2,coluna3 = st.columns([250,250,250])


with coluna1:
    st.image(Jabuti,width = 350) 

with coluna2:
    st.write('Olá!!, Seja muito bem vindo!')
    st.write('Ao lado esquerdo existe uma barra de seleção onde você encontrará todos os softwares que te ajudam a economizar um tempinho do seu dia!')
    st.write('Dúvidas ou sugestões entre em [contato!](mailto:Miguelorteg2001@gmail.com)')
    st.write('Este aplicativo foi feito por Miguel Ortega em seu tempo nem tão livre.')

with coluna3:
    #st.image(Minerva,width= 350)
