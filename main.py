import traceback

import pandas as pd
import os
import sys
import re
import codecs

# añadiendo a sys el path del proyecto:
# permitiendo el uso de librerías propias:
from my_lib.DefaultLogClass import DefaultConfig
from my_lib.subrutinas import *

main_path = os.path.dirname(os.path.abspath(__file__))
project_path = main_path
input_path = os.path.join(project_path, "input")
output_path = os.path.join(project_path, "output")
sys.path.append(main_path)
sys.path.append(project_path)

from my_lib.util import *
from constantes import *
from dto.resultados import Resultado
from to_print import print_this

log = LogDefaultConfig("app_log.log").logger
log_good = DefaultConfig("app_log_good.log").logger
log_fail = DefaultConfig("app_log_fail.log").logger
log_caso_new_case = LogDefaultConfig("nuevos_casos.log").logger


# global_variables
sep = "\t"
output_file = "salida.xlsx"
input_file = "condiciones_preprocesadas.csv"
condiciones_as_csv = "condiciones_as_csv.csv"
firmantes_as_csv = "firmantes.csv"
settings_file = "Config.xlsx"
path_settings_file = os.path.join(main_path, settings_file)
# configuración de logeo:
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', 1)


def process_df(df):
    success, df_set = read_settings(path_settings_file)
    firm_file_path = os.path.join(input_path, firmantes_as_csv)
    success, df_firm, msg = read_source_file(firm_file_path, sep=sep)
    c_0, c_1 = df_firm.columns[0], df_firm.columns[1]
    reg_ex_list = dict()
    for exp in exp_list:
        reg_ex_list[exp] = (list(df_set[exp].dropna()))

    if not success:
        return False, df_set

    resp_final = list()
    for acc_id, df_g in df.groupby(by=[co_cuenta, co_cod_cuenta]):
        lin_total = " ".join(df_g[co_descripcion])
        # encuentra todos los macthces posibles para todas las reglas:
        found_matches = search_matches(lin_total, exp_list, reg_ex_list)
        # CASO 1A y 1B (el número de operaciones y el número de cheques es 1)
        if exp_chk_desde in found_matches.keys() and exp_operaciones in found_matches.keys():
            if len(found_matches[exp_operaciones]) == 1 and len(found_matches[exp_chk_desde]) == 1:
                # filtrar data set de firmantes
                success, resp = case_operaciones_chk_1(acc_id, df_g, df_firm, found_matches, lin_total)
                if success:
                    resp_final += resp
                    continue
                # else:
                #     # está sin identificar  creo que en este caso no debe ecistir este else
                #     log_fail.info(f"\n-----> Account: {acc_id[0]} {acc_id[1]}")
                #     log_fail.info(df_g)

        # CASO 1C caso grupos pequeños:
        elif exp_operaciones in found_matches.keys():
            if len(df_g.index) <= 2 and len(found_matches[exp_operaciones]) == 1:
                c_0, c_1 = df_firm.columns[0], df_firm.columns[1]
                mask = (df_firm[c_0] == acc_id[0]) & (df_firm[c_1] == acc_id[1])
                df_firm_filter = df_firm[mask]
                success, resp = case_2_df_smaller_than_2(acc_id, df_g, df_firm, found_matches, lin_total)
                if success:
                    resp_final += resp
                    continue
                elif any([(ex in found_matches.keys()) for ex in [exp_f_conjunta, exp_f_individual, exp_monto_desde,
                                                                  exp_chk_hasta]]):
                    # CASOS A IMPLEMENTAR A FUTURO
                    log_caso_new_case.info(f"\n########## 2 x #######")
                    log_caso_new_case.info(f"\n-----> Account: {acc_id[0]} {acc_id[1]}")
                    log_caso_new_case.info(df_g)
                else:
                    result = Resultado()
                    result.condicion = found_matches[exp_operaciones][0]
                    result.fecha_desde = list(df_g[co_fecha_inicio])[0]
                    result.fecha_hasta = list(df_g[co_fecha_fin])[0]
                    result.secuencial = list(df_g[co_secuencial])
                    result.cuenta = str(acc_id[0]) + " " + str(acc_id[1])
                    result.observacion = "Datos insuficientes"
                    resp_final.append(result)
                    #log_fail.info(f"\n########## CASO INCOMPLETO #######")
                    # log_fail.info(f"\n-----> Account: {acc_id[0]} {acc_id[1]}")
                    # log_fail.info(df_g)

                    log_fail.info(f"\n-------------> Account: {c_0} {c_1}")
                    log_fail.info(df_g[co_descripcion])
                    log_fail.info(f"---> Firmantes:")
                    log_fail.info(df_firm_filter[co_nombre].to_string(index=False))
                    log_fail.info(f"---> Result:")
                    df_aux = pd.DataFrame([r.to_dict() for r in [result]])
                    log_fail.info(df_aux[heads].to_string(index=False))

            # caso grupo pequeño en que existen dos operaciones y en la segunda frase se tiene "DEMAS ALTERNANTES"
            elif len(df_g.index) <= 2 and len(found_matches[exp_operaciones]) == 2:
                c_0, c_1 = df_firm.columns[0], df_firm.columns[1]
                mask = (df_firm[c_0] == acc_id[0]) & (df_firm[c_1] == acc_id[1])
                df_firm_filter = df_firm[mask]

                if " DEMAS " in lin_total:
                    sub_lineas = lin_total.split(" DEMAS ")
                    parsed_names = match_string_list_in_linea(list(df_firm_filter[co_nombre]), lin_total)
                    order_dict = order_by_fisrt_ocurrence(parsed_names, lin_total)
                    sorted_x = sorted(order_dict.items(), key=lambda kv: kv[1])
                    parsed_names = [k for k, v in sorted_x]

                    for ix, sub_linea in enumerate(sub_lineas):
                        found_matches_demas = search_matches(sub_linea, exp_list, reg_ex_list)
                        if ix == 0:
                            if exp_chk_desde in found_matches_demas.keys() and exp_operaciones in found_matches_demas.keys():
                                if len(found_matches_demas[exp_operaciones]) == 1 and len(found_matches_demas[exp_chk_desde]) == 1:
                                    success, resp = case_operaciones_chk_1(acc_id, df_g, df_firm, found_matches, lin_total)
                                    if success:
                                        # caso 1A y 1B (con desde cheque)
                                        resp_final += resp
                                        continue
                                    else:
                                        log_caso_new_case.info(f"CASO 1D no determinado")
                                        log_caso_new_case.info(f"\n-----> Account: {acc_id[0]} {acc_id[1]}")
                                        log_caso_new_case.info(df_g)
                            else:
                                success, resp = case_2_df_smaller_than_2(acc_id, df_g, df_firm, found_matches,
                                                                       lin_total)
                                if success:
                                    # caso 1C (filtrando la mejor información que se tiene)
                                    resp_final += resp
                                    continue
                                else:
                                    log_caso_new_case.info(f"CASO 1E no determinado")
                                    log_caso_new_case.info(f"\n-----> Account: {acc_id[0]} {acc_id[1]}")
                                    log_caso_new_case.info(df_g)

                        if is_alternates(sub_linea) and exp_f_conjunta in found_matches_demas.keys():
                            # CASO 2A: Caso alternantes:

                            parsed_names_sub = match_string_list_in_linea(list(df_firm_filter[co_nombre]), sub_linea)
                            if len(parsed_names_sub) > 0:
                                log_caso_new_case.info(f"CASO 2B no determinado")
                                log_caso_new_case.info(f"\n-----> Account: {acc_id[0]} {acc_id[1]}")
                                log_caso_new_case.info(df_g)
                            else:
                                # CASO 2C
                                firm_principal = parsed_names[0]
                                alternante_firmantes = [f for f in list(df_firm_filter[co_nombre]) if firm_principal != f]
                                operacion = None
                                if exp_operaciones in found_matches_demas.keys():
                                    if "CONJ" in found_matches_demas[exp_operaciones][0]:
                                        operacion = "FIRMAS CONJUNTAS"
                                    elif "NDIV" in found_matches_demas[exp_operaciones][0]:
                                        operacion = "FIRMA INDIVIDUAL"
                                    else:
                                        operacion = "AMBIGUO"
                                success, resp = fill_values_case_2_b(firm_principal, alternante_firmantes,
                                                                     found_matches_demas, operacion, acc_id, df_g)
                                if success:
                                    # caso 2C (filtrando la mejor información que se tiene)
                                    resp_final += resp
                                    log_good.info(f"\n-------------> Account: {c_0} {c_1}")
                                    log_good.info(df_g[co_descripcion])
                                    log.info(f"---> Firmantes:")
                                    log_good.info(df_firm_filter[co_nombre].to_string(index=False))
                                    df_aux = pd.DataFrame([r.to_dict() for r in resp])
                                    log.info(f"---> Result:")
                                    log_good.info(df_aux[heads].to_string(index=False))


                                    continue
                                else:
                                    log_caso_new_case.info(f"CASO 1E no determinado")
                                    log_caso_new_case.info(f"\n-----> Account: {acc_id[0]} {acc_id[1]}")
                                    log_caso_new_case.info(df_g)

            elif len(df_g.index) <= 3 and len(found_matches[exp_operaciones]) == 3:
                #Caso 3 A
                log_caso_new_case.info(f"\n########## CASO 3 A #######")
                log_caso_new_case.info(f"\n-----> Account: {acc_id[0]} {acc_id[1]}")
                log_caso_new_case.info(df_g)

            elif len(df_g.index) <= 4 and len(found_matches[exp_operaciones]) == 4:
                #Caso 4 A
                log_caso_new_case.info(f"\n########## CASO 4 A #######")
                log_caso_new_case.info(f"\n-----> Account: {acc_id[0]} {acc_id[1]}")
                log_caso_new_case.info(df_g)

            elif len(df_g.index) <= 5 and len(found_matches[exp_operaciones]) == 5:
                #Caso 5 A
                log_caso_new_case.info(f"\n########## CASO 5 A #######")
                log_caso_new_case.info(f"\n-----> Account: {acc_id[0]} {acc_id[1]}")
                log_caso_new_case.info(df_g)

    return resp_final


