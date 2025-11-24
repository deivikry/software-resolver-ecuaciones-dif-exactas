class EcuacionDiferencial:
    def __init__(self, datos):
        self.M = datos.get('M', '')  # Coeficiente de dx
        self.N = datos.get('N', '')  # Coeficiente de dy
        self.tipo = 'exacta'
    
    def validar(self):
        """Valida que los datos sean correctos"""
        if not self.M or not self.N:
            raise ValueError("Debe proporcionar M y N")
        return True