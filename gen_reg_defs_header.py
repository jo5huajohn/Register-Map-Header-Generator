import argparse
import camelot
import os
import pandas as pd
import sys

# FUNCTION DEFINITIONS
def parse_args() -> argparse.Namespace:
    '''
    Parse the arguments provided by the user as command line parameters.

    Returns:
    Namespace: The namespace containing the command line parameters.
    '''
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
    parser.add_argument('--generated_file_name',
                        '-f',
                        type=str,
                        required=False,
                        help='A custom user defined name for the generated file.'
    )
    parser.add_argument('--peripheral',
                        '-P',
                        type=str,
                        required=False,
                        help='The peripheral the register map belongs to. If no custom file name is provided, this will be used to name the generated header file.'
    )

    return parser.parse_args()

def remove_if_exists(path_to_file: str):
    """
    Check if the file exists and remove it.

    Parameters:
    path_to_file (str): Path to the file.
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

# Read from the PDF and extract tables. A command line parameter to finetune the line_scale value
# will be introduced later.
register_map = camelot.read_pdf(filepath=params.pdf,
                                flavor="lattice",
                                pages=(str(params.beg) + "-" + str(params.end)), # Format: beg-end
                                line_scale=65,
                                strip_text=' .\n')


PATH_TO_CSV_TABLE = 'register_map.csv'

remove_if_exists(PATH_TO_CSV_TABLE)

# Iterate over extracted tables and export as CSV.
for i, table in enumerate(register_map, start=1):
    table.to_csv(PATH_TO_CSV_TABLE, mode='a', index=False)

register_map = pd.read_csv(PATH_TO_CSV_TABLE)

print("\n################################### USER NOTICE ###################################\n")
print("Since there are a lot of variations between data sheets, user must select the")
print("columns containing the hex addresses and register names to get the most accurate")
print("results.\n")
print("The user must input the column number of the hex addresss and register names")
print("separated by a comma with no whitespaces, with 0 corresponding to the first column.\n")
print(register_map.columns.values.tolist())
print("\n###################################################################################\n")

columns = input("Please input the hex address and register name columns: ")


keep_cols = columns.split(",", 1)
keep_cols_str = [register_map.columns[int(keep_cols[0])], register_map.columns[int(keep_cols[1])]]

for col in register_map.columns:
    if col not in keep_cols_str:
        register_map.drop(columns=col, axis=1, inplace=True)

if params.generated_file_name:
    PATH_TO_C_HEADER = params.generated_file_name
else:
    PATH_TO_C_HEADER = PERIPHERAL.lower() + "_reg.h"

remove_if_exists(PATH_TO_C_HEADER)

c_header_file = open(PATH_TO_C_HEADER, "w")
# Add include guards.
c_header_file.write("#ifndef " + PERIPHERAL +"_H_\n")
c_header_file.write("#define " + PERIPHERAL +"_H_\n\n")

# Write the register names and address to the file.
for index, row in register_map.iterrows():
    c_header_file.write("#define " + PERIPHERAL + "_" + row[keep_cols_str[1]] + "    " + "0x" + row[keep_cols_str[0]] + "\n")

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