def main():
    # file_name = "CONDICIONES.txt"
    # input_path_file = os.path.join(input_path, file_name)
    # output_path_file = os.path.join(input_path, output_file)
    # transform_file(input_path_file, output_path_file)
    # path_file = os.path.join(input_path, condiciones_as_csv)
    path_file = os.path.join(input_path, input_file)
    success, df, msg = read_source_file(path_file, sep=sep)
    if not success:
        return False, msg
    # set first column as index
    df.set_index(df.columns[0], inplace=True)

    if list(df.columns) != expected_columns:
        msg = "Las columnas del archivo no coinciden"
        return False, msg
    # preprocesando los casos continue (-->)
    # success, df = pre_process_df(df)
    # if not success:
    #     msg = "No se puede preprocesar los datos"
    #     return False, msg
    # df = df.sort_index()
    # df.index = [ix+2 for ix in df.index]
    # df.to_csv("condiciones_preprocesadas.csv", sep=sep)

    result = process_df(df)
    to_save = [r.to_dict() for r in result]
    df_save = pd.DataFrame(to_save)
    # df_save.drop_duplicates(subset=["cuenta", "firmante_2"], keep='first', inplace=True)

    path_output_file = os.path.join(output_path, output_file)
    df_save.to_excel(path_output_file)
    print_this()


