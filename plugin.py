# Domoticz Home Automation - Plugin Tinkerforge LCD 20x4 Bricklet
# @author Robert W.B. Linn
# @version 0.8.0 (Build 20200215)
#
# NOTE: after every change restart Domoticz & check the Domoticz Log
# sudo systemctl restart domoticz.service OR sudo service domoticz.sh restart
# REFERENCES:
# Domoticz Python Plugin Development:
# https://www.domoticz.com/wiki/Developing_a_Python_plugin
# Tinkerforge LCD 20x4 Bricklet:
# Hardware:
# https://www.tinkerforge.com/en/doc/Hardware/Bricklets/LCD_20x4.html#lcd-20x4-bricklet
# API Python Documentation:
# https://www.tinkerforge.com/en/doc/Software/Bricklets/LCD20x4_Bricklet_Python.html


"""
<plugin key="tflcd20x4" name="Tinkerforge LCD 20x4 Bricklet" author="rwbL" version="0.8.0">
    <description>
        <h2>Tinkerforge LCD 20x4 Bricklet</h2><br/>
        The plugin enables to write characters to the LCD 20x4 display via a Domoticz text device (Type:General, SubType:Text).<br/>
        The text to be displayed is defined as a JSON formatted string (array with up-to 4 line items).<br/>
        [{"line":1,"position":n,"clear":n,"text":"Text"},{"line":2,"position":n,"clear":n,"text":"Text"},{"line":3,"position":n,"clear":n,"text":"Text"},{"line":4,"position":n,"clear":n,"text":"Text"}] <br/>
        Each line item has the key:value pairs:
        <ul style="list-style-type:square">
            <li>"line":0-3 - Integer with line index 0 to 3.</li>
            <li>"position":0-19 - Integer with position index 0 - 19.</li>
            <li>"clear":1-2 - Integer to clear the line (1) or clear the display (2) prior writing the text to the line.</li>
            <li>"Text":"Text string" - The text to be displayed.</li>
        </ul>
        Custom characters are defined in an external file and displayed via Unicode.<br/>
        When the plugin starts, the backlight is switched on, the cursor is turned off and not blinking.<br/>
        If the text of the Domoticz device is modified, the plugin connects via IP to Tinkerforge, writes the LCD line(s) as defined by the JSON string and disconnects.<br/>
        <br/>
        Note: This is the full version of the plugin. There is also a lite version with a single Domoticz text device updated using JSON formatted string.
        <br/>
        <h3>Domoticz Devices</h3>
        <ul style="list-style-type:square">
            <li>Lines 0-3 JSON - Type:General, SubType:Text, Name:JSON (set text for up-to 4 LCD lines at any position using JSON array).</li>
            <li>Backlight - Type:Light/Switch, SubType:Switch, SwitchType:On/Off, Name:Backlight (set the backlight on/off).</li>
            <li>Cursor - Type:Light/Switch, SubType:Switch, SwitchType:On/Off, Name:Cursor (set the cursor [underscore] on/off).</li>
            <li>Blinking - Type:Light/Switch, SubType:Switch, SwitchType:On/Off, Name:Blinking (set the cursor blinking on/off).</li>
            <li>Buttons - Type:Light/Switch, SubType:Switch, SwitchType:On/Off, Name:Button 0 -3 (set the buttons).</li>
            <li>In total 8 Domoticz devices are created for the Tinkerforge LCD 20x4 bricklet.</li>
        </ul>
        <br/>
        <h3>Configuration</h3>
        <ul style="list-style-type:square">
            <li>Address: IP address of the host connected to. Default: 127.0.0.1 (for USB connection)</li>
            <li>Port: Port used by the host. Default: 4223</li>
            <li>UID: Unique identifier of the LCD 20x4 Bricklet. Obtain the UID via the Brick Viewer. Default: BHN</li>
        </ul>
    </description>
    <params>
        <param field="Address" label="Host" width="200px" required="true" default="127.0.0.1"/>
        <param field="Port" label="Port" width="75px" required="true" default="4223"/>
        <param field="Mode1" label="UID" width="200px" required="true" default="BHN"/>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug" default="true"/>
                <option label="False" value="Normal"/>
            </options>
        </param>
    </params>
</plugin>
""" 

