#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import glob
import re
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables
import argparse

def modify_font_name(font, suffix="-NL"):
    """
    Add suffix to font names in the name table and CFF table if present.
    
    Args:
        font (TTFont): The font object
        suffix (str): Base suffix to add to the font names (without spacing)
    """
    # Remove the hyphen from the suffix as we'll add proper spacing dynamically
    base_suffix = suffix.lstrip('-')
    
    # Update name table
    if 'name' in font:
        # Font name IDs to modify
        # 1: Font Family name
        # 2: Font Subfamily name
        # 3: Unique identifier
        # 4: Full font name
        # 6: PostScript name
        # 16: Typographic family name
        # 17: Typographic subfamily name
        # 21: WWS family name
        name_ids_to_modify = [1, 3, 4, 6, 16, 21]
        
        for record in font['name'].names:
            if record.nameID in name_ids_to_modify:
                # Decode the name string
                try:
                    name_str = record.toUnicode()
                    
                    # Skip if suffix is already applied
                    if name_str.endswith(f"-{base_suffix}") or name_str.endswith(f" {base_suffix}"):
                        continue
                    
                    # Determine appropriate suffix format based on naming pattern
                    # Special case for PostScript name (always use hyphen for ID 6)
                    if record.nameID == 6:
                        actual_suffix = f"-{base_suffix}"
                    # For other names, check if they use hyphens or spaces
                    elif '-' in name_str and ' ' not in name_str:
                        actual_suffix = f"-{base_suffix}"
                    else:
                        actual_suffix = f" {base_suffix}"
                    
                    # Add suffix
                    new_name = name_str + actual_suffix
                    
                    # Update the record
                    record.string = new_name.encode(record.getEncoding())
                    
                    print(f"  - Updated name ID {record.nameID}: {name_str} -> {new_name}")
                except Exception as e:
                    print(f"  - Error updating name ID {record.nameID}: {e}")
    
    # Update CFF table if present
    if 'CFF ' in font:
        cff = font['CFF '].cff
        
        if len(cff) > 0:
            cff_font = cff[0]
            
            # Update CFF font name (equivalent to PostScript name)
            # PostScript names always use hyphens, no spaces allowed
            if hasattr(cff_font, 'FontName'):
                old_name = cff_font.FontName
                # Convert to string for comparison if it's bytes
                old_name_str = old_name.decode('ascii', errors='replace') if isinstance(old_name, bytes) else old_name
                
                # Skip if suffix is already applied
                if old_name_str.endswith(f"-{base_suffix}"):
                    pass
                else:
                    # PostScript names always use hyphens
                    actual_suffix = f"-{base_suffix}"
                    
                    # Convert suffix to bytes if the original is bytes
                    if isinstance(old_name, bytes):
                        cff_font.FontName = old_name + actual_suffix.encode('ascii')
                    else:
                        cff_font.FontName = old_name + actual_suffix
                    
                    print(f"  - Updated CFF FontName: {old_name_str} -> {cff_font.FontName.decode('ascii', errors='replace') if isinstance(cff_font.FontName, bytes) else cff_font.FontName}")
            
            # Update CFF font Full Name
            if hasattr(cff_font, 'FullName'):
                old_name = cff_font.FullName
                # Convert to string for comparison if it's bytes
                old_name_str = old_name.decode('ascii', errors='replace') if isinstance(old_name, bytes) else old_name
                
                # Skip if suffix is already applied
                if old_name_str.endswith(f"-{base_suffix}") or old_name_str.endswith(f" {base_suffix}"):
                    pass
                else:
                    # Determine format based on existing name
                    if '-' in old_name_str and ' ' not in old_name_str:
                        actual_suffix = f"-{base_suffix}"
                    else:
                        actual_suffix = f" {base_suffix}"
                    
                    # Convert suffix to bytes if the original is bytes
                    if isinstance(old_name, bytes):
                        cff_font.FullName = old_name + actual_suffix.encode('ascii')
                    else:
                        cff_font.FullName = old_name + actual_suffix
                    
                    print(f"  - Updated CFF FullName: {old_name_str} -> {cff_font.FullName.decode('ascii', errors='replace') if isinstance(cff_font.FullName, bytes) else cff_font.FullName}")
            
            # Update CFF font Family Name
            if hasattr(cff_font, 'FamilyName'):
                old_name = cff_font.FamilyName
                # Convert to string for comparison if it's bytes
                old_name_str = old_name.decode('ascii', errors='replace') if isinstance(old_name, bytes) else old_name
                
                # Skip if suffix is already applied
                if old_name_str.endswith(f"-{base_suffix}") or old_name_str.endswith(f" {base_suffix}"):
                    pass
                else:
                    # Determine format based on existing name
                    if '-' in old_name_str and ' ' not in old_name_str:
                        actual_suffix = f"-{base_suffix}"
                    else:
                        actual_suffix = f" {base_suffix}"
                    
                    # Convert suffix to bytes if the original is bytes
                    if isinstance(old_name, bytes):
                        cff_font.FamilyName = old_name + actual_suffix.encode('ascii')
                    else:
                        cff_font.FamilyName = old_name + actual_suffix
                    
                    print(f"  - Updated CFF FamilyName: {old_name_str} -> {cff_font.FamilyName.decode('ascii', errors='replace') if isinstance(cff_font.FamilyName, bytes) else cff_font.FamilyName}")

