import seaborn as sns 
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import io
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from functools import wraps
import xlsxwriter

st.title('Bem-vindo ao tratamento de ABS!')
st.write('Software desenvolvido por Miguel O.')
st.write('Se necessário corrija o nome das amostras ou diluição')
st.write('')
abs_file = st.file_uploader(label = 'Selecione o arquivo txt com os dados do ABS:', type=['txt'])


coluna1,coluna2 = st.columns(2)

if abs_file:
    Dados = pd.read_csv(abs_file, delimiter='\t', skiprows=2, header=0)

    df_filtrado = Dados[Dados['Action'].str.endswith('AV')]

    Branco = df_filtrado.loc[df_filtrado["Action"] == 'BLK-AV' ]
    Padrao = df_filtrado.loc[df_filtrado["Action"] == 'STD-AV' ]
    Amostra = df_filtrado.loc[df_filtrado["Action"].str.startswith('UNK') ]

    Amostra.loc[:, 'Abs.'] = (Amostra['Abs.']) - (Branco['Abs.'].iloc[0])
    Padrao.loc[:, 'Abs.'] = (Padrao['Abs.']) - (Branco['Abs.'].iloc[0])
    
    x_original = Padrao['True Value (ppm)'].values
    y_original = Padrao['Abs.'].values

    selected_rows = []
    with coluna2:
        for index, row in Padrao.iterrows():
            selected = st.checkbox(f"{row['True Value (ppm)']}", key=index)
            if selected:
                selected_rows.append(index)

    Padrao = Padrao.drop(selected_rows)

    x = Padrao['True Value (ppm)'].values
    y = Padrao['Abs.'].values

    model = LinearRegression().fit(x.reshape(-1, 1), y)
    y_prev = model.predict(x.reshape(-1, 1))
    r_quadrado = r2_score(y, y_prev)

    fig = plt.figure()

    left, width = .25, .5
    bottom, height = .25, .5
    right = left + width
    top = bottom + height

    plt.title('')
    plt.scatter(x_original, y_original, alpha=0)
    plt.scatter(x,y, color ='Black')
    fig.text(right, top, f'$R^2 = {r_quadrado:.5f}$', horizontalalignment='right', verticalalignment='bottom')
    plt.plot(x, y_prev, color='red')

    with coluna1:
        st.pyplot(plt)

    a = model.coef_[0]
    b = model.intercept_

    valor_minimo = Padrao['Abs.'].values.min()
    valor_maximo = Padrao['Abs.'].values.max()

    PosiçãoNaCurva = []
    for index, row in Amostra.iterrows():
        if row['Abs.'] < valor_minimo:
            PosiçãoNaCurva.append('Abaixo')
        elif row['Abs.'] > valor_maximo:
            PosiçãoNaCurva.append('Acima')
        else:
            PosiçãoNaCurva.append('Dentro')
    Amostra.loc[:,'Posição na Curva'] = PosiçãoNaCurva

    Amostra.loc[:,'Concentração Calc.'] = (Amostra['Abs.']-b)/a

    def extract_fator(sample_id):
        sample_id = str(sample_id)
        # Extraímos o número seguido por 'X' ou 'x', e opcionalmente 'K' ou 'k'
        match = pd.Series(sample_id).str.extract(r'([\d.,]+)([Kk]?)([Xx])', expand=True)
        
        if match[1].str.contains('K|k', na=False).any():
            return float(match[0].str.replace(',', '.').iloc[0]) * 1000

        if not match.empty and not match[0].isna().iloc[0]:
            # Converte o número extraído para float, substituindo ',' por '.'
            value = float(match[0].str.replace(',', '.').iloc[0])
            return value
        else:
            # Se não houver 'X' ou 'x', retornar 1
            return 1
        
    def highlight_row(row):
        if row['Abs.'] < valor_minimo:
            return ['color: red'] * len(row)
        elif row['Abs.'] > valor_maximo:
            return ['color: red'] * len(row)
        else:
            return ['color: green'] *len(row)

    # Aplicar a extração ao DataFrame
    Amostra.loc[:,'Fator de diluição'] = Amostra['Sample ID'].apply(extract_fator)

    Amostra.loc[:,'Concentração Final'] = Amostra['Fator de diluição']*Amostra['Concentração Calc.']

    st.write('X')
    df_subset = st.data_editor(Amostra[['Sample ID', 'Fator de diluição']], height=300, hide_index=True)

    df_subset['Concentração Calc.'] = Amostra['Concentração Calc.']

    df_subset.loc[:,'Concentração Final'] = df_subset['Fator de diluição']*df_subset['Concentração Calc.']

    df_subset[['Posição na Curva','Abs.']] = Amostra[['Posição na Curva','Abs.']]

    df_subset = df_subset.drop(columns=['Concentração Calc.'])

    styled_df = df_subset[['Sample ID','Fator de diluição','Abs.','Concentração Final','Posição na Curva']].style\
        .apply(highlight_row, axis=1)\
        .format({
        'Fator de diluição': "{:.2f}",
        'Abs.': "{:.4f}",
        'Concentração Final': "{:.2f}"
    })
    st.table(styled_df)

    def convert_df(df_subset):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_subset.to_excel(writer, index=False, sheet_name='Sheet1')
            return output.getvalue()

    Excel = convert_df(df_subset)

    if Excel:
        st.download_button(
            label="Baixar Resultados",
            data=Excel,
            file_name='Resultados_ABS.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )

else:
    st.warning("Por favor, faça o upload do txt.")
