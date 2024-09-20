
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
    
    st.title("Inventario Oaxtepec")

    #? ANALISIS DE DATOS
    # Obtenemos los datos de la DB
    data = config.supabase.table(config.TAB_INVENTARIO).select("*").eq("estatus", "ESCANEADO").execute().data
    # Creamos el Dataframe
    df = pd.DataFrame(data)
    # Quitamos las columnas que no necesitamos
    df_inv = df[['clave', 'sucursal', 'producto', 'categoria', 'caducidad', 'estatus']]
    # Convertimos la columna de caducidad a datetime
    df_inv['caducidad'] = pd.to_datetime(df_inv['caducidad'])
    now = dt.now()
    # Si la columna caducidad es menor a la fecha actual, entonces se debe de cambiar el estatus a "CADUCADO"
    df_inv.loc[df_inv['caducidad'] < now, 'estatus'] = "CADUCADO"
    # Si la columna caducidad es igual a la fecha actual, entonces se debe de cambiar el estatus a "CADUCA HOY"
    df_inv.loc[df_inv['caducidad'] == now, 'estatus'] = "CADUCA HOY"
    # Si la columna caducidad es un dia despues de la fecha actual, entonces se debe de cambiar el estatus a "CADUCA EN UN DIA"
    df_inv.loc[df_inv['caducidad'] == now + td(days=1), 'estatus'] = "CADUCA EN UN DIA"
    # Si la columna caducidad es dos dias despues de la fecha actual, , entonces se debe de cambiar el estatus a "CADUCA EN DOS DIAS"
    df_inv.loc[df_inv['caducidad'] == now + td(days=2), 'estatus'] = "CADUCA EN DOS DIAS"
    # Si la columna caducidad es tres dias despues de la fecha actual, entonces se debe de cambiar el estatus a "-----"
    df_inv.loc[df_inv['caducidad'] >= now + td(days=3), 'estatus'] = "------"
    # Cantidad de productos de cada categoria de estatus
    optimos = df_inv[df_inv['estatus']== "------"].shape[0]
    caducados = df_inv[df_inv['estatus']== "CADUCADO"].shape[0]
    cadhoy = df_inv[df_inv['estatus']== "CADUCA HOY"].shape[0]
    cadundia = df_inv[df_inv['estatus']== "CADUCA EN UN DIA"].shape[0]
    caddosdias = df_inv[df_inv['estatus']== "CADUCA EN DOS DIAS"].shape[0]
    total = optimos + caducados + cadhoy + cadundia + caddosdias

    #? MARCADORES DE ESTATUS
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("ÓPTIMO", f"{optimos} Productos", f"{round(optimos*100/total, 2)}%")
    col2.metric("CADUCADO", f"{caducados} Productos", f"-{round(caducados*100/total, 2)}%")
    col3.metric("CADUCA HOY", f"{cadhoy} Productos", f"{round(cadhoy*100/total, 2)}%")
    col4.metric("CADUCA EN UN DÍA", f"{cadundia} Productos", f"{round(cadundia*100/total, 2)}%")
    col5.metric("CADUCA EN DOS DÍAS", f"{caddosdias} Productos", f"{round(caddosdias*100/total, 2)}%")

    col1_1, col1_2  = st.columns(2)
    with col1_1:
        #? FILTROS POR CATEGORIA
        # Widget para seleccionar una categoría
        categoria_seleccionada = st.multiselect('Filtrar por categoría:', df_inv['categoria'].unique())
        if categoria_seleccionada:
            df_filtrado = df_inv[df_inv['categoria'].isin(categoria_seleccionada)]
        else:
            df_filtrado = df_inv  # Mostrar todo si no hay selección
    with col1_2:
        #? FILTROS POR PRODUCTOS
        if categoria_seleccionada:
            # Solo mostrar productos que estén dentro de las categorías seleccionadas
            productos_disponibles = df_filtrado['producto'].unique()
        else:
            # Si no hay filtro de categoría, mostrar todos los productos
            productos_disponibles = df_inv['producto'].unique()

        producto_seleccionado = st.multiselect('Filtrar por producto:', productos_disponibles)
        if producto_seleccionado:
            df_filtrado = df_filtrado[df_filtrado['producto'].isin(producto_seleccionado)]

    #? FILTROS POR FECHA
    # Mostrar el rango de fechas en el DataFrame
    fecha_min = dt.strptime(df_filtrado['caducidad'].min().strftime("%Y-%m-%d"), '%Y-%m-%d').date()
    fecha_max = dt.strptime(df_filtrado['caducidad'].max().strftime("%Y-%m-%d"), '%Y-%m-%d').date()
    # Widget para seleccionar un rango de fechas
    fecha_inicio, fecha_fin = st.slider(
        'Selecciona un rango de fechas:',
        min_value=fecha_min,
        max_value=fecha_max,
        value=(fecha_min, fecha_max),
        format="YYYY-MM-DD"
    )
    fecha_inicio = pd.to_datetime(fecha_inicio)
    fecha_fin = pd.to_datetime(fecha_fin)

    # Filtrar el DataFrame según el rango de fechas seleccionado
    df_filtrado = df_filtrado[(df_filtrado['caducidad'] >= fecha_inicio) & (df_filtrado['caducidad'] <= fecha_fin)]

    #? BOTON DE DESCARGA
    # Función para convertir el DataFrame a un archivo Excel en memoria
    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Inventario')
            writer._save()
        output.seek(0)
        return output
    # Botón de descarga de archivo Excel
    excel_data = to_excel(df_filtrado)
    st.download_button(
        label="Descargar en formato Excel",
        data=excel_data,
        file_name='Inventario.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    st.table(df_filtrado)
