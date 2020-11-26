from constantes import *
from my_lib.util import *
from dto.resultados import Resultado
import pandas as pd


def case_operaciones_chk_1(acc_id, df_g, df_firm, found_matches, lin_total):
    c_0, c_1 = df_firm.columns[0], df_firm.columns[1]
    mask = (df_firm[c_0] == acc_id[0]) & (df_firm[c_1] == acc_id[1])
    df_firm_filter = df_firm[mask]

    if "CONJ" in found_matches[exp_operaciones][0]:
        operacion = "FIRMAS CONJUNTAS"
    elif "NDIV" in found_matches[exp_operaciones][0]:
        operacion = "FIRMA INDIVIDUAL"
    else:
        operacion = "AMBIGUO"

    # CASO 1A: Firma individual
    if operacion == "FIRMA INDIVIDUAL" and exp_f_individual in found_matches.keys():
        if len(found_matches[exp_f_individual]) == 1:
            partial_names = found_matches[exp_f_individual][0]
        else:
            partial_names = list()
            for g in found_matches[exp_f_individual]:
                if isinstance(g, tuple):
                    partial_names += list(g)
                elif isinstance(g, list):
                    continue
                elif isinstance(g, str):
                    partial_names.append(g)
                else:
                    print("No considerado")

        # antigua version
        # parsed_names = parse_to_complete_names(partial_names, list(df_firm_filter[co_nombre]))
        # pablo version:
        parsed_names = match_string_list_in_linea(list(df_firm_filter[co_nombre]), lin_total)
        #
        resp_final = list()
        for name in parsed_names:
            result = Resultado()
            result.firmante_1 = name
            if name is None:
                result.observacion = "No fue posible detectar nombre firmante"
            result.cuenta = str(acc_id[0]) + " " + str(acc_id[1])
            result.condicion = operacion
            attrs = ["cheque_desde", "cheque_hasta", "monto_desde", "monto_hasta"]
            evals = [exp_chk_desde, exp_chk_hasta, exp_monto_desde, exp_monto_hasta]
            for attr, this_exp in zip(attrs, evals):
                try:
                    if this_exp in found_matches.keys():
                        value = str(found_matches[this_exp][0][1]).replace(".", "")
                        setattr(result, attr, value)
                except Exception as e:
                    print("problema")
            result.fecha_desde = list(df_g[co_fecha_inicio])[0]
            result.fecha_hasta = list(df_g[co_fecha_inicio])[0]
            result.secuencial = list(df_g[co_secuencial])
            resp_final.append(result)
        return len(resp_final) > 0, resp_final
    # FIN CASO 1A

    # CASO 1B: Firmas Conjuntas
    if operacion == "FIRMAS CONJUNTAS" and exp_f_conjunta in found_matches.keys():
        if len(found_matches[exp_f_conjunta]) == 1:
            partial_names = list()
            for partial in found_matches[exp_f_conjunta][0]:
                partial = partial.split(" Y ")
                partial_names += partial
        else:
            partial_names = list()
            for g in found_matches[exp_f_conjunta]:
                if isinstance(g, tuple):
                    partial_names += list(g)
                elif isinstance(g, list):
                    continue
                elif isinstance(g, str):
                    partial_names.append(g)
                else:
                    print("No considerado")
        # Antigua versión
        # parsed_names = parse_to_complete_names(partial_names, list(df_firm_filter[co_nombre]))
        # pablo version:
        parsed_names = match_string_list_in_linea(list(df_firm_filter[co_nombre]), lin_total)
        # ordenar en orden de aparecimiento:
        order_dict = order_by_fisrt_ocurrence(parsed_names, lin_total)
        sorted_x = sorted(order_dict.items(), key=lambda kv: kv[1])
        parsed_names = [k for k, v in sorted_x]

        resp_final = list()
        for name in parsed_names[1:]:
            result = Resultado()
            result.firmante_1 = parsed_names[0]
            result.firmante_2 = name
            if name is None:
                result.observacion = "No fue posible detectar nombre firmante"
            result.cuenta = str(acc_id[0]) + " " + str(acc_id[1])
            result.condicion = operacion
            attrs = ["cheque_desde", "cheque_hasta", "monto_desde", "monto_hasta"]
            evals = [exp_chk_desde, exp_chk_hasta, exp_monto_desde, exp_monto_hasta]
            for attr, this_exp in zip(attrs, evals):
                try:
                    if this_exp in found_matches.keys():
                        value = str(found_matches[this_exp][0][1]).replace(".", "")
                        setattr(result, attr, value)
                except Exception as e:
                    print("problema")
            result.fecha_desde = list(df_g[co_fecha_inicio])[0]
            result.fecha_hasta = list(df_g[co_fecha_inicio])[0]
            result.secuencial = list(df_g[co_secuencial])
            resp_final.append(result)
        return len(resp_final) > 0, resp_final

    # FIN CASO 1B
    return False, None