## Imports
import Domoticz
import urllib
import urllib.request
import json 

# Amend the import path to enable using the Tinkerforge libraries
# Alternate (ensure to update in case newer Python API bindings):
# create folder tinkerforge and copy the binding content, i.e.
# /home/pi/domoticz/plugins/tflcd20x4
from os import path
import sys
sys.path
sys.path.append('/usr/local/lib/python3.7/dist-packages')

import tinkerforge
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_lcd_20x4 import BrickletLCD20x4

# Units
## 1 for JSON text to write up-to 4 lines
UNITJSON = 1
## 3 switches for settings
UNITBACKLIGHT = 2
UNITCURSOR = 3
UNITBLINKING = 4
## 4 buttons
## Be carefull changing the numbers as used by the button callback functions which use button index starting 0-3
## If button 0 is pressed, the button unit 5 (the switch) is triggered: Button Unit = 5 calculated by ButtonPressed + UNITBUTTON0, i.e. 0 + 5 = 5 or 1 + 5 = 6 etc.
UNITBUTTON0 = 5
UNITBUTTON1 = 6
UNITBUTTON2 = 7
UNITBUTTON3 = 8
# Device Status Level & Text
STATUSLEVELOK = 1
STATUSLEVELERROR = 5
STATUSTEXTOK = "OK"
STATUSTEXTERROR = "ERROR"
# Switch State On or Off - case sesitive
SWITCHON = "On"
SWITCHOFF = "Off"

# Custom Characters file JSON array format
CUSTOMCHARFILE = "/home/pi/domoticz/plugins/tflcd20x4/customchar.json"

# Messages (not all)
MSGERRNOIPCONN = "[ERROR] IP Connection failed. Check the settings."
MSGERRNOUID = "[ERROR] Bricklet UID not set. Get the UID using the Brick Viewer."
MSGERRSETCONFIG = "[ERROR] Set bricklet configuration failed. Check bricklet and settings."

