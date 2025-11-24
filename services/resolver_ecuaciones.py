import re
from sympy import symbols, sympify, diff, integrate, simplify


def limpiar_expresion(expr):
    """Limpia y prepara la expresión escrita por el usuario."""
    # asegurar string
    expr = str(expr)

    # Normalizar potencias: ^ -> **
    expr = expr.replace("^", "**")

    # Eliminar dx y dy (p. ej. cuando el usuario copia M(x,y)dx)
    expr = expr.replace("dx", "").replace("dy", "")

    # Eliminar espacios redundantes
    expr = expr.replace(" ", "")

    # Lista de funciones de sympy a proteger (puedes ampliar)
    funciones = ['sin', 'cos', 'tan', 'asin', 'acos', 'atan',
                 'sinh', 'cosh', 'tanh', 'exp', 'log', 'sqrt', 'Abs']

    # Proteger funciones: reemplazar 'sin(' por '__fn_sin__(' para no romperlas al insertar '*'
    placeholders = {}
    for fn in funciones:
        pattern = r'\b' + fn + r'(?=\()'   # función seguida de '('
        placeholder = f'__fn_{fn}__'
        # usar sub para reemplazar solo cuando va seguido de '('
        expr, n = re.subn(pattern, placeholder, expr)
        if n:
            placeholders[placeholder] = fn

    # Ahora insertar multiplicaciones donde hacen falta
    # 1) número seguido de letra o '('   ->  2x -> 2*x   ,  2(x+y) -> 2*(x+y)
    expr = re.sub(r'(?<!\*)(?<!\*\*)(\d+)(?=[A-Za-z(])', r'\1*', expr)

    # 2) letra o dígito o ')' seguida de '(' -> x(y) -> x*(y)   ;  ) (  -> )*(  ;  2( -> 2*(
    expr = re.sub(r'([A-Za-z0-9\)])(?=\()', r'\1*', expr)

    # 3) 
    #expr = re.sub(r'(?<!\*)([A-Za-z])(?=\d(?!\*))', r'\1*', expr)

    # 4) letra seguida de letra -> xy -> x*y
    #    Aplicar REPETIDAMENTE hasta que no queden letras juntas
    while re.search(r'([A-Za-z])([A-Za-z])', expr):
        expr = re.sub(r'([A-Za-z])([A-Za-z])', r'\1*\2', expr)

    # 5) Reducir dobles '*' si se produjeron (por seguridad)
    expr = re.sub(r'\*+', '*', expr)

    # Restaurar placeholders de funciones (volver a 'sin', 'cos', etc.)
    for placeholder, fn in placeholders.items():
        expr = expr.replace(placeholder, fn)

    # Evitar errores triviales: si queda algo como '+*' o '*+' limpialo
    expr = expr.replace('+*', '+').replace('*+', '+')
    expr = expr.replace('-*', '-').replace('*-', '-')

    # Retornar la expresión limpia
    return expr


def resolver_ecuacion_exacta(ecuacion):
    """
    Resuelve ecuación exacta M(x,y)dx + N(x,y)dy = 0
    """
    x, y = symbols('x y')
    
    # Limpiar expresiones del usuario
    M_raw = limpiar_expresion(ecuacion.M)
    N_raw = limpiar_expresion(ecuacion.N)

    # 🔍 DEBUG: Imprime qué se está enviando a SymPy
    print(f"DEBUG - Entrada original M: '{ecuacion.M}'")
    print(f"DEBUG - M limpia: '{M_raw}'")
    print(f"DEBUG - Entrada original N: '{ecuacion.N}'")
    print(f"DEBUG - N limpia: '{N_raw}'")

    try:
        M = sympify(M_raw)
        N = sympify(N_raw)
        
        # 🔍 DEBUG: Imprime las expresiones interpretadas
        print(f"DEBUG - M parseada: {M}")
        print(f"DEBUG - N parseada: {N}")
        
    except Exception as e:
        return {
            'error': True,
            'mensaje': f"Error al interpretar las expresiones: {str(e)}"
        }
    
    # Verificar si es exacta
    # Calcular derivadas parciales primero de M respecto a "Y"
    dM_dy = diff(M, y)
    # Luego de N respecto a "X"
    dN_dx = diff(N, x)
    
    # 🔍 DEBUG: Imprime las derivadas
    print(f"DEBUG - dM/dy: {dM_dy}")
    print(f"DEBUG - dN/dx: {dN_dx}")
    print(f"DEBUG - Diferencia: {simplify(dM_dy - dN_dx)}")
    
    if simplify(dM_dy - dN_dx) != 0:
        return {
            'es_exacta': False,
            'mensaje': 'La ecuación NO es exacta',
            'detalles': {
                'dM_dy': str(dM_dy),
                'dN_dx': str(dN_dx),
                'diferencia': str(simplify(dM_dy - dN_dx))
            }
        }
    
    # Resolver (integrar M respecto a x)
    f = integrate(M, x)
    # luego de esto vamos a obtener una ecuación con una función g(y) pendiente por determinar
    
    # Encontrar g(y) derivando y comparando con N
    # primero derivamos f respecto a y
    df_dy = diff(f, y)
    
    # luego restamos N - df/dy para encontrar g'(y)
    g_prime = simplify(N - df_dy)
    
    # integramos g'(y) respecto a y para encontrar g(y)
    g = integrate(g_prime, y)
    
    solucion = f + g
    
    return {
        'es_exacta': True,
        'solucion': str(solucion) + ' = C',
        'pasos': {
            'M': str(M),
            'N': str(N),
            'dM_dy': str(dM_dy),
            'dN_dx': str(dN_dx),
            'f(x,y)': str(f),
            "g'(y)": str(g_prime),
            "g(y)": str(g)
        }
    }