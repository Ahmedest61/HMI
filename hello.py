from flask import Flask
from flask import render_template
from flask import request, flash, url_for,redirect
import json
import subprocess
import os,time

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
    data['ethertype'] = request.form['ethertype']
    ethtype=str(data['ethertype'])
    data['payloadSize'] = request.form['payloadsize']
    payloadLength = float(data['payloadSize'])

    if 'vlancheck' in _keys:
	checkVlan = 1
        data['vlan_id'] = request.form['vlanid']
        vlanId = int(data['vlan_id'])
	overHeads = 4 + 4 + 8 + 12
    else:
        checkVlan = 0
        data['vlan_id'] = 0
	overHeads = 4 + 8 + 12
    data['vlan_priority'] = request.form['vlanpriority']
    vlanPrio = int(data['vlan_priority'] )
    data['vlan_cfi'] = request.form['vlancfi']
    vlanCfi = int(data['vlan_cfi'] )
    print("Overhead", overHeads)
    one_packet_length = payloadLength + overHeads
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
    data['noOfBurst'] = request.form['noofburst']
    noOfBurst  = int(data['noOfBurst'])
    data['burstTime'] = request.form['burstintervaltime']
    data['burstTimeUnit'] = request.form['burstintervaltimeunit']
    burstInterval = float(data['burstTime']) 
    burstIntervalUnit = data['burstTimeUnit']

    if 'M' in burstIntervalUnit:
        no_of_frameB = int(1000000/ float(one_packet_length * 8)* load * (burstInterval * 60))
    elif 'S' in burstIntervalUnit:
	no_of_frameB = int(1000000/ float(one_packet_length * 8)* load * (burstInterval))
    elif 'ms' in burstIntervalUnit:
	no_of_frameB = int(1000000/ float(one_packet_length * 8)* load * (burstInterval / float(1000)))
    elif 'us' in burstIntervalUnit:    
	no_of_frameB = int(1000000/ float(one_packet_length * 8)* load * (burstInterval / float(1000000)))
    elif 'ns' in burstIntervalUnit:    
	no_of_frameB = int(1000000/ float(one_packet_length * 8)* load * (burstInterval / float(1000000000)))

    if no_of_frameB<1:
	error = 'Frames cannot compensate in the user defined burst parameters '
        return render_template('fillForm.html',error=error)


    data['burstTimeEqualSleepTime'] = 0
    data['burstSleeptime'] = request.form['burstsleepintervaltime']
    burstSleepInterval = float(data['burstSleeptime'])
    data['burstSleeptimeUnit'] = request.form['burstsleepintervaltimeunit']
    burstSleepIntervalUnit = data['burstSleeptimeUnit']

    if 'checkNormalTime' in _keys:
        data['checkNormalTime'] = 1
	checkTime=1
    else:
        data['checkNormalTime'] = 0
	checkTime=0
    data['normalTime'] = request.form['normaltimeinterval']
    normalTime = float(data['normalTime'])

    data['normalTimeUnit'] = request.form['normaltimeintervalunit']
    normalTimeUnit = data['normalTimeUnit']

    if 'M' in normalTimeUnit:
        no_of_frameN = int(1000000/ float(one_packet_length * 8)* load * (normalTime * 60))
    elif 'S' in normalTimeUnit:
	no_of_frameN = int(1000000/ float(one_packet_length * 8)* load * (normalTime))
    elif 'ms' in normalTimeUnit:
	no_of_frameN = int(1000000/ float(one_packet_length * 8)* load * (normalTime / float(1000)))
    elif 'us' in normalTimeUnit:    
	no_of_frameN = int(1000000/ float(one_packet_length * 8)* load * (normalTime / float(1000000)))
    elif 'ns' in normalTimeUnit:    
	no_of_frameN = int(1000000/ float(one_packet_length * 8)* load * (normalTime / float(1000000000)))

    if no_of_frameN<1:
	error = 'Frames cannot compensate in the user defined time parameters '
        return render_template('fillForm.html',error=error)

    if 'checkUserDefinedPackets' in _keys:
        data['checkUserDefinedPackets'] = 1
	checkFrames=1
    else:
        data['checkUserDefinedPackets'] = 0
	checkFrames=0
    data['noOfFrames_noTimeInfo'] = request.form['numberofframes']        
    no_of_frameP = int(data['noOfFrames_noTimeInfo'])    
    timeP = float(no_of_frameP / float(1000000/ float(one_packet_length * 8) * load))	
    json_data = json.dumps(data)

    print ('JSON: ', json_data)
    with open(json_file,'w') as outfile:
        outfile.write(json.dumps(data, ensure_ascii=False))
    
 #   json_file = "send.json" 
    # now just send this json data to fpga server
    flash("User defined parameters send")
    
