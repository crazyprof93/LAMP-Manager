# From crazyprof93 
# 26.03.2026 
# https://github.com/crazyprof93/LAMP-Manager
# Feel free to use, modify and distribute this code

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import subprocess
import mysql.connector
from mysql.connector import Error
import threading
import time
import os
import yaml
import webbrowser
import json

class LanguageManager:
    """Manages the multilingualism of the application"""
    
    def __init__(self):
        self.languages_dir = os.path.join(os.path.dirname(__file__), 'languages')
        self.current_language = 'en'
        self.translations = {}
        self.load_language('en')
    
    def load_language(self, lang_code):
        """Loads the language file"""
        try:
            lang_file = os.path.join(self.languages_dir, f'{lang_code}.json')
            if os.path.exists(lang_file):
                with open(lang_file, 'r', encoding='utf-8') as f:
                    self.translations = json.load(f)
                    self.current_language = lang_code
                    print(f"Language loaded: {lang_code}")
                    return True
            else:
                print(f"Language file not found: {lang_file}")
                return False
        except Exception as e:
            print(f"Error loading language: {e}")
            return False
    
    def get(self, key, *args):
        """Gets a translated text"""
        text = self.translations.get(key, key)
        if args:
            return text.format(*args)
        return text
    
    def get_available_languages(self):
        """Returns available languages"""
        languages = {}
        for file in os.listdir(self.languages_dir):
            if file.endswith('.json'):
                lang_code = file[:-5]
                if lang_code == 'de':
                    languages[lang_code] = 'Deutsch'
                elif lang_code == 'en':
                    languages[lang_code] = 'English'
                else:
                    languages[lang_code] = lang_code.upper()
        return languages

