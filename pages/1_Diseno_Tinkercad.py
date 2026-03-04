import streamlit as st
import subprocess
import os
import shutil

# Configuración de estilo
st.set_page_config(page_title="Módulo 1 | Capacitación", layout="wide")

st.title("🧊 Módulo 1: Diseño 3D Educativo")
st.markdown("**Objetivo:** Diseñar objetos 3D aplicables al currículo escolar (modelos geométricos, moléculas) y exportar archivos en formato STL listos para la manufactura.")
st.divider()

# --- LAYOUT A DOS COLUMNAS ---
col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("Configuración del Recurso")
    st.write("Ajusta los parámetros para generar tu material didáctico.")
    
    tipo_mol = st.selectbox("Estructura Molecular:", ["H2O", "CO2", "CH4"])
    
    c1, c2 = st.columns(2)
    radio = c1.slider("Radio Atómico (mm)", 5, 20, 10)
    distancia = c2.slider("Longitud de Enlace (mm)", 10, 40, 22)
    
    relieve_opcion = st.radio("Marcador de Átomos (Texto):", ["Sobre-relieve", "Bajo-relieve"], horizontal=True)
    v_relieve = 1.5 if relieve_opcion == "Sobre-relieve" else -1.5

    # Lógica de colores ilustrativa para la interfaz
    st.markdown("### Composición")
    if tipo_mol == "H2O":
        st.info("🔴 1x Oxígeno (Centro)\n⚪ 2x Hidrógeno (Lados a 104.5°)")
    elif tipo_mol == "CO2":
        st.info("⚫ 1x Carbono (Centro)\n🔴 2x Oxígeno (Lados a 180°)")
    elif tipo_mol == "CH4":
        st.info("⚫ 1x Carbono (Centro)\n⚪ 4x Hidrógeno (Geometría Tetraédrica)")

with col2:
    st.subheader("Generación de Malla 3D")
    st.write("Este motor utiliza operaciones de Geometría Constructiva equivalentes a agrupar y perforar cilindros y esferas en el entorno gráfico.")
    
    # --- CÓDIGO OPENSCAD ---
    codigo_scad = f"""
    tipo = "{tipo_mol}"; radio_atomo = {radio}; distancia_enlace = {distancia};
    talla_letra = 7; relieve = {v_relieve}; 

    module atomo(r, letra, color_p) {{
        color(color_p) difference() {{
            sphere(r = r, $fn=50);
            if (relieve < 0) {{
                translate([0, 0, r + relieve]) linear_extrude(2)
                    text(letra, size=talla_letra, halign="center", valign="center");
            }}
        }}
        if (relieve > 0) {{
            color(color_p) translate([0, 0, r]) linear_extrude(relieve)
                text(letra, size=talla_letra, halign="center", valign="center");
        }}
    }}

    if (tipo == "H2O") {{
        atomo(radio_atomo, "O", "Red");
        for(a = [0, 104.5]) rotate([0, 0, a]) {{
            translate([distancia_enlace, 0, 0]) atomo(radio_atomo*0.6, "H", "White");
            rotate([0, 90, 0]) cylinder(h=distancia_enlace, d=3, $fn=20);
        }}
    }} else if (tipo == "CO2") {{
        atomo(radio_atomo, "C", "Grey");
        for(a = [0, 180]) rotate([0, 0, a]) {{
            translate([distancia_enlace, 0, 0]) atomo(radio_atomo*0.8, "O", "Red");
            rotate([0, 90, 0]) translate([0, 2, 0]) cylinder(h=distancia_enlace, d=2);
            rotate([0, 90, 0]) translate([0, -2, 0]) cylinder(h=distancia_enlace, d=2);
        }}
    }} else if (tipo == "CH4") {{
        atomo(radio_atomo, "C", "Grey");
        direcciones = [[0,0,0], [109.5,0,0], [109.5,0,120], [109.5,0,240]];
        for(d = direcciones) rotate(d) {{
            translate([0, 0, distancia_enlace]) atomo(radio_atomo*0.6, "H", "White");
            cylinder(h=distancia_enlace, d=3, $fn=20);
        }}
    }}
    """
    
    scad_file = "temp_mol.scad"
    stl_file = f"molecula_{tipo_mol}.stl"
    
    # Detección dinámica de la ruta de OpenSCAD (Cloud vs Local)
    ruta_openscad = shutil.which("openscad") or r"C:\Program Files\OpenSCAD\openscad.exe"

    if st.button("🛠️ Compilar y Generar Archivo STL", type="primary", use_container_width=True):
        with st.spinner("Procesando geometría y uniendo primitivas..."):
            with open(scad_file, "w") as f:
                f.write(codigo_scad)
            
            try:
                subprocess.run([ruta_openscad, "-o", stl_file, scad_file], check=True)
                st.success("¡Geometría compilada con éxito!")
            except Exception as e:
                st.error("Error al compilar la geometría.")
                st.info("Si estás en la nube, asegúrate de haber configurado el archivo `packages.txt` con la dependencia `openscad`.")
                st.code(codigo_scad, language="openscad")

    # --- INTERFAZ DE DESCARGA ---
    if os.path.exists(stl_file):
        with open(stl_file, "rb") as f:
            st.download_button(
                label=f"📥 DESCARGAR {stl_file.upper()} PARA IMPRESIÓN",
                data=f,
                file_name=stl_file,
                mime="application/sla",
                use_container_width=True
            )