class BasePlugin:

    def __init__(self):
        self.Debug = False
        # HTTP Connection
        self.httpConn = None
        self.httpConnected = 0

        # Tinkerforge ipconnection and iodevice
        # Flag to check if connected to the master brick
        self.ipConn = None
        self.ipConnected = 0
        self.lcdDev = None
        self.lcdUID = None
        
        # NOT USED=Placeholder
        # The Domoticz heartbeat is set to every 10 seconds. Do not use a higher value than 30 as Domoticz message "Error: hardware (N) thread seems to have ended unexpectedly"
        # The plugin heartbeat is set in Parameter.Mode5 (seconds). This is determined by using a hearbeatcounter which is triggered by:
        # (self.HeartbeatCounter * self.HeartbeatInterval) % int(Parameter.Mode5) = 0
        # Example: trigger action every 60s [every 6 heartbeats] = (6 * 10) mod 60 = 0 or every 5 minutes (300s) [every 30 heartbeats] = (30 * 10) mod 300 = 0
        # self.HeartbeatInterval = 10
        # self.HeartbeatCounter = 0

    def onStart(self):
        Domoticz.Debug("onStart called")
        Domoticz.Debug("Debug Mode:" + Parameters["Mode6"])
        if Parameters["Mode6"] == "Debug":
            self.debug = True
            Domoticz.Debugging(1)
            write_config_to_log()

        if (len(Devices) == 0):
            # Create new devices for the Hardware
            Domoticz.Debug("Creating devices")
            # General;Text
            Domoticz.Device(Name="JSON", Unit=UNITJSON, TypeName="Text", Used=1).Create()
            Domoticz.Debug("Device created: "+Devices[UNITJSON].Name)
            # Switches for the configuration
            Domoticz.Device(Name="Backlight", Unit=UNITBACKLIGHT, TypeName="Switch", Used=1).Create()
            Devices[UNITBACKLIGHT].Update(nValue=1,sValue="")
            Domoticz.Debug("Device created: "+Devices[UNITBACKLIGHT].Name)
            Domoticz.Device(Name="Cursor", Unit=UNITCURSOR, TypeName="Switch", Used=1).Create()
            Domoticz.Debug("Device created: "+Devices[UNITCURSOR].Name)
            Domoticz.Device(Name="Blinking", Unit=UNITBLINKING, TypeName="Switch", Used=1).Create()
            Domoticz.Debug("Device created: "+Devices[UNITBLINKING].Name)
            # Swiches for the push-buttons
            Domoticz.Device(Name="Button 0", Unit=UNITBUTTON0, TypeName="Switch", Used=1).Create()
            Domoticz.Debug("Device created: "+Devices[UNITBUTTON0].Name)
            Domoticz.Device(Name="Button 1", Unit=UNITBUTTON1, TypeName="Switch", Used=1).Create()
            Domoticz.Debug("Device created: "+Devices[UNITBUTTON1].Name)
            Domoticz.Device(Name="Button 2", Unit=UNITBUTTON2, TypeName="Switch", Used=1).Create()
            Domoticz.Debug("Device created: "+Devices[UNITBUTTON2].Name)
            Domoticz.Device(Name="Button 3", Unit=UNITBUTTON3, TypeName="Switch", Used=1).Create()
            Domoticz.Debug("Device created: "+Devices[UNITBUTTON3].Name)
            Domoticz.Debug("Creating device: OK")

        # Get the UID of the bricklet
        self.lcdUID = Parameters["Mode1"]
        if len(self.lcdUID) == 0:
            write_to_log(STATUSLEVELERROR, MSGERRNOUID)
            return

        # Flag to check if connected to the master brick
        self.ipConnected = 0
        # Create IP connection
        self.ipConn = IPConnection()
        # Create device object
        self.lcdDev = BrickletLCD20x4(self.lcdUID, self.ipConn)

        # Connect to brickd using Host and Port
        try:
            self.ipConn.connect(Parameters["Address"], int(Parameters["Port"]))
            self.ipConnected = 1
            Domoticz.Debug("IP Connection - OK")
        except:
            write_to_log(STATUSLEVELERROR, MSGERRNOIPCONN)
            return
       
        # Set the bricklet configuration: backlight, cursor, blink are set according their switch device state
        set_configuration(self)
        
        # Register button pressed callback to function cb_button_pressed
        self.lcdDev.register_callback(self.lcdDev.CALLBACK_BUTTON_PRESSED, onButtonPressedCallback)

        # Register button released callback to function cb_button_released
        self.lcdDev.register_callback(self.lcdDev.CALLBACK_BUTTON_RELEASED, onButtonReleasedCallback)

    def onStop(self):
        Domoticz.Debug("Plugin is stopping.")
        if self.ipConnected == 1:
            self.ipConn.disconnect()

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called")

    # Handle commands from the various switch devices
    # Example set backlight: if the switch backlight is switched to on, the lcd backlight is turned on by the api functionlcd.backlight_on()
    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level) + "', Hue: " + str(Hue))
        # Check unit, action, update the device
        # For the backlight,cursor,blinking the command is "On" or "Off"
        if Unit == UNITBACKLIGHT:
            set_backlight(self,Command)
        if Unit == UNITCURSOR:
            set_cursor(self,Command)
        if Unit == UNITBLINKING:
            set_blinking(self,Command)

    # Handle new text from the text units (devices). The text is in property Devices[Unit].sValue
    # The new text is taken from the device and written to the LCD display
    def onDeviceModified(self, Unit):
        Domoticz.Debug("onDeviceModified called Unit:" + str(Unit) + " (" + Devices[Unit].Name + "),nValue="+str(Devices[Unit].nValue) + ",sValue="+Devices[Unit].sValue)
        write_lines(self, Unit)
        
    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called")
        if self.ipConnected == 1:
            self.ipConn.disconnect()

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called")
        # NOT USED = PLACEHOLDER
        """
        self.HeartbeatCounter = self.HeartbeatCounter + 1
        Domoticz.Debug("onHeartbeat called. Counter=" + str(self.HeartbeatCounter * self.HeartbeatInterval) + " (Heartbeat=" + Parameters["Mode5"] + ")")
        # check the heartbeatcounter against the heartbeatinterval
        if (self.HeartbeatCounter * self.HeartbeatInterval) % int(Parameters["Mode5"]) == 0:
            try:
                #Domoticz.Log(
                return
            except:
                #Domoticz.Error("[ERROR] ...")
                return
        """

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onDeviceModified(Unit):
    global _plugin
    _plugin.onDeviceModified(Unit)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

