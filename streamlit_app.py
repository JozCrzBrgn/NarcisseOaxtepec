import streamlit as st

#? --- PAGE SETUP ---#
inventarios_page = st.Page(
    page="views/inventario.py",
    title="Inventario",
    icon="📋",
    default=True
)

ventas_page = st.Page(
    page="views/ventas.py",
    title="Ventas",
    icon="📈"
)

mermas_page = st.Page(
    page="views/mermas.py",
    title="Mermas",
    icon="📉"
)

insumos_page = st.Page(
    page="views/insumos.py",
    title="Insumos",
    icon="🍎"
)

pasteles_celebracion_page = st.Page(
    page="views/pasteles_celebracion.py",
    title="Pasteles de celebración",
    icon="🎂"
)

abonos_celebracion_page = st.Page(
    page="views/abonos_celebracion.py",
    title="Abonos de celebración",
    icon="💲"
)

#? --- NAVEGATION SETUP [WITH SECTIONS] ---#
pg = st.navigation(
    {
        "Productos en Sucursal": [inventarios_page, insumos_page],
        "Ventas y Mermas": [ventas_page, mermas_page],
        "Celebración": [pasteles_celebracion_page, abonos_celebracion_page],
    }
)

#? --- RUN NAVEGATION ---#
pg.run()