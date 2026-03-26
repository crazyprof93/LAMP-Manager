# LAMP Server Manager

A Python GUI application for managing multiple LAMP servers with Docker Compose and complete database management.

## Main Features

### **Multi-Server Management**
- **Tab System**: Manage multiple LAMP servers in tabs
- **Add Server**: Import new servers via YAML file
- **Delete Server**: With container and folder management options
- **Conflict Detection**: Automatic detection of port and container conflicts

### **Server Control**
- **Start/Stop**: Control Docker Compose containers
- **Live Status**: Automatic status updates every 5 seconds
- **Port Configuration**: Automatic detection from docker-compose.yml
- **Quick Access**: Direct access to web server, phpMyAdmin and folders

### **Database Management**
- **Database Overview**: With size and table count
- **Create/Delete**: Databases with UTF8MB4 support
- **User Management**: Complete MySQL/MariaDB user management
- **Rights Management**: Detailed permissions (SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, INDEX, ALL PRIVILEGES)

### **Multilingual**
- **German/English**: Complete localization
- **Language Switch**: Runtime switch without restart
- **Extensible**: Easy addition of new languages

### **File Access**
- **Log Folder**: Direct access to Apache logs
- **Database Folder**: Access to MySQL/MariaDB data
- **WWW Folder**: Quick access to web root
- **Browser Integration**: Automatic opening of URLs

## Installation

### 1. Prerequisites
- Python 3.7+ installed
- Docker and Docker Compose installed
- LAMP server project with docker-compose.yml

### 2. Install Tkinter (if not present)
If Tkinter is not installed:
```bash
# Debian/Ubuntu
sudo apt update
sudo apt install python3-tk -y

# Verify
python3 -m tkinter
```

### 3. Setup Docker Permissions
Add your user to the Docker group:
```bash
# Add user to Docker group
sudo usermod -aG docker $USER

# Important: Log out and log back in OR
newgrp docker
```

### 4. Install Python Dependencies
```bash
# Create virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

Start the application:
```bash
python lamp_manager.py
```

### Server Control
- **Start Server**: Starts all Docker containers in background (`docker-compose up -d`)
- **Stop Server**: Stops all containers (`docker-compose down`)

### Database Management
- **Refresh Databases**: Reloads all databases
- **New Database**: Creates a new database
- **Delete Database**: Deletes the selected database
- **Manage Users**: Opens user management window

### User Management
- **New User**: Creates new user with:
  - Multi-selection for databases (Ctrl+Click for multiple selection)
  - Detailed rights setting (SELECT, INSERT, UPDATE, DELETE, etc.)
  - Flexible host specification
- **Update User**: Reloads user list
- **Delete User**: Deletes selected user

## Configuration

### **Automatic Configuration**
The application automatically reads configuration from your `docker-compose.yml` files:
- **Database Port**: From port mapping (e.g. 3306:3306)
- **Web Server Port**: From Apache/Nginx port mapping  
- **phpMyAdmin Port**: From phpMyAdmin configuration
- **Credentials**: From environment variables (MYSQL_ROOT_PASSWORD, etc.)
- **Container Names**: For status checking and conflict detection

### **Multi-Server Setup**
Each server is managed via its own `docker-compose.yml`:
- **Add Server**: `+` tab → Select YAML file
- **Server Name**: Freely selectable (e.g. "Project A", "Testing")
- **Configuration**: Automatic extraction from YAML
- **Storage**: In `lamp_config.json`

### **Directory Structure**
The application expects the following directory structure per server:
```
your-project/
├── docker-compose.yml    # Docker configuration
├── www/                  # Web root (Apache/PHP)
├── logs/                 # Apache logs
├── db/                   # MySQL/MariaDB data
└── lamp_manager.py       # GUI application
```

### **Manual Adjustment**
Path to configuration file (automatically created):
```python
# lamp_config.json contains:
{
  "servers": {
    "server_0": {
      "name": "LAMP Server 1",
      "compose_path": "/path/to/docker-compose.yml"
    }
  },
  "language": "en"
}
```

## Extended Features

### **Server Management**
- **Start**: `docker-compose start` or `docker-compose up -d`
- **Stop**: `docker-compose stop` or `docker-compose down`
- **Status Check**: Container status every 5 seconds
- **Automatic Recovery**: Error handling and restart

### **User Management**
- **Create User**: With password, host and database rights
- **Edit User**: Change password, adjust rights
- **Delete User**: With security confirmation
- **Rights Management**: Granular permissions per database

### **Web Integration**
- **Browser Opening**: Automatically open URLs
- **phpMyAdmin**: Direct access to database web interface
- **Web Server**: Quick access to Apache/Nginx

### **Database Information**
- **Size**: MB specification per database
- **Tables**: Number of tables per database  
- **Users**: Assigned users with rights
- **Live Updates**: Automatic update on server start

## Troubleshooting

### **Common Problems**

#### Docker Permission denied
```bash
# Check if user is in Docker group
groups $USER | grep docker