# Tinkerforge Bricklet

"""
Set the bricklet configuration
Parameter:
"""
def set_configuration(self):
    Domoticz.Debug("set_configuration. IP-Connected: %d" % (self.ipConnected) )
    if self.ipConnected == 0:
        write_to_log(STATUSLEVELERROR, "Set configuration. Not connected to the Master Brick. Check settings, correct and restart Domoticz." )
        return
        
    try:
        state = SWITCHON if Devices[UNITBACKLIGHT].nValue == 1 else SWITCHOFF
        set_backlight(self,state)
        state = SWITCHON if Devices[UNITCURSOR].nValue == 1 else SWITCHOFF
        set_cursor(self,state)
        state = SWITCHON if Devices[UNITBLINKING].nValue == 1 else SWITCHOFF
        set_blinking(self,state)
        
        # Set Custom Characters with index 0-7 as max 8 custom characters can be defined.
        # dzVents Lua scripts:
        # The \ character needs to be escaped, i.e. line = string.format(line, l, p, "\\u0008", domoticz.helpers.isnowhhmm(domoticz) )
        # Ensure to write in unicode \u00NN and NOT \xNN - Example: lcdDev.write_line(0, 0, "Battery: " + "\u0008")
        # JSON has no hex escape \xNN but supports unicode escape \uNNNN
        # 
        # Example custom character definition and write to the lcd:
        #     battery = [14,27,17,17,17,17,17,31] 
        #     clock = [31,17,10,4,14,31,31,0]
        #     lcdDev.set_custom_character(0, clock)
        # 
        # JSON File
        # Read the custom characters from JSON array file as defined by constant CUSTOMCHARFILE
        # JSON format examplewith 2 characters: 
        # [
        #     {"id":0,"name":"battery","char":"14,27,17,17,17,17,17,31"},
        #     {"id":1,"name":"clock","char":"31,17,10,4,14,31,31,0"}
        # ]
        # Use exception handling in case file not found
        # The id must be in range 0-7 as max 8 custom characters can be defined
        try:
            with open(CUSTOMCHARFILE) as f:
                json_char_array = json.load(f)
                Domoticz.Debug("Customchar: characters: %d" % (len(json_char_array)) )
                if len(json_char_array) > 0:
                    for item in json_char_array:
                        id = int(item["id"])
                        name = item["name"]
                        char = item["char"].strip().split(",")
                        # Check if the character id is in range 0-7
                        if id >= 0 and id <= 7:
                            self.lcdDev.set_custom_character(id, char)
                            Domoticz.Debug("Customchar: Index=%d,Name=%s,Char=%s" % (id,name,item["char"]) )
                        else:
                            Domoticz.Error("Customchar: Index=%d not in range 0-7." % (id) )
                else:
                    Domoticz.Error("Customchar: No or wrong characters defined.")
        except:
            Domoticz.Error("Customchar: Can not open file=%s." % (CUSTOMCHARFILE) )
        Domoticz.Debug("set_configuration OK")
    except:
        write_to_log(STATUSLEVELERROR, "Set configuration failed. Check settings, correct and restart Domoticz." )
    return

