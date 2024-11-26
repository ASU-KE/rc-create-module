#!/usr/bin/env python3

import os
import pwd
from datetime import datetime
import subprocess
#from pathlib import Path

class ModuleInfo:
    def __init__(self):
        self.name = input("Enter module name: ").strip()
        self.version = input("Enter module version: ").strip()
        self.description = input("Enter module description: ").strip()
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
        module_info.edit = subprocess.run(["vim", output_file])
    else:
        print(f"Module file created successfully: {output_filename}")    
    
if __name__ == "__main__":
    main()
