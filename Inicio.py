import streamlit as st

st.set_page_config(
    page_title="Talleres MakerBox | UTalca",
    page_icon="⚙️",
    layout="wide"
)

st.title("Talleres de Innovación y Manufactura Digital")
st.subheader("Facultad de Ingeniería - MakerBox")

st.markdown("""
Les damos la bienvenida al ciclo de talleres de diseño aplicado. 

El objetivo de este ciclo es transitar desde el concepto teórico hasta la simulación y validación digital rápida, preparándolos para los desafíos de la Industria 4.0. Nuestro hito final será el diseño, simulación y manufactura de un sistema de propulsión eficiente (hélice carenada).

### 📅 Hoja de Ruta del Ciclo
En el menú lateral se irán habilitando las herramientas interactivas para cada sesión de 90 minutos:

* **Taller 1: Dualidad Digital** (Modelado CSG vs. B-Rep).
* **Taller 2: Bridas Paramétricas y Ensambles** (Diseño auto-ajustable).
* **Taller 3: Simulación FEA** (Validación estructural y Factor de Seguridad).
* **Taller 4: Aerodinámica** (De perfiles NACA a CFD).
* **Taller 5: Hidráulica y Efecto Venturi** (Validación del Principio de Bernoulli).

👈 **Seleccionen "Taller Dualidad" en el menú de la izquierda para comenzar nuestra primera sesión.**

---
*Plataforma de apoyo docente desarrollada por la académica Cris.*
""")