def case_2_df_smaller_than_2(acc_id, df_g, df_firm, found_matches, lin_total):
    # Rutina para encontrar la mejor información posible con respecto a los nombres
    # esta no te sirve?, esa ya se esta ejcutando
    c_0, c_1 = df_firm.columns[0], df_firm.columns[1]
    mask = (df_firm[c_0] == acc_id[0]) & (df_firm[c_1] == acc_id[1])
    df_firm_filter = df_firm[mask]
    parsed_names = match_string_list_in_linea(list(df_firm_filter[co_nombre]), lin_total)

    order_dict = order_by_fisrt_ocurrence(parsed_names, lin_total)
    sorted_x = sorted(order_dict.items(), key=lambda kv: kv[1])
    parsed_names = [k for k, v in sorted_x]

    if len(parsed_names) == 1 and parsed_names[0] is None:
        observacion = "No es posible encontrar el firmante"
    elif len(parsed_names) == 0:
        observacion = "No es posible encontrar el firmante"
        parsed_names = [None]

    operacion = None
    firm1 = None
    if exp_operaciones in found_matches.keys():
        if "CONJ" in found_matches[exp_operaciones][0]:
            operacion = "FIRMAS CONJUNTAS"
            firm1 = parsed_names[0]
            parsed_names = parsed_names[1:]
        elif "NDIV" in found_matches[exp_operaciones][0]:
            operacion = "FIRMA INDIVIDUAL"
        else:
            operacion = "AMBIGUO"
    resp_final = list()
    for name in parsed_names:
        result = Resultado()
        result.condicion = operacion
        result.cuenta = str(acc_id[0]) + " " + str(acc_id[1])
        if operacion == "FIRMAS CONJUNTAS":
            result.firmante_1 = firm1
            result.firmante_2 = name
        else:
            result.firmante_1 = name

        if len(parsed_names) == 1 and parsed_names[0] is None:
            result.observacion = "No es posible encontrar el firmante"
        elif len(parsed_names) == 0:
            result.observacion = "No es posible encontrar el firmante"

        attrs = ["cheque_desde", "cheque_hasta", "monto_desde", "monto_hasta"]
        evals = [exp_chk_desde, exp_chk_hasta, exp_monto_desde, exp_monto_hasta]
        for attr, this_exp in zip(attrs, evals):
            try:
                if this_exp in found_matches.keys():
                    value = str(found_matches[this_exp][0][1]).replace(".", "")
                    setattr(result, attr, value)
            except Exception as e:
                print("problema")
        result.fecha_desde = list(df_g[co_fecha_inicio])[0]
        result.fecha_hasta = list(df_g[co_fecha_inicio])[0]
        result.secuencial = list(df_g[co_secuencial])
        resp_final.append(result)
    return len(resp_final) > 0, resp_final

def fill_values_case_2_b(firmante_principal, altr_firmantes, found_matches, operacion, acc_id, df_g):
    # Rutina para cuando existe un " DEMAS ALTERNANTES " para llenar con la mejor información posible
    resp_final = list()
    for name in altr_firmantes:
        result = Resultado()
        result.condicion = operacion
        result.cuenta = str(acc_id[0]) + " " + str(acc_id[1])
        if operacion == "FIRMAS CONJUNTAS":
            result.firmante_1 = firmante_principal
            result.firmante_2 = name
        else:
            result.firmante_1 = name

        if len(altr_firmantes) == 1 and altr_firmantes[0] is None:
            result.observacion = "No es posible encontrar el firmante"
        elif len(altr_firmantes) == 0:
            result.observacion = "No es posible encontrar el firmante"

        attrs = ["cheque_desde", "cheque_hasta", "monto_desde", "monto_hasta"]
        evals = [exp_chk_desde, exp_chk_hasta, exp_monto_desde, exp_monto_hasta]
        for attr, this_exp in zip(attrs, evals):
            try:
                if this_exp in found_matches.keys():
                    value = str(found_matches[this_exp][0][1]).replace(".", "")
                    setattr(result, attr, value)
            except Exception as e:
                print("problema")
        result.fecha_desde = list(df_g[co_fecha_inicio])[0]
        result.fecha_hasta = list(df_g[co_fecha_inicio])[0]
        result.secuencial = list(df_g[co_secuencial])
        resp_final.append(result)
    return len(resp_final) > 0, resp_final