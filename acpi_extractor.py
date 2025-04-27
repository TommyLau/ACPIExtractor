#!/usr/bin/env python3
"""
ACPI Table Extractor

Extracts ACPI tables from BIOS files using UEFIExtract and saves them as .aml files.
"""
import os
import sys
import subprocess
import shutil
import binascii
import struct

# Target GUID for ACPI tables
TARGET_GUID = "7E374E25-8E01-4FEE-87F2-390C23C606CD"


def find_uefi_extract():
    """Find UEFIExtract executable in the bin directory."""
    bin_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin")
    
    # Look for UEFIExtract with different possible extensions
    for name in ["UEFIExtract", "UEFIExtract.exe"]:
        path = os.path.join(bin_dir, name)
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    
    raise FileNotFoundError("UEFIExtract not found in bin directory")


def extract_bios(uefi_extract_path, bios_file):
    """Extract BIOS file using UEFIExtract."""
    # UEFIExtract will create the .dump directory in the current working directory
    dump_dir = f"{bios_file}.dump"
    
    # Remove the .dump directory if it already exists
    if os.path.exists(dump_dir):
        shutil.rmtree(dump_dir)
    
    try:
        # Run UEFIExtract with the GUID parameter
        subprocess.run(
            [uefi_extract_path, bios_file, TARGET_GUID],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Check if the .dump directory was created
        if not os.path.exists(dump_dir):
            raise FileNotFoundError(f"UEFIExtract did not create dump directory: {dump_dir}")
        
        return dump_dir
    except subprocess.CalledProcessError as e:
        print(f"Error executing UEFIExtract: {e}")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)


def find_acpi_directories(extract_dir):
    """Find directories containing the target GUID."""
    acpi_dirs = []
    
    for root, dirs, files in os.walk(extract_dir):
        for dirname in dirs:
            if TARGET_GUID.lower() in dirname.lower():
                acpi_dirs.append(os.path.join(root, dirname))
    
    return acpi_dirs


def parse_acpi_header(file_path):
    """Parse the ACPI table header from an AML file."""
    try:
        with open(file_path, 'rb') as f:
            # Read the ACPI table header (36 bytes)
            header = f.read(36)
            
            if len(header) < 36:
                return None
            
            # Extract the signature (first 4 bytes)
            signature = header[0:4].decode('ascii', errors='ignore')
            
            # Extract the OEM ID (bytes 10-15, 6 bytes)
            oem_id = header[10:16].decode('ascii', errors='ignore').strip()
            
            # Extract the OEM Table ID (bytes 16-23, 8 bytes)
            oem_table_id = header[16:24].decode('ascii', errors='ignore').strip()
            
            # Extract table revision (byte 8, 1 byte)
            revision = header[8]
            
            return {
                'signature': signature,
                'oem_id': oem_id,
                'oem_table_id': oem_table_id,
                'revision': revision
            }
    except Exception as e:
        print(f"Error parsing ACPI header: {e}")
    
    return None


def process_acpi_tables(acpi_dirs, output_dir):
    """Process each ACPI table and save to output directory."""
    os.makedirs(output_dir, exist_ok=True)
    processed_files = 0
    
    for acpi_dir in acpi_dirs:
        # Find all section directories (like "0 Raw section", "1 Raw section", etc, and sort them numerically
        section_dirs = [d for d in os.listdir(acpi_dir) 
                        if os.path.isdir(os.path.join(acpi_dir, d)) and "Raw section" in d]
        
        # Sort by extracting the number at the beginning and converting to int
        section_dirs.sort(key=lambda x: int(x.split()[0]))
        
        for section_dir in section_dirs:
            section_path = os.path.join(acpi_dir, section_dir)
            body_bin_path = os.path.join(section_path, "body.bin")
            
            if os.path.isfile(body_bin_path):
                # Extract ACPI header information
                header_info = parse_acpi_header(body_bin_path)
                
                if header_info and all(k in header_info for k in ('signature', 'oem_id', 'oem_table_id')):
                    # Use the extracted information for the filename
                    # Clean any invalid characters first
                    signature = ''.join(c if c.isalnum() or c in '-_' else '_' for c in header_info['signature'])
                    oem_id = ''.join(c if c.isalnum() or c in '-_' else '_' for c in header_info['oem_id'])
                    oem_table_id = ''.join(c if c.isalnum() or c in '-_' else '_' for c in header_info['oem_table_id'])
                    
                    # Only include non-empty and non-underscore parts in the filename
                    filename_parts = [signature]
                    if oem_id and oem_id != "_" and oem_id != "__" and oem_id != "___" and oem_id != "____" and oem_id != "_____" and oem_id != "______":
                        filename_parts.append(oem_id)
                    if oem_table_id and oem_table_id != "_" and oem_table_id != "__" and oem_table_id != "___" and oem_table_id != "____" and oem_table_id != "_____" and oem_table_id != "______" and oem_table_id != "_______" and oem_table_id != "________":
                        filename_parts.append(oem_table_id)
                    
                    filename = "-".join(filename_parts)
                else:
                    # Read the first 4 bytes of body.bin if header parsing failed
                    with open(body_bin_path, 'rb') as f:
                        signature = f.read(4)
                        if len(signature) < 4:
                            continue
                        
                        # Convert to ASCII string
                        try:
                            filename = signature.decode('ascii')
                        except UnicodeDecodeError:
                            # Use hex representation if not ASCII
                            filename = binascii.hexlify(signature).decode('ascii')[:4]
                
                # Handle filename collisions
                base_filename = filename
                suffix = ""
                counter = 2
                
                while os.path.exists(os.path.join(output_dir, f"{base_filename}{suffix}.aml")):
                    suffix = str(counter)
                    counter += 1
                
                output_file = os.path.join(output_dir, f"{base_filename}{suffix}.aml")
                
                # Copy the body.bin to the output file
                shutil.copy2(body_bin_path, output_file)
                processed_files += 1
                print(f"Extracted: {output_file}")
    
    return processed_files


def main():
    """Main function to run the ACPI table extraction."""
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <bios_file> [output_dir]")
        sys.exit(1)
    
    bios_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "output"
    
    if not os.path.isfile(bios_file):
        print(f"Error: BIOS file '{bios_file}' not found")
        sys.exit(1)
    
    try:
        uefi_extract = find_uefi_extract()
        print(f"Found UEFIExtract: {uefi_extract}")
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"Extracting BIOS: {bios_file}")
        dump_dir = extract_bios(uefi_extract, bios_file)
        
        print("Searching for ACPI tables...")
        acpi_dirs = find_acpi_directories(dump_dir)
        
        if not acpi_dirs:
            print("No ACPI tables with the target GUID found")
            sys.exit(0)
        
        count = process_acpi_tables(acpi_dirs, output_dir)
        print(f"Extraction complete: {count} ACPI tables saved to '{output_dir}'")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 