#    print ("about to send the file")
    
    output = subprocess.check_output(u'scp ' + json_file + ' root@155.245.44.31:/home/root/Belgium_KUL_Oct/load_gen/', shell=True)
    os.remove(json_file)
  #  return("Json data send successfully to FPGA server")
	
    while(1):
	#print(os.path.isfile(load_generatedFile))
        if os.path.isfile(json_file):
	 #   with open(json_file, "r") as jsonFile:
         #       receiveddata = json.load(jsonFile)
	    if checkBurst:
                if not checkVlan:
 	            flash(str(load)+'% Load generated sucessfully for '+str(noOfBurst)+' bursts '+ '('+str(no_of_frameB)+' frames per burst, total frames: '+str(int(no_of_frameB)*int(noOfBurst))+') with burstTime '+str(burstInterval)+str(burstIntervalUnit)+' and sleepInterval '+str(burstSleepInterval)+str(burstSleepIntervalUnit) +' with ' + str(one_packet_length)+' frame size and 0x'+ethtype+' Ethertype')
                else:
		    flash(str(load)+'% Load generated sucessfully for '+str(noOfBurst)+' bursts '+ '('+str(no_of_frameB)+' frames per burst, total frames: '+str(int(no_of_frameB)*int(noOfBurst))+') with burstTime '+str(burstInterval)+str(burstIntervalUnit)+' and sleepInterval '+str(burstSleepInterval)+str(burstSleepIntervalUnit) +' with ' + str(one_packet_length)+' frame size and 0x'+ethtype+' Ethertype with Vlanid '+str(vlanId)+' VlanPriority '+str(vlanPrio)+' and VlanCFI '+str(vlanCfi) )
	    elif checkTime:
                if not checkVlan:
	            flash(str(load)+'% Load generated sucessfully for time '+str(normalTime)+str(normalTimeUnit)+' with '+str(no_of_frameN) +' frames with '+ str(one_packet_length)+' frame size and 0x'+ethtype+' Ethertype')
		else:
                    flash(str(load)+'% Load generated sucessfully for time '+str(normalTime)+str(normalTimeUnit)+' with '+str(no_of_frameN) +' frames with '+ str(one_packet_length)+' frame size and 0x'+ethtype+' Ethertype with Vlanid '+str(vlanId)+' VlanPriority '+str(vlanPrio)+' and VlanCFI '+str(vlanCfi) )
	    elif checkFrames:
	        if not checkVlan:
		    flash(str(load)+'% Load generated sucessfully for '+ str(no_of_frameP)+' frames in '+str(timeP)+'S time with '+ str(one_packet_length)+' frame size and 0x'+ethtype+' Ethertype')
		else:
		    flash(str(load)+'% Load generated sucessfully for '+ str(no_of_frameP)+' frames in '+str(timeP)+'S time with '+ str(one_packet_length)+' frame size and 0x'+ethtype+' Ethertype with Vlanid '+str(vlanId)+' VlanPriority '+str(vlanPrio)+' and VlanCFI '+str(vlanCfi) )
	 #   os.remove(load_generatedFile) 
	    break
	else:
	#    time.sleep(1)
	    continue
    
    
    return render_template('fillForm.html')

if __name__ == "__main__":
    app.run(host="155.245.44.23",port=5000)
  #  app.run(host="10.245.108.228",port=5000)

   
