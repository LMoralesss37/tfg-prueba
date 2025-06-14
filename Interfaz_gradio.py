import gradio as gr
import pandas as pd

# Función para procesar el CSV y aplicar filtros
def procesar_csv(csv_file, nombre_filtro, apellidos_filtro, fecha_inicio_filtro, fecha_fin_filtro):
    try:
        # Leer el archivo CSV
        df = pd.read_csv(csv_file.name)
    except Exception:
        # Si tiene delimitadores extraños o problemas de lectura, usar el engine='python'
        df = pd.read_csv(csv_file.name, sep=None, engine='python')

    # Copiamos el dataframe original
    df_limpio = df.copy()

    # Limpiar el dataframe
    df_limpio = df_limpio.dropna()
    df_limpio.columns = df_limpio.columns.str.replace(';;', '', regex=False)
    df_limpio['Hora de conexión'] = df_limpio['Hora de conexión'].str.split('.').str[0]
    df_limpio['Tiempo de juego'] = df_limpio['Tiempo de juego'].str.split('.').str[0]
    df_limpio['Fecha de conexión'] = pd.to_datetime(df_limpio['Fecha de conexión']).dt.strftime('%d/%m/%Y')
    df_limpio['% tarea completado'] = df_limpio['% tarea completado'].apply(lambda x: f"{x}%")
    df_limpio['Dolor'] = df_limpio['Dolor'].str.replace(';;', '', regex=False)

    # Filtrar por nombre (si se proporciona)
    if nombre_filtro:
        df_limpio = df_limpio[df_limpio['Nombre y apellidos'].str.contains(nombre_filtro, case=False, na=False)]
    
    # Filtrar por apellidos (si se proporciona)
    if apellidos_filtro:
        df_limpio = df_limpio[df_limpio['Nombre y apellidos'].str.contains(apellidos_filtro, case=False, na=False)]
    
    # Filtrar por fecha (si se proporciona un rango de fechas)
    if fecha_inicio_filtro and fecha_fin_filtro:
        df_limpio['Fecha de conexión'] = pd.to_datetime(df_limpio['Fecha de conexión'], format='%d/%m/%Y')
        fecha_inicio = pd.to_datetime(fecha_inicio_filtro, format='%d/%m/%Y')
        fecha_fin = pd.to_datetime(fecha_fin_filtro, format='%d/%m/%Y')
        df_limpio = df_limpio[(df_limpio['Fecha de conexión'] >= fecha_inicio) & (df_limpio['Fecha de conexión'] <= fecha_fin)]

    # Devolver el dataframe limpio y filtrado
    return df_limpio

# Crear la interfaz de Gradio
inputs = [
    gr.File(label="Sube el archivo CSV"),  # Cargar el archivo CSV
    gr.Textbox(label="Filtro por Nombre"),  # Campo para filtro por nombre
    gr.Textbox(label="Filtro por Apellidos"),  # Campo para filtro por apellidos
    gr.Textbox(label="Fecha de inicio (dd/mm/yyyy)", placeholder="Formato: dd/mm/yyyy"),  # Filtro por fecha inicio
    gr.Textbox(label="Fecha de fin (dd/mm/yyyy)", placeholder="Formato: dd/mm/yyyy")  # Filtro por fecha fin
]

outputs = gr.Dataframe(label="Datos filtrados")

# Configurar la interfaz de Gradio
gr.Interface(
    fn=procesar_csv,
    inputs=inputs,
    outputs=outputs,
    live=True
).launch()
