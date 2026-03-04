import streamlit as st
import streamlit.components.v1 as components
import subprocess
import os
import shutil
import base64

# Configuración de estilo
st.set_page_config(page_title="Tren de Engranajes | Capacitación", layout="wide")

st.title("⚙️ Generador de Trenes de Transmisión")
st.markdown("**Objetivo:** Diseñar pares de engranajes rectos para enseñar relaciones de transmisión, torque y velocidad, listos para montar en tableros didácticos.")
st.divider()

with st.expander("💡 Cinemática en el Tablero MDF (Reflexión Pedagógica)", expanded=True):
    st.markdown("""
    Un excelente proyecto de aula es pedir a los estudiantes que perforen un tablero de MDF para trasladar el movimiento de un punto A a un punto B. 
    
    Para que el sistema fluya, esta herramienta calcula la **Distancia entre Centros Exacta**. Si los estudiantes hacen los agujeros en el MDF a esa distancia precisa, los engranajes encajarán perfectamente gracias a la **tolerancia (Backlash)**. Al previsualizar el modelo, verás los engranajes alineados exactamente como quedarán en la vida real.
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
            camera.position.set(0, 60, 90);
            
            var renderer = new THREE.WebGLRenderer({{antialias: true, alpha: true}});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.getElementById('viewer').appendChild(renderer.domElement);
            
            var controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.autoRotate = true; 
            controls.autoRotateSpeed = 1.0;
            
            scene.add(new THREE.AmbientLight(0xffffff, 0.7));
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
            
            // Material Morado MakerBox
            var material = new THREE.MeshStandardMaterial({{color: 0x46247a, roughness: 0.5, metalness: 0.2}});
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
    st.subheader("1. Configura la Transmisión")
    
    st.write("**Engranajes** (Mismo módulo para que encajen)")
    c1, c2, c3 = st.columns(3)
    modulo = c1.number_input("Módulo (m)", min_value=1.0, max_value=5.0, value=2.0, step=0.5)
    z1 = c2.number_input("Dientes Motor (Z1)", min_value=8, max_value=60, value=12, step=1)
    z2 = c3.number_input("Dientes Salida (Z2)", min_value=8, max_value=60, value=24, step=1)
    
    st.write("**Manufactura y Montaje**")
    c4, c5, c6 = st.columns(3)
    espesor = c4.number_input("Grosor (mm)", min_value=3.0, value=5.0)
    eje = c5.number_input("Eje (mm)", min_value=2.0, value=5.0)
    tolerancia = c6.number_input("Tolerancia", min_value=0.1, max_value=0.5, value=0.25, step=0.05, help="Espacio libre entre dientes. 0.25mm es ideal para impresión 3D.")
    
    # Cálculos cinemáticos críticos
    relacion = z2 / z1
    dp1 = modulo * z1
    dp2 = modulo * z2
    distancia_centros = (dp1 + dp2) / 2.0
    
    st.markdown("### Datos Críticos para el Aula")
    
    if relacion > 1:
        st.info(f"🐢 **Reductor de Velocidad:** El sistema gira {relacion:.1f} veces más lento, pero tiene **{relacion:.1f}x más fuerza (Torque)**.")
    elif relacion < 1:
        st.error(f"🐇 **Multiplicador de Velocidad:** El sistema gira {1/relacion:.1f} veces más rápido, pero pierde fuerza.")
    else:
        st.success("⚖️ **Transmisión 1:1:** Misma velocidad y fuerza. Útil solo para trasladar el movimiento espacialmente.")
        
    st.metric("🎯 Perforación en Tablero MDF (Distancia entre Ejes)", f"{distancia_centros:.1f} mm")

    # Lógica CSG para DOS engranajes alineados visualmente
    codigo_scad = f"""
    m = {modulo}; z1 = {z1}; z2 = {z2}; h = {espesor}; eje = {eje}; tol = {tolerancia};

    module gear(z) {{
        dp = m * z;
        de = dp + 2 * m;
        df = dp - 2.5 * m;
        ang = 360 / z;

        difference() {{
            linear_extrude(height = h) {{
                union() {{
                    circle(d = df + m, $fn=100); 
                    for (i = [0 : z-1]) {{
                        rotate([0, 0, i * ang])
                        // Reducimos el ancho del diente para generar el Backlash
                        polygon([
                            [(df)/2, -(m*1.0 - tol/2)],
                            [de/2,   -(m*0.35 - tol/2)],
                            [de/2,    (m*0.35 - tol/2)],
                            [(df)/2,  (m*1.0 - tol/2)]
                        ]);
                    }}
                }}
            }}
            translate([0,0,-1]) cylinder(h=h+2, d=eje, $fn=50);
        }}
    }}

    // Engranaje 1 (Motor) - Generado en el origen
    gear(z1);

    // =================================================================
    // ---> ZONA DE AJUSTE DE IMPRESIÓN Y ENGRANE <---
    // =================================================================
    dist_centros = (m * z1)/2 + (m * z2)/2;
    
    // MODIFICA ESTE VALOR: Separación en el STL = Centros + (2 * Tolerancia)
    distancia_impresion = dist_centros + (2 * tol); 

    // Alineación geométrica: Rotamos (180 + 180/z2) para asegurar que un 
    // "hueco" apunte hacia el diente del Engranaje 1, evitando colisiones
    translate([distancia_impresion, 0, 0]) 
        rotate([0, 0, 180 + (180/z2)]) 
        gear(z2);
    // =================================================================
    """
    
    scad_file = "temp_tren.scad"
    stl_file = f"tren_engranajes_z{z1}_z{z2}.stl"
    ruta_openscad = shutil.which("openscad") or r"C:\Program Files\OpenSCAD\openscad.exe"

    st.write("") 
    if st.button("✨ Generar Set de Transmisión", type="primary", use_container_width=True):
        with st.spinner("Calculando tolerancias y alineando par cinemático..."):
            with open(scad_file, "w") as f:
                f.write(codigo_scad)
            try:
                subprocess.run([ruta_openscad, "-o", stl_file, scad_file], check=True)
            except Exception as e:
                st.error("Error al generar el modelo.")

with col2:
    st.subheader("2. Previsualización y Descarga")
    
    if os.path.exists(stl_file):
        mostrar_visor_3d(stl_file)
        
        with open(stl_file, "rb") as f:
            st.download_button(
                label=f"📥 DESCARGAR SET DE ENGRANAJES (.STL)",
                data=f,
                file_name=stl_file,
                mime="application/sla",
                use_container_width=True
            )
    else:
        st.info("👈 Configura la relación de transmisión a la izquierda y haz clic en el botón para fabricar tu set.")
