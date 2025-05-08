#!/usr/bin/env python3

import os
import pwd
import getpass
from datetime import datetime
import subprocess

import textwrap

def format_text(text):
    wrapper = textwrap.TextWrapper(
        width=78,
        expand_tabs=True,
        break_long_words=False,
        break_on_hyphens=False
    )
    wrapped_lines = wrapper.wrap(text)
    indented_text = '\n'.join('  ' + line for line in wrapped_lines)
    return indented_text

class ModuleInfo:
    def __init__(self):
        self.name = input("Enter module name: ").strip()
        self.version = input("Enter module version: ").strip()
        self.desc = input("Enter module description: ").strip()
        self.description = format_text(self.desc)
        self.url = input("Enter module URL: ").strip()
        
        try:
            self.asurite = os.getlogin()  # May fail in some cases (e.g., cron jobs, SSH)
        except Exception:
            self.asurite = getpass.getuser()  # Alternative method
        # Check if username is 'root' or 'software'
        if self.asurite in ['root', 'software']:
            self.asurite = input("Enter your asurite: ").strip()
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
    current_dir = os.getcwd()
    file_path = os.path.join(current_dir, "module.tmpl")
    with open(file_path, "r") as template_file:
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
