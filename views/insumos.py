
from io import BytesIO

import pandas as pd
from datetime import datetime as dt
from datetime import timedelta as td 

import streamlit as st
import streamlit_authenticator as stauth

from configuracion import config
from configuracion import read_json_from_supabase

st.set_page_config(
    page_title="Narcisse Oaxtepec",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded"
)


#* USER AUTHENTICATION
credenciales = read_json_from_supabase(config.BUCKET_GENERAL, config.CREDENCIALES_FILE)
authenticator = stauth.Authenticate(
    credenciales,
    st.secrets["COOKIE_NAME"],
    st.secrets["COOKIE_KEY"],
    int(st.secrets["COOKIE_EXPIRY_DAYS"]),
)
name, authentication_status, username = authenticator.login()

if authentication_status is False:
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.warning('Please enter your username ands password')
elif authentication_status:
    col1, col2 = st.columns([4,1])
    with col1:
        st.success('Bienvenido {}'.format(name))
    with col2:
        authenticator.logout('Logout', 'main')
    
    st.title("Insumos Oaxtepec")

    #? ANALISIS DE DATOS
    # Obtenemos los datos de la DB
    data = config.supabase.table(config.TAB_INVENTARIOS_VARIOS).select("producto,categoria,Oaxtepec").execute().data
    # Creamos el Dataframe
    df = pd.DataFrame(data)
    # Renombrar la columna 'tipo_combo' a 'promocion'
    df.rename(columns={'Oaxtepec': 'cantidad'}, inplace=True)

    if df.empty==False:
        col1_1, col1_2  = st.columns(2)
        with col1_1:
            #? FILTROS POR CATEGORIA
            # Widget para seleccionar una categoría
            categoria_seleccionada = st.multiselect('Filtrar por categoría:', df['categoria'].unique())
            if categoria_seleccionada:
                df_filtrado = df[df['categoria'].isin(categoria_seleccionada)]
            else:
                df_filtrado = df  # Mostrar todo si no hay selección
        with col1_2:
            #? FILTROS POR PRODUCTOS
            if categoria_seleccionada:
                # Solo mostrar productos que estén dentro de las categorías seleccionadas
                productos_disponibles = df_filtrado['producto'].unique()
            else:
                # Si no hay filtro de categoría, mostrar todos los productos
                productos_disponibles = df_filtrado['producto'].unique()

            producto_seleccionado = st.multiselect('Filtrar por producto:', productos_disponibles)
            if producto_seleccionado:
                df_filtrado = df_filtrado[df_filtrado['producto'].isin(producto_seleccionado)]

        #? BOTON DE DESCARGA
        # Función para convertir el DataFrame a un archivo Excel en memoria
        def to_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Insumos')
                writer._save()
            output.seek(0)
            return output
        # Botón de descarga de archivo Excel
        excel_data = to_excel(df_filtrado)
        st.download_button(
            label="Descargar en formato Excel",
            data=excel_data,
            file_name='Insumos.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        # Mostrar tabla filtrada
        st.table(df_filtrado)