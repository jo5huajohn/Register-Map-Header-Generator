# Register-Map-Header-Generator
This script generates a C header file containing all the register names and hex addresses from the datasheet. This can be used to save time during sensor library development.

### Options:
* -p | --pdf : The datasheet PDF
* -b | --beg : The page number that corresponds to the beginning of the register map.
* -e | --end : The page number that corresponds to the end of the register map.
* -f | --gen_file_name : A custom user defined name for the generated file.
* -P | --peripheral: The peripheral the register map belongs to. If no custom file name is provided, this will be used to name the generated header file.

**Example:** python3 gen_reg_defs_header.py -p ~/Downloads/DS-000292-ICM-42605-v1.6.pdf -b 57 -e 59 -P ICM42605

**Note:** I've only tested this with InvenSense and MAX30100 datasheets. I will be testing this script on other datasheets and make the script compatible with them if needed.
