import streamlit as st
import streamlit.components.v1 as components
import subprocess
import os
import shutil
import base64

# Configuración de estilo
st.set_page_config(page_title="Fracciones 3D | Capacitación", layout="wide")

st.title("🍕 Generador Paramétrico de Fracciones 3D")
st.markdown("**Objetivo:** Diseñar material didáctico tangible para la enseñanza de matemáticas, controlando la geometría mediante proporciones angulares.")
st.divider()

# --- CONEXIÓN PEDAGÓGICA (TINKERCAD VS PARAMÉTRICO) ---
with st.expander("💡 De lo Manual a lo Paramétrico (Ver reflexión pedagógica)", expanded=True):
    st.markdown("""
    Durante nuestra sesión sincrónica, aprendimos a modelar el concepto de fracciones **manualmente usando Tinkercad** (puedes revisar el [ejemplo de clase aquí](https://www.tinkercad.com/things/jd2LLO30qJE-fracciones)). 
    
    Ese ejercicio es vital para que tus estudiantes desarrollen visión espacial. Sin embargo, como docentes, nuestro tiempo es limitado. Si necesitas imprimir un set completo de 50 fichas para todo tu curso escolar, modelar cada cuña manualmente no es eficiente. 
    
    **¡Utiliza esta herramienta como tu Biblioteca de Recursos!** Aquí el código matemático hace el trabajo pesado por ti. Solo elige la fracción y descarga el modelo listo para la impresora.
    """)

# --- FUNCIÓN DEL VISOR 3D (THREE.JS) ---
def mostrar_visor_3d(ruta_stl):
    """Inyecta un visor Three.js interactivo leyendo el archivo STL en base64."""
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
            
            // Material Magenta MakerBox para las fracciones
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
    components.html(html_code, height=400)


# --- LAYOUT A DOS COLUMNAS ---
col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("Parámetros de la Ficha")
    
    c1, c2 = st.columns(2)
    numerador = c1.number_input("Numerador", min_value=1, max_value=12, value=1)
    denominador = c2.selectbox("Denominador", [2, 3, 4, 5, 6, 8, 10, 12], index=1) 
    
    radio = st.slider("Radio del cilindro completo (mm)", 20.0, 60.0, 30.0, step=1.0)
    espesor = st.slider("Espesor de la ficha (mm)", 2.0, 5.0, 3.0, step=0.5)
    
    if numerador > denominador:
        st.warning("⚠️ Fracción impropia. El numerador es mayor al denominador. Se modelará como una fracción de un círculo completo (modulando a 360°).")
        
    angulo_sector = (numerador / denominador) * 360.0
    
    st.markdown("### Análisis Geométrico")
    st.latex(r"\theta = \left( \frac{" + str(numerador) + "}{" + str(denominador) + r"} \right) \times 360^\circ = " + f"{angulo_sector:.1f}^\circ")

with col2:
    st.subheader("Generador CSG (OpenSCAD)")
    
    codigo_scad = f"""
    radio = {radio};
    espesor = {espesor};
    num = {numerador};
    den = {denominador};
    angulo = {angulo_sector};
    texto_fraccion = str(num, "/", den);

    angulo_real = angulo >= 360 ? 359.99 : angulo;

    difference() {{
        rotate_extrude(angle=angulo_real, $fn=100)
            square([radio, espesor]);
        
        rotate([0, 0, angulo_real / 2])
            translate([radio * 0.55, 0, espesor - 1]) 
            linear_extrude(2)
            text(texto_fraccion, size=radio * 0.25, halign="center", valign="center", font="Arial:style=Bold");
    }}
    """
    
    scad_file = "temp_fraccion.scad"
    stl_file = f"fraccion_{numerador}_{denominador}.stl"
    
    ruta_openscad = shutil.which("openscad") or r"C:\Program Files\OpenSCAD\openscad.exe"

    if st.button("🛠️ Compilar Ficha de Fracción", type="primary", use_container_width=True):
        with st.spinner("Calculando geometría y generando bajo-relieve..."):
            with open(scad_file, "w") as f:
                f.write(codigo_scad)
            
            try:
                subprocess.run([ruta_openscad, "-o", stl_file, scad_file], check=True)
                st.success(f"¡Ficha {numerador}/{denominador} compilada con éxito!")
            except Exception as e:
                st.error("Error al compilar la geometría.")
                st.info("Asegúrate de que el archivo `packages.txt` contenga `openscad` si estás en la nube.")

# --- ÁREA DE VISUALIZACIÓN Y DESCARGA ---
if os.path.exists(stl_file):
    st.divider()
    col3, col4 = st.columns([2, 1])
    
    with col3:
        st.subheader("Previsualización 3D")
        mostrar_visor_3d(stl_file)
        
    with col4:
        st.subheader("Manufactura")
        st.write("Tu ficha didáctica está lista para imprimir.")
        st.write(f"- **Fracción:** {numerador}/{denominador}")
        st.write(f"- **Ángulo de barrido:** {angulo_sector:.1f}°")
        st.write(f"- **Diámetro total:** {radio * 2} mm")
        
        with open(stl_file, "rb") as f:
            st.download_button(
                label=f"📥 DESCARGAR FICHA {numerador}-{denominador}.STL",
                data=f,
                file_name=stl_file,
                mime="application/sla",
                use_container_width=True,
                type="primary"
            )
