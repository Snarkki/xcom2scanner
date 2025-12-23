import os
import re
from concurrent.futures import ProcessPoolExecutor
from typing import List, Dict

# Regex: Case insensitive, tolerates whitespace, optional +, handles quotes or no quotes
HEADER_REGEX = re.compile(r'^\s*\[(\w+)\s+X2AbilityTemplate\]', re.IGNORECASE)
PROP_REGEX = re.compile(r'^\s*[\+]?(Loc\w+)\s*=\s*(.*)', re.IGNORECASE)

def read_file_content(file_path: str) -> List[str]:
    """
    Tries multiple encodings to read the file. 
    Crucial for XCOM 2 mods which mix UTF-8, UTF-16, and Windows-1252.
    """
    encodings = ['utf-8-sig', 'utf-16', 'cp1252', 'latin-1']
    
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                # Read strictly; if encoding is wrong, it usually throws UnicodeError immediately
                lines = f.readlines()
                
                # Sanity check: If we read "lines" but they look like binary garbage (lots of nulls), fail this encoding.
                # A valid text file shouldn't have null bytes in the first few lines.
                if len(lines) > 0 and '\0' in lines[0]:
                    continue
                    
                return lines
        except (UnicodeDecodeError, UnicodeError):
            continue
            
    # If all fail, return empty
    print(f"FAILED to read file (encoding issue): {file_path}")
    return []

def parse_single_file(file_path: str) -> List[Dict]:
    results = []
    
    # Defaults
    current_template = None
    current_data = {}

    lines = read_file_content(file_path)
    
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 1. Check for Header
        header_match = HEADER_REGEX.match(line)
        if header_match:
            # Save previous ability
            if current_template:
                # Only save if we found a template name
                results.append(current_data)

            # Reset for new ability
            current_template = header_match.group(1)
            current_data = {
                "template_name": current_template,
                "source_file": file_path,
                "friendly_name": "Unknown", # Default
                "description": "",
                "help_text": "",
                "promotion_text": "",
                "flyover_text": ""
            }
            continue

        # 2. Check for Properties (only if we are inside a template block)
        if current_template:
            prop_match = PROP_REGEX.match(line)
            if prop_match:
                key = prop_match.group(1)
                val = prop_match.group(2)
                
                # IMPROVEMENT: Remove comments (//) then strip quotes
                val = val.split('//')[0].strip().strip('"')
                # Cleanup: Remove surrounding quotes if they exist
                # .strip('"') removes " from start/end. 

                # Case-Insensitive Key Matching
                key_lower = key.lower()

                if key_lower == "locfriendlyname":
                    current_data["friendly_name"] = val
                elif key_lower == "loclongdescription":
                    current_data["description"] = val
                elif key_lower == "lochelptext":
                    current_data["help_text"] = val
                elif key_lower == "locpromotionpopuptext":
                    current_data["promotion_text"] = val
                elif key_lower == "locflyovertext":
                    current_data["flyover_text"] = val

    # Append the last one found in file
    if current_template:
        results.append(current_data)
        
    return results

def scan_directory_fast(root_path: str) -> List[Dict]:
    files_to_scan = []
    for root, _, files in os.walk(root_path):
        for file in files:
            if file.lower() == "xcomgame.int":
                files_to_scan.append(os.path.join(root, file))

    print(f"Found {len(files_to_scan)} 'XComGame.int' files. Processing...")

    all_abilities = []
    
    with ProcessPoolExecutor() as executor:
        results = executor.map(parse_single_file, files_to_scan)
        for file_result in results:
            all_abilities.extend(file_result)
            
    return all_abilities