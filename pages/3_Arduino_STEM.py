import streamlit as st

st.set_page_config(page_title="Módulo 3 | Capacitación", layout="wide")

st.title("🔌 Módulo 3: Lógica Interactiva con Arduino")
st.markdown("**Objetivo:** Diseñar la lógica de control de una 'Herramienta de selección múltiple' y generar el código para integrarlo a nuestros modelos 3D didácticos.")
st.divider()

with st.expander("💡 De la Lógica a la Electrónica (Reflexión Pedagógica)", expanded=True):
    st.markdown("""
    En este módulo, daremos vida a los modelos que imprimimos en la Unidad 2. 
    
    Aprender a programar desde cero puede ser frustrante. Por eso, esta herramienta separa la **lógica pedagógica** de la **sintaxis de programación**. Aquí definirás cómo quieres que se comporte tu dispositivo didáctico. Una vez que valides la lógica probando los botones virtuales, la plataforma generará el código en C++ exacto. 
    
    Solo tendrás que copiarlo, pegarlo en **Tinkercad Circuits**, y armar el cableado físico siguiendo el esquema.
    """)

# --- VARIABLES DE ESTADO PARA EL SIMULADOR WEB ---
if 'estado_led' not in st.session_state:
    st.session_state.estado_led = "ESPERANDO"

def evaluar_respuesta(opcion_seleccionada, opcion_correcta):
    if opcion_seleccionada == opcion_correcta:
        st.session_state.estado_led = "CORRECTO"
    else:
        st.session_state.estado_led = "INCORRECTO"

def reiniciar():
    st.session_state.estado_led = "ESPERANDO"

# --- INTERFAZ DEL CONSTRUCTOR ---
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("1. Configura tu Dispositivo")
    st.write("Diseña cómo interactuarán tus estudiantes con la herramienta de selección múltiple.")
    
    num_opciones = st.radio("Cantidad de alternativas (Botones):", [2, 3, 4], index=1, horizontal=True)
    opcion_correcta = st.selectbox("¿Cuál es el botón con la respuesta correcta?", [f"Botón {chr(65+i)}" for i in range(num_opciones)])
    
    st.markdown("### 2. Prueba tu Lógica (Simulador)")
    st.write("Presiona los botones como si fueras un estudiante resolviendo el cuestionario.")
    
    # Botones virtuales
    botones_cols = st.columns(num_opciones)
    for i in range(num_opciones):
        letra = chr(65+i)
        nombre_boton = f"Botón {letra}"
        if botones_cols[i].button(nombre_boton, use_container_width=True):
            evaluar_respuesta(nombre_boton, opcion_correcta)
            
    st.button("🔄 Reiniciar Sistema", on_click=reiniciar, type="secondary")

with col2:
    st.subheader("3. Panel de Reacción (Hardware Virtual)")
    
    # Pantalla de estado visual
    if st.session_state.estado_led == "ESPERANDO":
        st.info("🟡 **Estado:** Esperando respuesta del estudiante... (LEDs apagados)")
    elif st.session_state.estado_led == "CORRECTO":
        st.success("🟢 **¡CORRECTO!** El LED Verde se enciende por 3 segundos.")
    elif st.session_state.estado_led == "INCORRECTO":
        st.error("🔴 **INCORRECTO.** El LED Rojo parpadea 2 veces.")
        
    st.divider()
    
    st.subheader("4. Tu Código Arduino Generado")
    st.write("Copia este código y pégalo en la sección de código de Tinkercad Circuits.")
    
    # Generador Dinámico de C++
    pines_botones = [2, 3, 4, 5][:num_opciones]
    pin_led_verde = 8
    pin_led_rojo = 9
    
    codigo_setup_pines = "\n".join([f"  pinMode({pin}, INPUT_PULLUP); // Botón {chr(65+i)}" for i, pin in enumerate(pines_botones)])
    
    codigo_loop_lectura = ""
    for i, pin in enumerate(pines_botones):
        letra = chr(65+i)
        if f"Botón {letra}" == opcion_correcta:
            reaccion = "respuestaCorrecta();"
        else:
            reaccion = "respuestaIncorrecta();"
            
        codigo_loop_lectura += f"""
  if (digitalRead({pin}) == LOW) {{ // Si se presiona el Botón {letra}
    {reaccion}
    delay(300); // Antirrebote
  }}"""

    codigo_arduino = f"""// --- HERRAMIENTA DE SELECCIÓN MÚLTIPLE ---
// Generado automáticamente por la Plataforma MakerBox

// Definición de Pines
const int pinLedVerde = {pin_led_verde};
const int pinLedRojo = {pin_led_rojo};

void setup() {{
  // Configuración de LEDs como salida
  pinMode(pinLedVerde, OUTPUT);
  pinMode(pinLedRojo, OUTPUT);
  
  // Configuración de Botones usando resistencias internas
{codigo_setup_pines}
}}

void loop() {{{codigo_loop_lectura}
}}

// Funciones de Reacción
void respuestaCorrecta() {{
  digitalWrite(pinLedVerde, HIGH); // Enciende Verde
  delay(3000);                     // Espera 3 segundos
  digitalWrite(pinLedVerde, LOW);  // Apaga Verde
}}

void respuestaIncorrecta() {{
  for(int i = 0; i < 2; i++) {{     // Parpadea Rojo 2 veces
    digitalWrite(pinLedRojo, HIGH);
    delay(200);
    digitalWrite(pinLedRojo, LOW);
    delay(200);
  }}
}}
"""
    st.code(codigo_arduino, language="cpp")