if __name__ == "__main__":
    result = main()
    print(result)

    # para saber cuantas operaciones se van a realizar:
    # success, match1 = search_match(lin_total, reg_ex_list[exp_chk_desde])
    # success, match2 = search_match(lin_total, reg_ex_list[exp_chk_hasta])
    # success, match3 = search_match(lin_total, reg_ex_list[exp_f_conjunta])
    # success, match4 = search_match(lin_total, reg_ex_list[exp_monto_desde])
    # success, match5 = search_match(lin_total, reg_ex_list[exp_monto_hasta])
    # success, match6 = search_match(lin_total, reg_ex_list[exp_f_individual])
    # success, match7 = search_match(lin_total, reg_ex_list[exp_f_conjunta])
    # success, match8 = search_match(lin_total, reg_ex_list[exp_operaciones])
    # t_p = [match1, match2, match3, match4, match5, match6, match7, match8]
    # t_p = "\n".join([str(t) for t in t_p])

# if exp_f_conjunta in found_matches.keys():
#     parsed_names = parse_to_complete_names(found_matches[exp_f_conjunta][0], list(df_firm_filter[co_nombre]))
#     if any([True for p in parsed_names if p is None]):
#         print("firmantes no coincidentes")
#     else:
#         print(parsed_names)

# print(lin_total)

