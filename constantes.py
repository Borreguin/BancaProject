# columnas input file
co_cuenta = 'co_cuenta'
co_cod_cuenta = 'cod_cuenta'
co_secuencial = 'co_secuencial'
co_fecha_inicio = 'co_fecha_inicio'
co_fecha_fin = 'co_fecha_fin'
co_descripcion = 'co_descripcion'
co_fecha_reg = 'co_fecha_reg'

expected_columns = [co_cuenta, co_cod_cuenta, co_secuencial, co_fecha_inicio, co_fecha_fin,
                    co_descripcion, co_fecha_reg]

# columnas de resultado:
cl_cuenta = "cuenta"
cl_secuencial = "secuencial"
cl_desde_chk = "cheque desde"
cl_hasta_chk = "cheque hasta"
cl_firm_1 = "firmante 1"
cl_firm_2 = "firmante 2"
cl_condicion = "tipo de condición"
cl_desde_fecha = "fecha desde"
cl_hasta_fecha = "fecha hasta"
cl_desde_monto = "Monto desde"
cl_hasta_monto = "Monto hasta"
columns_resp = [cl_cuenta, cl_secuencial, cl_desde_chk, cl_hasta_chk, cl_firm_1, cl_firm_2,
                cl_condicion, cl_desde_fecha, cl_hasta_fecha, cl_desde_monto, cl_hasta_monto]

# columnas de reglas regex
exp_siguiente = "SGTE CONDICION"
exp_chk_desde = "CHK_DESDE_EXP"
exp_chk_hasta =	"CHK_HASTA_EXP"
exp_monto_desde = "MONTO_DESDE_EXP"
exp_monto_hasta = "MONTO_HASTA_EXP"
exp_f_individual = "F_INDIVIDUAL_EXP"
exp_f_conjunta = "F_CONJUNTA_EXP"
exp_operaciones = "OP_EXP"

exp_list = [exp_chk_desde, exp_chk_hasta, exp_monto_desde, exp_monto_hasta, exp_f_individual,
            exp_f_conjunta, exp_operaciones]

co_nombre = "nombre"