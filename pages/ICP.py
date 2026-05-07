import seaborn as sns
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import io
import xlsxwriter

from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

st.set_page_config(
    page_icon='jabuti-05.png',
    page_title='Facilitador'
)

st.title('Bem-vindo ao tratamento de ICP!')
st.write('Software desenvolvido por Miguel O.')

# =========================================================
# UPLOAD DO EXCEL
# =========================================================

icp_file = st.file_uploader(
    label='Selecione o arquivo Excel com os dados ICP:',
    type=['xlsx']
)

# =========================================================
# LEITURA DO ARQUIVO
# =========================================================

if icp_file:

    icp = pd.read_excel(icp_file)

    # Converte para csv temporário
    csv_buffer = io.StringIO()
    icp.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    grafico = pd.read_csv(csv_buffer)


    # =====================================================
    # DETECÇÃO AUTOMÁTICA DAS COLUNAS
    # =====================================================

    def encontrar_coluna(df, possibilidades):

        for col in df.columns:

            for nome in possibilidades:

                if nome.lower() in col.lower():

                    return col

        return None

    col_type = encontrar_coluna(
        grafico,
        ['Type', 'Class']
    )

    col_element = encontrar_coluna(
        grafico,
        ['Element']
    )

    if 'Intensity[Ave]' in grafico.columns:
        col_int = 'Intensity[Ave]'
    else:
        col_int = 'Int'

    col_conc = encontrar_coluna(
        grafico,
        ['Soln Conc', 'Analysis Condition']
    )

    col_solution = encontrar_coluna(
        grafico,
        ['Solution Label', 'Sample Name']
    )

    # =====================================================
    # VERIFICAÇÃO
    # =====================================================
    grafico[col_int] = pd.to_numeric(
    grafico[col_int]
    .astype(str)
    .str.replace(',', '.'),
    errors='coerce'
    ).fillna(0)

    grafico[col_conc] = pd.to_numeric(
        grafico[col_conc]
        .astype(str)
        .str.replace(',', '.'),
        errors='coerce'
    ).fillna(0)

    colunas_necessarias = [
        col_type,
        col_element,
        col_int,
        col_conc,
        col_solution
    ]

    if any(col is None for col in colunas_necessarias):

        st.error('Não foi possível identificar automaticamente todas as colunas.')

        st.stop()

    # =====================================================
    # FILTRAGEM DOS DADOS
    # =====================================================

    Branco = grafico.loc[
    (grafico[col_type] == 'Blk') | (grafico[col_solution] == 'Branco')]

    Padrao = grafico.loc[
    (grafico[col_type] == 'Std') |
    (grafico[col_type].str.startswith('CAL'))]

    Amostra = grafico.loc[grafico[col_type].isin(['Samp', 'UNK'])]

    # =====================================================
    # ANALITOS DISPONÍVEIS
    # =====================================================

    analitos_disponiveis = sorted(
        grafico[col_element]
        .dropna()
        .unique()
    )

    Analito = st.selectbox(
        'Defina o elemento/comprimento de onda:',
        analitos_disponiveis
    )

    # =====================================================
    # FILTRA ANALITO
    # =====================================================

    PontoB = Branco.loc[
        Branco[col_element] == Analito
    ]

    PontoP = Padrao.loc[
        Padrao[col_element] == Analito
    ]

    PontoA = Amostra.loc[
        Amostra[col_element] == Analito
    ]

    # =====================================================
    # REMOVE LIMPEZA
    # =====================================================

    PontoA = PontoA[
        PontoA[col_solution] != 'Limpeza'
    ]

    # =====================================================
    # CORREÇÃO PELO BRANCO
    # =====================================================


    blank = PontoB[col_int].iloc[0]

    PontoP[col_int] = PontoP[col_int] - blank

    PontoA[col_int] = PontoA[col_int] - blank

    # =====================================================
    # LAYOUT
    # =====================================================

    coluna1, coluna2, = st.columns([6, 4])

    # =====================================================
    # DADOS ORIGINAIS
    # =====================================================

    x_original = PontoP[col_conc].values

    y_original = PontoP[col_int].values

    selected_rows = []

    # =====================================================
    # CHECKBOXES
    # =====================================================

    st.subheader("Editar pontos")
    PontoP[col_conc] = PontoP[col_conc].astype(float)
    PontoP[col_int] = PontoP[col_int].astype(float)

    # adiciona coluna de controle de exclusão
    PontoP["Excluir"] = False

    # data editor (tipo Excel)
    PontoP_edit = st.data_editor(
        PontoP[[col_conc, col_int, "Excluir"]].copy(),
        num_rows="dynamic",
        )

    # =====================================================
    # REMOVE PONTOS MARCADOS
    # =====================================================

    PontoP_edit = PontoP_edit[PontoP_edit["Excluir"] == False]

    # remove NaN caso usuário edite manualmente
    PontoP= PontoP_edit.dropna(subset=[col_conc, col_int])

    PontoP = PontoP_edit

    # =====================================================
    # REGRESSÃO
    # =====================================================

    x = PontoP[col_conc].values

    y = PontoP[col_int].values

    model = LinearRegression()

    model.fit(
        x.reshape(-1, 1),
        y
    )

    y_prev = model.predict(
        x.reshape(-1, 1)
    )

    r_quadrado = r2_score(y, y_prev)

    # =====================================================
    # GRÁFICO
    # =====================================================

    fig = plt.figure()

    left, width = .25, .5
    bottom, height = .25, .5

    right = left + width
    top = bottom + height

    plt.scatter(
        x_original,
        y_original,
        alpha=0
    )

    plt.scatter(
        x,
        y,
        color='black'
    )

    fig.text(
        right,
        top,
        f'$R^2 = {r_quadrado:.5f}$',
        horizontalalignment='right',
        verticalalignment='bottom'
    )

    plt.plot(
        x,
        y_prev,
        color='red'
    )

    plt.xlabel('Concentração')

    plt.ylabel('Intensidade')

    plt.title(Analito)

    with coluna1:

        st.pyplot(fig)

    # =====================================================
    # EQUAÇÃO
    # =====================================================

    a = model.coef_[0]

    b = model.intercept_

    # =====================================================
    # LIMITES
    # =====================================================

    valor_referencia = PontoP[col_int].min()

    valor_maximo = PontoP[col_int].max()

    FGX = PontoA[col_int]

    df_valores_ref = pd.DataFrame({
        'Máximo': [valor_maximo],
        'Mínimo': [valor_referencia]
    })

    with coluna2:

        st.dataframe(
            df_valores_ref,
            hide_index=True
        )

    # =====================================================
    # POSIÇÃO NA CURVA
    # =====================================================

    PosicaoNaCurva = []

    for index, row in PontoA.iterrows():

        if row[col_int] < valor_referencia:

            PosicaoNaCurva.append('Abaixo')

        elif row[col_int] > valor_maximo:

            PosicaoNaCurva.append('Acima')

        else:

            PosicaoNaCurva.append('Dentro')

    # =====================================================
    # CÁLCULO DAS CONCENTRAÇÕES
    # =====================================================

    PontoA[col_int] = (
        PontoA[col_int] - b
    ) / a

    PontoA = PontoA.rename(columns={
        col_solution: 'Nome da Amostra',
        col_int: 'Concentração'
    })

    df_subset = PontoA[
        ['Nome da Amostra', 'Concentração']
    ]

    # =====================================================
    # FATORES DE DILUIÇÃO
    # =====================================================

    st.subheader('INSIRA OS FATORES DE DILUIÇÃO')

    temp_df = df_subset.copy()

    temp_df['Fator de diluição'] = (
        temp_df['Nome da Amostra']
        .str.extract(r'([\d.,]+)x', expand=False)
    )

    # =====================================================
    # LIMPEZA DOS FATORES
    # =====================================================

    def clean_fator_diluicao(value):

        if isinstance(value, str):

            value = value.replace('.', '')

            value = value.replace(',', '.')

        try:

            return float(value)

        except:

            return 1

    temp_df['Fator de diluição'] = (
        temp_df['Fator de diluição']
        .apply(clean_fator_diluicao)
    )

    # =====================================================
    # EDITOR
    # =====================================================

    df_subset = st.data_editor(
        temp_df[
            ['Nome da Amostra', 'Fator de diluição']
        ],
        height=300,
        hide_index=True
    )

    # =====================================================
    # RESULTADOS
    # =====================================================

    df_subset['Concentração'] = (
        PontoA['Concentração'].values
    )

    df_subset['Resultado'] = (
        df_subset['Concentração']
        *
        df_subset['Fator de diluição']
    )

    df_subset['Resultado (ppm)'] = (
        df_subset['Resultado']
        .round(2)
    )

    df_subset['Int'] = FGX.values

    df_subset['Posição na Curva'] = PosicaoNaCurva

    # =====================================================
    # HIGHLIGHT
    # =====================================================

    def highlight_row(row):

        if row['Int'] < valor_referencia:

            return ['color: red'] * len(row)

        elif row['Int'] > valor_maximo:

            return ['color: red'] * len(row)

        else:

            return ['color: green'] * len(row)

    styled_df = df_subset.style.apply(
        highlight_row,
        axis=1
    )

    # =====================================================
    # FORMATAÇÃO
    # =====================================================

    df_subset['Fator de diluição'] = (
        df_subset['Fator de diluição']
        .map(lambda x: f"{x:.1f}")
    )

    # =====================================================
    # TABELA
    # =====================================================

    st.table(styled_df)

    # =====================================================
    # EXPORTAÇÃO EXCEL
    # =====================================================

    def convert_df(df):

        output = io.BytesIO()

        with pd.ExcelWriter(
            output,
            engine='xlsxwriter'
        ) as writer:

            df.to_excel(
                writer,
                index=False,
                sheet_name='Resultados'
            )

        return output.getvalue()

    Excel = convert_df(df_subset)

    # =====================================================
    # DOWNLOAD
    # =====================================================

    st.download_button(
        label='Baixar Resultados',
        data=Excel,
        file_name='Resultados_ICP.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

else:

    st.warning(
        'Por favor, faça o upload do Excel.'
    )