# if exp_chk_desde in found_matches.keys():
#     if not len(found_matches[exp_operaciones]) == len(found_matches[exp_chk_desde]):
#         continue
#     # found_matches[exp_chk_desde] es la lista de coincidencias de exp_chk_desde
#     # para interactuar se tiene tupla: (text, valor)
#     separadores = [valor for text, valor in found_matches[exp_chk_desde]]
#     for separador in separadores:
#         if len(separador)==0:
#             log_fail.info(str(acc_id)+str(separadores))
#             continue
#         if len(found_matches[exp_operaciones])==1:
#             lineas = [lin_total]
#         else:
#             lineas = lin_total.split(separador)
#
#         for linea in lineas:
#             details_matches = search_matches(linea,
#                                              [exp_chk_hasta, exp_monto_desde, exp_monto_hasta,
#                                               exp_operaciones, exp_f_conjunta, exp_f_individual], reg_ex_list)
#             op_result = Resultado()
#             op_result.cheque_desde = separador
#             if exp_chk_hasta in details_matches.keys():
#                 aux = details_matches[exp_chk_hasta]
#                 success,respu = search_unique_value(aux,log_fail,acc_id,linea)
#                 if success:
#                     op_result.cheque_hasta = respu
#
#             if exp_monto_desde in details_matches.keys():
#                 aux = details_matches[exp_monto_desde]
#                 success, respu = search_unique_value(aux,log_fail,acc_id,linea)
#                 if success:
#                     log_good.info(acc_id)
#                     op_result.monto_desde = respu
#
#             if exp_monto_hasta in details_matches.keys():
#                 aux = details_matches[exp_monto_hasta]
#                 success, respu = search_unique_value(aux, log_fail, acc_id, linea)
#                 if success:
#                     op_result.monto_hasta = respu
#                     log_good.info(acc_id)
#
#             if exp_f_individual in details_matches.keys():
#                 aux = details_matches[exp_f_individual]
#                 success, respu = search_unique_value_individual(aux, log_fail, acc_id, linea)
#                 if success:
#                     op_result.firmante_1 = respu
#                     log_good.info(acc_id)
#
#             if exp_operaciones in details_matches.keys():
#                 aux = details_matches[exp_operaciones]
#                 success, respu = search_unique_value_individual(aux, log_fail, acc_id, linea)
#                 if success:
#                     op_result.condicion = respu
#                     log_good.info(acc_id)
#
#             # if exp_f_individual in details_matches.keys():
#             #     op_result.firmante_1 = [valor for text, valor in details_matches[exp_f_individual]]
#             # if exp_f_conjunta in details_matches.keys():
#             #     op_result.firmante_2 = [valor for text, valor in details_matches[exp_f_conjunta]]
#             # if exp_monto_desde in details_matches.keys():
#             #     op_result.monto_desde = [valor for text, valor in details_matches[exp_monto_desde]]
#             # if exp_monto_hasta in details_matches.keys():
#             #     op_result.monto_hasta = [valor for text, valor in details_matches[exp_monto_hasta]]
#             # interactuar con matches y llenar resultados:
#             print("---------------------------RESULT---------------------------------")
#             print(op_result)

# Si se encuentran cheques, entonces tomarlos
# como separadores
