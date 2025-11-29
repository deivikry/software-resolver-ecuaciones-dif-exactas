import re
from sympy import symbols, sympify, diff, integrate, simplify


def limpiar_expresion(expr):
    """Limpia y prepara la expresión escrita por el usuario."""
    # asegurar string
    expr = str(expr)

    # Eliminar espacios redundantes PRIMERO
    expr = expr.replace(" ", "")

    # Eliminar dx y dy (cuando el usuario copia M(x,y)dx)
    expr = expr.replace("dx", "").replace("dy", "")

    # Lista de funciones de sympy a proteger
    funciones = ['sin', 'cos', 'tan', 'asin', 'acos', 'atan',
                 'sinh', 'cosh', 'tanh', 'exp', 'log', 'sqrt', 'Abs']

    # Proteger funciones: reemplazar 'sin(' por '__fn_sin__('
    placeholders = {}
    for fn in funciones:
        pattern = r'\b' + fn + r'(?=\()'
        placeholder = f'__fn_{fn}__'
        expr, n = re.subn(pattern, placeholder, expr)
        if n:
            placeholders[placeholder] = fn

    # ===== MANEJO ESPECIAL DE POTENCIAS ^  =====
    # Proteger expresiones con ^ para procesarlas al final
    # Patrón: captura cosas como x^2, y^3, (x+y)^2, sin(x)^2
    potencias_placeholders = {}
    contador_pot = 0
    
    # Patrón mejorado: variable/paréntesis/función seguida de ^exponente
    patron_potencia = r'([A-Za-z_]+\([^)]*\)|\([^)]+\)|[A-Za-z])\^([0-9]+|\([^)]+\))'
    
    def reemplazar_potencia(match):
        nonlocal contador_pot
        base = match.group(1)
        exponente = match.group(2)
        placeholder = f'__POT{contador_pot}__'
        potencias_placeholders[placeholder] = f'{base}**{exponente}'
        contador_pot += 1
        return placeholder
    
    # Aplicar repetidamente hasta procesar todas las potencias anidadas
    while '^' in expr:
        expr_anterior = expr
        expr = re.sub(patron_potencia, reemplazar_potencia, expr)
        if expr == expr_anterior:  # Evitar bucle infinito
            break

    # ===== INSERTAR MULTIPLICACIONES IMPLÍCITAS =====
    
    # 1) número seguido de letra o '(' -> 2x -> 2*x, 2(x+y) -> 2*(x+y)
    expr = re.sub(r'(\d)(?=[A-Za-z_(])', r'\1*', expr)

    # 2) ')' seguido de '(' o letra -> )(  -> )*(, )x -> )*x
    expr = re.sub(r'(\))(?=[\(A-Za-z_])', r'\1*', expr)

    # 3) letra/placeholder seguido de '(' -> x( -> x*(
    expr = re.sub(r'([A-Za-z_])(?=\()', r'\1*', expr)
    
    # 4) letra seguida de letra -> xy -> x*y (REPETIDAMENTE)
    # Pero EXCLUIR placeholders tipo __POT0__
    while True:
        expr_antes = expr
        # Solo aplicar entre letras que NO sean parte de __PALABRA__
        expr = re.sub(r'(?<!_)([a-z])(?=[a-z])(?!_)', r'\1*', expr, flags=re.IGNORECASE)
        if expr == expr_antes:
            break

    # 5) Limpiar asteriscos dobles accidentales
    expr = re.sub(r'\*{2,}', '**', expr)  # mantener ** como potencia
    expr = re.sub(r'(?<!\*)\*(?!\*)\*(?!\*)', '*', expr)  # triple * -> *

    # ===== RESTAURAR POTENCIAS =====
    for placeholder, potencia in potencias_placeholders.items():
        expr = expr.replace(placeholder, potencia)

    # ===== RESTAURAR FUNCIONES =====
    for placeholder, fn in placeholders.items():
        expr = expr.replace(placeholder, fn)

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