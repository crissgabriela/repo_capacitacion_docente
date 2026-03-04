import streamlit as st

st.set_page_config(page_title="Módulo 3 | Capacitación", layout="wide")

st.title("🔌 Módulo 3: Lógica Interactiva con Arduino")
st.markdown("**Objetivo:** Diseñar la lógica de control de una 'Herramienta de selección múltiple' y generar el código para integrarlo a nuestros modelos 3D didácticos.")
st.divider()

with st.expander("💡 De la Lógica a la Electrónica (Reflexión Pedagógica)", expanded=True):
    st.markdown("""
    En este módulo daremos vida a los modelos que imprimimos en la Unidad 2. 
    
    Aprender a programar y cablear desde cero puede ser frustrante. Por eso, esta herramienta separa la **lógica pedagógica** de la **sintaxis técnica**. Aquí definirás cómo quieres que se comporte tu dispositivo didáctico. Una vez que lo valides probando los botones virtuales, la plataforma generará tanto el **Código C++** como la **Guía de Cableado**. 
    
    Podrás armar tu circuito en el simulador *Tinkercad Circuits* o directamente con tu kit físico de Arduino.
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
    
    st.markdown("### 3. Panel de Reacción")
    # Pantalla de estado visual
    if st.session_state.estado_led == "ESPERANDO":
        st.info("🟡 **Estado:** Esperando respuesta del estudiante... (LEDs apagados)")
    elif st.session_state.estado_led == "CORRECTO":
        st.success("🟢 **¡CORRECTO!** El LED Verde se enciende por 3 segundos.")
    elif st.session_state.estado_led == "INCORRECTO":
        st.error("🔴 **INCORRECTO.** El LED Rojo parpadea 2 veces.")

with col2:
    st.subheader("4. Tu Kit de Integración")
    
    tab_codigo, tab_hardware = st.tabs(["💻 Código Arduino", "🛠️ Guía de Cableado Físico"])
    
    # Definición de Pines (Compartidos entre código y hardware)
    pines_botones = [2, 3, 4, 5][:num_opciones]
    pin_led_verde = 8
    pin_led_rojo = 9
    
    with tab_codigo:
        st.write("Copia este código y pégalo en el IDE de Arduino o en Tinkercad Circuits.")
        
        # Generador Dinámico de C++
        codigo_setup_pines = "\n".join([f"  pinMode({pin}, INPUT_PULLUP); // Botón {chr(65+i)}" for i, pin in enumerate(pines_botones)])
        
        codigo_loop_lectura = ""
        for i, pin in enumerate(pines_botones):
            letra = chr(65+i)
            reaccion = "respuestaCorrecta();" if f"Botón {letra}" == opcion_correcta else "respuestaIncorrecta();"
            codigo_loop_lectura += f"""
  if (digitalRead({pin}) == LOW) {{ // Si se presiona el Botón {letra}
    {reaccion}
    delay(300); // Antirrebote para evitar doble lectura
  }}"""

        codigo_arduino = f"""// --- HERRAMIENTA DE SELECCIÓN MÚLTIPLE ---
// Generado automáticamente para {num_opciones} botones.

const int pinLedVerde = {pin_led_verde};
const int pinLedRojo = {pin_led_rojo};

void setup() {{
  pinMode(pinLedVerde, OUTPUT);
  pinMode(pinLedRojo, OUTPUT);
  
  // Usamos INPUT_PULLUP para no necesitar resistencias físicas en los botones
{codigo_setup_pines}
}}

void loop() {{{codigo_loop_lectura}
}}

void respuestaCorrecta() {{
  digitalWrite(pinLedVerde, HIGH); 
  delay(3000);                     
  digitalWrite(pinLedVerde, LOW);  
}}

void respuestaIncorrecta() {{
  for(int i = 0; i < 2; i++) {{     
    digitalWrite(pinLedRojo, HIGH);
    delay(200);
    digitalWrite(pinLedRojo, LOW);
    delay(200);
  }}
}}
"""
        st.code(codigo_arduino, language="cpp")

    with tab_hardware:
        st.write("Sigue este manual paso a paso para armar el circuito. Hemos optimizado el diseño para usar la menor cantidad de componentes posibles.")
        
        st.markdown("#### 📦 Materiales Necesarios")
        st.write(f"- 1x Placa Arduino UNO y cable USB")
        st.write(f"- 1x Protoboard (Placa de pruebas)")
        st.write(f"- **{num_opciones}x** Pulsadores (Botones)")
        st.write(f"- 1x LED Verde y 1x LED Rojo")
        st.write(f"- 2x Resistencias (220Ω o 330Ω) solo para los LEDs")
        st.write(f"- Varios cables puente (Jumper wires)")
        
        st.markdown("#### ⚡ Paso 1: Alimentación Base")
        st.write("1. Conecta un cable desde el pin **GND** del Arduino a la línea azul (negativa) de tu protoboard. Esta será nuestra tierra común.")
        
        st.markdown("#### 💡 Paso 2: Conexión de los LEDs")
        st.write("1. **LED Verde:** Conecta la pata larga (ánodo) al **Pin 8** del Arduino. Conecta la pata corta (cátodo) a una resistencia, y el otro extremo de la resistencia a la línea de tierra (GND) del protoboard.")
        st.write("2. **LED Rojo:** Conecta la pata larga al **Pin 9** del Arduino. Conecta la pata corta a la otra resistencia, y de ahí a la tierra (GND).")
        
        st.markdown(f"#### 🔘 Paso 3: Conexión de los {num_opciones} Botones")
        st.info("💡 **Truco Docente:** Gracias a que nuestro código usa `INPUT_PULLUP`, **no necesitamos resistencias** para los botones. ¡El Arduino usa las suyas internas!")
        
        for i, pin in enumerate(pines_botones):
            letra = chr(65+i)
            st.write(f"- **Botón {letra}:** Conecta una patita del botón al **Pin {pin}** del Arduino. Conecta la patita contraria directamente a la línea de tierra (GND) del protoboard.")
            
        st.divider()
        st.success("✅ **¡Listo!** Conecta tu Arduino al computador, sube el código de la pestaña anterior y tu herramienta de selección múltiple cobrará vida.")
