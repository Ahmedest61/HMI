from flask import Flask
from flask import render_template
from flask import request, flash, url_for,redirect
import json
import subprocess
import os,time
json_file = "/home/ahmad/INCASE/January/HMI/input.json" 

with open(json_file, "r") as jsonFile:
    receiveddata = json.load(jsonFile)
print (receiveddata)
