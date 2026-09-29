import re

ARCHIVO_ENTRADA = "archivo_original.cps"
ARCHIVO_SALIDA = "archivo_corregido.cps"


def swap_decimal_string(valor_decimal):
    valor_str = str(valor_decimal)
    primeros_18 = valor_str[:18]
    digito_19 = valor_str[18]

    pares = [primeros_18[i:i + 2] for i in range(0, len(primeros_18), 2)]
    pares_intercambiados = [par[::-1] for par in pares]

    resultado = ''.join(pares_intercambiados) + 'F' + digito_19
    return resultado


def contar_registros(lineas):
    """Recorre todas las lineas y cuenta ICCID (BinaryRec) e IMSI (Imsi)."""
    total_iccid = 0
    total_imsi = 0
    for linea in lineas:
        if re.search(r"BinaryRec\(\d+\)", linea):
            total_iccid += 1
        if re.search(r"Imsi\(\d+\)", linea):
            total_imsi += 1
    return total_iccid, total_imsi


def procesar(lineas):
    """Aplica las transformaciones (TransportKey y BinaryRec) linea por linea."""
    lineas_corregidas = []

    for linea in lineas:
        # Reemplazo de TransportKey sin modificar espacios
        match = re.search(r"TransportKey\(0, (\d{1,3}), (\d{1,3})\)", linea)
        if match:
            nueva_linea = re.sub(
                r"TransportKey\(0, \d{1,3}, \d{1,3}\)",
                f"TransportKey(0, {match.group(2)}, 101)",
                linea
            )
            lineas_corregidas.append(nueva_linea)

        # Conversion de BinaryRec
        elif "BinaryRec(" in linea:
            inicio = linea.find("BinaryRec(") + len("BinaryRec(")
            fin = linea.find(")", inicio)
            valor_decimal = linea[inicio:fin]
            valor_swap = swap_decimal_string(valor_decimal)
            nueva_linea = re.sub(
                r"BinaryRec\(\d+\)",
                f"BinaryRec({valor_swap})",
                linea
            )
            lineas_corregidas.append(nueva_linea)

        else:
            lineas_corregidas.append(linea)

    return lineas_corregidas


def main():
    with open(ARCHIVO_ENTRADA, "r") as archivo:
        lineas = archivo.readlines()

    total_iccid, total_imsi = contar_registros(lineas)

    print(f"Archivo: {ARCHIVO_ENTRADA}")
    print(f"Se cuentan {total_iccid} ICCID y {total_imsi} IMSI.")

    if total_iccid != total_imsi:
        print("AVISO: la cantidad de ICCID e IMSI no coincide, revisa el archivo.")

    respuesta = input("Desea proceder con el cambio? (s/n): ").strip().lower()
    if respuesta not in ("s", "si", "sí", "y", "yes"):
        print("Operacion cancelada. No se genero ningun archivo.")
        return

    lineas_corregidas = procesar(lineas)

    with open(ARCHIVO_SALIDA, "w") as archivo_nuevo:
        archivo_nuevo.writelines(lineas_corregidas)

    print(f"✅ El archivo corregido ha sido generado como '{ARCHIVO_SALIDA}'.")


if __name__ == "__main__":
    main()