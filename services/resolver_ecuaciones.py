import re
from sympy import symbols, sympify, diff, integrate, simplify


def limpiar_expresion(expr):
    """Limpia y prepara la expresión escrita por el usuario."""
    # asegurar string
    expr = str(expr)

    # Eliminar espacios
    expr = expr.replace(" ", "")

    # Eliminar dx y dy
    expr = expr.replace("dx", "").replace("dy", "")

    # Lista de funciones de sympy a proteger
    funciones = ['sin', 'cos', 'tan', 'asin', 'acos', 'atan',
                 'sinh', 'cosh', 'tanh', 'exp', 'log', 'sqrt', 'Abs']

    # Proteger funciones: reemplazar temporalmente
    for i, fn in enumerate(funciones):
        # Reemplazar 'sin(' por un marcador único que no contenga letras
        expr = expr.replace(f'{fn}(', f'@F{i}@(')

    # ===== INSERTAR MULTIPLICACIONES IMPLÍCITAS =====
    
    # 1) número seguido de letra o '(' o '@' -> 2x -> 2*x
    expr = re.sub(r'(\d)(?=[A-Za-z_(@])', r'\1*', expr)

    # 2) ')' seguido de '(' o letra -> )(  -> )*(
    expr = re.sub(r'(\))(?=[\(A-Za-z_])', r'\1*', expr)

    # 3) letra seguida de '(' -> x( -> x*(
    expr = re.sub(r'([A-Za-z])(?=\()', r'\1*', expr)
    
    # 4) letra seguida de letra -> xy -> x*y (REPETIDAMENTE)
    # Esta es la clave: solo aplicar entre letras normales
    max_iterations = 50
    for _ in range(max_iterations):
        expr_antes = expr
        # Solo entre a-z y A-Z, ignorando @
        expr = re.sub(r'([a-zA-Z])([a-zA-Z])', r'\1*\2', expr)
        if expr == expr_antes:
            break

    # 5) Limpiar múltiples asteriscos (pero mantener **)
    # Primero proteger **
    expr = expr.replace('**', '§§§')
    # Quitar * múltiples
    expr = re.sub(r'\*+', '*', expr)
    # Restaurar **
    expr = expr.replace('§§§', '**')

    # ===== RESTAURAR FUNCIONES =====
    for i, fn in enumerate(funciones):
        expr = expr.replace(f'@F{i}@(', f'{fn}(')

    # Limpiar operadores mal formados
    expr = expr.replace('+*', '+').replace('*+', '+')
    expr = expr.replace('-*', '-').replace('*-', '-')
    expr = expr.replace('/*', '/').replace('*/', '/')

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
    dM_dy = diff(M, y)
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
    
    # Encontrar g(y)
    df_dy = diff(f, y)
    g_prime = simplify(N - df_dy)
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