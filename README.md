# ACPI Table Extractor

A Python utility for extracting ACPI tables from BIOS/UEFI firmware files.

## Description

This tool extracts ACPI tables from BIOS files by:
1. Using UEFIExtract to extract the BIOS contents
2. Locating ACPI tables by finding directories with the GUID: `7E374E25-8E01-4FEE-87F2-390C23C606CD`
3. Parsing the ACPI table headers to extract signature, OEM ID, and OEM Table ID
4. Saving tables as `.aml` files with intelligent naming based on table content
5. Handling filename collisions by adding numeric suffixes

## Features

- Parses binary ACPI table headers according to the ACPI specification
- Names files based on table signature, OEM ID, and OEM Table ID (e.g., `SSDT-HPQOEM-Plat_Wmi.aml`)
- Skips empty or meaningless OEM fields in filenames
- Falls back to signature-only filenames if header parsing fails
- Handles non-ASCII characters and ensures valid filenames

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

This will extract all ACPI tables from `my_bios.rom` and save them to the `custom_output` directory with intelligently formatted filenames based on each table's header information. 