import traceback

import pandas as pd
import os
import sys
import re
import codecs

# añadiendo a sys el path del proyecto:
# permitiendo el uso de librerías propias:
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
log_good = LogDefaultConfig("app_log_good.log").logger
log_fail = LogDefaultConfig("app_log_fail.log").logger

# global_variables
sep = "\t"
output_file = "salida.xlsx"
input_file = "condiciones_preprocesadas.csv"
condiciones_as_csv = "condiciones_as_csv.csv"
firmantes_as_csv = "firmantes.csv"
settings_file = "Config.xlsx"
path_settings_file = os.path.join(main_path, settings_file)


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
        # print("*************************ACCOUNT*********************")
        # print(f"Account {acc_id}")
        # pretty(found_matches, 2)
        # [print(li) for li in df_g[co_descripcion]]
        # caso simple operaciones = 1 y cheque desde = 1
        if exp_chk_desde in found_matches.keys() and exp_operaciones in found_matches.keys():
            if len(found_matches[exp_operaciones]) == 1 and len(found_matches[exp_chk_desde]) == 1:
                mask = (df_firm[c_0] == acc_id[0]) & (df_firm[c_1] == acc_id[1])
                df_firm_filter = df_firm[mask]

                if "CONJ" in found_matches[exp_operaciones][0]:
                    operacion = "FIRMAS CONJUNTAS"
                elif "NDIV" in found_matches[exp_operaciones][0]:
                    operacion = "FIRMA INDIVIDUAL"
                else:
                    operacion = "AMBIGUO"

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
                    # if any([True for p in parsed_names if p is None]):
                    #    parsed_names = [None]

                    for name in parsed_names:
                        result = Resultado()
                        result.firmante_1 = name
                        if name is None:
                            result.observacion = "No fue posible detectar nombre firmante"
                        result.cuenta = str(acc_id[0]) + " " + str(acc_id[1])
                        result.condicion = operacion
                        attrs = ["cheque_desde", "cheque_hasta", "monto_desde", "monto_hasta"]
                        evals = [exp_chk_desde, exp_chk_hasta, exp_monto_desde, exp_chk_hasta]
                        for attr, this_exp in zip(attrs, evals):
                            try:
                                if this_exp in found_matches.keys():
                                    value = str(found_matches[this_exp][0][1]).replace(".", "")
                                    setattr(result, attr, value)
                            except Exception as e:
                                print("problema")
                        result.fecha_desde = list(df_g[co_fecha_inicio])
                        result.fecha_hasta = list(df_g[co_fecha_inicio])
                        result.secuencial = list(df_g[co_secuencial])
                        resp_final.append(result)

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
                    parsed_names =[ k for k,v  in  sorted_x]

                    for name in parsed_names[1:]:
                        result = Resultado()
                        result.firmante_1 = parsed_names[0]
                        result.firmante_2 = name
                        if name is None:
                            result.observacion = "No fue posible detectar nombre firmante"
                        result.cuenta = str(acc_id[0]) + " " + str(acc_id[1])
                        result.condicion = operacion
                        attrs = ["cheque_desde", "cheque_hasta", "monto_desde", "monto_hasta"]
                        evals = [exp_chk_desde, exp_chk_hasta, exp_monto_desde, exp_chk_hasta]
                        for attr, this_exp in zip(attrs, evals):
                            try:
                                if this_exp in found_matches.keys():
                                    value = str(found_matches[this_exp][0][1]).replace(".", "")
                                    setattr(result, attr, value)
                            except Exception as e:
                                print("problema")
                        result.fecha_desde = list(df_g[co_fecha_inicio])
                        result.fecha_hasta = list(df_g[co_fecha_inicio])
                        result.secuencial = list(df_g[co_secuencial])
                        resp_final.append(result)


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
        #             log_fail.error(str(acc_id)+str(separadores))
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