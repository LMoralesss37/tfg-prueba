import gradio as gr
import pandas as pd
import os

# Definimos el usuario y contraseña
USUARIO_VALIDO = "admin"
CONTRASEÑA_VALIDA = "1234"

CSV_FILE = "datos.csv"

# Función de login
def verificar_login(usuario, contraseña):
    if usuario == USUARIO_VALIDO and contraseña == CONTRASEÑA_VALIDA:
        return gr.update(visible=False), gr.update(visible=True), ""
    else:
        return None, None, "Usuario o contraseña incorrecta."

# Procesamiento CSV
def procesar_csv(nombre_filtro, apellidos_filtro, fecha_inicio_filtro, fecha_fin_filtro):
    try:
        df = pd.read_csv(CSV_FILE)
    except Exception as e:
        return f"Error leyendo el CSV: {e}"

    df_limpio = df.copy().dropna()
    if 'Hora de conexión' in df_limpio.columns:
        df_limpio['Hora de conexión'] = df_limpio['Hora de conexión'].astype(str).str.split('.').str[0]
    if 'Tiempo de juego' in df_limpio.columns:
        df_limpio['Tiempo de juego'] = df_limpio['Tiempo de juego'].astype(str).str.split('.').str[0]
    if 'Fecha de conexión' in df_limpio.columns:
        df_limpio['Fecha de conexión'] = pd.to_datetime(df_limpio['Fecha de conexión'], errors='coerce', format='%d/%m/%Y')

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

    df_limpio['Fecha de conexión'] = df_limpio['Fecha de conexión'].dt.strftime('%d/%m/%Y')
    return df_limpio

def limpiar_filtros():
    return "", "", "", ""

# Paleta de colores personalizada
tema_css = """
.gradio-container {
    background-color: #E9E1DA;
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
    color: #0C4876 !important;
}
"""

# Interfaz principal
with gr.Blocks(css=tema_css) as interfaz:
    
    # LOGIN
    login = gr.Column(visible=True)
    with login:
        gr.HTML("""
            <div style='display: flex; align-items: center; gap: 20px;'>
                <img src='logo.png' style='height: 80px;'>
                <h1>CandiLVerse</h1>
            </div>
        """)
        gr.Markdown("## Iniciar sesión")
        usuario_input = gr.Textbox(label="Usuario")
        contraseña_input = gr.Textbox(label="Contraseña", type="password")
        login_boton = gr.Button("Acceder")
        mensaje_login = gr.Markdown("")

    # PANTALLA PRINCIPAL DE FILTROS
    filtros = gr.Column(visible=False)
    with filtros:
        gr.HTML("""
            <div style='display: flex; align-items: center; gap: 20px;'>
                <img src='logo.png' style='height: 80px;'>
                <h1>CandiLVerse</h1>
            </div>
        """)

        with gr.Row():
            nombre = gr.Textbox(label="Filtro por Nombre")
            apellidos = gr.Textbox(label="Filtro por Apellidos")
        
        with gr.Row():
            fecha_inicio = gr.Textbox(label="Fecha de inicio (dd/mm/yyyy)", placeholder="Formato: dd/mm/yyyy")
            fecha_fin = gr.Textbox(label="Fecha de fin (dd/mm/yyyy)", placeholder="Formato: dd/mm/yyyy")
        
        boton_filtrar = gr.Button("Filtrar")
        boton_borrar = gr.Button("Borrar todos los filtros")
        
        salida = gr.Dataframe(value=pd.DataFrame(columns=[
            "Nombre", "Apellidos", "Fecha de conexión", "Hora de conexión", 
            "Tiempo de juego", "% tarea completado", "Dolor"
        ]))

        boton_filtrar.click(fn=procesar_csv, inputs=[nombre, apellidos, fecha_inicio, fecha_fin], outputs=salida)
        boton_borrar.click(fn=limpiar_filtros, inputs=[], outputs=[nombre, apellidos, fecha_inicio, fecha_fin])

    login_boton.click(fn=verificar_login, inputs=[usuario_input, contraseña_input], outputs=[login, filtros, mensaje_login])

interfaz.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
