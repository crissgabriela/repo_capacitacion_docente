import streamlit as st
import streamlit.components.v1 as components
import subprocess
import os
import shutil
import base64

# Configuración de estilo
st.set_page_config(page_title="Moléculas 3D | Capacitación", layout="wide")

st.title("🧊 Generador de Moléculas 3D")
st.markdown("**Objetivo:** Diseñar modelos moleculares tridimensionales para la enseñanza de ciencias, listos para la manufactura aditiva sin necesidad de conocimientos previos en software CAD.")
st.divider()

# --- CONEXIÓN PEDAGÓGICA ---
with st.expander("💡 De lo Manual a lo Automático (Reflexión Pedagógica)", expanded=True):
    st.markdown("""
    En nuestra primera sesión virtual, ingresamos a **Tinkercad** y utilizamos formas primitivas (esferas para los átomos y cilindros para los enlaces) para construir manualmente una molécula de agua. 
    
    Ese proceso te permitió entender la lógica del modelado 3D en el espacio. Sin embargo, si necesitas imprimir un set de 20 moléculas de Metano (CH4) para que tus estudiantes entiendan la geometría tetraédrica, hacerlo a mano tomaría demasiado tiempo. 
    
    **¡Usa esta herramienta como tu asistente de diseño!** Configura los parámetros físicos, visualiza el resultado y descarga el archivo STL listo para llevar al software de laminado.
    """)

# --- FUNCIÓN DEL VISOR 3D (THREE.JS) ---
def mostrar_visor_3d(ruta_stl):
    """Inyecta un visor interactivo ocultando la complejidad del código."""
    with open(ruta_stl, "rb") as f:
        datos_b64 = base64.b64encode(f.read()).decode("utf-8")
        
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
            controls.autoRotate = true; 
            controls.autoRotateSpeed = 2.0;
            
            scene.add(new THREE.AmbientLight(0xffffff, 0.7));
            var dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
            dirLight.position.set(50, 50, 50);
            scene.add(dirLight);
            
            var base64 = "{datos_b64}";
            var binary = atob(base64);
            var bytes = new Uint8Array(binary.length);
            for (var i = 0; i < binary.length; i++) {{
                bytes[i] = binary.charCodeAt(i);
            }}
            
            var loader = new THREE.STLLoader();
            var geometry = loader.parse(bytes.buffer);
            
            // Material Cian MakerBox para las moléculas
            var material = new THREE.MeshStandardMaterial({{color: 0x00aeef, roughness: 0.4, metalness: 0.1}});
            var mesh = new THREE.Mesh(geometry, material);
            
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
    components.html(html_code, height=350)

# --- INTERFAZ LIMPIA PARA USUARIOS SIN CAD ---
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("1. Configura tu Molécula")
    
    tipo_mol = st.selectbox("Estructura Molecular:", ["H2O", "CO2", "CH4"])
    
    c1, c2 = st.columns(2)
    radio = c1.slider("Radio Atómico (mm)", 5, 20, 10)
    distancia = c2.slider("Longitud Enlace (mm)", 10, 40, 22)
    
    relieve_opcion = st.radio("Marcador de Átomos (Texto):", ["Sobre-relieve", "Bajo-relieve"], horizontal=True)
    v_relieve = 1.5 if relieve_opcion == "Sobre-relieve" else -1.5

    st.markdown("### Composición")
    if tipo_mol == "H2O":
        st.info("🔴 1x Oxígeno (Centro)\n⚪ 2x Hidrógeno (Lados a 104.5°)")
    elif tipo_mol == "CO2":
        st.info("⚫ 1x Carbono (Centro)\n🔴 2x Oxígeno (Lados a 180°)")
    elif tipo_mol == "CH4":
        st.info("⚫ 1x Carbono (Centro)\n⚪ 4x Hidrógeno (Geometría Tetraédrica a 109.5°)")

    # Lógica "invisible" de OpenSCAD
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
    ruta_openscad = shutil.which("openscad") or r"C:\Program Files\OpenSCAD\openscad.exe"

    st.write("") # Espaciador
    if st.button("✨ Visualizar y Preparar Molécula", type="primary", use_container_width=True):
        with st.spinner("Ensamblando estructura molecular..."):
            with open(scad_file, "w") as f:
                f.write(codigo_scad)
            try:
                subprocess.run([ruta_openscad, "-o", stl_file, scad_file], check=True)
            except Exception as e:
                st.error("Error al generar el modelo. Si estás en la nube, verifica el archivo packages.txt.")

with col2:
    st.subheader("2. Previsualización y Descarga")
    
    if os.path.exists(stl_file):
        mostrar_visor_3d(stl_file)
        
        with open(stl_file, "rb") as f:
            st.download_button(
                label=f"📥 DESCARGAR MODELO {tipo_mol} (.STL)",
                data=f,
                file_name=stl_file,
                mime="application/sla",
                use_container_width=True
            )
    else:
        st.info("👈 Ajusta los parámetros a la izquierda y haz clic en el botón mágico para ver tu molécula aquí.")
