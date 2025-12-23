import os
import re
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import List, Dict

# Pre-compile Regex (This runs in C)
HEADER_REGEX = re.compile(r'^\[(\w+)\s+X2AbilityTemplate\]')
PROP_REGEX = re.compile(r'^\+(Loc\w+)="(.*)"')

def parse_single_file(file_path: str) -> List[Dict]:
    """
    Parses a single .int file. 
    This function is self-contained so it can be pickled to other processes.
    """
    results = []
    current_ability = {} # type: Dict[str, str]
    
    try:
        # 'errors="ignore"' handles potential encoding issues in mod files
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for Header
            header_match = HEADER_REGEX.match(line)
            if header_match:
                if current_ability:
                    results.append(current_ability)
                current_ability = {
                    "template_name": header_match.group(1),
                    "source_file": file_path,
                    "friendly_name": "Unknown",
                    "description": "",
                    "help_text": ""
                }
                continue

            # Check for Properties
            if current_ability:
                prop_match = PROP_REGEX.match(line)
                if prop_match:
                    key = prop_match.group(1)
                    val = prop_match.group(2)
                    
                    if key == "LocFriendlyName":
                        current_ability["friendly_name"] = val
                    elif key == "LocLongDescription":
                        current_ability["description"] = val
                    elif key == "LocHelpText":
                        current_ability["help_text"] = val

        # Add the last one
        if current_ability:
            results.append(current_ability)
            
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        
    return results

def scan_directory_fast(root_path: str) -> List[Dict]:
    """
    Finds all .int files and parses them using all CPU cores.
    """
    # 1. Quickly gather all .int file paths
    # os.walk is okay here, but glob can be cleaner. 
    # For maximum speed on huge dirs, os.scandir is best, but this is usually fast enough.
    files_to_scan = []
    for root, dirs, files in os.walk(root_path):
        for file in files:
            if file.lower().endswith(".int"):
                files_to_scan.append(os.path.join(root, file))

    print(f"Found {len(files_to_scan)} localization files. Processing...")

    all_abilities = []

    # 2. Parallel Processing
    # This uses all your CPU cores to parse files simultaneously.
    with ProcessPoolExecutor() as executor:
        # map returns results in order
        results = executor.map(parse_single_file, files_to_scan)
        
        for file_result in results:
            all_abilities.extend(file_result)
            
    return all_abilities