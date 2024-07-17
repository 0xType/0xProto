import os
from fontTools.ttLib import TTFont

input_files = [
    '0xProto-Regular.otf',
    '0xProto-Regular.ttf',
    '0xProto-Italic.otf',
    '0xProto-Italic.ttf',
]
output_files = [
    'ZXProto-Regular.otf',
    'ZXProto-Regular.ttf',
    'ZXProto-Italic.otf',
    'ZXProto-Italic.ttf',
]

new_font_names = [
    'ZX Proto Regular',
    'ZX Proto Regular',
    'ZX Proto Italic',
    'ZX Proto Italic',
]

new_family_names = [
    'ZX Proto',
    'ZX Proto',
    'ZX Proto',
    'ZX Proto',
]

new_full_names = new_font_names

def change_font_names(input_files, output_files, new_font_names, new_family_names, new_full_names, directory='./fonts'):
    for input_file, output_file, new_font_name, new_family_name, new_full_name in zip(input_files, output_files, new_font_names, new_family_names, new_full_names):
        input_path = os.path.join(directory, input_file)
        output_path = os.path.join(directory, output_file)
        
        font = TTFont(input_path)
        
        name_table = font['name']

        version = None
        for record in name_table.names:
            if record.nameID == 5:
                version_str = record.toStr()
                version = version_str.split(' ')[1]
                break
        
        for record in name_table.names:
            if record.nameID == 1:  # Font Family Name
                record.string = new_family_name.encode('utf-16-be')
            elif record.nameID == 3:  # Unique font identifier
                unique_identifier = f"{version};0xType;{new_font_name}"
                record.string = unique_identifier.encode('utf-16-be')
            elif record.nameID == 4:  # Full Font Name
                record.string = new_full_name.encode('utf-16-be')
            elif record.nameID == 6:  # PostScript Name
                record.string = new_font_name.encode('utf-16-be')

        if 'CFF ' in font:
            cff = font['CFF '].cff
            cff.fontNames = [new_font_name]

            for font_name in cff.fontNames:
                cff[font_name].FullName = new_full_name
                cff[font_name].FamilyName = new_family_name
        
        font.save(output_path)
        print(f"generated {output_path}")

change_font_names(input_files, output_files, new_font_names, new_family_names, new_full_names)