class LAMPManager:
    def __init__(self, root):
        self.root = root
        self.root.title("LAMP Server Manager")
        self.root.geometry("800x600")
        
        # Initialize language manager
        self.lang = LanguageManager()
        
        # Tab system for multiple servers
        self.servers = {}
        self.current_server_id = None
        self.server_counter = 0
        
        self.config_file = os.path.join(os.path.dirname(__file__), 'lamp_config.json')
        self.load_servers_config()
        
        if self.current_server_id and self.current_server_id in self.servers:
            self.load_server_config(self.current_server_id)
        
        self.quick_paths = {}
        self.server_running = False
        self.status_thread = None
        
        self.setup_ui()
        self.check_server_status()
    
    def load_servers_config(self):
        """Loads configuration for multiple servers"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    loaded_servers = config.get('servers', {})
                    if loaded_servers:
                        self.servers = loaded_servers.copy()
                    self.lang.load_language(config.get('language', 'de'))
                    if not self.servers:
                        self.add_default_server()
                    else:
                        self.current_server_id = list(self.servers.keys())[0]
            else:
                self.add_default_server()
        except Exception as e:
            print(f"Error loading server configuration: {e}")
            if not self.servers:
                self.add_default_server()
    
    def add_default_server(self):
        """Adds a default server - only if no servers exist"""
        if self.servers:
            return
        default_path = os.path.join(os.path.dirname(__file__), 'docker-compose.yml')
        server_id = f"server_{self.server_counter}"
        self.server_counter += 1
        self.servers[server_id] = {
            'name': 'LAMP Server 1',
            'compose_path': default_path
        }
        if not self.current_server_id:
            self.current_server_id = server_id
        self.save_servers_config()
    
    def save_servers_config(self):
        """Saves configuration for multiple servers"""
        try:
            config = {
                'servers': self.servers,
                'language': self.lang.current_language
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"Configuration saved to: {self.config_file}")
        except Exception as e:
            print(f"Error saving server configuration: {e}")
    
    def setup_ui(self):
        """Sets up the UI with tab system"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Globale Sprachauswahl oben rechts
        lang_frame = ttk.Frame(main_frame)
        lang_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.E, tk.N), pady=(0, 10))
        
        self.lang_label = ttk.Label(lang_frame, text=self.lang.get('language') + ":")
        self.lang_label.pack(side=tk.RIGHT, padx=(0, 5))
        
        self.lang_var = tk.StringVar(value=self.lang.get_available_languages()[self.lang.current_language])
        self.lang_combo = ttk.Combobox(lang_frame, textvariable=self.lang_var, width=10, state='readonly')
        self.lang_combo['values'] = list(self.lang.get_available_languages().values())
        self.lang_combo.pack(side=tk.RIGHT)
        self.lang_combo.bind('<<ComboboxSelected>>', lambda e: self.change_language(self.lang_var.get()))
        
        # Tooltip für Sprachauswahl
        self.create_tooltip(self.lang_combo, self.lang.get('select_language'))
        
        # Tab control for servers
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.server_tabs = {}
        self.create_server_tabs()
        
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
    
    def create_tooltip(self, widget, text):
        """Creates a tooltip for a widget"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(tooltip, text=text, background="lightyellow", 
                           relief=tk.SOLID, borderwidth=1, font=("Arial", 9))
            label.pack()
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def create_server_tabs(self):
        """Creates tabs for all servers"""
        for server_id, server_config in self.servers.items():
            self.create_server_tab(server_id, server_config)
        self.add_plus_tab()
    
    def create_server_tab(self, server_id, server_config):
        """Creates a single server tab"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text=server_config['name'])
        self.server_tabs[server_id] = tab_frame
        
        tab_frame.server_config = server_config
        tab_frame.server_id = server_id
        
        compose_file = server_config['compose_path']
        tab_frame.compose_file = compose_file
        tab_frame.compose_path = os.path.dirname(compose_file)
        
        # Quick-Access Pfade direkt am Tab speichern
        tab_frame.quick_paths = {
            'server_logs': os.path.join(tab_frame.compose_path, 'logs'),
            'database_logs': os.path.join(tab_frame.compose_path, 'db'),
            'www_folder': os.path.join(tab_frame.compose_path, 'www')
        }
        
        try:
            with open(tab_frame.compose_file, 'r') as f:
                yaml_content = yaml.safe_load(f)
                tab_frame.db_config = self.extract_db_config(yaml_content)
                tab_frame.server_config_docker = self.extract_server_config(yaml_content)
        except Exception as e:
            print(f"Error loading configuration for {server_id}: {e}")
            tab_frame.db_config = self.get_default_db_config()
            tab_frame.server_config_docker = {}
        
        self.create_server_ui(tab_frame, server_id)
    
    def extract_db_config(self, yaml_content):
        """Extracts the database configuration from YAML"""
        try:
            services = yaml_content.get('services', {})
            db_service = services.get('database', services.get('db', services.get('mysql', {})))
            if db_service:
                env = db_service.get('environment', {})
                ports = db_service.get('ports', ['3306:3306'])
                db_port = ports[0].split(':')[0] if ports else '3306'
                db_password = env.get('MYSQL_ROOT_PASSWORD', 'root')
                db_user = env.get('MYSQL_ROOT_USER', 'root')
                return {
                    'host': '127.0.0.1',
                    'port': int(db_port),
                    'user': db_user,
                    'password': db_password
                }
        except Exception as e:
            print(f"Error extracting DB configuration: {e}")
        return self.get_default_db_config()
    
    def extract_server_config(self, yaml_content):
        """Extracts the server configuration from YAML"""
        try:
            services = yaml_content.get('services', {})
            config = {}
            web_service = services.get('web', services.get('apache', services.get('nginx', {})))
            if web_service and web_service.get('ports'):
                web_port = web_service['ports'][0].split(':')[0]
                config['web'] = {'port': web_port, 'url': f'http://localhost:{web_port}'}
            pma_service = services.get('phpmyadmin', {})
            if pma_service and pma_service.get('ports'):
                pma_port = pma_service['ports'][0].split(':')[0]
                config['phpmyadmin'] = {'port': pma_port, 'url': f'http://localhost:{pma_port}'}
            db_service = services.get('database', services.get('db', services.get('mysql', {})))
            if db_service and db_service.get('ports'):
                db_port = db_service['ports'][0].split(':')[0]
                config['database'] = {'port': db_port, 'host': '127.0.0.1'}
            return config
        except Exception as e:
            print(f"Error extracting server configuration: {e}")
            return {}
    
    def create_server_ui(self, parent_frame, server_id):
        """Creates the UI for a specific server"""
        tab_config = parent_frame
        server_config = tab_config.server_config_docker

        # ── Server-Frame ──────────────────────────────────────────────────────
        server_frame = ttk.LabelFrame(parent_frame, text=self.lang.get('server_control'), padding="10")
        server_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # YAML-Datei Anzeige
        yaml_frame = ttk.Frame(server_frame)
        yaml_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        yaml_title_label = ttk.Label(yaml_frame, text=self.lang.get('docker_compose'))
        yaml_title_label.grid(row=0, column=0, padx=5, sticky=tk.W)
        yaml_label = ttk.Label(yaml_frame, text=tab_config.compose_file, font=("Arial", 9))
        yaml_label.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        
        # Server-Buttons
        start_btn = ttk.Button(server_frame, text=self.lang.get('start_server'),
                               command=lambda: self.start_server(server_id))
        start_btn.grid(row=1, column=0, padx=5, pady=5)
        
        stop_btn = ttk.Button(server_frame, text=self.lang.get('stop_server'),
                              command=lambda: self.stop_server(server_id))
        stop_btn.grid(row=1, column=1, padx=5, pady=5)
        
        delete_btn = ttk.Button(server_frame, text=self.lang.get('delete_server'),
                                command=lambda: self.delete_server(server_id))
        delete_btn.grid(row=1, column=2, padx=5, pady=5)
        
        # Status-Labels
        info_frame = ttk.Frame(server_frame)
        info_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        web_port  = server_config.get('web', {}).get('port', '8080')
        pma_port  = server_config.get('phpmyadmin', {}).get('port', '8081')
        db_port   = server_config.get('database', {}).get('port', '3306')
        
        web_label = ttk.Label(info_frame, foreground="red")
        web_label.grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        
        pma_label = ttk.Label(info_frame, foreground="red")
        pma_label.grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        
        db_label = ttk.Label(info_frame, foreground="red")
        db_label.grid(row=2, column=0, padx=5, pady=2, sticky=tk.W)

        # ── Quick-Access Frame ────────────────────────────────────────────────
        quick_frame = ttk.LabelFrame(parent_frame, text=self.lang.get('quick_access'), padding="10")
        quick_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        open_web_btn = ttk.Button(quick_frame, text=self.lang.get('open_web'),
                                  command=lambda: self.open_url(server_id, 'web'))
        open_web_btn.grid(row=0, column=0, padx=5, pady=5)
        
        open_pma_btn = ttk.Button(quick_frame, text=self.lang.get('open_phpmyadmin'),
                                  command=lambda: self.open_url(server_id, 'phpmyadmin'))
        open_pma_btn.grid(row=0, column=1, padx=5, pady=5)
        
        server_logs_btn = ttk.Button(quick_frame, text=self.lang.get('server_logs'),
                                     command=lambda: self.open_folder(server_id, 'server_logs'))
        server_logs_btn.grid(row=0, column=2, padx=5, pady=5)
        
        db_logs_btn = ttk.Button(quick_frame, text=self.lang.get('database_logs'),
                                 command=lambda: self.open_folder(server_id, 'database_logs'))
        db_logs_btn.grid(row=0, column=3, padx=5, pady=5)
        
        www_folder_btn = ttk.Button(quick_frame, text=self.lang.get('www_folder'),
                                    command=lambda: self.open_folder(server_id, 'www_folder'))
        www_folder_btn.grid(row=0, column=4, padx=5, pady=5)

        # ── Database Frame ───────────────────────────────────────────────────
        db_frame = ttk.LabelFrame(parent_frame, text=self.lang.get('database_management'), padding="10")
        db_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        refresh_db_btn = ttk.Button(db_frame, text=self.lang.get('refresh_databases'),
                                    command=lambda: self.refresh_databases(server_id))
        refresh_db_btn.grid(row=0, column=0, padx=5, pady=5)
        
        new_db_btn = ttk.Button(db_frame, text=self.lang.get('new_database'),
                                command=lambda: self.create_database(server_id))
        new_db_btn.grid(row=0, column=1, padx=5, pady=5)
        
        del_db_btn = ttk.Button(db_frame, text=self.lang.get('delete_database'),
                                command=lambda: self.delete_database(server_id))
        del_db_btn.grid(row=0, column=2, padx=5, pady=5)
        
        manage_users_btn = ttk.Button(db_frame, text=self.lang.get('manage_users'),
                                      command=lambda: self.manage_users(server_id))
        manage_users_btn.grid(row=0, column=3, padx=5, pady=5)
        
        # Database-Tree
        list_frame = ttk.Frame(db_frame)
        list_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        columns = ('Users', 'Size', 'Tables')
        db_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', height=15)
        db_tree.heading('#0', text=self.lang.get('database_name'))
        db_tree.heading('Users', text=self.lang.get('users'))
        db_tree.heading('Size', text=self.lang.get('size'))
        db_tree.heading('Tables', text=self.lang.get('tables'))
        db_tree.column('#0', width=150)
        db_tree.column('Users', width=200)
        db_tree.column('Size', width=100)
        db_tree.column('Tables', width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=db_tree.yview)
        db_tree.configure(yscrollcommand=scrollbar.set)
        db_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Status Bar with GitHub link
        status_frame = ttk.Frame(parent_frame)
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        status_bar = ttk.Label(status_frame, text=self.lang.get('ready'), relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        github_btn = ttk.Button(status_frame, text='GitHub', 
                               command=lambda: webbrowser.open('https://github.com/crazyprof93/LAMP-Manager'))
        github_btn.grid(row=0, column=1, padx=(5, 0))
        
        status_frame.columnconfigure(0, weight=1)

        # ── Alle Widget-Referenzen zentral speichern ──────────────────────────
        # Keys are stable internal names, NOT translated text.
        parent_frame.ui_elements = {
            # LabelFrames (for title translation)
            'server_frame':     server_frame,
            'quick_frame':      quick_frame,
            'db_frame':         db_frame,
            # Labels
            'yaml_title_label': yaml_title_label,
            'yaml_label':       yaml_label,
            'web_label':        web_label,
            'pma_label':        pma_label,
            'db_label':         db_label,
            'status_bar':       status_bar,
            'github_btn':        github_btn,
            # Port info for status labels
            'web_port':         web_port,
            'pma_port':         pma_port,
            'db_port':          db_port,
            # Buttons Server
            'start_btn':        start_btn,
            'stop_btn':         stop_btn,
            'delete_btn':       delete_btn,
            # Buttons Quick-Access
            'open_web_btn':     open_web_btn,
            'open_pma_btn':     open_pma_btn,
            'server_logs_btn':  server_logs_btn,
            'db_logs_btn':      db_logs_btn,
            'www_folder_btn':   www_folder_btn,
            # Buttons Database
            'refresh_db_btn':   refresh_db_btn,
            'new_db_btn':       new_db_btn,
            'del_db_btn':       del_db_btn,
            'manage_users_btn': manage_users_btn,
            # Tree
            'db_tree':          db_tree,
        }

        # Initialize status labels
        self._update_status_labels(parent_frame.ui_elements, running=False)

        # Grid weights
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.rowconfigure(2, weight=1)
        server_frame.columnconfigure(1, weight=1)
        info_frame.columnconfigure(0, weight=1)
        yaml_frame.columnconfigure(1, weight=1)
        for col in range(5):
            quick_frame.columnconfigure(col, weight=1)
        for col in range(4):
            db_frame.columnconfigure(col, weight=1)
        db_frame.rowconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
    
    def _update_status_labels(self, ui_elements, running: bool):
        """Sets the three status labels based on the running state."""
        state_key  = 'online' if running else 'offline'
        state_text = self.lang.get(state_key)
        color      = 'green' if running else 'red'

        web_port = ui_elements.get('web_port', '8080')
        pma_port = ui_elements.get('pma_port', '8081')
        db_port  = ui_elements.get('db_port',  '3306')

        ui_elements['web_label'].config(
            text=f"🌐 {self.lang.get('web_server')} (localhost:{web_port}) {state_text}",
            foreground=color)
        ui_elements['pma_label'].config(
            text=f"🗄️ {self.lang.get('phpmyadmin')} (localhost:{pma_port}) {state_text}",
            foreground=color)
        ui_elements['db_label'].config(
            text=f"🔧 {self.lang.get('database')} (localhost:{db_port}) {state_text}",
            foreground=color)

    def add_plus_tab(self):
        """Adds a + tab for adding new servers"""
        plus_frame = ttk.Frame(self.notebook)
        self.notebook.add(plus_frame, text="+")
        add_btn = ttk.Button(plus_frame, text=self.lang.get('add_server'), command=self.add_new_server)
        add_btn.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    def add_new_server(self):
        """Adds a new server - first select YAML file"""
        yaml_file = filedialog.askopenfilename(
            title=self.lang.get('select_yaml_file'),
            filetypes=[
                (self.lang.get('yaml_files'), '*.yml *.yaml'),
                (self.lang.get('all_files'), '*.*')
            ],
            parent=self.root
        )
        if not yaml_file:
            return
        try:
            with open(yaml_file, 'r') as f:
                yaml_content = yaml.safe_load(f)
                if not yaml_content or 'services' not in yaml_content:
                    messagebox.showerror(self.lang.get('error'), self.lang.get('invalid_yaml_file'))
                    return
                if self.check_container_conflicts(yaml_file, yaml_content):
                    return
        except Exception as e:
            messagebox.showerror(self.lang.get('error'), self.lang.get('yaml_read_error', str(e)))
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title(self.lang.get('add_server'))
        dialog.geometry("500x300")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.focus_set()
        
        ttk.Label(dialog, text=self.lang.get('docker_compose_file')).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        yaml_label = ttk.Label(dialog, text=yaml_file, font=("Arial", 9))
        yaml_label.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(dialog, text=self.lang.get('select_file'),
                   command=lambda: self.change_yaml_file(dialog, yaml_label)).grid(row=0, column=3, padx=5)
        
        ttk.Label(dialog, text=self.lang.get('server_name')).grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))
        name_entry.insert(0, f"LAMP Server {len(self.servers) + 1}")
        
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=2, column=0, columnspan=4, pady=20)
        ttk.Button(button_frame, text=self.lang.get('save'),
                   command=lambda: self.save_new_server(dialog, name_entry.get(), yaml_label.cget('text'))).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text=self.lang.get('cancel'),
                   command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        dialog.columnconfigure(1, weight=1)
    
    def change_yaml_file(self, dialog, yaml_label):
        """Changes the YAML file in the dialog"""
        yaml_file = filedialog.askopenfilename(
            title=self.lang.get('select_yaml_file'),
            filetypes=[(self.lang.get('yaml_files'), '*.yml *.yaml'), (self.lang.get('all_files'), '*.*')],
            parent=dialog
        )
        if yaml_file:
            try:
                with open(yaml_file, 'r') as f:
                    yaml_content = yaml.safe_load(f)
                    if not yaml_content or 'services' not in yaml_content:
                        messagebox.showerror(self.lang.get('error'), self.lang.get('invalid_yaml_file'))
                        return
            except Exception as e:
                messagebox.showerror(self.lang.get('error'), self.lang.get('yaml_read_error', str(e)))
                return
            yaml_label.config(text=yaml_file)
            messagebox.showinfo(self.lang.get('success'), self.lang.get('yaml_changed', yaml_file))
    
    def save_new_server(self, dialog, name, yaml_file):
        """Saves a new server"""
        if not name or not yaml_file:
            messagebox.showwarning(self.lang.get('warning'), self.lang.get('fill_required_fields'))
            return
        for server_id, server_config in self.servers.items():
            if server_config.get('name') == name:
                messagebox.showwarning(self.lang.get('warning'), self.lang.get('server_exists', name))
                return
        
        self.server_counter += 1
        server_id = f"server_{self.server_counter}"
        self.servers[server_id] = {'name': name, 'compose_path': yaml_file}
        self.save_servers_config()
        self.create_server_tab(server_id, self.servers[server_id])
        self.move_plus_tab_to_end()
        self.notebook.select(self.server_tabs[server_id])
        self.current_server_id = server_id
        dialog.destroy()
        messagebox.showinfo(self.lang.get('success'), self.lang.get('server_added', name))
    
    def delete_server(self, server_id):
        """Deletes a server with container options"""
        if not server_id or server_id not in self.servers:
            return
        server_config = self.servers[server_id]
        server_name = server_config['name']
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"{self.lang.get('delete_server')}: {server_name}")
        dialog.geometry("550x400")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.focus_set()
        
        ttk.Label(dialog, text=self.lang.get('confirm_delete_server', server_name),
                  font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, padx=20, pady=10)
        ttk.Label(dialog, text=self.lang.get('container_options'), font=('Arial', 10, 'bold')).grid(
            row=1, column=0, columnspan=2, padx=20, pady=(10, 5), sticky=tk.W)
        
        container_var = tk.StringVar(value="keep")
        ttk.Radiobutton(dialog, text=self.lang.get('container_keep'), variable=container_var, value="keep").grid(
            row=2, column=0, columnspan=2, padx=20, pady=2, sticky=tk.W)
        ttk.Radiobutton(dialog, text=self.lang.get('container_stop'), variable=container_var, value="stop").grid(
            row=3, column=0, columnspan=2, padx=20, pady=2, sticky=tk.W)
        ttk.Radiobutton(dialog, text=self.lang.get('container_remove'), variable=container_var, value="remove").grid(
            row=4, column=0, columnspan=2, padx=20, pady=2, sticky=tk.W)
        
        ttk.Label(dialog, text=self.lang.get('folder_options'), font=('Arial', 10, 'bold')).grid(
            row=5, column=0, columnspan=2, padx=20, pady=(15, 5), sticky=tk.W)
        folders_var = tk.StringVar(value="keep")
        ttk.Radiobutton(dialog, text=self.lang.get('folder_keep'), variable=folders_var, value="keep").grid(
            row=6, column=0, columnspan=2, padx=20, pady=2, sticky=tk.W)
        ttk.Radiobutton(dialog, text=self.lang.get('folder_remove'), variable=folders_var, value="remove").grid(
            row=7, column=0, columnspan=2, padx=20, pady=2, sticky=tk.W)
        
        warning_label = ttk.Label(dialog, text=self.lang.get('delete_server_warning'),
                                  foreground="red", wraplength=450)
        warning_label.grid(row=8, column=0, columnspan=2, padx=20, pady=5)
        
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=9, column=0, columnspan=2, pady=10)
        
        def delete_action():
            try:
                container_option = container_var.get()
                folders_option   = folders_var.get()
                compose_path = os.path.dirname(server_config['compose_path'])
                
                if container_option == "stop":
                    os.chdir(compose_path)
                    subprocess.run(['docker-compose', 'stop'], capture_output=True, text=True)
                elif container_option == "remove":
                    os.chdir(compose_path)
                    subprocess.run(['docker-compose', 'down', '-v'], capture_output=True, text=True)
                
                if folders_option == "remove":
                    import shutil
                    for folder in ['www', 'logs', 'db']:
                        folder_path = os.path.join(compose_path, folder)
                        if os.path.exists(folder_path):
                            shutil.rmtree(folder_path)
                
                del self.servers[server_id]
                if server_id in self.server_tabs:
                    self.notebook.forget(self.server_tabs[server_id])
                    del self.server_tabs[server_id]
                
                self.save_servers_config()
                
                if self.current_server_id == server_id and self.servers:
                    first_id = list(self.servers.keys())[0]
                    self.notebook.select(self.server_tabs[first_id])
                    self.current_server_id = first_id
                
                messagebox.showinfo(self.lang.get('success'), self.lang.get('server_deleted', server_name))
                dialog.destroy()
            except Exception as e:
                messagebox.showerror(self.lang.get('error'), self.lang.get('error_delete_server', str(e)))
        
        ttk.Button(button_frame, text=self.lang.get('delete'), command=delete_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text=self.lang.get('cancel'), command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def check_container_conflicts(self, yaml_file, yaml_content):
        """Checks container name and port conflicts"""
        try:
            result = subprocess.run(['docker', 'ps', '-a', '--format', '{{.Names}}'],
                                    capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return False
            all_containers = set(result.stdout.strip().split('\n')) if result.stdout.strip() else set()
            
            running_result = subprocess.run(['docker', 'ps', '--format', '{{.Names}}\t{{.Ports}}'],
                                            capture_output=True, text=True, timeout=10)
            used_ports = set()
            container_ports = {}
            if running_result.returncode == 0:
                for line in running_result.stdout.strip().split('\n'):
                    if line and '\t' in line:
                        name, ports = line.split('\t', 1)
                        container_ports[name] = ports
                        for pm in ports.split(','):
                            if '->' in pm:
                                used_ports.add(pm.split('->')[0].split(':')[-1])
            
            services = yaml_content.get('services', {})
            container_names = set()
            required_ports = set()
            for sname, scfg in services.items():
                container_names.add(scfg.get('container_name', sname))
                for pm in scfg.get('ports', []):
                    if isinstance(pm, str) and ':' in pm:
                        required_ports.add(pm.split(':')[0])
            
            name_conflicts = [f"Container '{n}'" for n in container_names if n in all_containers]
            port_conflicts = []
            for port in required_ports:
                if port in used_ports:
                    owner = next((c for c, p in container_ports.items() if f":{port}->" in p), "unknown")
                    port_conflicts.append(self.lang.get('container_port_conflict', port, owner))
            
            if name_conflicts or port_conflicts:
                all_conflicts = name_conflicts + port_conflicts
                msg = (self.lang.get('container_conflict_message') + "\n" +
                       (self.lang.get('container_name_conflict') + "\n" if name_conflicts else "") +
                       "\n".join(f"• {c}" for c in all_conflicts) + "\n\n" +
                       self.lang.get('container_conflict_solutions'))
                messagebox.showwarning(self.lang.get('container_conflict_title'), msg)
                return True
            return False
        except Exception as e:
            print(f"Error during container conflict check: {e}")
            return False
    
    def move_plus_tab_to_end(self):
        """Moves the + tab to the end"""
        for i in range(self.notebook.index("end")):
            if self.notebook.tab(i, "text") == "+":
                plus_frame = self.notebook.tabs()[i]
                self.notebook.forget(plus_frame)
                self.notebook.add(plus_frame, text="+")
                break
    
    def on_tab_changed(self, event):
        """Called when the tab is changed"""
        selected_tab = self.notebook.select()
        tab_text = self.notebook.tab(selected_tab, "text")
        if tab_text == "+":
            self.add_new_server()
            return
        for server_id, server_config in self.servers.items():
            if server_config['name'] == tab_text:
                self.current_server_id = server_id
                self.load_server_config(server_id)
                self.refresh_server_tab_data(server_id)
                break
    
    def refresh_server_tab_data(self, server_id):
        """Updates all data for the selected server tab"""
        if server_id not in self.server_tabs:
            return
        current_tab = self.server_tabs[server_id]
        if not hasattr(current_tab, 'ui_elements'):
            return
        try:
            self.refresh_databases(server_id)
            self.update_status_ui(server_id)
        except Exception as e:
            print(f"Error updating server tab: {e}")
    
    def load_server_config(self, server_id):
        """Loads configuration for a specific server"""
        if server_id not in self.servers:
            return
        server_config = self.servers[server_id]
        compose_file = server_config['compose_path']
        if os.path.isfile(compose_file):
            self.compose_file = compose_file
            self.compose_path = os.path.dirname(compose_file)
        else:
            self.compose_path = compose_file
            self.compose_file = os.path.join(self.compose_path, 'docker-compose.yml')
        self.quick_paths = {
            'server_logs': os.path.join(self.compose_path, 'logs'),
            'database_logs': os.path.join(self.compose_path, 'db'),
            'www_folder': os.path.join(self.compose_path, 'www')
        }
        self.db_config = self.load_db_config()
        self.server_config = self.load_server_config_from_docker()
    
    def load_server_config_from_docker(self):
        """Loads server configuration from docker-compose.yml"""
        try:
            with open(self.compose_file, 'r') as f:
                config = yaml.safe_load(f)
            services = config.get('services', {})
            server_info = {}
            for service_name, service_config in services.items():
                if 'web' in service_name.lower():
                    for pm in service_config.get('ports', []):
                        if ':' in pm:
                            host_port = pm.split(':')[0]
                            server_info['web'] = {'url': f'http://localhost:{host_port}', 'port': host_port}
                            break
            for service_name, service_config in services.items():
                if 'phpmyadmin' in service_name.lower() or 'pma' in service_name.lower():
                    for pm in service_config.get('ports', []):
                        if ':' in pm:
                            host_port = pm.split(':')[0]
                            server_info['phpmyadmin'] = {'url': f'http://localhost:{host_port}', 'port': host_port}
                            break
            for service_name, service_config in services.items():
                if any(k in service_name.lower() for k in ['db', 'mysql', 'mariadb']):
                    db_port = 3306
                    for pm in service_config.get('ports', []):
                        if ':' in pm:
                            db_port = int(pm.split(':')[0])
                            break
                    server_info['database'] = {'host': '127.0.0.1', 'port': db_port}
                    break
            return server_info
        except Exception as e:
            print(f"Error loading server configuration: {e}")
            return {
                'web': {'url': 'http://localhost:8080', 'port': '8080'},
                'phpmyadmin': {'url': 'http://localhost:8081', 'port': '8081'},
                'database': {'host': '127.0.0.1', 'port': 3306}
            }
    
    def save_language(self, lang_code):
        """Saves the language setting"""
        try:
            config = {}
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
            config['language'] = lang_code
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving language: {e}")
    
    def change_language(self, event=None):
        """Changes the application language"""
        selected_name = self.lang_var.get()
        available_langs = self.lang.get_available_languages()
        lang_code = next((code for code, name in available_langs.items() if name == selected_name), None)
        if lang_code and self.lang.load_language(lang_code):
            self.save_language(lang_code)
            self._retranslate_all()

    # ── Single, central translation method ─────────────────────────────────
    def _retranslate_all(self):
        """
        Translates all UI texts.
        Uses only the saved widget references in ui_elements –
        no widget tree walk, no text comparisons, no double logic.
        """
        self.root.title(self.lang.get('app_title'))

        # Sprach-Label im Header
        if hasattr(self, 'lang_label'):
            self.lang_label.config(text=self.lang.get('language') + ":")

        # Translate each server tab
        for server_id, tab_frame in self.server_tabs.items():
            if not hasattr(tab_frame, 'ui_elements'):
                continue
            el = tab_frame.ui_elements

            # LabelFrame-Titel
            el['server_frame'].config(text=self.lang.get('server_control'))
            el['quick_frame'].config(text=self.lang.get('quick_access'))
            el['db_frame'].config(text=self.lang.get('database_management'))

            # Statische Labels
            el['yaml_title_label'].config(text=self.lang.get('docker_compose'))

            # Status-Labels (mit aktuellem Laufzustand neu rendern)
            running = self.check_server_status_for_tab(server_id)
            self._update_status_labels(el, running)

            # Status-Bar
            el['status_bar'].config(text=self.lang.get('ready'))
            el['github_btn'].config(text=self.lang.get('github_link'))

            # Buttons Server
            el['start_btn'].config(text=self.lang.get('start_server'))
            el['stop_btn'].config(text=self.lang.get('stop_server'))
            el['delete_btn'].config(text=self.lang.get('delete_server'))

            # Buttons Quick-Access
            el['open_web_btn'].config(text=self.lang.get('open_web'))
            el['open_pma_btn'].config(text=self.lang.get('open_phpmyadmin'))
            el['server_logs_btn'].config(text=self.lang.get('server_logs'))
            el['db_logs_btn'].config(text=self.lang.get('database_logs'))
            el['www_folder_btn'].config(text=self.lang.get('www_folder'))

            # Buttons Database
            el['refresh_db_btn'].config(text=self.lang.get('refresh_databases'))
            el['new_db_btn'].config(text=self.lang.get('new_database'))
            el['del_db_btn'].config(text=self.lang.get('delete_database'))
            el['manage_users_btn'].config(text=self.lang.get('manage_users'))

            # Treeview column headers
            el['db_tree'].heading('#0',     text=self.lang.get('database_name'))
            el['db_tree'].heading('Users',  text=self.lang.get('users'))
            el['db_tree'].heading('Size',   text=self.lang.get('size'))
            el['db_tree'].heading('Tables', text=self.lang.get('tables'))

    def load_db_config(self):
        """Loads database configuration from docker-compose.yml"""
        try:
            with open(self.compose_file, 'r') as f:
                config = yaml.safe_load(f)
            for service_name, service_config in config.get('services', {}).items():
                if any(k in service_name.lower() for k in ['db', 'mysql', 'mariadb']):
                    ports = service_config.get('ports', [])
                    db_port = 3306
                    for pm in ports:
                        if ':' in pm:
                            db_port = int(pm.split(':')[0])
                            break
                    env = service_config.get('environment', {})
                    return {
                        'host': '127.0.0.1',
                        'port': db_port,
                        'user': env.get('MYSQL_ROOT_USER', 'root'),
                        'password': env.get('MYSQL_ROOT_PASSWORD', 'root')
                    }
        except Exception as e:
            print(f"Error loading configuration: {e}")
        return self.get_default_db_config()
    
    def get_default_db_config(self):
        return {'host': '127.0.0.1', 'port': 3306, 'user': 'root', 'password': 'root'}
    
    def open_url(self, server_id, service):
        """Opens the URL of the specified service in browser"""
        if server_id is None:
            server_id = self.current_server_id
        if not server_id or server_id not in self.server_tabs:
            return
        current_tab = self.server_tabs[server_id]
        if not hasattr(current_tab, 'server_config_docker'):
            return
        if not self.check_server_status_for_tab(server_id):
            messagebox.showwarning(self.lang.get('warning'), self.lang.get('server_must_be_started'))
            return
        service_info = current_tab.server_config_docker.get(service)
        if service_info and 'url' in service_info:
            webbrowser.open(service_info['url'])
        else:
            messagebox.showerror(self.lang.get('error'), self.lang.get('cannot_open_url', service))
    
    def open_folder(self, server_id, folder_type):
        """Opens the specified folder in file manager"""
        if server_id is None:
            server_id = self.current_server_id
        if not server_id or server_id not in self.server_tabs:
            return
        current_tab = self.server_tabs[server_id]
        if not hasattr(current_tab, 'quick_paths'):
            return
        folder_path = current_tab.quick_paths.get(folder_type)
        if not folder_path:
            messagebox.showerror(self.lang.get('error'), self.lang.get('path_not_found', folder_type))
            return
        if not os.path.exists(folder_path):
            messagebox.showwarning(self.lang.get('warning'), self.lang.get('folder_not_found', folder_path))
            return
        try:
            subprocess.run(['xdg-open', folder_path], check=True)
        except Exception as e:
            messagebox.showerror(self.lang.get('error'), self.lang.get('cannot_open_folder', str(e)))
        
    def check_server_status(self):
        """Checks server status in background"""
        def status_check():
            while True:
                try:
                    result = subprocess.run(['docker', 'ps', '--filter', 'name=lamp_', '--format', '{{.Names}}'],
                                            capture_output=True, text=True)
                    containers = result.stdout.strip().split('\n') if result.stdout.strip() else []
                    self.server_running = len(containers) > 0 and containers[0] != ''
                    self.root.after(0, self.update_status_ui)
                except Exception as e:
                    print(f"Status check error: {e}")
                time.sleep(5)
        self.status_thread = threading.Thread(target=status_check, daemon=True)
        self.status_thread.start()
    
    def update_status_ui(self, server_id=None):
        """Updates status UI for the specified server"""
        if server_id is None:
            server_id = self.current_server_id
        if not server_id or server_id not in self.server_tabs:
            return
        current_tab = self.server_tabs[server_id]
        if not hasattr(current_tab, 'ui_elements'):
            return
        el = current_tab.ui_elements
        try:
            running = self.check_server_status_for_tab(server_id)
            el['start_btn'].config(state='disabled' if running else 'normal')
            el['stop_btn'].config(state='normal' if running else 'disabled')
            self._update_status_labels(el, running)
            if running:
                # Give database server time to start up
                self.root.after(2000, lambda: self.refresh_databases(server_id))
            else:
                for item in el['db_tree'].get_children():
                    el['db_tree'].delete(item)
                el['status_bar'].config(text=self.lang.get('server_stopped'))
        except Exception as e:
            print(f"Error updating status UI for server {server_id}: {e}")
    
    def check_server_status_for_tab(self, server_id):
        """Checks server status for a specific tab"""
        if server_id not in self.server_tabs:
            return False
        current_tab = self.server_tabs[server_id]
        if not hasattr(current_tab, 'compose_path'):
            return False
        try:
            os.chdir(current_tab.compose_path)
            result = subprocess.run(['docker-compose', 'ps'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return any('Up' in line for line in result.stdout.split('\n'))
            return False
        except Exception as e:
            print(f"Error checking server status for {server_id}: {e}")
            return False
    
    def refresh_databases(self, server_id=None):
        """Updates database list for a specific server"""
        if server_id is None:
            server_id = self.current_server_id
        if not server_id or server_id not in self.server_tabs:
            return
        current_tab = self.server_tabs[server_id]
        if not hasattr(current_tab, 'ui_elements'):
            return
        el = current_tab.ui_elements
        if not self.check_server_status_for_tab(server_id):
            el['status_bar'].config(text=self.lang.get('server_stopped'))
            return
        el['status_bar'].config(text=self.lang.get('loading_databases'))
        db_tree = el['db_tree']
        db_tree.delete(*db_tree.get_children())
        
        # Try to connect with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                connection = self.get_db_connection(server_id)
                if connection:
                    break
                if attempt < max_retries - 1:
                    el['status_bar'].config(text=f"Versuch {attempt + 1}/{max_retries}...")
                    time.sleep(2)
            except:
                if attempt < max_retries - 1:
                    time.sleep(2)
                continue
        else:
            el['status_bar'].config(text=self.lang.get('no_db_connection'))
            return
            
        try:
            cursor = connection.cursor()
            cursor.execute("SHOW DATABASES")
            for (db_name,) in cursor.fetchall():
                if db_name in ('information_schema', 'performance_schema', 'mysql', 'sys'):
                    continue
                cursor.execute(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '{db_name}'")
                table_count = cursor.fetchone()[0]
                cursor.execute(f"""
                    SELECT ROUND(SUM(data_length + index_length) / 1024 / 1024, 2)
                    FROM information_schema.tables WHERE table_schema = '{db_name}'
                """)
                size_result = cursor.fetchone()
                size = f"{size_result[0]} MB" if size_result[0] else "0 MB"
                cursor.execute(f"""
                    SELECT DISTINCT GRANTEE FROM information_schema.schema_privileges
                    WHERE TABLE_SCHEMA = '{db_name}'
                      AND PRIVILEGE_TYPE IN ('SELECT','INSERT','UPDATE','DELETE','CREATE','DROP','ALTER','INDEX')
                    UNION
                    SELECT DISTINCT CONCAT(User,'@',Host) FROM mysql.db WHERE Db = '{db_name}'
                """)
                user_list = sorted({row[0].replace("'", "").strip() for row in cursor.fetchall()})
                users_text = ", ".join(user_list) if user_list else "Keine Benutzer"
                db_tree.insert('', 'end', text=db_name, values=(users_text, size, table_count))
            cursor.close()
            connection.close()
            el['status_bar'].config(text=self.lang.get('databases_found').format(len(db_tree.get_children())))
        except Exception as e:
            messagebox.showerror(self.lang.get('error'), f"{self.lang.get('error')}:\n{str(e)}")
            if 'connection' in locals() and connection:
                connection.close()
    
    def start_server(self, server_id=None):
        """Starts the LAMP-Server"""
        if server_id is None:
            server_id = self.current_server_id
        if not server_id or server_id not in self.server_tabs:
            return
        current_tab = self.server_tabs[server_id]
        if not hasattr(current_tab, 'ui_elements'):
            return
        el = current_tab.ui_elements
        try:
            el['status_bar'].config(text=self.lang.get('server_starting'))
            os.chdir(current_tab.compose_path)
            start_result = subprocess.run(['docker-compose', 'start'], capture_output=True, text=True)
            if start_result.returncode == 0:
                check_result = subprocess.run(['docker-compose', 'ps'], capture_output=True, text=True)
                if any('Up' in l for l in check_result.stdout.split('\n')):
                    el['status_bar'].config(text=self.lang.get('server_started'))
                    messagebox.showinfo(self.lang.get('success'), self.lang.get('server_started'))
                    return
            result = subprocess.run(['docker-compose', 'up', '-d'], capture_output=True, text=True)
            if result.returncode == 0:
                check_result = subprocess.run(['docker-compose', 'ps'], capture_output=True, text=True)
                if any('Up' in l for l in check_result.stdout.split('\n')):
                    el['status_bar'].config(text=self.lang.get('server_started'))
                    messagebox.showinfo(self.lang.get('success'), self.lang.get('server_started'))
                else:
                    el['status_bar'].config(text=self.lang.get('error'))
                    messagebox.showerror(self.lang.get('error'), self.lang.get('server_start_error', result.stderr))
            else:
                el['status_bar'].config(text=self.lang.get('error'))
                messagebox.showerror(self.lang.get('error'),
                                     f"{self.lang.get('error')}:\n{result.stderr or result.stdout}")
        except Exception as e:
            el['status_bar'].config(text=self.lang.get('error'))
            messagebox.showerror(self.lang.get('error'), f"{self.lang.get('error')}:\n{str(e)}")
    
    def stop_server(self, server_id=None):
        """Stops the LAMP-Server"""
        if server_id is None:
            server_id = self.current_server_id
        if not server_id or server_id not in self.server_tabs:
            return
        current_tab = self.server_tabs[server_id]
        if not hasattr(current_tab, 'ui_elements'):
            return
        el = current_tab.ui_elements
        try:
            el['status_bar'].config(text=self.lang.get('server_stopping'))
            os.chdir(current_tab.compose_path)
            result = subprocess.run(['docker-compose', 'stop'], capture_output=True, text=True)
            if result.returncode == 0:
                el['status_bar'].config(text=self.lang.get('server_stopped'))
                messagebox.showinfo(self.lang.get('success'), self.lang.get('server_stopped'))
            else:
                el['status_bar'].config(text=self.lang.get('error'))
                messagebox.showerror(self.lang.get('error'), f"{self.lang.get('error')}:\n{result.stderr}")
        except Exception as e:
            el['status_bar'].config(text=self.lang.get('error'))
            messagebox.showerror(self.lang.get('error'), f"{self.lang.get('error')}:\n{str(e)}")
    
    def get_db_connection(self, server_id=None):
        """Establishes a connection to the database"""
        if server_id is None:
            server_id = self.current_server_id
        if not server_id or server_id not in self.server_tabs:
            return None
        current_tab = self.server_tabs[server_id]
        if not hasattr(current_tab, 'db_config'):
            return None
        db_config = current_tab.db_config
        try:
            return mysql.connector.connect(
                host=db_config['host'],
                port=db_config['port'],
                user=db_config['user'],
                password=db_config['password'],
                connection_timeout=5
            )
        except Error as e:
            messagebox.showerror(self.lang.get('error'), f"{self.lang.get('error')}:\n{str(e)}")
            return None
    
    def create_database(self, server_id=None):
        """ Creates a new database"""
        if server_id is None:
            server_id = self.current_server_id
        if not server_id or server_id not in self.server_tabs:
            return
        if not self.check_server_status_for_tab(server_id):
            messagebox.showwarning(self.lang.get('warning'), self.lang.get('server_must_be_started'))
            return
        dialog = tk.Toplevel(self.root)
        dialog.title(self.lang.get('new_database'))
        dialog.geometry("350x100")
        dialog.transient(self.root)
        dialog.grab_set()
        ttk.Label(dialog, text=self.lang.get('database_name')).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        db_entry = ttk.Entry(dialog, width=30)
        db_entry.grid(row=0, column=1, padx=5, pady=5)
        
        def create_action():
            db_name = db_entry.get().strip()
            if not db_name:
                messagebox.showerror(self.lang.get('error'), self.lang.get('enter_database_name'))
                return
            try:
                connection = self.get_db_connection(server_id)
                cursor = connection.cursor()
                cursor.execute(f"CREATE DATABASE `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                connection.commit()
                messagebox.showinfo(self.lang.get('success'), self.lang.get('database_created').format(db_name))
                self.refresh_databases(server_id)
                dialog.destroy()
            except Exception as e:
                messagebox.showerror(self.lang.get('error'), f"{self.lang.get('error')}:\n{str(e)}", parent=self.root)
        
        ttk.Button(dialog, text=self.lang.get('create'), command=create_action).grid(row=1, column=0, columnspan=2, pady=20)
    
    def delete_database(self, server_id=None):
        """Deletes a database"""
        if server_id is None:
            server_id = self.current_server_id
        if not server_id or server_id not in self.server_tabs:
            return
        current_tab = self.server_tabs[server_id]
        if not hasattr(current_tab, 'ui_elements'):
            return
        el = current_tab.ui_elements
        if 'db_tree' not in el:
            return
        selected = el['db_tree'].selection()
        if not selected:
            messagebox.showwarning(self.lang.get('warning'), self.lang.get('select_database'), parent=self.root)
            return
        db_name = el['db_tree'].item(selected[0])['text']
        if messagebox.askyesno(self.lang.get('warning'), self.lang.get('confirm_delete_database', db_name), parent=self.root):
            try:
                connection = self.get_db_connection(self.current_server_id)
                if connection:
                    cursor = connection.cursor()
                    cursor.execute(f"DROP DATABASE IF EXISTS `{db_name}`")
                    connection.commit()
                    cursor.close()
                    connection.close()
                    messagebox.showinfo(self.lang.get('success'), self.lang.get('database_deleted', db_name), parent=self.root)
                    self.refresh_databases(self.current_server_id)
                else:
                    messagebox.showerror(self.lang.get('error'), self.lang.get('no_db_connection'), parent=self.root)
            except Exception as e:
                messagebox.showerror(self.lang.get('error'), f"{self.lang.get('error')}:\n{str(e)}", parent=self.root)

    def manage_users(self, server_id=None):
        """User management window"""
        if server_id is None:
            server_id = self.current_server_id
        if not server_id or server_id not in self.server_tabs:
            return
        if not self.check_server_status_for_tab(server_id):
            messagebox.showwarning(self.lang.get('warning'), self.lang.get('server_must_be_started'), parent=self.root)
            return
        user_window = tk.Toplevel(self.root)
        user_window.title(self.lang.get('user_management'))
        user_window.geometry("600x300")
        user_window.transient(self.root)
        user_window.grab_set()
        user_window.focus_set()
        user_window.server_id = server_id
        
        user_frame = ttk.Frame(user_window)
        user_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Button(user_frame, text=self.lang.get('refresh_users'),
                   command=lambda: self.refresh_users(user_window, server_id)).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(user_frame, text=self.lang.get('new_user'),
                   command=lambda: self.create_user(user_window, server_id)).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(user_frame, text=self.lang.get('edit_user'),
                   command=lambda: self.edit_user(user_window, server_id)).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(user_frame, text=self.lang.get('delete_user'),
                   command=lambda: self.delete_user(user_window, server_id)).grid(row=0, column=3, padx=5, pady=5)
        
        columns = ('User', 'Host', 'Rights')
        user_tree = ttk.Treeview(user_frame, columns=columns, show='headings', height=20)
        for col in columns:
            user_tree.heading(col, text=col)
            user_tree.column(col, width=200)
        user_tree.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        user_window.user_tree = user_tree
        
        v_scrollbar = ttk.Scrollbar(user_frame, orient='vertical', command=user_tree.yview)
        v_scrollbar.grid(row=1, column=4, sticky=(tk.N, tk.S))
        user_tree.configure(yscrollcommand=v_scrollbar.set)
        h_scrollbar = ttk.Scrollbar(user_frame, orient='horizontal', command=user_tree.xview)
        h_scrollbar.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E))
        user_tree.configure(xscrollcommand=h_scrollbar.set)
        
        user_window.columnconfigure(0, weight=1)
        user_window.rowconfigure(0, weight=1)
        user_frame.columnconfigure(0, weight=1)
        user_frame.rowconfigure(1, weight=1)
        
        self.refresh_users(user_window, server_id)
    
    def refresh_users(self, window, server_id=None):
        """Refreshes the user list"""
        if server_id is None:
            server_id = getattr(window, 'server_id', self.current_server_id)
        if not server_id or server_id not in self.server_tabs:
            return
        if not hasattr(window, 'user_tree'):
            return
        user_tree = window.user_tree
        user_tree.delete(*user_tree.get_children())
        try:
            connection = self.get_db_connection(server_id)
            if connection:
                cursor = connection.cursor()
                cursor.execute("SELECT User, Host FROM mysql.user")
                users = cursor.fetchall()
                user_data = []
                for username, host in users:
                    if not (username and host and username.strip() and host.strip()):
                        continue
                    if username in ['root', 'mysql.sys', 'mysql.session', 'healthcheck', 'mariadb.sys']:
                        continue
                    cursor.execute(f"SHOW GRANTS FOR '{username}'@'{host}'")
                    grant_text = '\n'.join([g[0] for g in cursor.fetchall()])
                    user_data.append((username, host, grant_text))
                cursor.close()
                connection.close()
                for username, host, rights in user_data:
                    user_tree.insert('', 'end', values=(username, host, rights))
                user_tree.column('User', width=200, minwidth=100, stretch=False)
                user_tree.column('Host', width=200, minwidth=100, stretch=False)
                max_len = max((len(r) for _, _, r in user_data), default=0)
                user_tree.column('Rights', width=max(300, max_len * 9), minwidth=200, stretch=False)
            else:
                messagebox.showerror(self.lang.get('error'), self.lang.get('no_db_connection'))
        except Exception as e:
            messagebox.showerror(self.lang.get('error'), f"{self.lang.get('error')}:\n{str(e)}")
    
    def create_user(self, window, server_id=None):
        """Creates a new user"""
        if server_id is None:
            server_id = getattr(window, 'server_id', self.current_server_id)
        if not server_id or server_id not in self.server_tabs:
            return
        dialog = tk.Toplevel(window)
        dialog.title(self.lang.get('new_user'))
        dialog.geometry("600x450")
        dialog.transient(window)
        dialog.grab_set()
        dialog.focus_set()
        
        ttk.Label(dialog, text=self.lang.get('username_label')).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        username_entry = ttk.Entry(dialog, width=30)
        username_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text=self.lang.get('password_label')).grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        password_entry = ttk.Entry(dialog, width=30, show="*")
        password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text=self.lang.get('host_label')).grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        host_entry = ttk.Entry(dialog, width=30)
        host_entry.insert(0, "localhost")
        host_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text=self.lang.get('databases_label')).grid(row=3, column=0, padx=5, pady=5, sticky=tk.NW)
        db_frame = ttk.Frame(dialog)
        db_frame.grid(row=3, column=1, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        db_listbox = tk.Listbox(db_frame, selectmode=tk.MULTIPLE, height=8)
        db_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        db_scrollbar = ttk.Scrollbar(db_frame, orient='vertical', command=db_listbox.yview)
        db_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        db_listbox.configure(yscrollcommand=db_scrollbar.set)
        
        try:
            connection = self.get_db_connection(server_id)
            cursor = connection.cursor()
            cursor.execute("SHOW DATABASES")
            for (db,) in cursor.fetchall():
                if db not in ('information_schema', 'mysql', 'performance_schema', 'sys'):
                    db_listbox.insert(tk.END, db)
        except Exception as e:
            print(f"Error loading databases: {e}")
        
        ttk.Label(dialog, text=self.lang.get('rights_label')).grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        rights_frame = ttk.Frame(dialog)
        rights_frame.grid(row=4, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        rights_vars = {}
        rights_list = [
            ("SELECT", self.lang.get('data_read')),
            ("INSERT", self.lang.get('data_insert')),
            ("UPDATE", self.lang.get('data_update')),
            ("DELETE", self.lang.get('data_delete')),
            ("CREATE", self.lang.get('create_tables')),
            ("DROP", self.lang.get('drop_tables')),
            ("INDEX", self.lang.get('manage_indexes')),
            ("ALTER", self.lang.get('alter_tables')),
            ("ALL PRIVILEGES", self.lang.get('all_privileges'))
        ]
        for i, (right, description) in enumerate(rights_list):
            var = tk.BooleanVar()
            rights_vars[right] = var
            ttk.Checkbutton(rights_frame, text=f"{right} - {description}", variable=var).grid(
                row=i // 2, column=i % 2, sticky=tk.W, padx=5, pady=2)
        
        def create_user_action():
            username = username_entry.get().strip()
            password = password_entry.get()
            host     = host_entry.get().strip()
            if not username or not password:
                messagebox.showerror(self.lang.get('error'), self.lang.get('enter_username_password'))
                return
            selected_dbs    = [db_listbox.get(i) for i in db_listbox.curselection()]
            selected_rights = [r for r, v in rights_vars.items() if v.get()]
            if not selected_dbs:
                messagebox.showerror(self.lang.get('error'), self.lang.get('select_database'))
                return
            if not selected_rights:
                messagebox.showerror(self.lang.get('error'), self.lang.get('select_rights'))
                return
            try:
                connection = self.get_db_connection(server_id)
                cursor = connection.cursor()
                cursor.execute("SELECT User, Host FROM mysql.user WHERE User = %s AND Host = %s", (username, host))
                if cursor.fetchone():
                    messagebox.showerror(self.lang.get('error'), self.lang.get('user_exists', username, host))
                    return
                cursor.execute(f"CREATE USER '{username}'@'{host}' IDENTIFIED BY '{password}'")
                rights_str = ', '.join(selected_rights)
                for db in selected_dbs:
                    cursor.execute(f"GRANT {rights_str} ON `{db}`.* TO '{username}'@'{host}'")
                connection.commit()
                messagebox.showinfo(self.lang.get('success'), self.lang.get('user_created', username))
                self.refresh_users(window, server_id)
                dialog.destroy()
            except Exception as e:
                messagebox.showerror(self.lang.get('error'), f"{self.lang.get('error')}:\n{str(e)}")
        
        ttk.Button(dialog, text=self.lang.get('create'), command=create_user_action).grid(
            row=5, column=0, columnspan=2, pady=20)
    
    def edit_user(self, window, server_id=None):
        """Edit a existing user"""
        if server_id is None:
            server_id = getattr(window, 'server_id', self.current_server_id)
        if not server_id or server_id not in self.server_tabs:
            return
        selected = window.user_tree.selection()
        if not selected:
            messagebox.showwarning(self.lang.get('warning'), self.lang.get('select_user'), parent=window)
            return
        user_info = window.user_tree.item(selected[0])
        username = user_info['values'][0]
        host     = user_info['values'][1]
        
        dialog = tk.Toplevel(window)
        dialog.title(f"{self.lang.get('edit_user')}: {username}")
        dialog.geometry("600x500")
        dialog.transient(window)
        dialog.grab_set()
        dialog.focus_set()
        
        ttk.Label(dialog, text=self.lang.get('username_label')).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        username_entry = ttk.Entry(dialog, width=30)
        username_entry.insert(0, username)
        username_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text=self.lang.get('host_label')).grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        host_entry = ttk.Entry(dialog, width=30)
        host_entry.insert(0, host)
        host_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text=self.lang.get('new_password')).grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        password_entry = ttk.Entry(dialog, width=30, show="*")
        password_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text=self.lang.get('databases_label')).grid(row=3, column=0, padx=5, pady=5, sticky=tk.NW)
        db_frame = ttk.Frame(dialog)
        db_frame.grid(row=3, column=1, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        db_listbox = tk.Listbox(db_frame, selectmode=tk.MULTIPLE, height=6)
        db_scrollbar = ttk.Scrollbar(db_frame, orient=tk.VERTICAL, command=db_listbox.yview)
        db_listbox.configure(yscrollcommand=db_scrollbar.set)
        db_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        db_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        ttk.Label(dialog, text=self.lang.get('rights_label')).grid(row=4, column=0, padx=5, pady=5, sticky=tk.NW)
        rights_frame = ttk.Frame(dialog)
        rights_frame.grid(row=4, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        rights_vars = {}
        rights_list = [
            ("SELECT", self.lang.get('data_read')),
            ("INSERT", self.lang.get('data_insert')),
            ("UPDATE", self.lang.get('data_update')),
            ("DELETE", self.lang.get('data_delete')),
            ("CREATE", self.lang.get('table_create')),
            ("DROP", self.lang.get('table_drop')),
            ("ALTER", self.lang.get('table_alter')),
            ("INDEX", self.lang.get('index_create')),
            ("ALL PRIVILEGES", self.lang.get('all_privileges'))
        ]
        for i, (right, description) in enumerate(rights_list):
            var = tk.BooleanVar()
            rights_vars[right] = var
            ttk.Checkbutton(rights_frame, text=f"{right} - {description}", variable=var).grid(
                row=i // 2, column=i % 2, sticky=tk.W, padx=5, pady=2)
        
        try:
            connection = self.get_db_connection(self.current_server_id)
            if connection:
                cursor = connection.cursor()
                cursor.execute("SHOW DATABASES")
                user_databases = set()
                user_rights    = set()
                all_dbs = [db[0] for db in cursor.fetchall()
                           if db[0] not in ('information_schema', 'performance_schema', 'mysql', 'sys')]
                for db in all_dbs:
                    db_listbox.insert(tk.END, db)
                cursor.execute(f"SHOW GRANTS FOR '{username}'@'{host}'")
                for (grant_text,) in cursor.fetchall():
                    if 'ON `' in grant_text:
                        db_part = grant_text.split('ON `')[1].split('`')[0]
                        if db_part != '*':
                            user_databases.add(db_part)
                    if 'GRANT' in grant_text:
                        rights_part = grant_text.split('GRANT ')[1].split(' ON')[0]
                        if rights_part == 'ALL PRIVILEGES':
                            user_rights.add('ALL PRIVILEGES')
                        else:
                            for r in rights_part.split(', '):
                                if r.strip() != 'USAGE':
                                    user_rights.add(r.strip())
                for i in range(db_listbox.size()):
                    if db_listbox.get(i) in user_databases:
                        db_listbox.selection_set(i)
                if not user_databases and 'ALL PRIVILEGES' in user_rights:
                    for i in range(db_listbox.size()):
                        db_listbox.selection_set(i)
                for right, var in rights_vars.items():
                    if right in user_rights:
                        var.set(True)
                cursor.close()
                connection.close()
        except Exception as e:
            print(f"Error loading user data: {e}")
        
        def update_user_action():
            nonlocal username, host
            new_username = username_entry.get()
            new_host     = host_entry.get()
            new_password = password_entry.get()
            if not new_username:
                messagebox.showwarning(self.lang.get('warning'), self.lang.get('username_required'), parent=dialog)
                return
            selected_databases = [db_listbox.get(i) for i in db_listbox.curselection()]
            selected_rights    = [r for r, v in rights_vars.items() if v.get()]
            if not selected_rights:
                messagebox.showwarning(self.lang.get('warning'), self.lang.get('select_rights'), parent=dialog)
                return
            try:
                connection = self.get_db_connection(self.current_server_id)
                if connection:
                    cursor = connection.cursor()
                    cursor.execute(f"REVOKE ALL PRIVILEGES, GRANT OPTION FROM '{username}'@'{host}'")
                    if new_password:
                        cursor.execute(f"ALTER USER '{username}'@'{host}' IDENTIFIED BY '{new_password}'")
                    if new_username != username:
                        cursor.execute(f"RENAME USER '{username}'@'{host}' TO '{new_username}'@'{new_host}'")
                        username = new_username
                        host     = new_host
                    rights_str = ', '.join(selected_rights)
                    if selected_databases:
                        for db in selected_databases:
                            cursor.execute(f"GRANT {rights_str} ON `{db}`.* TO '{username}'@'{host}'")
                    else:
                        cursor.execute(f"GRANT {rights_str} ON *.* TO '{username}'@'{host}'")
                    cursor.execute("FLUSH PRIVILEGES")
                    connection.commit()
                    cursor.close()
                    connection.close()
                    messagebox.showinfo(self.lang.get('success'), self.lang.get('user_updated', username))
                    self.refresh_users(window)
                    dialog.destroy()
            except Exception as e:
                messagebox.showerror(self.lang.get('error'), f"{self.lang.get('error')}:\n{str(e)}")
        
        ttk.Button(dialog, text=self.lang.get('save'), command=update_user_action).grid(
            row=5, column=0, columnspan=2, pady=20)
    
    def delete_user(self, window, server_id=None):
        """Delete a user"""
        if server_id is None:
            server_id = getattr(window, 'server_id', self.current_server_id)
        if not server_id or server_id not in self.server_tabs:
            return
        if not hasattr(window, 'user_tree'):
            return
        selected = window.user_tree.selection()
        if not selected:
            messagebox.showwarning(self.lang.get('warning'), self.lang.get('select_user'), parent=window)
            return
        user_info = window.user_tree.item(selected[0])
        username = user_info['values'][0]
        host     = user_info['values'][1]
        if messagebox.askyesno(self.lang.get('warning'),
                               self.lang.get('confirm_delete_user', username, host), parent=window):
            try:
                connection = self.get_db_connection(server_id)
                if connection:
                    cursor = connection.cursor()
                    cursor.execute(f"DROP USER IF EXISTS '{username}'@'{host}'")
                    cursor.execute("FLUSH PRIVILEGES")
                    connection.commit()
                    cursor.close()
                    connection.close()
                    messagebox.showinfo(self.lang.get('success'), self.lang.get('user_deleted', username, host))
                    self.refresh_users(window, server_id)
            except Exception as e:
                messagebox.showerror(self.lang.get('error'), f"{self.lang.get('error')}:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = LAMPManager(root)
    root.mainloop()
