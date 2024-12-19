#!/usr/bin/env python3

import os
import pwd
from datetime import datetime
import subprocess

def format_text(input_text, width=70, tolerance=10):
    lines = []
    words = input_text.split()  # Split text into words
    current_line = []
    current_length = 0

    for word in words:
        word_length = len(word)
        # Check if adding the word would exceed the tolerance
        if current_length + word_length + len(current_line) <= width + tolerance:
            current_line.append(word)
            current_length += word_length
        else:
            # Check if the current line meets the lower tolerance limit
            if current_length >= width - tolerance:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_length = word_length
            else:
                # If not, try to adjust by appending the word to the current line
                if current_length + word_length + len(current_line) <= width + tolerance:
                    current_line.append(word)
                    current_length += word_length
                else:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                    current_length = word_length

    # Add any remaining text as the last line
    if current_line:
        lines.append(" ".join(current_line))

    return "\n".join(lines)

# Example usage
# input_text = "This is an example of a long string of text that we want to format such that no line exceeds 70 characters in width, with a tolerance of 10 characters, while not splitting any words in half."
# formatted_text = format_text(input_text)
# print(formatted_text)

class ModuleInfo:
    def __init__(self):
        self.name = input("Enter module name: ").strip()
        self.version = input("Enter module version: ").strip()
        self.desc = input("Enter module description: ").strip()
        self.description = format_text(self.desc)
        self.url = input("Enter module URL: ").strip()
        self.asurite = os.getlogin()
        if self.asurite == 'root':
            # prompt for asurite
            self.asurite = input("Please enter your ASURITE ID: ")
        user_info = pwd.getpwnam(self.asurite)
        full_name = user_info.pw_gecos.split(',')[0]
        self.admin = full_name.split()[1]
        self.date = datetime.today().strftime('%Y-%m-%d')
        self.edit = input("Do you want to edit this file? [y/n]: ").strip().lower()

def replace_templates(template, info):
    replacements = {
        '{{name}}': info.name,
        '{{version}}': info.version,
        '{{description}}': info.description,
        '{{url}}': info.url,
        '{{admin}}': info.admin,
        '{{asurite}}': info.asurite,
        '{{date}}': info.date
    }
    
    for placeholder, value in replacements.items():
        template = template.replace(placeholder, value)
    
    return template

def main():
    # Get user input
    module_info = ModuleInfo()

    # Read the template file
    with open("/packages/modulefiles/apps/template/module.tmpl", "r") as template_file:
        template = template_file.read()

    # Replace templates
    output = replace_templates(template, module_info)

    # Create the directory
    dir_path = os.path.join('/packages/modulefiles/apps', module_info.name)
    os.makedirs(dir_path, exist_ok=True)
    
    # Create the output file
    output_filename = os.path.join(dir_path, f"{module_info.version}.lua")
    with open(output_filename, "w") as output_file:
        output_file.write(output)
    
    if module_info.edit == 'y':
        module_info.edit = subprocess.run(["vim", output_filename])
    else:
        print(f"Module file created successfully: {output_filename}")    
    
if __name__ == "__main__":
    main()
