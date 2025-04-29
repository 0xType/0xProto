from fontTools.ttLib import TTFont
import os

def create_renamed_font(input_path, output_path, old_base_name, new_base_name_internal, new_base_name_file):
    """
    Create a new font with renamed font family from an existing font
    
    Parameters:
        input_path (str): Path to the input font file
        output_path (str): Path to the output font file
        old_base_name (str): Original font name base
        new_base_name_internal (str): New internal font name base (with spaces)
        new_base_name_file (str): New file name base (without spaces)
    """
    # Open the original font
    font = TTFont(input_path)
    
    # Process the name table
    for name_record in font['name'].names:
        decoded_name = name_record.toUnicode()
        
        if old_base_name in decoded_name:
            # For nameID 3 (Unique identifier) and nameID 6 (PostScript name), use new_base_name_file (without spaces)
            if name_record.nameID in (3, 6):
                new_string = decoded_name.replace(old_base_name, new_base_name_file)
            # For all other nameIDs, use new_base_name_internal (with spaces)
            else:
                new_string = decoded_name.replace(old_base_name, new_base_name_internal)
                
            name_record.string = new_string.encode(encoding=name_record.getEncoding())
    
    # Process CFF table if it exists (for .otf fonts)
    if 'CFF ' in font:
        try:
            # Get the CFF table
            cff_table = font['CFF ']
            
            # Process the font names in the CFF table
            if hasattr(cff_table, 'cff'):
                cff = cff_table.cff
                
                # Update the fontNames list
                for i, fontname in enumerate(cff.fontNames):
                    if old_base_name in fontname:
                        cff.fontNames[i] = fontname.replace(old_base_name, new_base_name_file)
                
                # Process each font in the CFF table
                for font_name in cff.keys():
                    cff_font = cff[font_name]
                    
                    # Update strings in the TopDict
                    if hasattr(cff_font, 'ROS'):
                        # Skip CID-keyed fonts which have different structure
                        continue
                        
                    # Update FontName (PostScript name)
                    if hasattr(cff_font, 'FontName') and old_base_name in cff_font.FontName:
                        cff_font.FontName = cff_font.FontName.replace(old_base_name, new_base_name_file)
                    
                    # Access and update the Top DICT strings
                    top_dict = cff_font.rawDict
                    
                    # Update FullName if it exists
                    if 'FullName' in top_dict and old_base_name in top_dict['FullName']:
                        top_dict['FullName'] = top_dict['FullName'].replace(old_base_name, new_base_name_internal)
                    
                    # Update FamilyName if it exists
                    if 'FamilyName' in top_dict and old_base_name in top_dict['FamilyName']:
                        top_dict['FamilyName'] = top_dict['FamilyName'].replace(old_base_name, new_base_name_internal)
                        
                    # Debug information
                    print(f"CFF table for {os.path.basename(input_path)}:")
                    if 'FullName' in top_dict:
                        print(f"  - FullName: {top_dict['FullName']}")
                    if 'FamilyName' in top_dict:
                        print(f"  - FamilyName: {top_dict['FamilyName']}")
                
        except Exception as e:
            print(f"Warning: Could not fully process CFF table: {e}")
            print(f"The font will still be processed, but CFF names might not be updated correctly.")
    
    # Save the modified font as a new file
    font.save(output_path)
    
    # Free memory
    font.close()
    
    return output_path

def process_font_directory(directory_path, old_base_name, new_base_name_internal, new_base_name_file):
    """
    Process all font files in a directory
    
    Parameters:
        directory_path (str): Path to the directory containing font files
        old_base_name (str): Original font name base
        new_base_name_internal (str): New internal font name base (with spaces)
        new_base_name_file (str): New file name base (without spaces)
    """
    # Check if directory exists
    if not os.path.isdir(directory_path):
        print(f"Error: Directory '{directory_path}' not found.")
        return
    
    # Get all files in the directory
    all_files = os.listdir(directory_path)
    font_files = []
    
    # Filter files matching the pattern
    for file in all_files:
        # Select files starting with 0xProto- and ending with .otf or .ttf
        if file.startswith(f"{old_base_name}-") and (file.endswith(".otf") or file.endswith(".ttf")):
            font_files.append(os.path.join(directory_path, file))
    
    # Display search results
    print(f"Total files in directory: {len(all_files)}")
    print(f"Detected font files: {len(font_files)}")
    
    if not font_files:
        print(f"Warning: No files matching '{old_base_name}-*.(otf|ttf)' pattern found.")
        # Display files in directory (for debugging)
        print("\nFiles in directory:")
        for file in all_files:
            print(f"- {file}")
        return
    
    # Create output directory
    output_dir = os.path.join(directory_path, "ZxProto")
    os.makedirs(output_dir, exist_ok=True)
    
    processed_files = 0
    failed_files = []
    otf_files_processed = 0
    ttf_files_processed = 0
    
    for input_path in font_files:
        # Get filename only (no path)
        filename = os.path.basename(input_path)
        
        # Create new filename (without spaces)
        new_filename = filename.replace(old_base_name, new_base_name_file)
        output_path = os.path.join(output_dir, new_filename)
        
        # Check if output file exists
        if os.path.exists(output_path):
            response = input(f"{output_path} already exists. Overwrite? (y/n): ")
            if response.lower() != 'y':
                print(f"Skipping {output_path}.")
                continue
        
        # Rename and copy font
        try:
            created_file = create_renamed_font(
                input_path, 
                output_path, 
                old_base_name, 
                new_base_name_internal, 
                new_base_name_file
            )
            print(f"Processed: {filename} -> {os.path.basename(created_file)}")
            processed_files += 1
            
            # Count by file type
            if filename.endswith(".otf"):
                otf_files_processed += 1
            elif filename.endswith(".ttf"):
                ttf_files_processed += 1
                
        except Exception as e:
            print(f"Error ({filename}): {e}")
            failed_files.append(filename)
    
    # Display results
    print("\nProcessing results:")
    print(f"- Target files: {len(font_files)}")
    print(f"- Successfully processed: {processed_files}")
    print(f"  - OTF files: {otf_files_processed}")
    print(f"  - TTF files: {ttf_files_processed}")
    
    if failed_files:
        print(f"- Failed: {len(failed_files)}")
        print("\nFiles that failed processing:")
        for f in failed_files:
            print(f"- {f}")
    
    print(f"\nConverted files have been saved to '{output_dir}' directory.")

if __name__ == "__main__":
    font_directory = "fonts"
    old_name = "0xProto"
    new_name_internal = "Zx Proto"  # Internal font name with spaces
    new_name_file = "ZxProto"       # File name without spaces
    
    print(f"Processing fonts in '{font_directory}' directory...")
    print(f"Search pattern: '{old_name}-*.(otf|ttf)'")
    print(f"Internal font name: '{old_name}' → '{new_name_internal}' (most name records)")
    print(f"PostScript name & unique ID: '{old_name}' → '{new_name_file}' (nameID 3 and 6)")
    print(f"CFF table names: Will be updated accordingly (for .otf fonts)")
    print(f"File name: '{old_name}' → '{new_name_file}'")
    print("")
    
    process_font_directory(font_directory, old_name, new_name_internal, new_name_file)
    print("\nProcessing complete.")