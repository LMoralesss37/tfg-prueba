import gradio as gr
import pandas as pd
import os

# Ruta fija al CSV (supongamos que siempre se llama igual)
CSV_PATH = "prueba.csv"

# Función para aplicar filtros sobre el CSV que ya está subido
def procesar_csv(nombre_filtro, apellidos_filtro, fecha_inicio_filtro, fecha_fin_filtro):
    try:
        df = pd.read_csv(CSV_PATH)
    except Exception:
        df = pd.read_csv(CSV_PATH, sep=None, engine='python')

    df_limpio = df.copy()

    df_limpio = df_limpio.dropna()
    df_limpio.columns = df_limpio.columns.str.replace(';;', '', regex=False)
    df_limpio['Hora de conexión'] = df_limpio['Hora de conexión'].str.split('.').str[0]
    df_limpio['Tiempo de juego'] = df_limpio['Tiempo de juego'].str.split('.').str[0]
    df_limpio['Fecha de conexión'] = pd.to_datetime(df_limpio['Fecha de conexión']).dt.strftime('%d/%m/%Y')
    df_limpio['% tarea completado'] = df_limpio['% tarea completado'].apply(lambda x: f"{x}%")
    df_limpio['Dolor'] = df_limpio['Dolor'].str.replace(';;', '', regex=False)

    if nombre_filtro:
        df_limpio = df_limpio[df_limpio['Nombre y apellidos'].str.contains(nombre_filtro, case=False, na=False)]
    
    if apellidos_filtro:
        df_limpio = df_limpio[df_limpio['Nombre y apellidos'].str.contains(apellidos_filtro, case=False, na=False)]
    
    if fecha_inicio_filtro and fecha_fin_filtro:
        df_limpio['Fecha de conexión'] = pd.to_datetime(df_limpio['Fecha de conexión'], format='%d/%m/%Y')
        fecha_inicio = pd.to_datetime(fecha_inicio_filtro, format='%d/%m/%Y')
        fecha_fin = pd.to_datetime(fecha_fin_filtro, format='%d/%m/%Y')
        df_limpio = df_limpio[(df_limpio['Fecha de conexión'] >= fecha_inicio) & (df_limpio['Fecha de conexión'] <= fecha_fin)]

    return df_limpio

# Crear la interfaz de Gradio sin necesidad de subir el CSV
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
    live=True
)

# IMPORTANTE: Para Render
port = int(os.environ.get("PORT", 7860))
iface.launch(server_name="0.0.0.0", server_port=port)


port = int(os.environ.get("PORT", 7860))
iface.launch(server_name="0.0.0.0", server_port=port)
