

class Resultado():
    cuenta = None
    secuencial = list()
    cheque_desde = None
    cheque_hasta = 999999999
    firmante_1 = None
    firmante_2 = None
    condicion = None
    fecha_desde = None
    fecha_hasta = None
    monto_desde = 0
    monto_hasta = "ilimitado"

    def __init__(self, *args, **values):
        super().__init__(*args, **values)

    def to_dict(self):
        return dict(cuenta=self.cuenta, secuencial = self.secuencial,
                    cheque_desde=self.cheque_desde, cheque_hasta=self.cheque_hasta,
                    firmante_1=self.firmante_1, firmante_2=self.firmante_2,
                    condicion=self.condicion, fecha_desde=self.fecha_desde,
                    fecha_hasta = self.fecha_hasta, monto_desde=self.monto_desde,
                    monto_hasta=self.monto_hasta)

    def __repr__(self):
        return f"<r {self.cuenta}: \nchk_d:{self.cheque_desde}> "
