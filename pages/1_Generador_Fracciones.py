import streamlit as st
import streamlit.components.v1 as components
import subprocess
import os
import shutil
import base64

# Configuración de estilo
st.set_page_config(page_title="Set de Fracciones | Capacitación", layout="wide")

st.title("🍕 Generador de Sets de Fracciones 3D")
st.markdown("**Objetivo:** Diseñar sets completos de fracciones (piezas + bandeja contenedora) listos para manufactura interactiva en el aula.")
st.divider()

with st.expander("💡 De la Pieza al Set Completo (Reflexión Pedagógica)", expanded=True):
    st.markdown("""
    Durante nuestra sesión, modelamos una pieza suelta en Tinkercad. Ahora, esta herramienta automatiza la creación del **Set Completo**. 
    
    Al seleccionar una fracción (ej. 1/4), el motor matemático generará automáticamente las **4 piezas** necesarias para formar el entero, más una **bandeja contenedora**. La bandeja tiene una tolerancia exacta de 0.4 mm para que las piezas encajen como un rompecabezas, permitiendo a los estudiantes interactuar de forma tangible con el concepto de unidad.
    """)

# --- FUNCIÓN DEL VISOR 3D (THREE.JS) ---
def mostrar_visor_3d(ruta_stl):
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
            camera.position.set(0, 80, 100);
            
            var renderer = new THREE.WebGLRenderer({{antialias: true, alpha: true}});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.getElementById('viewer').appendChild(renderer.domElement);
            
            var controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.autoRotate = true; 
            controls.autoRotateSpeed = 2.0;
            
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

# --- INTERFAZ LÓGICA ---
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("1. Configura tu Set de Fracciones")
    
    fraccion_seleccionada = st.selectbox(
        "Fracción a generar:", 
        ["1/2", "1/3", "1/4", "1/5", "1/6", "1/8"],
        index=2
    )
    
    # Extraer el denominador del texto (ej. "1/4" -> 4)
    denominador = int(fraccion_seleccionada.split('/')[1])
    
    # Reducimos un poco el radio máximo sugerido para que el Set completo quepa en impresoras estándar (200x200mm)
    radio = st.slider("Radio del círculo completo (mm)", 20.0, 45.0, 30.0, step=1.0)
    espesor = st.slider("Grosor de las piezas (mm)", 2.0, 5.0, 3.0, step=0.5)
    
    # Lógica CSG Automatizada (Bandeja + Piezas)
    codigo_scad = f"""
    radio = {radio}; 
    espesor = {espesor}; 
    den = {denominador}; 
    tol = 0.4; // Tolerancia para que las piezas entren suaves en la bandeja
    texto_fraccion = "1/{denominador}";
    ang = 360 / den;

    module ficha() {{
        difference() {{
            rotate_extrude(angle=ang, $fn=100) square([radio, espesor]);
            
            // Posicionamiento del texto en la bisectriz de la pieza
            rotate([0, 0, ang / 2])
                translate([radio * 0.55, 0, espesor - 1]) 
                linear_extrude(2)
                text(texto_fraccion, size=radio * 0.25, halign="center", valign="center", font="Arial:style=Bold");
        }}
    }}

    // ==========================================
    // 1. BANDEJA CONTENEDORA (A la Izquierda)
    // ==========================================
    translate([-(radio + 10), 0, 0]) {{
        difference() {{
            // Borde exterior (Radio de piezas + Tolerancia + 3mm de pared gruesa)
            cylinder(h=espesor + 2, r=radio + tol + 3, $fn=100);
            
            // Hueco interior para que encajen las piezas (Profundidad = espesor + 1mm para cogerlas fácil)
            translate([0, 0, 2]) 
                cylinder(h=espesor + 1, r=radio + tol, $fn=100);
        }}
    }}

    // ==========================================
    // 2. PIEZAS DEL ROMPECABEZAS (A la Derecha)
    // ==========================================
    translate([radio + 10, 0, 0]) {{
        for (i = [0 : den - 1]) {{
            rotate([0, 0, i * ang])
            // Separación radial (tipo pizza explotada) de 2mm para que se impriman sueltas
            translate([cos(ang/2)*2, sin(ang/2)*2, 0])
            ficha();
        }}
    }}
    """
    
    scad_file = "temp_fraccion.scad"
    stl_file = f"set_fraccion_1_de_{denominador}.stl"
    ruta_openscad = shutil.which("openscad") or r"C:\Program Files\OpenSCAD\openscad.exe"

    st.write("") 
    if st.button("✨ Generar Set Completo", type="primary", use_container_width=True):
        with st.spinner(f"Modelando bandeja y {denominador} piezas de {fraccion_seleccionada}..."):
            with open(scad_file, "w") as f:
                f.write(codigo_scad)
            try:
                subprocess.run([ruta_openscad, "-o", stl_file, scad_file], check=True)
            except Exception as e:
                st.error("Error al generar el modelo. Verifica que OpenSCAD esté configurado en el servidor.")

with col2:
    st.subheader("2. Previsualización y Descarga")
    
    if os.path.exists(stl_file):
        mostrar_visor_3d(stl_file)
        
        with open(stl_file, "rb") as f:
            st.download_button(
                label=f"📥 DESCARGAR SET DE {denominador} PIEZAS Y BANDEJA (.STL)",
                data=f,
                file_name=stl_file,
                mime="application/sla",
                use_container_width=True
            )
    else:
        st.info("👈 Selecciona la fracción a la izquierda y haz clic en el botón mágico para visualizar tu Set Didáctico.")
