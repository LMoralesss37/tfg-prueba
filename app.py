import gradio as gr
import pandas as pd
import os

# Leer directamente el archivo CSV fijo (que está subido a GitHub y Render lo tiene en el mismo directorio)
CSV_FILE = "datos.csv"

# Función para procesar y filtrar el CSV
def procesar_csv(nombre_filtro, apellidos_filtro, fecha_inicio_filtro, fecha_fin_filtro):
    try:
        df = pd.read_csv(CSV_FILE)
    except Exception as e:
        return f"Error leyendo el CSV: {e}"

    # Copiamos el dataframe original
    df_limpio = df.copy()

    # Limpieza de datos (ajusta según tu CSV)
    df_limpio = df_limpio.dropna()
    if 'Hora de conexión' in df_limpio.columns:
        df_limpio['Hora de conexión'] = df_limpio['Hora de conexión'].astype(str).str.split('.').str[0]
    if 'Tiempo de juego' in df_limpio.columns:
        df_limpio['Tiempo de juego'] = df_limpio['Tiempo de juego'].astype(str).str.split('.').str[0]
    if 'Fecha de conexión' in df_limpio.columns:
        df_limpio['Fecha de conexión'] = pd.to_datetime(df_limpio['Fecha de conexión'], errors='coerce', format='%d/%m/%Y')

    # Aplicar filtros
    if nombre_filtro:
        df_limpio = df_limpio[df_limpio['Nombre'].str.contains(nombre_filtro, case=False, na=False)]

    if apellidos_filtro:
        df_limpio = df_limpio[df_limpio['Apellidos'].str.contains(apellidos_filtro, case=False, na=False)]

    if fecha_inicio_filtro and fecha_fin_filtro:
        try:
            fecha_inicio = pd.to_datetime(fecha_inicio_filtro, format='%d/%m/%Y', errors='coerce')
            fecha_fin = pd.to_datetime(fecha_fin_filtro, format='%d/%m/%Y', errors='coerce')
            df_limpio = df_limpio[(df_limpio['Fecha de conexión'] >= fecha_inicio) & (df_limpio['Fecha de conexión'] <= fecha_fin)]
        except Exception as e:
            return f"Error en el filtrado de fechas: {e}"

    # Convertimos las fechas de vuelta al formato texto para mostrar
    df_limpio['Fecha de conexión'] = df_limpio['Fecha de conexión'].dt.strftime('%d/%m/%Y')
    
    return df_limpio

# Función para resetear filtros (truco porque Interface no tiene clear_button)
def limpiar_filtros():
    return "", "", "", ""

# Definimos interfaz
with gr.Blocks() as interfaz:
    gr.Markdown("## Filtro de datos CSV")

    with gr.Row():
        nombre = gr.Textbox(label="Filtro por Nombre")
        apellidos = gr.Textbox(label="Filtro por Apellidos")
    
    with gr.Row():
        fecha_inicio = gr.Textbox(label="Fecha de inicio (dd/mm/yyyy)", placeholder="Formato: dd/mm/yyyy")
        fecha_fin = gr.Textbox(label="Fecha de fin (dd/mm/yyyy)", placeholder="Formato: dd/mm/yyyy")

    boton_filtrar = gr.Button("Filtrar")
    boton_borrar = gr.Button("Borrar todos los filtros")

    salida = gr.Dataframe()

    boton_filtrar.click(
        fn=procesar_csv,
        inputs=[nombre, apellidos, fecha_inicio, fecha_fin],
        outputs=salida
    )

    boton_borrar.click(
        fn=limpiar_filtros,
        inputs=[],
        outputs=[nombre, apellidos, fecha_inicio, fecha_fin]
    )

interfaz.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))



