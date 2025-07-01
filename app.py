import gradio as gr
import pandas as pd
import random
import os

# Usuario y contraseña válidos
USUARIO_VALIDO = "admin"
CONTRASEÑA_VALIDA = "1234"

CSV_FILE = "datos.csv"

# Función de login
def verificar_login(usuario, contraseña):
    if usuario == USUARIO_VALIDO and contraseña == CONTRASEÑA_VALIDA:
        return gr.update(visible=False), gr.update(visible=True), ""
    else:
        return None, None, "Usuario o contraseña incorrecta."

# Procesamiento CSV con filtros
def procesar_csv(identificador_filtro, fecha_inicio_filtro, fecha_fin_filtro):
    try:
        df = pd.read_csv(CSV_FILE)
    except Exception as e:
        print(f"Error leyendo el CSV: {e}")
        return pd.DataFrame()

    df_limpio = df.copy()

    if 'Hora de conexión' in df_limpio.columns:
        df_limpio['Hora de conexión'] = df_limpio['Hora de conexión'].astype(str).str.split('.').str[0]
    if 'Tiempo de juego' in df_limpio.columns:
        df_limpio['Tiempo de juego'] = df_limpio['Tiempo de juego'].astype(str).str.split('.').str[0]

    if 'Fecha de conexión' in df_limpio.columns:
        df_limpio['Fecha de conexión'] = pd.to_datetime(df_limpio['Fecha de conexión'], errors='coerce')
    
        fecha_inicio = pd.to_datetime(fecha_inicio_filtro, format='%d/%m/%Y', errors='coerce') if fecha_inicio_filtro else None
        fecha_fin = pd.to_datetime(fecha_fin_filtro, format='%d/%m/%Y', errors='coerce') if fecha_fin_filtro else None
    
        if fecha_inicio and fecha_fin:
            df_limpio = df_limpio[
                (df_limpio['Fecha de conexión'] >= fecha_inicio) &
                (df_limpio['Fecha de conexión'] <= fecha_fin)
            ]
        elif fecha_inicio:
            df_limpio = df_limpio[df_limpio['Fecha de conexión'] >= fecha_inicio]
        elif fecha_fin:
            df_limpio = df_limpio[df_limpio['Fecha de conexión'] <= fecha_fin]
    
        # Volver a formatear para mostrar
        df_limpio['Fecha de conexión'] = df_limpio['Fecha de conexión'].dt.strftime('%d/%m/%Y')


    if identificador_filtro:
        df_limpio = df_limpio[df_limpio['ID'].astype(str).str.contains(identificador_filtro, case=False, na=False)]

    if 'Fecha de conexión' in df_limpio.columns and 'Hora de conexión' in df_limpio.columns:
        # Unificamos fecha y hora en una columna nueva para ordenar
        try:
            fecha_hora = pd.to_datetime(
                df_limpio['Fecha de conexión'].astype(str) + ' ' + df_limpio['Hora de conexión'].astype(str),
                format='%d/%m/%Y %H:%M:%S', errors='coerce'
            )
        except:
            fecha_hora = pd.to_datetime(
                df_limpio['Fecha de conexión'].astype(str) + ' ' + df_limpio['Hora de conexión'].astype(str),
                errors='coerce'
            )

        df_limpio['FechaHora'] = fecha_hora
        df_limpio = df_limpio.sort_values(by='FechaHora', ascending=False).drop(columns=['FechaHora'])

    return df_limpio


# Limpiar filtros
def limpiar_filtros():
    return "", "", ""

# Generar ID único con estilo visual embebido
def generar_identificador():
    try:
        df = pd.read_csv(CSV_FILE)
        existentes = set(df['ID'].astype(str).values)
    except:
        existentes = set()

    while True:
        nuevo = str(random.randint(100000, 999999))
        if nuevo not in existentes:
            return f"""
<div style='
    background-color: white;
    padding: 40px;
    border-radius: 10px;
    min-height: 320px;
    display: flex;
    align-items: center;
    justify-content: center;
'>
    <span style='font-size: 60px; font-weight: bold; color: #0C4876;'>
         {nuevo}
    </span>
</div>
"""

# Tema visual
tema_css = """
.gradio-container {
    background-color: #AEC5D8;
}
h1 {
    color: #0C4876;
    font-size: 55px;
    font-family: Arial, sans-serif;
}
button {
    background-color: #608FB7 !important;
    color: white !important;
}
input, textarea {
    background-color: #ffffff !important;
    border-color: #AEC5D8 !important;
}
.dataframe thead {
    background-color: #C2ACB4 !important;
    color: #0C4876;
}
"""

# Interfaz principal
with gr.Blocks(css=tema_css) as interfaz:

    # LOGIN
    login = gr.Column(visible=True)
    with login:
        with gr.Row():
            with gr.Column(scale=0):
                gr.Image("logo.png", height=100, width=100, show_label=False)
            with gr.Column():
                gr.Markdown("<h1 style='font-size:45px;color:#0C4876'>CandiLVerse</h1>")
        gr.Markdown("## Iniciar sesión")
        usuario_input = gr.Textbox(label="Usuario")
        contraseña_input = gr.Textbox(label="Contraseña", type="password")
        login_boton = gr.Button("Acceder")
        mensaje_login = gr.Markdown("")

    # PANTALLA PRINCIPAL
    filtros = gr.Column(visible=False)
    with filtros:
        with gr.Row():
            with gr.Column(scale=0):
                gr.Image("logo.png", height=100, width=100, show_label=False)
            with gr.Column():
                gr.Markdown("<h1 style='font-size:45px;color:#0C4876'>CandiLVerse</h1>")

        with gr.Row():
            # Columna izquierda: filtros
            with gr.Column():
                identificador = gr.Textbox(label="Filtro por Identificador")
                fecha_inicio = gr.Textbox(label="Fecha de inicio (dd/mm/yyyy)", placeholder="Formato: dd/mm/yyyy")
                fecha_fin = gr.Textbox(label="Fecha de fin (dd/mm/yyyy)", placeholder="Formato: dd/mm/yyyy")
                boton_filtrar = gr.Button("Filtrar")
                boton_borrar = gr.Button("Borrar todos los filtros")

            # Columna derecha: ID generado en recuadro alto y centrado
            with gr.Column(scale=1):
                boton_generar_id = gr.Button("Generar ID único", scale=1)
                id_generado = gr.Markdown("")

        salida = gr.Dataframe(value=pd.DataFrame(columns=[
            "ID", "Edad", "Altura", "Peso", "Articulación", "Descripción de la tarea",
            "Nivel de dificultad", "Hombro a rehabilitar", "FC mínima", "FC máxima", "FC media",
            "Fecha de conexión", "Hora de conexión", "Tiempo de juego", "% tarea completado",
            "Series", "Repeticiones completas", "Ajuste de nivel", "Dolor"
        ]))

        # Conexiones
        boton_filtrar.click(fn=procesar_csv, inputs=[identificador, fecha_inicio, fecha_fin], outputs=salida)
        boton_borrar.click(fn=limpiar_filtros, inputs=[], outputs=[identificador, fecha_inicio, fecha_fin])
        boton_generar_id.click(fn=generar_identificador, inputs=[], outputs=id_generado)

    login_boton.click(fn=verificar_login, inputs=[usuario_input, contraseña_input], outputs=[login, filtros, mensaje_login])

# Lanzamiento
interfaz.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))