# ACPI Table Extractor

A Python utility for extracting ACPI tables from BIOS/UEFI firmware files.

## Description

This tool extracts ACPI tables from BIOS files by:
1. Using UEFIExtract to extract the BIOS contents
2. Locating ACPI tables by finding directories with the GUID: `7E374E25-8E01-4FEE-87F2-390C23C606CD`
3. Processing each table and saving it as an `.aml` file named after its signature
4. Handling filename collisions by adding numeric suffixes

## Prerequisites

- Python 3.6 or higher
- UEFIExtract utility (place in the `bin` directory)

## Installation

1. Clone this repository or download the script
2. Ensure UEFIExtract is present in the `bin` directory
3. Make the script executable (Linux/macOS):
   ```
   chmod +x acpi_extractor.py
   ```

## Usage

```
./acpi_extractor.py <bios_file> [output_dir]
```

Arguments:
- `bios_file`: Path to the BIOS/UEFI firmware file to process
- `output_dir`: (Optional) Directory to save extracted tables (default: "output")

## Example

```
./acpi_extractor.py my_bios.rom custom_output
```

This will extract all ACPI tables from `my_bios.rom` and save them to the `custom_output` directory. 