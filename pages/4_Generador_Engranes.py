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

with st.expander("💡 Cinemática y Manufactura (Reflexión Pedagógica)", expanded=True):
    st.markdown("""
    Para que dos engranajes funcionen juntos, DEBEN tener exactamente el mismo módulo. 
    
    Esta herramienta te permite diseñar de dos formas:
    1. **Modo Asistido:** Ingresas cuánto quieres aumentar o reducir la velocidad, y el sistema te propone los engranajes ideales que caben en una impresora escolar (Ender 3).
    2. **Modo Manual:** Tienes control total sobre el Módulo y los Dientes.
    
    La geometría generada respeta la norma estándar para impresión 3D, incluyendo la tolerancia (Backlash) necesaria entre 0.1 y 0.3 para que los dientes no se atasquen.
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
            camera.position.set(0, 60, 100);
            
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
    components.html(html_code, height=380)

# --- INTERFAZ LÓGICA ---
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("1. Configura la Transmisión")
    
    modo_diseno = st.radio("Método de Diseño", ["Asistido (Recomendado)", "Manual"], horizontal=True)
    
    if modo_diseno == "Asistido (Recomendado)":
        st.write("Ingresa la relación deseada. Te propondremos el sistema óptimo que quepa en tu impresora.")
        target_ratio = st.number_input("Relación de Transmisión (Ej: 2.0 = El motor gira el doble de rápido que la salida)", min_value=1.0, max_value=8.0, value=2.0, step=0.1)
        
        best_error = 999
        best_z1, best_z2 = 12, 24
        
        for z1_test in range(10, 25):
            z2_test = round(z1_test * target_ratio)
            error = abs((z2_test / z1_test) - target_ratio)
            if error < best_error and z2_test <= 60:
                best_error = error
                best_z1 = z1_test
                best_z2 = z2_test
                
        m_max = 200 / (best_z2 + 2)
        m_min = max(1.0, 20 / (best_z1 + 2))
        
        if m_min > m_max:
            st.error("⚠️ La relación es tan extrema que no es posible fabricarla en una cama de 20x20cm con boquilla de 0.4mm. Intenta una relación más baja.")
            m_optimo = 1.0
        else:
            m_optimo = min(max(m_min, 2.0), m_max) 
            st.success(f"💡 **Recomendación:** Z1=**{best_z1}**, Z2=**{best_z2}**, Módulo=**{m_optimo:.1f}**")
            
        c1, c2, c3 = st.columns(3)
        modulo = c1.number_input("Módulo (m)", value=float(round(m_optimo*2)/2), step=0.5)
        z1 = c2.number_input("Motor (Z1)", value=int(best_z1), step=1)
        z2 = c3.number_input("Salida (Z2)", value=int(best_z2), step=1)

    else:
        c1, c2, c3 = st.columns(3)
        modulo = c1.number_input("Módulo (m)", min_value=1.0, max_value=8.0, value=2.0, step=0.5)
        z1 = c2.number_input("Motor (Z1)", min_value=8, max_value=80, value=12, step=1)
        z2 = c3.number_input("Salida (Z2)", min_value=8, max_value=80, value=24, step=1)

    st.write("**Manufactura y Montaje**")
    c4, c5, c6 = st.columns(3)
    espesor = c4.number_input("Grosor (mm)", min_value=3.0, value=5.0)
    eje = c5.number_input("Eje (mm)", min_value=2.0, value=5.0)
    tolerancia = c6.number_input("Backlash", min_value=0.1, max_value=0.5, value=0.25, step=0.05, help="Espacio entre caras.")
    
    relacion_real = z2 / z1
    dp1 = modulo * z1
    dp2 = modulo * z2
    de1 = dp1 + 2 * modulo
    de2 = dp2 + 2 * modulo
    distancia_centros = (dp1 + dp2) / 2.0
    
    if de1 > 200 or de2 > 200:
        st.error(f"🚨 **¡Error Dimensional!** El engranaje mayor tiene un diámetro de {max(de1, de2):.1f} mm. No cabrá en una cama de 200x200 mm.")
    elif de1 < 20 or de2 < 20:
        st.warning(f"⚠️ **Atención:** El engranaje menor mide {min(de1, de2):.1f} mm. Podría perder precisión con una boquilla de 0.4mm.")
        
    st.markdown("### Datos Críticos para el Aula")
    st.metric("🎯 Perforación en Tablero MDF (Distancia entre Ejes)", f"{distancia_centros:.1f} mm")

    # --- LÓGICA CSG CORREGIDA (UNION DE MALLAS Y BACKLASH) ---
    codigo_scad = f"""
    m = {modulo}; z1 = {z1}; z2 = {z2}; h = {espesor}; eje = {eje}; tol = {tolerancia};

    module gear(z) {{
        dp = m * z;
        de = dp + 2 * m;        
        df = dp - 2.5 * m;      
        
        w_base = 1.24 * m;
        w_punta = 0.42 * m;
        
        ang = 360 / z;
        overlap = 0.8; // Soluciona el error de "geometría non-manifold"

        difference() {{
            linear_extrude(height = h) {{
                union() {{
                    // Cuerpo base del engrane
                    circle(d = df, $fn=100); 
                    
                    for (i = [0 : z-1]) {{
                        rotate([0, 0, i * ang])
                        // El diente penetra 'overlap' mm hacia el centro para asegurar soldadura
                        polygon([
                            [df/2 - overlap, -(w_base - tol/2)],
                            [de/2,           -(w_punta - tol/2)],
                            [de/2,            (w_punta - tol/2)],
                            [df/2 - overlap,  (w_base - tol/2)]
                        ]);
                    }}
                }}
            }}
            translate([0,0,-1]) cylinder(h=h+2, d=eje, $fn=50);
        }}
    }}

    // Engranaje 1 (Motor)
    gear(z1);

    // Separación para impresión y engrane
    dist_centros = (m * z1)/2 + (m * z2)/2;
    distancia_impresion = dist_centros + (0 * tol); 

    translate([distancia_impresion, 0, 0]) 
        rotate([0, 0, 180 + (180/z2)]) 
        gear(z2);
    """
    
    scad_file = "temp_tren.scad"
    stl_file = f"tren_engranajes_z{z1}_z{z2}.stl"
    ruta_openscad = shutil.which("openscad") or r"C:\Program Files\OpenSCAD\openscad.exe"

    st.write("") 
    if st.button("✨ Generar Set de Transmisión", type="primary", use_container_width=True):
        with st.spinner("Calculando geometría involutiva y fabricando par cinemático..."):
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
