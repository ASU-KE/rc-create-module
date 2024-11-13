#!/usr/bin/env python3

import os
import pwd
from datetime import datetime
from pathlib import Path

class ModuleInfo:
    def __init__(self):
        self.name = input("Enter module name: ").strip()
        self.version = input("Enter module version: ").strip()
        self.description = input("Enter module description: ").strip()
        self.url = input("Enter module URL: ").strip()
        self.asurite = os.getlogin()
        user_info = pwd.getpwnam(self.asurite)
        full_name = user_info.pw_gecos.split(',')[0]
        self.admin = full_name.split()[1]
        self.date = datetime.today().strftime('%Y-%m-%d')


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
    #mod_path = Path('/packages/modulefiles/apps/')
    #dir_path = mod_path(module_info.name)
    dir_path = os.path.join('/packages/modulefiles/apps', module_info.name)
    os.makedirs(dir_path, exist_ok=True)
    
    # Create the output file
    output_filename = os.path.join(dir_path, f"{module_info.version}.lua")
    # output_filename = f"{module_info.name}_{module_info.version}.lua"
    with open(output_filename, "w") as output_file:
        output_file.write(output)

    print(f"Module file created successfully: {output_filename}")

if __name__ == "__main__":
    main()
