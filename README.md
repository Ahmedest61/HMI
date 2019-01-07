# HMi for Netjury

# The user needs to have Flask module installed inside the OS to make it work

# hmi.py is the main file, the user needs to make the following changes inside it:

1. Define the ethernet port to be used for webserver (By default, Port = "eth0")
2. Define the netjury related parameters including user, ip, and directory of load generator i.e. "netjury_user", "netjury_ip" and "netjury_load_dir"

# Inside the load generator script, following are the variables need to be modified:

1. The Webser user, ip and path controlled by "WEBSERVER_USER","WEBSERVER_IP" and "WEBSERVER_PATH"
