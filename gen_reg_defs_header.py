import argparse
import string
import camelot
import os
import pandas as pd
import sys

parser = argparse.ArgumentParser(description='Import the register map from the datasheet PDF.')
parser.add_argument('--pdf',
                    '-p',
                    type=str,
                    required=True,
                    help='The datasheet PDF'
)
parser.add_argument('--beg',
                    '-b',
                    type=int,
                    required=True,
                    help='The page number that corresponds to the beginning of the register map.'
)
parser.add_argument('--end',
                    '-e',
                    type=int,
                    required=True,
                    help='The page number that corresponds to the end of the register map.'
)
parser.add_argument('--peripheral',
                    '-P',
                    type=str,
                    required=False,
                    help='The peripheral the register map belongs to.'
)

args = parser.parse_args()

peripheral = args.peripheral.upper()+"_"

try:
    os.path.exists(args.pdf)
except:
    sys.exit("File does not exist.\n")

register_map = camelot.read_pdf(filepath=args.pdf,
                                flavor="lattice",
                                pages=(str(args.beg) + "-" + str(args.end)), # Format: beg-end
                                line_scale=65,
                                strip_text=' .\n')


path_to_file = 'register_map.csv'

if os.path.exists(path_to_file):
    os.remove(path_to_file)

# iterate over extracted tables and export as excel individually
for i, table in enumerate(register_map, start=1):
    table.to_csv(path_to_file, mode='a', index=False)

register_map = pd.read_csv(path_to_file)

print("\n################################### USER NOTICE ###################################\n")
print("Since there are a lot of variations between data sheets, user must select the")
print("columns containing the hex addresses and register names to get the most accurate")
print("results.\n")
print("The user must input the column number of the hex addresss and register names")
print("separated by a comma with no whitespaces, with 0 corresponding to the first column.\n")
print(register_map.columns.values.tolist())

columns = input("\nPlease input the hex address and register name columns: ")

print("\n###################################################################################\n")

keep_cols = columns.split(",", 1)
keep_cols_str = [register_map.columns[int(keep_cols[0])], register_map.columns[int(keep_cols[1])]]

for col in register_map.columns:
    if col not in keep_cols_str:
        register_map.drop(columns=col, axis=1, inplace=True)

path_to_c_header = args.peripheral.lower() + "_reg.h"

if os.path.exists(path_to_c_header):
    os.remove(path_to_c_header)

c_header_file = open(path_to_c_header, "w")

c_header_file.write("#ifndef SENSOR_H_\n")
c_header_file.write("#define SENSOR_H_\n\n")

for index, row in register_map.iterrows():
    c_header_file.write("#define " + peripheral + row[keep_cols_str[1]] + "    " + "0x" + row[keep_cols_str[0]] + "\n")

c_header_file.write("\n#endif\n")
c_header_file.close

try:
    os.path.exists(path_to_c_header)
except:
    sys.exit("Failed to generate header file.\n")
finally:
    print("Header file successfully generated for your peripheral.\n")

sys.exit(0)