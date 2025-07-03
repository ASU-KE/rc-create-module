#!/usr/bin/env python3

import os
import pwd
import getpass
from datetime import datetime
import subprocess
import textwrap
import argparse
import sys
import json

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
        self.name = ""
        self.version = ""
        self.desc = ""
        self.description = ""
        self.url = ""
        self.asurite = ""
        self.admin = ""
        self.date = datetime.today().strftime('%Y-%m-%d')

def get_user_details(username=None, privileged_users=None):
    """Gets username and full name, handling errors."""
    if privileged_users is None:
        privileged_users = ['root', 'software']

    if username:
        asurite = username
    else:
        try:
            asurite = os.getlogin()
        except Exception:
            asurite = getpass.getuser()

    if asurite in privileged_users:
        asurite = input(f"Running as '{asurite}'. Please enter your personal username: ").strip()
        if not asurite:
            print("Error: Username cannot be empty.", file=sys.stderr)
            sys.exit(1)

    try:
        user_info = pwd.getpwnam(asurite)
        full_name = user_info.pw_gecos.split(',')[0]
        admin = full_name.split()[1]
        return asurite, admin
    except KeyError:
        print(f"Error: User '{asurite}' not found.", file=sys.stderr)
        sys.exit(1)
    except IndexError:
        print(f"Warning: Could not determine full name for user '{asurite}'. Using username as admin.", file=sys.stderr)
        return asurite, asurite


def replace_templates(template, info, domain):
    replacements = {
        '{{name}}': info.name,
        '{{version}}': info.version,
        '{{description}}': info.description,
        '{{url}}': info.url,
        '{{admin}}': info.admin,
        '{{asurite}}': f"{info.asurite}@{domain}",
        '{{date}}': info.date
    }
    
    for placeholder, value in replacements.items():
        template = template.replace(placeholder, value)
    
    return template

def main():
    # --- Configuration File Handling ---
    script_dir = os.path.dirname(os.path.realpath(__file__))
    config_file_path = os.path.join(script_dir, 'config.json')

    settings = {}
    try:
        with open(config_file_path, 'r') as config_file:
            config = json.load(config_file)
            settings = config.get('Settings', {})
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    default_output_dir = settings.get('output_dir', '/packages/modulefiles/apps')
    default_domain = settings.get('domain', 'asu.edu')
    default_template = settings.get('module_template', 'module.tmpl')
    default_editor = settings.get('editor', 'vim')
    privileged_users = settings.get('privileged_users', ['root', 'software'])

    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(
        description="Create a Lua module file for a manually installed application.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('-n', '--name', help="The name of the module.")
    parser.add_argument('-v', '--version', help="The version of the module.")
    parser.add_argument('-d', '--desc', help="A short, one-line description of the module.")
    parser.add_argument('-u', '--url', help="A URL for the software's homepage.")
    parser.add_argument('-a', '--asurite', help="The username of the module creator.")
    parser.add_argument(
        '-o', '--output-dir',
        default=default_output_dir,
        help=f"The base directory to write the module file to. (Default: {default_output_dir})"
    )
    parser.add_argument(
        '--domain',
        default=default_domain,
        help=f"The email domain for the module creator. (Default: {default_domain})"
    )
    parser.add_argument(
        '-e', '--edit',
        action='store_true',
        help=f"Immediately open the new module file in '{default_editor}' after creation."
    )
    args = parser.parse_args()

    module_info = ModuleInfo()

    # Populate from args or interactive input
    module_info.name = args.name or input("Enter module name: ").strip()
    module_info.version = args.version or input("Enter module version: ").strip()
    module_info.desc = args.desc or input("Enter module description: ").strip()
    module_info.url = args.url or input("Enter module URL: ").strip()

    if not all([module_info.name, module_info.version, module_info.desc]):
        print("Error: Name, version, and description are required.", file=sys.stderr)
        sys.exit(1)

    module_info.description = format_text(module_info.desc)
    module_info.asurite, module_info.admin = get_user_details(args.asurite, privileged_users)

    # Read the template file
    try:
        if os.path.isabs(default_template):
            file_path = default_template
        else:
            file_path = os.path.join(script_dir, default_template)
        with open(file_path, "r") as template_file:
            template = template_file.read()
    except FileNotFoundError:
        print(f"Error: Template file not found at '{file_path}'", file=sys.stderr)
        sys.exit(1)

    # Replace templates
    output = replace_templates(template, module_info, args.domain)

    # Create the directory
    try:
        dir_path = os.path.join(args.output_dir, module_info.name)
        os.makedirs(dir_path, exist_ok=True)
    except OSError as e:
        print(f"Error: Could not create directory '{dir_path}': {e}", file=sys.stderr)
        sys.exit(1)
    
    # Create the output file
    output_filename = os.path.join(dir_path, f"{module_info.version}.lua")
    try:
        with open(output_filename, "w") as output_file:
            output_file.write(output)
    except IOError as e:
        print(f"Error: Could not write to file '{output_filename}': {e}", file=sys.stderr)
        sys.exit(1)
    
    if args.edit:
        subprocess.run([default_editor, output_filename])
    else:
        print(f"Module file created successfully: {output_filename}")
        answer = input(f"Do you want to edit the module file with {default_editor} now? (y/n) ").lower().strip()
        if answer == 'y':
            subprocess.run([default_editor, output_filename])    
    
if __name__ == "__main__":
    main()

