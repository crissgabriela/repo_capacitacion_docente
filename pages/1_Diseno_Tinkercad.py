import streamlit as st
import streamlit.components.v1 as components
import subprocess
import os
import shutil
import base64

# Configuración de estilo
st.set_page_config(page_title="Módulo 1 | Capacitación", layout="wide")

st.title("🧊 Módulo 1: Diseño 3D Educativo")
st.markdown("**Objetivo:** Diseñar objetos 3D aplicables al currículo escolar (modelos geométricos, moléculas) y exportar archivos en formato STL listos para la manufactura.")
st.divider()

# --- FUNCIÓN DEL VISOR 3D (THREE.JS) ---
def mostrar_visor_3d(ruta_stl):
    """Inyecta un visor Three.js interactivo leyendo el archivo STL en base64."""
    with open(ruta_stl, "rb") as f:
        datos_b64 = base64.b64encode(f.read()).decode("utf-8")
        
    # Código HTML/JS incrustado para renderizar el STL
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/STLLoader.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    </head>
    <body style="margin: 0; overflow: hidden; background-color: #f8f9fa; border-radius: 10px; border: 1px solid #e2e8f0;">
        <div id="viewer" style="width: 100vw; height: 100vh;"></div>
        <script>
            var scene = new THREE.Scene();
            var camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(60, 60, 60);
            
            var renderer = new THREE.WebGLRenderer({{antialias: true, alpha: true}});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.getElementById('viewer').appendChild(renderer.domElement);
            
            var controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.autoRotate = true; // Rotación automática activada
            controls.autoRotateSpeed = 2.0;
            
            // Iluminación
            scene.add(new THREE.AmbientLight(0xffffff, 0.7));
            var dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
            dirLight.position.set(50, 50, 50);
            scene.add(dirLight);
            
            // Decodificar Base64
            var base64 = "{datos_b64}";
            var binary = atob(base64);
            var bytes = new Uint8Array(binary.length);
            for (var i = 0; i < binary.length; i++) {{
                bytes[i] = binary.charCodeAt(i);
            }}
            
            var loader = new THREE.STLLoader();
            var geometry = loader.parse(bytes.buffer);
            
            // Material usando el Cian de MakerBox
            var material = new THREE.MeshStandardMaterial({{color: 0x00aeef, roughness: 0.4, metalness: 0.1}});
            var mesh = new THREE.Mesh(geometry, material);
            
            // Centrar el modelo en la cámara
            geometry.computeBoundingBox();
            var center = new THREE.Vector3();
            geometry.boundingBox.getCenter(center);
            mesh.position.sub(center);
            
            scene.add(mesh);
            
            function animate() {{
                requestAnimationFrame(animate);
                controls.update();
                renderer.render(scene, camera);
            }}
            animate();
            
            window.addEventListener('resize', function() {{
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            }});
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=450)


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
    st.subheader("Generador CSG (OpenSCAD)")
    st.write("El código de Geometría Constructiva de Sólidos (CSG) se recalcula en tiempo real.")
    
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
    
    # Detección dinámica de la ruta de OpenSCAD (Nube vs Local)
    ruta_openscad = shutil.which("openscad") or r"C:\Program Files\OpenSCAD\openscad.exe"

    if st.button("🛠️ Compilar y Generar Malla 3D", type="primary", use_container_width=True):
        with st.spinner("Procesando geometría y uniendo primitivas..."):
            with open(scad_file, "w") as f:
                f.write(codigo_scad)
            
            try:
                subprocess.run([ruta_openscad, "-o", stl_file, scad_file], check=True)
                st.success("¡Geometría compilada con éxito!")
            except Exception as e:
                st.error("Error al compilar la geometría.")
                st.info("Asegúrate de que el archivo `packages.txt` contenga `openscad` si estás en la nube.")

# --- ÁREA DE VISUALIZACIÓN Y DESCARGA ---
if os.path.exists(stl_file):
    st.divider()
    col3, col4 = st.columns([2, 1])
    
    with col3:
        st.subheader(f"Previsualización 3D: {tipo_mol}")
        mostrar_visor_3d(stl_file)
        st.caption("Puedes arrastrar el ratón para rotar el modelo y usar la rueda para hacer zoom.")
        
    with col4:
        st.subheader("Manufactura")
        st.write("Tu modelo ha sido exportado en formato **.STL** (Standard Triangle Language) y está listo para ser laminado (Slicing).")
        st.write(f"- **Tipo:** {tipo_mol}")
        st.write(f"- **Distancia de enlaces:** {distancia} mm")
        st.write("- **Geometría:** Optimizada sin soportes adicionales requeridos.")
        
        with open(stl_file, "rb") as f:
            st.download_button(
                label="📥 DESCARGAR ARCHIVO STL",
                data=f,
                file_name=stl_file,
                mime="application/sla",
                use_container_width=True,
                type="primary"
            )
