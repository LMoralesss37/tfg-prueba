import gradio as gr
import pandas as pd
import os

# Ruta al CSV en el servidor
CSV_PATH = "datos.csv"

# Función para procesar el CSV y aplicar filtros
def procesar_csv(nombre_filtro, apellidos_filtro, fecha_inicio_filtro, fecha_fin_filtro):
    try:
        df = pd.read_csv(CSV_PATH)
    except Exception as e:
        return f"Error al leer el CSV: {str(e)}"

    df_limpio = df.dropna()

    # Convertimos % tarea completado a string con %
    if "% tarea completado" in df_limpio.columns:
        df_limpio['% tarea completado'] = df_limpio['% tarea completado'].astype(str) + '%'

    # Normalizamos fecha sólo si no es datetime aún
    if 'Fecha de conexión' in df_limpio.columns:
        if not pd.api.types.is_datetime64_any_dtype(df_limpio['Fecha de conexión']):
            df_limpio['Fecha de conexión'] = pd.to_datetime(df_limpio['Fecha de conexión'], format='%d/%m/%Y')

    # Filtro por Nombre
    if nombre_filtro and 'Nombre' in df_limpio.columns:
        df_limpio = df_limpio[df_limpio['Nombre'].str.contains(nombre_filtro, case=False, na=False)]

    # Filtro por Apellidos
    if apellidos_filtro and 'Apellidos' in df_limpio.columns:
        df_limpio = df_limpio[df_limpio['Apellidos'].str.contains(apellidos_filtro, case=False, na=False)]

    # Filtro por Fechas
    if fecha_inicio_filtro and fecha_fin_filtro and 'Fecha de conexión' in df_limpio.columns:
        try:
            fecha_inicio = pd.to_datetime(fecha_inicio_filtro, format='%d/%m/%Y')
            fecha_fin = pd.to_datetime(fecha_fin_filtro, format='%d/%m/%Y')
            df_limpio = df_limpio[(df_limpio['Fecha de conexión'] >= fecha_inicio) & (df_limpio['Fecha de conexión'] <= fecha_fin)]
        except Exception as e:
            return f"Error al convertir fechas: {str(e)}"

    # Volvemos a mostrar las fechas como string en la tabla
    df_limpio['Fecha de conexión'] = df_limpio['Fecha de conexión'].dt.strftime('%d/%m/%Y')

    return df_limpio

# Crear la interfaz Gradio
inputs = [
    gr.Textbox(label="Filtro por Nombre"),
    gr.Textbox(label="Filtro por Apellidos"),
    gr.Textbox(label="Fecha de inicio (dd/mm/yyyy)", placeholder="Formato: dd/mm/yyyy"),
    gr.Textbox(label="Fecha de fin (dd/mm/yyyy)", placeholder="Formato: dd/mm/yyyy")
]

outputs = gr.Dataframe(label="Datos filtrados")

iface = gr.Interface(
    fn=procesar_csv,
    inputs=inputs,
    outputs=outputs,
    live=True,
    allow_flagging="never",  # 🔧 Desactiva el botón de Flag
    clear_button="Borrar todos los filtros"  # 🔧 Personaliza el texto del botón Clear
)

# Para que funcione en Render
port = int(os.environ.get("PORT", 7860))
iface.launch(server_name="0.0.0.0", server_port=port)


