import streamlit as st
import streamlit.components.v1 as components
import subprocess
import os
import shutil
import base64

# Configuración de estilo
st.set_page_config(page_title="Fracciones 3D | Capacitación", layout="wide")

st.title("🍕 Generador de Fracciones 3D")
st.markdown("**Objetivo:** Diseñar material didáctico tangible para la enseñanza de matemáticas de forma rápida y sin necesidad de conocimientos previos en diseño.")
st.divider()

with st.expander("💡 De lo Manual a lo Automático (Reflexión Pedagógica)", expanded=True):
    st.markdown("""
    Durante nuestra sesión sincrónica, aprendimos a modelar el concepto de fracciones **manualmente usando Tinkercad** (puedes revisar el [ejemplo de clase aquí](https://www.tinkercad.com/things/jd2LLO30qJE-fracciones)). 
    
    Ese ejercicio es vital para desarrollar tu visión espacial y la de tus estudiantes. Sin embargo, para imprimir un set completo para tu colegio, modelar cada pieza manualmente no es eficiente. **¡Utiliza esta herramienta como tu Biblioteca de Recursos!** Solo elige la fracción y descarga el modelo listo para tu impresora 3D.
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
            camera.position.set(0, 50, 80);
            
            var renderer = new THREE.WebGLRenderer({{antialias: true, alpha: true}});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.getElementById('viewer').appendChild(renderer.domElement);
            
            var controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.autoRotate = true; 
            controls.autoRotateSpeed = 3.0;
            
            scene.add(new THREE.AmbientLight(0xffffff, 0.6));
            var dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
            dirLight.position.set(20, 50, 20);
            scene.add(dirLight);
            
            var base64 = "{datos_b64}";
            var binary = atob(base64);
            var bytes = new Uint8Array(binary.length);
            for (var i = 0; i < binary.length; i++) {{
                bytes[i] = binary.charCodeAt(i);
            }}
            
            var loader = new THREE.STLLoader();
            var geometry = loader.parse(bytes.buffer);
            
            // Material Magenta MakerBox
            var material = new THREE.MeshStandardMaterial({{color: 0xc72979, roughness: 0.3, metalness: 0.1}});
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
    st.subheader("1. Configura tu Ficha")
    
    c1, c2 = st.columns(2)
    numerador = c1.number_input("Numerador", min_value=1, max_value=12, value=1)
    denominador = c2.selectbox("Denominador", [2, 3, 4, 5, 6, 8, 10, 12], index=1)
    
    radio = st.slider("Radio total de la ficha (mm)", 20.0, 60.0, 30.0, step=1.0)
    espesor = st.slider("Grosor de la ficha (mm)", 2.0, 5.0, 3.0, step=0.5)
    
    if numerador > denominador:
        st.warning("⚠️ El numerador es mayor al denominador. Se generará como una cuña proporcional al círculo completo.")
        
    angulo_sector = (numerador / denominador) * 360.0
    
    # Lógica "invisible" de OpenSCAD
    codigo_scad = f"""
    radio = {radio}; espesor = {espesor}; num = {numerador}; den = {denominador}; angulo = {angulo_sector};
    texto_fraccion = str(num, "/", den);
    angulo_real = angulo >= 360 ? 359.99 : angulo;
    difference() {{
        rotate_extrude(angle=angulo_real, $fn=100) square([radio, espesor]);
        rotate([0, 0, angulo_real / 2])
            translate([radio * 0.55, 0, espesor - 1]) 
            linear_extrude(2)
            text(texto_fraccion, size=radio * 0.25, halign="center", valign="center", font="Arial:style=Bold");
    }}
    """
    
    scad_file = "temp_fraccion.scad"
    stl_file = f"fraccion_{numerador}_{denominador}.stl"
    ruta_openscad = shutil.which("openscad") or r"C:\Program Files\OpenSCAD\openscad.exe"

    st.write("") # Espaciador
    if st.button("✨ Visualizar y Preparar Ficha", type="primary", use_container_width=True):
        with st.spinner("Creando modelo 3D..."):
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
                label=f"📥 DESCARGAR MODELO PARA IMPRIMIR (.STL)",
                data=f,
                file_name=stl_file,
                mime="application/sla",
                use_container_width=True
            )
    else:
        st.info("👈 Ajusta los parámetros a la izquierda y haz clic en el botón mágico para ver tu ficha didáctica aquí.")
