# Register-Map-Header-Generator
This script generates a C header file containing all the register names and hex addresses from the datasheet. This can be used to save time during sensor library development.

### Options:
* **-i | --input :** The file path or URL to the datasheet PDF
* **-b | --beg :** The page number that corresponds to the beginning of the register map.
* **-e | --end :** The page number that corresponds to the end of the register map. If the map starts and ends on the same page, you can just enter the same page number here.
* **-f | --gen_file_name :** A custom user defined name for the generated file.
* **-P | --peripheral:** The peripheral the register map belongs to. If no custom file name is provided, this will be used to name the generated header file.

**Example:** `python3 gen_reg_defs_header.py -i ~/Downloads/DS-000292-ICM-42605-v1.6.pdf -b 57 -e 59 -P ICM42605`

### Datasheets tested with:
* **Bosch**
    - BME280

* **Infineon**
    - ICM20498
    - ICM42605
    - MPU6050

* **Maxim**
    - MAX30100

* **ST**
    - STUSB4500

### Known Issues:
* In some scenarios where the new line escape sequence is used to split the register name, the words are combined. Eg.: MAX30100 datasheet.
* When tables that are not part of the register map are present on the same page, the script includes it in the generated header file. Eg.: BME280 and MPU6050 datasheets.