def modify_output_path(output_path, suffix="-NL"):
    """
    Add suffix to the output filename.
    Base suffix is applied with a hyphen, regardless of the font name format.
    
    Args:
        output_path (str): Original output path
        suffix (str): Suffix to add to the filename
    
    Returns:
        str: Modified output path
    """
    # Remove any leading hyphen from suffix for consistency
    base_suffix = suffix.lstrip('-')
    
    # Split the path into directory, filename, and extension
    directory, filename = os.path.split(output_path)
    name, ext = os.path.splitext(filename)
    
    # Add suffix to the name if it doesn't already have it
    if not (name.endswith(f"-{base_suffix}") or name.endswith(f" {base_suffix}")):
        # For filenames, we always use hyphen format
        new_name = name + f"-{base_suffix}"
        new_filename = new_name + ext
        new_path = os.path.join(directory, new_filename)
        return new_path
    
    return output_path

def remove_calt_feature(input_font_path, output_font_path=None, suffix="-NL"):
    """
    Remove the 'calt' OpenType feature from a font file and save as a new font.
    Also update font names with the given suffix.
    
    Args:
        input_font_path (str): Path to the input font file
        output_font_path (str, optional): Path to save the modified font. 
                                         If None, will use input name + suffix
        suffix (str): Suffix to add to the font names
    
    Returns:
        str: Path to the output font file
    """
    # Remove any leading hyphen from suffix for consistency when determining file paths
    base_suffix = suffix.lstrip('-')
    
    # Determine output path if not specified
    if output_font_path is None:
        file_name, file_ext = os.path.splitext(input_font_path)
        output_font_path = f"{file_name}-{base_suffix}{file_ext}"
    else:
        # Add suffix to output filename if it doesn't have it already
        output_font_path = modify_output_path(output_font_path, f"-{base_suffix}")
    
    # Open the font
    try:
        font = TTFont(input_font_path)
    except Exception as e:
        print(f"Error opening font file: {e}")
        return None
    
    # Check if the font has GSUB table (which contains OpenType features)
    if 'GSUB' not in font:
        print(f"  - This font does not have a GSUB table (no OpenType layout features)")
    else:
        # Get the GSUB table
        gsub = font['GSUB']
        
        # Check if there's a feature list
        if not hasattr(gsub.table, 'FeatureList') or not gsub.table.FeatureList.FeatureRecord:
            print(f"  - No feature records found in GSUB table")
        else:
            # Find and remove 'calt' features
            calt_indices = []
            for i, feature_record in enumerate(gsub.table.FeatureList.FeatureRecord):
                if feature_record.FeatureTag == 'calt':
                    calt_indices.append(i)
            
            if not calt_indices:
                print(f"  - No 'calt' feature found in the font")
            else:
                # Remove 'calt' feature references from feature list
                # We need to process in reverse order to maintain correct indices
                for index in sorted(calt_indices, reverse=True):
                    print(f"  - Removing 'calt' feature at index {index}")
                    del gsub.table.FeatureList.FeatureRecord[index]
                
                # Now we need to update any script records that might reference the 'calt' feature
                if hasattr(gsub.table, 'ScriptList') and gsub.table.ScriptList.ScriptRecord:
                    for script_record in gsub.table.ScriptList.ScriptRecord:
                        # Process default language system if present
                        if script_record.Script.DefaultLangSys:
                            remove_feature_indices_from_langsys(script_record.Script.DefaultLangSys, calt_indices)
                        
                        # Process other language systems
                        if script_record.Script.LangSysRecord:
                            for lang_sys_record in script_record.Script.LangSysRecord:
                                remove_feature_indices_from_langsys(lang_sys_record.LangSys, calt_indices)
    
    # Modify font names to add suffix
    modify_font_name(font, suffix)
    
    # Save the modified font
    try:
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_font_path) or '.', exist_ok=True)
        
        font.save(output_font_path)
        print(f"  - Modified font saved to: {output_font_path}")
        return output_font_path
    except Exception as e:
        print(f"  - Error saving modified font: {e}")
        return None

