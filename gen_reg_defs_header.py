#!/usr/bin/env python3

"""This script reads the PDF provided via command line arguments and generates
a header file containing the register names and addresses defined as macros.
"""

__author__ = 'Joshua John'
__email__ = 'joshuajohnv@protonmail.com'
__status__ = 'Development'
__version__ = '0.3'

import argparse
import camelot
import os
import pandas as pd
import sys

# FUNCTION DEFINITIONS
def parse_args() -> argparse.Namespace:
    """Parse the arguments provided by the user as command line parameters.

    Returns:
    Namespace -- The namespace containing the command line parameters.
    """
    parser = argparse.ArgumentParser(description='Import the register map \
        from the datasheet PDF.')

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
                        help='The page number that corresponds to the \
                            beginning of the register map.'
    )
    parser.add_argument('--end',
                        '-e',
                        type=int,
                        required=True,
                        help='The page number that corresponds to the end of \
                            the register map.'
    )
    parser.add_argument('--generated_file_name',
                        '-f',
                        type=str,
                        required=False,
                        help='A custom user defined name for the generated \
                            file.'
    )
    parser.add_argument('--peripheral',
                        '-P',
                        type=str,
                        required=True,
                        help='The peripheral the register map belongs to. If \
                            no custom file name is provided, this will be \
                            used to name the generated header file.'
    )

    return parser.parse_args()

def remove_if_exists(path_to_file: str):
    """Check if the file exists and remove it.

    Keyword arguments:
    path_to_file (str) -- Path to the file.
    """
    if os.path.exists(path_to_file):
        os.remove(path_to_file)

# END FUNCTION DEFINITIONS

params = parse_args()

PERIPHERAL = params.peripheral.upper()

try:
    os.path.exists(params.pdf)
except:
    sys.exit("File does not exist.\n")

# Read from the PDF and extract tables. A command line parameter to finetune
# the line_scale value will be introduced later.
register_map = camelot.read_pdf(filepath=params.pdf,
                                flavor="lattice",
                                pages=(str(params.beg) + "-" + str(params.end)),
                                line_scale=65,
                                strip_text=' .\n')


PATH_TO_CSV_TABLE = 'register_map.csv'

remove_if_exists(PATH_TO_CSV_TABLE)

# Iterate over extracted tables and export as CSV.
for i, table in enumerate(register_map, start=1):
    table.to_csv(PATH_TO_CSV_TABLE, mode='a', index=False)

register_map = pd.read_csv(PATH_TO_CSV_TABLE)

print("\n########################## USER NOTICE ##########################\n")
print("Since there are a lot of variations between data sheets, user must")
print("select the columns containing the register addresses and names to")
print("get the most accurate results.\n")
print("The user must input the column number of the register names and")
print("addresses.\n")
print(register_map.columns.values.tolist())
print("\n#################################################################\n")

COL_REG_NAME = input("Enter the column number of the register names: ")
COL_REG_ADDR = input("Enter the column number of the register addresses: ")

REG_NAME = register_map.columns[int(COL_REG_NAME)]
REG_ADDR = register_map.columns[int(COL_REG_ADDR)]

for col in register_map.columns:
    if col not in [REG_NAME, REG_ADDR]:
        register_map.drop(columns=col, axis=1, inplace=True)

register_map.drop_duplicates(keep=False,inplace=True)

if params.generated_file_name:
    PATH_TO_C_HEADER = params.generated_file_name
else:
    PATH_TO_C_HEADER = PERIPHERAL.lower() + "_reg.h"

remove_if_exists(PATH_TO_C_HEADER)

c_header_file = open(PATH_TO_C_HEADER, "w")
# Add include guards.
c_header_file.write("#ifndef " + PERIPHERAL +"_H_\n")
c_header_file.write("#define " + PERIPHERAL +"_H_\n\n")

# Find max length of string in register name column (for formatting purposes)
REG_NAME_MAX_LEN = register_map.loc[:,REG_NAME].map(len).max() \
                    + len(PERIPHERAL) \
                    + 3

# Write the register names and address to the file.
for index, row in register_map.iterrows():
    c_header_file.write("#define "
        + f'{PERIPHERAL + "_" + row[REG_NAME]:<{REG_NAME_MAX_LEN}}'
        + f'{"0x" + row[REG_ADDR]:>4}'
        + "\n")

c_header_file.write("\n#endif\n")
c_header_file.close

# Cleanup
remove_if_exists(PATH_TO_CSV_TABLE)

try:
    os.path.exists(PATH_TO_C_HEADER)
except:
    sys.exit("\nFailed to generate header file.\n")
finally:
    print("\nHeader file successfully generated for your peripheral.\n")

sys.exit(0)