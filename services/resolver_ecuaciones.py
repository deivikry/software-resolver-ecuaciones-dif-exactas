import re
from sympy import symbols, sympify, diff, integrate, simplify


def limpiar_expresion(expr):
    """Limpia y prepara la expresión escrita por el usuario."""

    # Convertir a string por si envían objetos raros
    expr = str(expr)

    # Eliminar dx y dy
    expr = expr.replace("dx", "").replace("dy", "")

    # Eliminar espacios
    expr = expr.replace(" ", "")

    # Insertar * entre número y letra (2x -> 2*x)
    expr = re.sub(r"(\d)([a-zA-Z])", r"\1*\2", expr)

    # Insertar * entre letra y letra (xy -> x*y)
    expr = re.sub(r"([a-zA-Z])([a-zA-Z])", r"\1*\2", expr)

    return expr

def resolver_ecuacion_exacta(ecuacion):
    """
    Resuelve ecuación exacta M(x,y)dx + N(x,y)dy = 0
    """
    x, y = symbols('x y')
    
    
 # 🔥 Limpiar expresiones del usuario
    M_raw = limpiar_expresion(ecuacion.M)
    N_raw = limpiar_expresion(ecuacion.N)

    try:
        M = sympify(M_raw)
        N = sympify(N_raw)
    except Exception as e:
        return {
            'error': True,
            'mensaje': f"Error al interpretar las expresiones: {str(e)}"
        }
    
    # Convertir strings a expresiones sympy
    #M = sympify(ecuacion.M)
    #N = sympify(ecuacion.N)
    
    # Verificar si es exacta
    
    # Calcular derivadas parciales primero de M respecto a "Y"
    dM_dy = diff(M, y)
    # Luego de N respecto a "X"
    dN_dx = diff(N, x)
    
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
    
    # Resolver (integrarl M respecto a x)
    f = integrate(M, x)
    #luego de esto vamos a obtener una ecucación con una función g(y) pendiente por determinar
    
    
    # Encontrar g(y) derivando y comparando con N
    
    #primero derivamos f respecto a y
    df_dy = diff(f, y)
    
    #luego restamos N - df/dy para encontrar g'(y)
    g_prime = simplify(N - df_dy)
    
    #integramos g'(y) respecto a y para encontrar g(y)
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