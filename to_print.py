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
from my_lib.DefaultLogClass import DefaultConfig

log = DefaultConfig("result_conjuntas.log").logger

# global_variables
sep = "\t"
output_file = None
input_file = "condiciones_preprocesadas.csv"
condiciones_as_csv = "condiciones_as_csv.csv"
firmantes_as_csv = "firmantes.csv"
settings_file = "Config.xlsx"
path_settings_file = os.path.join(main_path, settings_file)


def main():

    # input_path_file = os.path.join(input_path, file_name)
    # output_path_file = os.path.join(input_path, output_file)
    # transform_file(input_path_file, output_path_file)
    # path_file = os.path.join(input_path, condiciones_as_csv)
    path_file = os.path.join(input_path, input_file)
    success, df, msg = read_source_file(path_file, sep=sep)
    if not success:
        return False, msg
    # set first column as index
    df.set_index([co_secuencial], inplace=True)

    file_name = "Operaciones_conjuntas.xlsx"
    path_file = os.path.join(input_path, file_name)
    df_result = pd.read_excel(path_file)
    df_result.set_index(df_result.columns[0], inplace=True)

    firmantes_as_csv = "firmantes.csv"
    firm_file_path = os.path.join(input_path, firmantes_as_csv)
    success, df_firm, msg = read_source_file(firm_file_path, sep=sep)

    for acc_id, df_g in df_result.groupby(by=["cuenta"]):
        c_0, c_1 = acc_id.split(" ")
        df[co_cod_cuenta] = [int(v) for v in df[co_cod_cuenta]]

        mask = (df[co_cuenta] == c_0) & (df[co_cod_cuenta]==int(c_1))
        df_filter = df[mask]

        n_0 = df_firm.columns[0]
        n_1 = df_firm.columns[1]
        mask = (df_firm[n_0] == c_0) & (df_firm[n_1]==int(c_1))
        df_firm_filter = df_firm[mask]

        log.info(f"\n-------------> Account: {c_0} {c_1}")
        log.info(df_filter[co_descripcion])
        log.info(f"---> Firmantes:")
        log.info(df_firm_filter[co_nombre].to_string(index=False))
        log.info(f"---> Result:")
        log.info(df_g.to_string(index=False))



if __name__ == "__main__":
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', -1)
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
