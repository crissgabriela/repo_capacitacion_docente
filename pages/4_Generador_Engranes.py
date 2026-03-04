# Lógica CSG matemáticamente exacta con soldadura profunda de raíz
    codigo_scad = f"""
    m = {modulo}; z1 = {z1}; z2 = {z2}; h = {espesor}; eje = {eje}; tol = {tolerancia};

    module gear(z) {{
        dp = m * z;
        de = dp + 2 * m;        
        df = dp - 2.5 * m;      
        
        w_base = 1.24 * m;
        w_punta = 0.42 * m;
        
        ang = 360 / z;

        difference() {{
            linear_extrude(height = h) {{
                union() {{
                    // Cuerpo base del engrane
                    circle(d = df, $fn=100); 
                    
                    for (i = [0 : z-1]) {{
                        rotate([0, 0, i * ang])
                        // Hundimos y ensanchamos la raíz del diente muy por 
                        // dentro del círculo para una fusión booleana perfecta
                        polygon([
                            [df/2 - 2*m, -(w_base + m)],
                            [de/2,       -(w_punta - tol/2)],
                            [de/2,        (w_punta - tol/2)],
                            [df/2 - 2*m,  (w_base + m)]
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
    distancia_impresion = dist_centros + (2 * tol); 

    translate([distancia_impresion, 0, 0]) 
        rotate([0, 0, 180 + (180/z2)]) 
        gear(z2);
    """