"""
Set the lcd backlight On or Off and update the Domoticz switch device to On or Off
Parameter
state - String On or Off - note the string is case sensitive
"""
def set_backlight(self,state):
    Domoticz.Debug("set_backlight: Change state=%s" % (state) )
    if self.ipConnected == 0:
        write_to_log(STATUSLEVELERROR, "[ERROR] Set backlight failed. Not connected to the Master Brick. Check settings." )
        return
    try:
        if state == SWITCHON:
            self.lcdDev.backlight_on()
            Devices[UNITBACKLIGHT].Update(nValue=1,sValue="")
        else:
            self.lcdDev.backlight_off()
            Devices[UNITBACKLIGHT].Update(nValue=0,sValue="")
        Domoticz.Debug("set_backlight: OK")
    except:
        write_to_log(STATUSLEVELERROR, "[ERROR] Set backlight failed. Check settings." )
    return

"""
Set the lcd cursor to On or Off and update the Domoticz switch device to On or Off
Parameter
state - String On or Off - note the string is case sensitive
"""
def set_cursor(self,state):
    Domoticz.Debug("set_cursor: Change state=%s" % (state) )
    if self.ipConnected == 0:
        write_to_log(STATUSLEVELERROR, "Set cursor failed. Not connected to the Master Brick. Check settings." )
        return
    try:
        obj = self.lcdDev.get_config()
        if state == SWITCHON:
            self.lcdDev.set_config(True, obj.blinking)
            Devices[UNITCURSOR].Update(nValue=1,sValue="")
        else:
            self.lcdDev.set_config(False, obj.blinking)
            Devices[UNITCURSOR].Update(nValue=0,sValue="")
        Domoticz.Debug("set_cursor: OK")
    except:
        write_to_log(STATUSLEVELERROR, "Set cursor failed. Check settings." )
    return

"""
Set the lcd cursor blinking to On or Off and update the Domoticz switch device to On or Off
Parameter
state - String On or Off - note the string is case sensitive
"""
def set_blinking(self,state):
    Domoticz.Debug("set_blinking: Change state=%s" % (state) )
    if self.ipConnected == 0:
        write_to_log(STATUSLEVELERROR, "Set blinking failed. Not connected to the Master Brick. Check settings." )
        return
    try:
        obj = self.lcdDev.get_config()
        if state == SWITCHON:
            self.lcdDev.set_config(obj.cursor, True)
            Devices[UNITBLINKING].Update(nValue=1,sValue="")
        else:
            self.lcdDev.set_config(obj.cursor, False)
            Devices[UNITBLINKING].Update(nValue=0,sValue="")
        Domoticz.Debug("set_blinking: OK")
    except:
        write_to_log(STATUSLEVELERROR, "Set blinking failed. Check settings." )
    return

