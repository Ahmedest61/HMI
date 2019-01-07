from flask import Flask
from flask import render_template
from flask import request, flash, url_for,redirect
import json
import subprocess
import os,time
import socket
import fcntl
import struct

port = "eth0"
netjury_user = "root"
netjury_ip = "155.245.23.55"
netjury_load_dir = "/home/root/Load_Generator/"


def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

app = Flask(__name__,static_url_path='/static')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/login/fillForm')
def show_form():
    return render_template('fillForm.html')


@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'INCASE' or \
                request.form['password'] != 'INCASE':
            error = 'Invalid credentials'
        else:
            flash('You were successfully logged in')
            return redirect(url_for('show_form'))
    return render_template('login.html', error=error)

@app.route('/handle_data', methods=['POST'])
def handle_data():
    error = None
    json_file = "input.json" 

   # load_generatedFile = "output.json"
   
    with open(json_file, "r") as jsonFile:
        data = json.load(jsonFile)
  #  data = {}
#    load = request.form['load']
#    data['load'] = load


    _keys = list(request.form.keys())
    print ('keys:...',_keys)
    print ('Request form', request.form)


    data['load'] = request.form['load']
    load = float(data['load'])

    
    srcMAC = request.form['srcMac']

    if srcMAC.count(':') != 5 or len(srcMAC)!= 17:
	error = 'Source MAC address not correct, missing :'	
        return render_template('fillForm.html',error=error)                                                                                                                
                                                                                                                 
    for i in srcMAC.split(':'):                                                                                          
        for j in i:                                                                                                           
	    if j > 'F' or j < 'A' and not j.isdigit() or len(i) != 2:                                                                                               
	        srcMacAllFine = False                                                                                               
	        break                                                                                                         
	    else:                                                                                                             
	        srcMacAllFine = True                                                                                                
    if not srcMacAllFine:                                                                                                           
	error = 'Source MAC address not correct, incorrect alphabat'	
        return render_template('fillForm.html',error=error)
    else:
	data['srcMac'] = srcMAC   

    dstMAC = request.form['dstMac']

    if dstMAC.count(':') != 5 or len(dstMAC)!= 17:
	error = 'Destination MAC address not correct, missing :'	
        return render_template('fillForm.html',error=error)                                                                                                                
                                                                                                                 
    for i in dstMAC.split(':'):                                                                                          
        for j in i:                                                                                                           
	    if j > 'F' or j < 'A' and not j.isdigit() or len(i) != 2:                                                                                               
	        srcDestAllFine = False                                                                                               
	        break                                                                                                         
	    else:                                                                                                             
	        srcMacAllFine = True                                                                                                
    if not srcMacAllFine:                                                                                                           
	error = 'Destinatiom MAC address not correct, incorrect alphabat'	
        return render_template('fillForm.html',error=error)
    else:
	data['dstMac'] = dstMAC  

    data['ethertype'] = request.form['ethertype']
    ethtype=str(data['ethertype'])
    data['payloadSize'] = request.form['payloadSize']
    payloadLength = float(data['payloadSize'])



    if 'setScriptingMode' in _keys:
        data['setScriptingMode'] = 1
    else:
	data['setScriptingMode'] = 0
    data['loadPort'] = request.form['loadPort']

	
    if 'checkVlanTag' in _keys:
	checkVlanTag = 1
	data['checkVlanTag'] = 1
        data['vlan_id'] = request.form['vlanid']
        vlanId = int(data['vlan_id'])
	overHeads = 4 + 4 + 8 + 12
    else:
	checkVlanTag = 0
	data['checkVlanTag'] = 0
        data['vlan_id'] = 0
	overHeads = 4 + 8 + 12

    data['vlan_priority'] = request.form['vlanpriority']
    vlanPrio = int(data['vlan_priority'] )
    data['vlan_cfi'] = request.form['vlancfi']
    vlanCfi = int(data['vlan_cfi'] )
    print("Overhead", overHeads)
    one_packet_length = payloadLength + overHeads
    one_packet_last = float(one_packet_length*8 / float(load))
    print("one packet length", one_packet_length)
    

    if not 'checkBurst' in _keys and not 'checkNormalTime' in _keys and not 'checkUserDefinedPackets' in _keys:
	error = 'The user needs to check atleast one option'	
        return render_template('fillForm.html',error=error)

    elif 'checkBurst' in _keys and 'checkNormalTime' in _keys:
	error = 'The user cannot check burst and normal time at once'	
        return render_template('fillForm.html',error=error)

    elif 'checkBurst' in _keys and 'checkUserDefinedPackets' in _keys:
	error = 'The user cannot check burst and user defined frame at once'
        return render_template('fillForm.html',error=error)

    elif 'checkUserDefinedPackets' in _keys and 'checkNormalTime' in _keys:
	error= 'The user cannot check user defined frame and normal time at once'
        return render_template('fillForm.html',error=error)

    if 'checkBurst' in _keys:
        data['checkBurst'] = 1
	checkBurst=1
    else:
        data['checkBurst'] = 0
	checkBurst=0

    if data['checkBurst']:
	    data['noOfBurst'] = request.form['noOfBurst']
	    noOfBurst  = int(data['noOfBurst'])
	    data['burstTime'] = request.form['burstTime']
	    data['burstTimeUnit'] = request.form['burstTimeUnit']
	    data['Method'] = request.form['method']
	    print("ok")
	    burstInterval = float(data['burstTime']) 
	    burstIntervalUnit = data['burstTimeUnit']


	    if 'M' in burstIntervalUnit:
		no_of_frameB = int(1000000/ float(one_packet_length * 8)* load * (burstInterval * 60))
		act_time = one_packet_last * no_of_frameB / float(1000000 * 60)
	    elif 'S' in burstIntervalUnit:
		no_of_frameB = int(1000000/ float(one_packet_length * 8)* load * (burstInterval))
		act_time = one_packet_last * no_of_frameB / float(1000000)
	    elif 'ms' in burstIntervalUnit:
		no_of_frameB = int(1000000/ float(one_packet_length * 8)* load * (burstInterval / float(1000)))
		act_time = one_packet_last * no_of_frameB*1000 / float(1000000)
	    elif 'us' in burstIntervalUnit:    
		no_of_frameB = int(1000000/ float(one_packet_length * 8)* load * (burstInterval / float(1000000)))
		act_time = one_packet_last * no_of_frameB*1000000 / float(1000000)
	    elif 'ns' in burstIntervalUnit:    
		no_of_frameB = int(1000000/ float(one_packet_length * 8)* load * (burstInterval / float(1000000000)))
		act_time = one_packet_last * no_of_frameB*1000000000 / float(1000000)

	    if no_of_frameB<1:
		error = 'Frames cannot compensate in the user defined burst parameters '
		return render_template('fillForm.html',error=error)


	    data['checkBurstTimeEqualSleepTime'] = 0
	    data['burstSleeptime'] = request.form['burstSleeptime']
	    burstSleepInterval = float(data['burstSleeptime'])
	    data['burstSleeptimeUnit'] = request.form['burstSleeptimeUnit']
	    burstSleepIntervalUnit = data['burstSleeptimeUnit']


    if 'checkNormalTime' in _keys:
        data['checkNormalTime'] = 1
	checkTime=1
    else:
        data['checkNormalTime'] = 0
	checkTime=0

    if data['checkNormalTime']:
	    data['normalTime'] = request.form['normalTime']
	    normalTime = float(data['normalTime'])

	    data['normalTimeUnit'] = request.form['normalTimeUnit']
	    normalTimeUnit = data['normalTimeUnit']

	    if 'M' in normalTimeUnit:
		no_of_frameN = int(1000000/ float(one_packet_length * 8)* load * (normalTime * 60))
		act_time = one_packet_last * no_of_frameN / float(1000000 * 60)
	    elif 'S' in normalTimeUnit:
		no_of_frameN = int(1000000/ float(one_packet_length * 8)* load * (normalTime))
		act_time = one_packet_last * no_of_frameN / float(1000000)
	    elif 'ms' in normalTimeUnit:
		no_of_frameN = int(1000000/ float(one_packet_length * 8)* load * (normalTime / float(1000)))
		act_time = one_packet_last * no_of_frameN*1000 / float(1000000)
	    elif 'us' in normalTimeUnit:    
		no_of_frameN = int(1000000/ float(one_packet_length * 8)* load * (normalTime / float(1000000)))
		act_time = one_packet_last * no_of_frameN*1000000 / float(1000000)
	    elif 'ns' in normalTimeUnit:    
		no_of_frameN = int(1000000/ float(one_packet_length * 8)* load * (normalTime / float(1000000000)))
		act_time = one_packet_last * no_of_frameN*1000000000 / float(1000000)

	    if no_of_frameN<1:
		error = 'Frames cannot compensate in the user defined time parameters '
		return render_template('fillForm.html',error=error)

    if 'checkUserDefinedPackets' in _keys:
        data['checkUserDefinedPackets'] = 1
	checkFrames=1
    else:
        data['checkUserDefinedPackets'] = 0
	checkFrames=0

    if  data['checkUserDefinedPackets']:
	    data['noOfFrames_noTimeInfo'] = request.form['noOfFrames_noTimeInfo']        
	    no_of_frameP = int(data['noOfFrames_noTimeInfo'])    
	    timeP = float(no_of_frameP / float(1000000/ float(one_packet_length * 8) * load))	
	    act_time = timeP
    json_data = json.dumps(data)

    print ('JSON: ', json_data)
    with open(json_file,'w') as outfile:
        outfile.write(json.dumps(data, ensure_ascii=False))
    
 #   json_file = "send.json" 
    # now just send this json data to fpga server
    flash("User defined parameters send")
    
    print ("about to send the file")
    output = subprocess.check_output(u'scp ' + json_file + " "+netjury_user +'@'+netjury_ip+':'+ netjury_load_dir, shell=True)
    os.remove(json_file)
  #  return("Json data send successfully to FPGA server")
	
    while(1):
	#print(os.path.isfile(load_generatedFile))
        if os.path.isfile(json_file):
	    useReceivedFile= False
	    if useReceivedFile:
		    with open("/home/ahmad/INCASE/January/HMI/input.json", "r") as jsonFile:
		        receiveddata = json.load(jsonFile)
		    if checkBurst:
		        if not checkVlanTag:
	 	            flash(str(load)+'% Load generated sucessfully for '+str(noOfBurst)+' bursts '+ '('+str(receiveddata['framesSendPerBurst'])+' frames per burst, total frames: '+str(receiveddata['framesSendAllBurst'])+') with burstTime '+str(receiveddata['burstTime'])+str(receiveddata['burstTimeUnit'])+' and sleepInterval '+str(receiveddata['burstSleeptime'])+str(receiveddata['burstSleeptimeUnit']) +' with ' + str(receiveddata['one_packet_length'])+' frame size and 0x'+ethtype+' Ethertype')
		        else:
	 	            flash(str(load)+'% Load generated sucessfully for '+str(noOfBurst)+' bursts '+ '('+str(receiveddata['framesSendPerBurst'])+' frames per burst, total frames: '+str(receiveddata['framesSendAllBurst'])+') with burstTime '+str(receiveddata['burstTime'])+str(receiveddata['burstTimeUnit'])+' and sleepInterval '+str(receiveddata['burstSleeptime'])+str(receiveddata['burstSleeptimeUnit']) +' with ' + str(receiveddata['one_packet_length'])+' frame size and 0x'+ethtype+' Ethertype with Vlanid '+str(vlanId)+' VlanPriority '+str(vlanPrio)+' and VlanCFI '+str(vlanCfi) )

		    elif checkTime:
		        if not checkVlanTag:
			    flash(str(load)+'% Load generated sucessfully for time '+str(receiveddata['framesSendTime'])+str(receiveddata['framesSendTimeUnit'])+' with '+str(receiveddata['framesSend']) +' frames with '+ str(receiveddata['one_packet_length'])+' frame size and 0x'+ethtype+' Ethertype')
			else:
			    flash(str(load)+'% Load generated sucessfully for time '+str(receiveddata['framesSendTime'])+str(receiveddata['framesSendTimeUnit'])+' with '+str(receiveddata['framesSend']) +' frames with '+ str(receiveddata['one_packet_length'])+' frame size and 0x'+ethtype+' Ethertype with Vlanid '+str(vlanId)+' VlanPriority '+str(vlanPrio)+' and VlanCFI '+str(vlanCfi) )

		    elif checkFrames:
			if not checkVlanTag:
			    flash(str(load)+'% Load generated sucessfully for '+ str(receiveddata['framesSend'])+' frames in '+str(receiveddata['framesSendTime'])+'S time with '+ str(receiveddata['one_packet_length'])+' frame size and 0x'+ethtype+' Ethertype')
			else:
			    flash(str(load)+'% Load generated sucessfully for '+ str(receiveddata['framesSend'])+' frames in '+str(receiveddata['framesSendTime'])+'S time with '+ str(receiveddata['one_packet_length'])+' frame size and 0x'+ethtype+' Ethertype with Vlanid '+str(vlanId)+' VlanPriority '+str(vlanPrio)+' and VlanCFI '+str(vlanCfi) )

		 #   os.remove(load_generatedFile) 
		    break
	    else:
		    if checkBurst:
		        if not checkVlanTag:
	 	            flash(str(load)+'% Load generated sucessfully for '+str(noOfBurst)+' bursts '+ '('+str(no_of_frameB)+' frames per burst, total frames: '+str(int(no_of_frameB)*int(noOfBurst))+') with burstTime '+str(act_time)+str(burstIntervalUnit)+' and sleepInterval '+str(burstSleepInterval)+str(burstSleepIntervalUnit) +' with ' + str(one_packet_length)+' frame size and 0x'+ethtype+' Ethertype')
		        else:
			    flash(str(load)+'% Load generated sucessfully for '+str(noOfBurst)+' bursts '+ '('+str(no_of_frameB)+' frames per burst, total frames: '+str(int(no_of_frameB)*int(noOfBurst))+') with burstTime '+str(act_time)+str(burstIntervalUnit)+' and sleepInterval '+str(burstSleepInterval)+str(burstSleepIntervalUnit) +' with ' + str(one_packet_length)+' frame size and 0x'+ethtype+' Ethertype with Vlanid '+str(vlanId)+' VlanPriority '+str(vlanPrio)+' and VlanCFI '+str(vlanCfi) )
		    elif checkTime:
		        if not checkVlanTag:
			    flash(str(load)+'% Load generated sucessfully for time '+str(act_time)+str(normalTimeUnit)+' with '+str(no_of_frameN) +' frames with '+ str(one_packet_length)+' frame size and 0x'+ethtype+' Ethertype')
			else:
		            flash(str(load)+'% Load generated sucessfully for time '+str(act_time)+str(normalTimeUnit)+' with '+str(no_of_frameN) +' frames with '+ str(one_packet_length)+' frame size and 0x'+ethtype+' Ethertype with Vlanid '+str(vlanId)+' VlanPriority '+str(vlanPrio)+' and VlanCFI '+str(vlanCfi) )
		    elif checkFrames:
			if not checkVlanTag:
			    flash(str(load)+'% Load generated sucessfully for '+ str(no_of_frameP)+' frames in '+str(act_time)+'S time with '+ str(one_packet_length)+' frame size and 0x'+ethtype+' Ethertype')
			else:
			    flash(str(load)+'% Load generated sucessfully for '+ str(no_of_frameP)+' frames in '+str(act_time)+'S time with '+ str(one_packet_length)+' frame size and 0x'+ethtype+' Ethertype with Vlanid '+str(vlanId)+' VlanPriority '+str(vlanPrio)+' and VlanCFI '+str(vlanCfi) )
		    break
	else:
#	    print('waiting for file')
	#    time.sleep(1)
	    continue
    
    
    return render_template('fillForm.html')

if __name__ == "__main__":
    ip_webserver = get_ip_address(port)
    app.run(host=ip_webserver,port=5000)
  #  app.run(host="10.245.108.228",port=5000)

   
