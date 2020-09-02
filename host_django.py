#!/usr/bin/python3
import subprocess
import shlex
from termcolor import cprint, colored
import os


class Host():
    """This is the main application class of the whole program."""
    def __init__(self, server_name):
        self.server_name = server_name
        cprint("[+] Initializing the setup.", color='green')
        if os.getuid() != 0:
            cprint("[x] Root access not detected, run with sudo.", color='red')
            exit()
        else:
            cprint("[+] Root access acheived, running setup...", color='green')
    
    def check_program(self, program_name):
        cprint(f"[~] Checking {program_name} with 'which' command...", color='yellow')
        command = "which " + program_name
        process = subprocess.run(shlex.split(command), capture_output=True)
        if process.returncode != 0:
            cprint(f"[x] Not found '{program_name}' in system.", color='red')
            return False
        else:
            cprint(f"[+] Found '{program_name}' installation at {process.stdout.decode()[:-1]}", color='green')
            return True
    
    def generate_configuration(self, home_dir):
        self.validate_home_dir(home_dir)
        cprint(f"[~] Generating configuration content...", color='yellow')
        configuration_content = f"""
            <VirtualHost *:80>
            ServerName {self.server_name}
            ServerAdmin webmaster@localhost
            DocumentRoot /var/www/html
            ErrorLog ${{APACHE_LOG_DIR}}/error.log
            CustomLog ${{APACHE_LOG_DIR}}/access.log combined
            Alias /static {self.static_filepath}
            <Directory {self.static_filepath}>
            </Directory>
            <Directory {self.project_home}>
                   <Files wsgi.py>
                           Require all granted
                   </Files>
            </Directory>
            WSGIDaemonProcess shortner python-home={self.env_path} python-path={home_dir}
            WSGIProcessGroup shortner
            WSGIScriptAlias / {self.wsgi_filepath}
            </VirtualHost>
        """
        cprint(f"[+] Generated content for configuration file.", color='green')
        return configuration_content

    def install_program(self, program_name):
        cprint(f"[~] Installing {program_name}...", color='yellow')
        command = "apt install " + program_name
        process = subprocess.run(shlex.split(command), capture_output=True)
        if process.returncode != 0:
            cprint(f"[x] There is some problem while installing {program_name}.", color='red')
            return False
        else:
            cprint(f"[+] Installed {program_name}, successfully.", color='green')
            return True

    def run_command(self, command):
        cprint(f"[~] Running {command} ...", color='yellow')
        command_list = shlex.split(command)
        process = subprocess.run(command_list, capture_output=True)
        if process.returncode != 0:
            cprint(f"[x] There is some problem while running {command}.", color='red')
            return False
        else:
            cprint(f"[+] Successfully run {command}.", color='green')
            return True
    
    def validate_home_dir(self, home_dir):
        cprint("[~] Validating Project Home directory...", color='yellow')
        file_names = os.listdir(home_dir)
        success = False
        if "db.sqlite3" in file_names:
            cprint("[+] Validated, Found db.sqlite3 file in home dir.", color='green')
            self.db_sqlite3_filepath = os.path.join(home_dir, 'db.sqlite3')
            cprint(f"[+] Generate, filepath for 'db.sqlite3' i.e {self.db_sqlite3_filepath}", color='green')
            success = True
        if "manage.py" in file_names:
            cprint("[+] Validated, Found manage.py file in home dir.", color='green')
            self.manage_py_filepath = os.path.join(home_dir, 'manage.py')
            cprint(f"[+] Generate, filepath for 'manage.py' i.e {self.manage_py_filepath}", color='green')
            success = True
        else:
            cprint("[x] Found db.sqlite3 file in home dir.", color='green')
            success =  False
        
        self.home_dir = home_dir
        self.static_filepath = os.path.join(home_dir, 'static/')
        if home_dir[-1] != "/":
            self.project_home = os.path.join(home_dir, home_dir.split("/")[-1])
        else:
            self.project_home = os.path.join(home_dir, home_dir[:-1].split("/")[-1])
        self.wsgi_filepath = os.path.join(self.project_home, 'wsgi.py')
        if os.path.isdir(os.path.join(home_dir, 'env/')):
            self.env_path = os.path.join(home_dir, 'env/')
        return success

    def change_permission(self):
        cprint("[~] Begining to change permissions...", color='yellow')
        self.run_command("chmod 664 " + self.db_sqlite3_filepath)
        self.run_command("chown :www-data " + self.db_sqlite3_filepath)
        self.run_command("chown :www-data  " + self.home_dir)
        cprint("[+] Permission changed.", color='green')
        return True
    
    def restart_apache2(self):
        cprint("[~] Verifying Configuration content...", color='yellow')
        self.run_command("apache2ctl configtest")
        cprint("[+] Verified, configuration file content.", color='green')
        cprint("[~] Restaring 'apache2' ...", color='yellow')
        self.run_command('systemctl restart apache2')
        cprint("[+] PROJECT HOSTED. {*_*}/", color="blue")
    
    def change_default_conf(self, configuration_content):
        cprint("[~] Changing the content of 000-default.conf file...", color='yellow')
        with open('/etc/apache2/sites-available/000-default.conf', 'w+') as file:
            file.write(configuration_content)
        cprint("[+] Changed.", color='green')


            
logo = """ 
  .--.            .--.
 ( (`\\\\."--``--".//`) )
  '-.   __   __    .-'
   /   /__\ /__\   \      [+] Host Django
  |    \ 0/ \ 0/    |     [+] Automating the Django Hosting...
  \     `/   \`     /     [+] @Author: @vivekascoder
   `-.  /-\"\"\"-\  .-`      [+] @Github: vivekascoder/host_django
     /  '.___.'  \\
     \     I     /
      `;--'`'--;`
        '.___.'
"""


if __name__ == "__main__":
    cprint(logo, color="red")
    home_dir = input(colored("[~] Enter the project's folder: ", color='blue'))
    host_name = input(colored("[~] Enter the host name: ", color='blue'))
    host = Host(host_name)
    apache2 = host.check_program('apache2')
    if apache2 == False:
        host.install_program('apache2')
    lib_apache = host.install_program('libapache2-mod-wsgi-py3')
    home = host.validate_home_dir(home_dir)
    conf = host.generate_configuration(home_dir)
    host.change_default_conf(conf)
    host.change_permission()
    host.restart_apache2()