# If not present:
sudo usermod -aG docker $USER
# Important: Log out and log back in!
```

#### Tkinter not found
```bash
# Install (Debian/Ubuntu)
sudo apt update && sudo apt install python3-tk -y

# Test
python3 -c "import tkinter; print('Tkinter OK')"
```

#### Database connection failed
1. **Start server**: Click on "Start Server"
2. **Check port**: `docker ps` should show port 3306
3. **Check configuration**: Terminal shows loaded configuration
4. **Wait**: MariaDB sometimes needs 30-60 seconds to start

#### Container Conflicts
- **Error message**: "Port already in use" or "Container name exists"
- **Solution**: Use different ports in docker-compose.yml
- **Automatic Check**: Application warns of conflicts when adding

#### YAML File Errors
- **Validation**: Application automatically checks YAML syntax
- **Required**: `services` section must be present
- **Ports**: Correct port mapping syntax `host:container`

### **Debugging**

#### Show Logs
```bash
# Docker logs
docker-compose logs

# Specific service
docker-compose logs web
docker-compose logs db
```

#### Check Configuration
```bash
# Docker Compose configuration
docker-compose config

# Container status
docker ps -a
```

#### Network Problems
```bash
# Port in use?
netstat -tulpn | grep :8080

# Container networks
docker network ls
```

### **Important Notes**

#### Security
- Application connects as root user to database
- Passwords are displayed in plain text in GUI
- Use application only in secure environment

#### Performance
- Status updates every 5 seconds (can generate CPU load)
- Large databases take longer for table counting
- Multi-server management increases memory usage

#### Compatibility
- **Python**: 3.7+ required
- **Docker**: Compose v2+ recommended
- **Database**: MySQL 5.7+ / MariaDB 10.3+
- **OS**: Linux (tested on Ubuntu/Debian)

## **Project Structure**

```
LAMP-Manager/
├── lamp_manager.py          # Main application (GUI)
├── requirements.txt         # Python dependencies
├── docker-compose.yml       # Docker configuration
├── Dockerfile              # Apache/PHP image
├── lamp_config.json        # Server configuration (auto)
├── start_lamp_manager.sh   # Start script
├── languages/              # Language files
│   ├── de.json            # German
│   └── en.json            # English
├── www/                   # Web root (Apache)
├── logs/                  # Apache logs
├── db/                    # MySQL/MariaDB data
└── README.md              # This file
```

## **Quick Start**

```bash
# 1. Clone/extract repository
cd LAMP-Manager

# 2. Set up Python environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Docker permissions (if needed)
sudo usermod -aG docker $USER
newgrp docker

# 5. Start application
python lamp_manager.py
```

## **License**

This project is Open Source. Feel free to use, modify and distribute.

## **Contributing**

Issues and Pull Requests are welcome!

---

**Version**: 2.0+  
**Last Updated**: 2025  
**Developed with**: Python 3, Tkinter, Docker, MySQL Connector
