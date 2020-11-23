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
log = LogDefaultConfig("app_log.log").logger

# global_variables
sep = "\t"
output_file = None
input_file = "condiciones_preprocesadas.csv"
condiciones_as_csv = "condiciones_as_csv.csv"


settings_file = "Config.xlsx"
path_settings_file = os.path.join(main_path, settings_file)


def process_df(df):
    success, df_set = read_settings(path_settings_file)
    reg_ex_list = dict()
    for exp in exp_list:
        reg_ex_list[exp] = (list(df_set[exp].dropna()))

    if not success:
        return False, df_set

    resp = dict()
    for acc_id, df_g in df.groupby(by=[co_cuenta, co_cod_cuenta]):
        lin_total = " ".join(df_g[co_descripcion])
        # encuentra todos los macthces posibles para todas las reglas:
        found_matches = search_matches(lin_total,exp_list,reg_ex_list)

        print(f"Account {acc_id}")
        pretty(found_matches, 2)
        [print(li) for li in df_g[co_descripcion]]
        if exp_chk_desde in found_matches.keys():
            # found_matches[exp_chk_desde] es la lista de coincidencias de exp_chk_desde
            # para interactuar se tiene tupla: (text, valor)
            separadores = [valor for text, valor in found_matches[exp_chk_desde]]
            for separador in separadores:
                linea_split = lin_total.split(separador)
                details_matches = search_matches(linea_split,
                                                 [exp_chk_hasta, exp_monto_desde, exp_monto_hasta,
                                                  exp_operaciones, exp_f_conjunta, exp_f_individual], reg_ex_list)
                op_result = Resultado()
                op_result.cheque_desde = separador
                # interactuar con matches y llenar resultados:

                print(op_result)

        # Si se encuentran cheques, entonces tomarlos
        # como separadores










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

    process_df(df[1000:2000])


if __name__ == "__main__":
    success, msg = main()
    if not success:
        print(f"Error: \n {msg}")


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