def remove_feature_indices_from_langsys(lang_sys, indices_to_remove):
    """
    Remove feature indices from a LangSys object and adjust remaining indices.
    
    Args:
        lang_sys: LangSys object from the GSUB table
        indices_to_remove (list): List of feature indices to remove
    """
    if not hasattr(lang_sys, 'FeatureIndex') or not lang_sys.FeatureIndex:
        return
    
    # Create a new list of feature indices, excluding the ones to remove
    # and adjusting the remaining indices for the removed features
    new_feature_indices = []
    for idx in lang_sys.FeatureIndex:
        # Skip indices that should be removed
        if idx in indices_to_remove:
            continue
        
        # Adjust the index based on how many removed indices precede it
        adjustment = sum(1 for removed_idx in indices_to_remove if removed_idx < idx)
        new_feature_indices.append(idx - adjustment)
    
    # Update the feature indices
    lang_sys.FeatureIndex = new_feature_indices

def process_directory(input_dir, output_dir, suffix="-NL"):
    """
    Process all font files in a directory.
    
    Args:
        input_dir (str): Directory containing font files
        output_dir (str): Directory to save processed fonts
        suffix (str): Suffix to add to the font names
    
    Returns:
        tuple: (success_count, failure_count)
    """
    # Normalize paths
    input_dir = os.path.normpath(input_dir)
    output_dir = os.path.normpath(output_dir)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all font files
    font_files = []
    for ext in ['.ttf', '.otf']:
        font_files.extend(glob.glob(os.path.join(input_dir, f'*{ext}')))
        # Also look in subdirectories
        font_files.extend(glob.glob(os.path.join(input_dir, f'**/*{ext}'), recursive=True))
    
    if not font_files:
        print(f"No font files found in {input_dir}")
        return 0, 0
    
    print(f"Found {len(font_files)} font files to process")
    
    # Process each font file
    success_count = 0
    failure_count = 0
    
    for font_file in font_files:
        # Calculate relative path from input_dir
        rel_path = os.path.relpath(font_file, input_dir)
        output_path = os.path.join(output_dir, rel_path)
        
        print(f"\nProcessing: {rel_path}")
        
        # Process the font
        result = remove_calt_feature(font_file, output_path, suffix)
        
        if result:
            success_count += 1
        else:
            failure_count += 1
    
    return success_count, failure_count

def process_single_file(input_file, output_file=None, suffix="-NL"):
    """
    Process a single font file.
    
    Args:
        input_file (str): Path to input font file
        output_file (str, optional): Path to save processed font
        suffix (str): Suffix to add to the font names
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Remove any leading hyphen from suffix for consistency
    base_suffix = suffix.lstrip('-')
    
    # If output_file is a directory, calculate the output file path
    if output_file and os.path.isdir(output_file):
        filename = os.path.basename(input_file)
        name, ext = os.path.splitext(filename)
        new_filename = f"{name}-{base_suffix}{ext}"
        output_file = os.path.join(output_file, new_filename)
    
    print(f"Processing: {input_file}")
    result = remove_calt_feature(input_file, output_file, suffix)
    
    return result is not None

def main():
    parser = argparse.ArgumentParser(description="Remove 'calt' OpenType feature from font files and add suffix to font names")
    parser.add_argument("input_path", 
                        help="Path to the input font file or directory containing font files")
    parser.add_argument("-o", "--output", 
                        help="Path to save the modified font or directory for output files (optional)")
    parser.add_argument("-s", "--suffix", default="-NL",
                        help="Suffix to add to font names (default: -NL)")
    args = parser.parse_args()
    
    input_path = args.input_path
    output_path = args.output
    suffix = args.suffix
    
    # Check if input is a directory
    if os.path.isdir(input_path):
        # If output is not specified, create a directory next to the input
        if not output_path:
            output_path = input_path + suffix
        
        print(f"Processing directory: {input_path}")
        print(f"Output directory: {output_path}")
        print(f"Using suffix: {suffix}")
        
        success, failure = process_directory(input_path, output_path, suffix)
        
        print(f"\nProcessing complete!")
        print(f"Successfully processed: {success} font files")
        if failure > 0:
            print(f"Failed to process: {failure} font files")
            sys.exit(1)
    else:
        # Process single file
        result = process_single_file(input_path, output_path, suffix)
        
        if result:
            print(f"Success! Font without 'calt' feature saved with {suffix} suffix.")
        else:
            print("Failed to process the font file.")
            sys.exit(1)

if __name__ == "__main__":
    main()