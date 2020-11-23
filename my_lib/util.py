import traceback

import pandas as pd
import os
import sys
import re
import codecs

import os, sys

from constantes import *

# añadiendo a sys el path del proyecto:
# permitiendo el uso de librerías propias:
my_lib_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.dirname(my_lib_path)
sys.path.append(project_path)
log_path = os.path.join(project_path, "logs")
from my_lib.DefaultLogClass import LogDefaultConfig
log = LogDefaultConfig("utils.log").logger

sep = "\t"

def transform_file(input_path_file, output_path_file):
    with open(input_path_file) as fp:
        s_final = str()
        line = "Linea a leer"
        cnt = 0
        while line:
            cnt += 1
            line = fp.readline()
            if cnt == 2 or len(line) <= 1:
                continue

            if cnt == 1:
                s_final = re.split("\s", line)
                s_final = [s for s in s_final if s != ""]
                s_final = sep.join(s_final) + "\n"
                print(s_final)
            else:
                # sustituyendo el separador para la primera columna:
                p1 = re.compile(r'X([\d]{3}\s)')
                s = p1.findall(line)[0]
                p_line = p1.sub(s + sep, line, count=1)
                # realizando la separación de:
                # cod_cuenta  co_secuencial co_fecha_inicio co_fecha_fin
                p2 = re.compile(r'(\s){2,}')
                p_line = p2.sub(sep, p_line, count=5)
                # reconocimiento de la última columna:
                n = 14
                aux_line = p_line[-n:]
                p3 = re.compile(r'([\d]{2}/[\d]{2}/[\d]{4})')
                resp = p3.findall(aux_line)
                if len(resp) > 0:
                    p_line = p_line[:-n].strip() + sep + resp[0] + "\n"
                else:
                    print(aux_line)
                s_final += p_line

        text_file = codecs.open(output_path_file, "w", "utf-8")
        n = text_file.write(s_final)
        text_file.close()


def search_match(str_to, exp_list):
    found_results = list()
    for ix, exp in enumerate(exp_list):
        rg = re.compile(exp)
        match = rg.findall(str_to)
        if len(match) > 0:
            found_results += match

    return len(found_results) > 0, found_results


def read_settings(path_settings_file):
    if not os.path.exists(path_settings_file):
        return False, "No se puede leer el archivo de configuraciones"
    try:
        df = pd.read_excel(path_settings_file)
        return True, df
    except Exception as e:
        return False, "No se puede leer el archivo de "


def read_source_file(path_file, **kwargs):
    if not os.path.exists(path_file):
        return False, None, "No se encuentra el archivo"
    try:
        df = pd.read_csv(path_file, **kwargs)
        return True, df, f"Archivo {path_file} leído"
    except Exception as e:
        return False, None, f"No se puede leer el archivo: {str(e)}"

def pre_process_df(df, path_settings_file):
    success, df_set = read_settings(path_settings_file)
    rules, exps = list(df_set[exp_siguiente + "_RULE"]), list(df_set[exp_siguiente + "_EXP"])
    if not success:
        return False, df_set

    df_final = pd.DataFrame(columns=df.columns)
    for acc_id, _df in df.groupby(by=[co_cuenta, co_cod_cuenta]):
        skip = False
        for ix, idx in enumerate(_df.index):
            # ix -> 1 a N  idx-> ind original
            # Trabajando con linea actual
            linea = _df[co_descripcion].iloc[ix]
            # Si se debe esquivar la linea por concantenacion:
            if skip:
                skip = False
                continue

            # aplicando lista de reglas
            exp_applied = False
            for rule, exp in zip(rules, exps):
                e1 = re.compile(exp)
                n = int(rule)
                resp = e1.findall(linea[n:])
                if len(resp) == 0:
                    continue
                try:
                    # se encontro una coincidencia
                    linea_ex = e1.sub("", linea, 1)
                    linea_next = _df[co_descripcion].iloc[ix+1]
                    # limpiando y concatenando la siguiente fila
                    reini = re.compile(r"([\(][\d]{1}[\)]*[\s]*[-]*[>]*)")
                    linea_next = reini.sub("", linea_next, count=1)
                    linea_ex = linea_ex + " " + linea_next
                    skip = True
                    exp_applied = True
                    to_modify = df[df.index.isin([idx])].copy()
                    to_modify[co_descripcion].loc[idx] = linea_ex
                    df_final = df_final.append(to_modify)
                    # es suficiente que se ejecute una regla
                    break
                except Exception as e:
                    tb = traceback.format_exc()
                    msg = f"No se pudo procesar la línea {idx} " + "\n" + linea + f"\n{str(e)}"
                    log.error(msg)


            if not exp_applied:
                # no se ha utilizado ninguna regla
                df_final = df_final.append(df.loc[idx])

    return True, df_final


def pretty(d, indent=0):
   for key, value in d.items():
      print('\t' * indent + str(key))
      if isinstance(value, dict):
         pretty(value, indent+1)
      else:
         print('\t' * (indent+1) + str(value))

def search_matches(linea, exp_list, reg_exp_dict):
    # linea es un string
    # exp_list de nombres de expresiones regulares a interactuar
    # diccionario con listas de expr reg (regex) a utilizar por cada nombre
    found_matches = dict()
    for exp in exp_list:
        success, match = search_match(linea, reg_exp_dict[exp])
        if success:
            found_matches[exp] = match
    return found_matches