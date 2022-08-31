#!/usr/bin/env python3.10

"""This script reads the PDF provided via command line arguments and generates
a header file containing the register names and addresses defined as macros.
"""

__author__ = "Joshua John"
__email__ = "joshuajohnv@protonmail.com"
__license__ = "Apache License 2.0"
__status__ = "Development"
__version__ = "0.5"

import argparse
import camelot
import os
import pandas as pd
import sys

from urllib.request import urlopen

# FUNCTION DEFINITIONS
def data_frame_cleanup(
        data_frame: pd.DataFrame,
        col_reg_name: str,
        col_reg_addr: str) -> pd.DataFrame:
    """Clean up the data frame.

    Keyword arguments:
    register_map (DataFrame): The data frame to be cleaned.
    col_reg_name (str): The column header register name.
    col_reg_addr (str): The column header register address.

    Returns:
    pd.DataFrame: The cleaned data frame.
    """
    # Delete unwanted columns.
    for col in data_frame.columns:
        if col not in [col_reg_name, col_reg_addr]:
            data_frame.drop(columns=col, axis=1, inplace=True)

    # Drop rows containing column headers.
    data_frame.drop_duplicates(keep=False,inplace=True)

    # Drop rows containing NaN.
    data_frame.dropna(inplace=True)

    # Drop rows containing Reserved name.
    data_frame.drop(index=data_frame[data_frame[col_reg_name].str.contains(pat="Reserved",
                                                                           case=False)].index,
                    inplace=True)

    # Replace tabs with underscores.
    data_frame[col_reg_name].replace("\t", "_", inplace=True, regex=True)

    return data_frame

def parse_args() -> argparse.Namespace:
    """Parse the arguments provided by the user as command line parameters.

    Returns:
    Namespace: The namespace containing the command line parameters.
    """
    parser = argparse.ArgumentParser(description='Import the register map \
        from the datasheet PDF.')

    parser.add_argument("--input",
                        "-i",
                        type=str,
                        required=True,
                        help="The path/URL to the datasheet PDF"
    )
    parser.add_argument("--beg",
                        "-b",
                        type=int,
                        required=True,
                        help="The page number that corresponds to the \
                            beginning of the register map."
    )
    parser.add_argument("--end",
                        "-e",
                        type=int,
                        required=True,
                        help="The page number that corresponds to the end of \
                            the register map."
    )
    parser.add_argument("--gen_file_name",
                        "-f",
                        type=str,
                        required=False,
                        help="A custom user defined name for the generated \
                            file."
    )
    parser.add_argument("--peripheral",
                        "-P",
                        type=str,
                        required=True,
                        help="The peripheral the register map belongs to. If \
                            no custom file name is provided, this will be \
                            used to name the generated header file."
    )
    parser.add_argument("--scale",
                        "-s",
                        type=int,
                        required=False,
                        help="Tweak the line size scaling factor used by the \
                            script to import the table from the PDF. The \
                            larger the value the smaller the detected lines. \
                            The default value is set to 100.",
                        default=100
    )

    return parser.parse_args()

def remove_if_exists(path_to_file: str):
    """Check if the file exists and remove it.

    Keyword arguments:
    path_to_file (str): Path to the file.
    """
    if os.path.exists(path_to_file):
        os.remove(path_to_file)

# END FUNCTION DEFINITIONS

params = parse_args()

# GLOBAL CONSTANTS
HEX_PREFIX = "0x"
SCALING_FACTOR = params.scale
PATH_TO_CSV_TABLE = "register_map.csv"
PDF_PAGE_RANGE: str = str(params.beg) + "-" + str(params.end)
PERIPHERAL_PREFIX: str = params.peripheral.upper() + "_"
PATH_TO_HEADER: str = params.gen_file_name if params.gen_file_name \
                        else PERIPHERAL_PREFIX.lower() + "reg.h"
SCALING_FACTOR = params.scale

# END GLOBAL CONSTANTS

try:
    os.path.exists(params.input)
except:
    try:
        urlopen(params.input)
    except:
        sys.exit("Argument passed is not a valid file or URL.\n")

# Read from the PDF and extract tables. A command line parameter to finetune
# the line_scale value will be introduced later.
register_map = camelot.read_pdf(filepath=params.input,
                                flavor="lattice",
                                pages=(PDF_PAGE_RANGE),
                                line_scale=SCALING_FACTOR,
                                strip_text=" .-\n")

remove_if_exists(PATH_TO_CSV_TABLE)

# Iterate over extracted tables and export as CSV.
for i, table in enumerate(register_map, start=1):
    table.to_csv(PATH_TO_CSV_TABLE, mode="a", index=False)

register_map = pd.read_csv(PATH_TO_CSV_TABLE)


print("\n########################## USER NOTICE ##########################\n")
print("Since there are a lot of variations between data sheets, the user")
print("must select the columns containing the register addresses and")
print("names to get the most accurate results.\n")
print("The user must then input the column number of the register names and")
print("addresses, with 0 corresponding to the first column.\n")
print(register_map.columns.values.tolist())
print("\n#################################################################\n")

COL_REG_NAME = input("Enter the column number of the register names: ")
COL_REG_ADDR = input("Enter the column number of the register addresses: ")

REG_NAME = register_map.columns[int(COL_REG_NAME)]
REG_ADDR = register_map.columns[int(COL_REG_ADDR)]

register_map = data_frame_cleanup(register_map, REG_NAME, REG_ADDR)

# Start writing to file.
remove_if_exists(PATH_TO_HEADER)

c_header_file = open(PATH_TO_HEADER, "w")
# Add include guards.
c_header_file.write("#ifndef " + PERIPHERAL_PREFIX + "H_\n")
c_header_file.write("#define " + PERIPHERAL_PREFIX + "H_\n\n")

# Find max length of string in register name column (for formatting purposes).
REG_NAME_MAX_LEN: int = len(PERIPHERAL_PREFIX) \
                        + register_map.loc[:,REG_NAME].map(len).max() \
                        + 2

# Write the register names and address to the file.

# Check if the register addresses contain the hex prefix 0x. If not, add it.
if register_map[REG_ADDR].str.contains(HEX_PREFIX).any():
    for index, row in register_map.iterrows():
        c_header_file.write("#define "
                            + f"{PERIPHERAL_PREFIX + row[REG_NAME].upper():<{REG_NAME_MAX_LEN}}"
                            + f"{row[REG_ADDR]:>4}"
                            + "\n")
else:
    for index, row in register_map.iterrows():
        c_header_file.write("#define "
                            + f"{PERIPHERAL_PREFIX + row[REG_NAME].upper():<{REG_NAME_MAX_LEN}}"
                            + f"{HEX_PREFIX + row[REG_ADDR]:>4}"
                            + "\n")

c_header_file.write("\n#endif\n")
c_header_file.close

# Cleanup
remove_if_exists(PATH_TO_CSV_TABLE)

try:
    os.path.exists(PATH_TO_HEADER)
except:
    sys.exit("\nFailed to generate header file.\n")
finally:
    print("\nHeader file successfully generated for your peripheral.\n")

sys.exit(0)