"""
Set LCD text for the 4 lines and 20 columns using json.
Parameter:
unit - unit number as defined in the constants (see top) for the text device holding the JSON string.
The text as JSON array string [{},{}] is provided by a device unit using the property device.sValue
The JSON array has 1 to N entries with line properties.
It is possible to define an entry for a line or multiple entries for a line for different positions.
JSON keys with value explain
"line" - 0-3
"position" - 0-19
"clear": clear the display: 0=no clear,1=clear line,2=clear display
"text": text to display at the line

Example JSON string = JSON array for the 4 lines
jsonarraystring = '
[
    {"line":0,"position":0,"clear":1,"text":"TEXT 1"},
    {"line":1,"position":0,"clear":1,"text":"TEXT 2"},
    {"line":2,"position":0,"clear":1,"text":"TEXT 3"},
    {"line":3,"position":0,"clear":1,"text":"TEXT 4"}
]'
"""
def write_lines(self,unit):
    Domoticz.Debug("write_lines: Unit=%d,ID=%d,JSON=%s" % (unit, Devices[unit].ID, Devices[unit].sValue) )
    EMPTYLINE = "                    "
    jsonstring = Devices[unit].sValue
    if len(jsonstring) == 0:
        write_to_log(STATUSLEVELERROR,"No JSON string defined for the text device (Unit sValue empty).")
        return
    try:
        # Define the lcd function write_line parameter
        line = 0
        position = 0
        text = ""
        clear = 0
        # parse the json string
        json_array = json.loads(jsonstring, encoding=None)
        Domoticz.Debug("write_lines: Lines: %d" % (len(json_array)) )
        for item in json_array:
            line = int(item["line"])
            position = int(item["position"])
            text = item["text"]
            clear = int(item["clear"])
            # Domoticz.Debug("write_lines: Items (l,p,t,c): %d,%d,%s,%d" % (line,position,text,clear) )
            # Checks
            if (line < 0 or line > 3):
                write_to_log(STATUSLEVELERROR, "write_lines: Wrong line number: %d. Ensure 0-3." % (line) )
                return
            if (position < 0 or position > 19):
                write_to_log(STATUSLEVELERROR, "write_lines: Wrong position number: %d. Ensure 0-19." % (position) )
                return
            # Clear action: 1=clear line;2=clear display
            if clear == 1:
                self.lcdDev.write_line(line, 0, EMPTYLINE)
            if clear == 2:
                self.lcdDev.clear_display()
            # Write text 
            self.lcdDev.write_line(line, position, text)
            write_to_log(STATUSLEVELOK, "write_lines: Line=%d,Position=%d,Text=%s" % (line,position,text) )
        Domoticz.Debug("write_lines: OK")
    except:
        write_to_log(STATUSLEVELERROR, "write_lines: Failed writing text (Unit=%d,ID=%d,JSON=%s). Check JSON definition." % (unit, Devices[unit].ID, Devices[unit].sValue) )
    return

#
# Buttons
#

def set_button_device_state(button, state):
    Domoticz.Debug("set_button_device_state: Button %d to State %d" % (button,state) )
    # Get the button id 0-3 and assign to the button unit 9-12 (see top under constants)
    buttonUnit = button + UNITBUTTON0
    # Switch the Domoticz Button Device ON (=1) or OFF (=0)
    try:
        Devices[buttonUnit].Update(nValue=state,sValue="")
        Domoticz.Debug("set_button_device_state: OK for Button %s (%d)" % (Devices[buttonUnit].Name,Devices[buttonUnit].ID) )
    except:
        Domoticz.Error("set_button_device_state: OK for Button %s (%d)" % (Devices[buttonUnit].Name,Devices[buttonUnit].ID) )

# Callback function for button pressed callback
def onButtonPressedCallback(button):
    Domoticz.Debug("Button Pressed: " + str(button))
    set_button_device_state(button, 1)

# Callback function for button released callback
def onButtonReleasedCallback(button):
    Domoticz.Debug("Button Released: " + str(button))
    set_button_device_state(button, 0)

##
# Generic helper functions
##

# Dump the plugin parameter & device information to the domoticz debug log
def write_config_to_log():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return

# Log a status message, either to the domoticz log or error
# Alert Level: 1=OK, 4=ERROR
def write_to_log(level,text):
    if level == STATUSLEVELOK:
        Domoticz.Log(text)
    if level == STATUSLEVELERROR:
        Domoticz.Error(text)
    return

# Map a value range from to.
# Example mapping 0-100% to 0-255: map_range(255,0,100,0,255) gives 255.
def map_range(x,a,b,c,d):
    try:
        y=(x-a)/(b-a)*(d-c)+c
    except:
        y=-1
    return round(y)
  
# Check if a string is JSON format  
def is_string_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        return False
    return True

