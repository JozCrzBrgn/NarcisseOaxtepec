
import pandas as pd
from io import BytesIO

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
    
    st.title("Pasteles de Celebración")

    #? ANALISIS DE DATOS
    # Obtenemos los datos de la DB
    data = config.supabase.table(config.TAB_CELEBRACION).select("*").execute().data
    # Creamos el Dataframe
    df = pd.DataFrame(data)
    # Quitamos las columnas que no necesitamos
    df_celeb = df[
        ['clave', 'cliente', 'email', 'celular', 'fecha_entrega', 'hora_entrega', 'costo_total', 'personas', 'base', 
         'relleno', 'pastel', 'cobertura', 'lugar_entrega', 'descripcion', 'empleado', 'estatus', 'bool_descuento', 'leyenda', 
         'flete', 'extras']
         ]
    # Renombrar la columna 'tipo_combo' a 'promocion'
    df_celeb.rename(columns={'bool_descuento': 'con_descuento'}, inplace=True)
    # Convertimos la columna de caducidad a datetime
    df_celeb['fecha_entrega'] = pd.to_datetime(df_celeb['fecha_entrega'])

    col1_1, col1_2, col1_3  = st.columns(3)
    with col1_1:
        #? FILTROS POR MES
        # Extraer los meses de la columna de fechas
        df_celeb['mes'] = df_celeb['fecha_entrega'].dt.month
        df_celeb['dia'] = df_celeb['fecha_entrega'].dt.day

        # Definir los nombres de los meses
        meses = {
            1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
            5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
            9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
        }

        # Filtro por mes, inicializando en enero (mes 1)
        mes_seleccionado = st.selectbox('Selecciona un mes de entrega:', options=list(meses.keys()), format_func=lambda x: meses[x], index=0)

        # Filtrar el DataFrame según el mes seleccionado
        df_filtrado = df_celeb[df_celeb['mes'] == mes_seleccionado]

    with col1_2:
        #? FILTROS POR DÍAS
        # Verificar si el DataFrame filtrado está vacío
        if df_filtrado.empty:
            st.warning(f"No hay datos disponibles para {meses[mes_seleccionado]}.")
        else:
            # Obtener los días disponibles para el mes seleccionado
            dia_min = df_filtrado['dia'].min()
            dia_max = df_filtrado['dia'].max()

            # Filtro por número de día usando un slider
            dias_seleccionados = st.slider(
                'Filtrar por días:',
                min_value=dia_min,
                max_value=dia_max,
                value=(dia_min, dia_max)
            )
            # Filtrar el DataFrame según los días seleccionados
            df_filtrado = df_filtrado[(df_filtrado['dia'] >= dias_seleccionados[0]) & (df_filtrado['dia'] <= dias_seleccionados[1])]

    with col1_3:
            #? FILTROS POR CATEGORIA
            # Widget para seleccionar una categoría
            estatus_seleccionada = st.multiselect('Filtrar por estatus:', df_filtrado['estatus'].unique())
            if estatus_seleccionada:
                df_filtrado = df_filtrado[df_filtrado['estatus'].isin(estatus_seleccionada)]
            else:
                df_filtrado = df_filtrado  # Mostrar todo si no hay selección

    #? BOTON DE DESCARGA
    # Función para convertir el DataFrame a un archivo Excel en memoria
    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='PastelesCelebracion')
            writer._save()
        output.seek(0)
        return output
    # Botón de descarga de archivo Excel
    excel_data = to_excel(df_filtrado)
    st.download_button(
        label="Descargar en formato Excel",
        data=excel_data,
        file_name='PastelesCelebracion.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    # Mostrar tabla filtrada
    st.table(df_filtrado[
        ['clave', 'cliente', 'email', 'celular', 'fecha_entrega', 'hora_entrega', 'costo_total', 'personas', 'base', 
         'relleno', 'pastel', 'cobertura', 'lugar_entrega', 'descripcion', 'empleado', 'estatus', 'con_descuento', 'leyenda', 
         'flete', 'extras']
    ])