# domoticz-plugin-tinkerforge-lcd20x4
[Domoticz](https://www.domoticz.com/) plugin to interact with the [Tinkerforge LCD 20x4 Bricklet](https://www.tinkerforge.com/en/doc/Hardware/Bricklets/LCD_20x4.html#lcd-20x4-bricklet).

# Objectives
* To write characters and use the buttons of the Tinkerforge LCD 20x4 Bricklet.
* To learn how to write Python plugin(s) for the Domoticz Home Automation system interacting with [Tinkerforge](http://www.tinkerforge.com) Building Blocks.

_Abbreviations_: TF=Tinkerforge, Bricklet=Tinkerforge LCD 20x4 Bricklet, GUI=Domoticz Web UI.

## Solution
The plugin enables to write characters to the LCD 20x4 display via a Domoticz text device (Type:General, SubType:Text) and to use the 4 LCD buttons ia Domoticz Switch devices (Type:Light/Switch, SubType:Switch, SwitchType:On/Off).
At plugin start, an IP connection is established until either Domoticz stops or the plugin is disabled.
The text to be displayed is defined as a JSON formatted string (array with up-to 4 line items).
```
[{"line":1,"position":n,"clear":n,"text":"Text"},{"line":2,"position":n,"clear":n,"text":"Text"},{"line":3,"position":n,"clear":n,"text":"Text"},{"line":4,"position":n,"clear":n,"text":"Text"}] 
```
Each line item has the key:value pairs:
* "line":0-3 - Integer with line index 0 to 3.
* "position":0-19 - Integer with position index 0 - 19.
* "clear":1-2 - Integer to clear the line (1) or clear the display (2) prior writing the text to the line.
* "Text":"Text string" - The text to be displayed.
Custom characters are defined in an external file and displayed via Unicode. LCD table characters are also displayed via Unicode.
When the plugin starts, the backlight is switched on, the cursor is turned off and not blinking.
If the text of the Domoticz device is modified, the plugin connects via IP to Tinkerforge, writes the LCD line(s) as defined by the JSON string and disconnects.
Modifying the text of the Domoticz device can be done via scripts, API etc. See examples below.

**Note**
This is the full version of the plugin. There is also a lite version with a single Domoticz text device updated using JSON formatted string.
        
### Domoticz Devices
* Lines 0-3 JSON - Type:General, SubType:Text, Name:JSON (set text for up-to 4 LCD lines at any position using JSON array).
* Backlight - Type:Light/Switch, SubType:Switch, SwitchType:On/Off, Name:Backlight (set the backlight on/off).
* Cursor - Type:Light/Switch, SubType:Switch, SwitchType:On/Off, Name:Cursor (set the cursor [underscore] on/off).
* Blinking - Type:Light/Switch, SubType:Switch, SwitchType:On/Off, Name:Blinking (set the cursor blinking on/off).
* Buttons - Type:Light/Switch, SubType:Switch, SwitchType:On/Off, Name:Button 0 -3 (set the buttons).

In total 8 Domoticz devices are created for the Tinkerforge LCD 20x4 bricklet.

### Configuration
* Address: IP address of the host connected to. Default: 127.0.0.1 (for USB connection)
* Port: Port used by the host. Default: 4223
* UID: Unique identifier of the LCD 20x4 Bricklet. Obtain the UID via the Brick Viewer. Default: BHN

The bricklet is connected to a Tinkerforge Master Brick which is direct connected via USB with the Domoticz Home Automation system.
The Domoticz Home Automation system is running on a Raspberry Pi 3B+.

### Logic
The only function of the plugin is to set the text for each line to the display.
Any additional logic to be defined in Domoticz. Either by additional devices or scripts.
_Examples_ (Scripts)
* Clock - Display clock CHH:MM - C is the custom character (index1, \u0009) clock symbol (update every minute).
* Raspberry Pi Monitor - Display the CPU Temperature, RAM & Disc usage and the time (update every minute).
More see section "dzVents Lua Automation Script Examples".

## Hardware Parts
* Raspberry Pi 3B+ [(Info)](https://www.raspberrypi.org)
* Tinkerforge Master Brick 2.1 FW 2.4.10 [(Info)](https://www.tinkerforge.com/en/doc/Hardware/Bricks/Master_Brick.html#master-brick)
* Tinkerforge LCD 20x4 Bricklet 1.2 FW 2.0.6 [(Info)](https://www.tinkerforge.com/en/doc/Hardware/Bricklets/LCD_20x4.html#lcd-20x4-bricklet)

## Software
* Raspberry Pi Raspian Debian Linux Buster 4.19.93-v7+ #1290
* Domoticz Home Automation System V4.11717 (beta) 
* Tinkerforge Brick Daemon 2.4.1, Brick Viewer 2.4.11
* Tinkerforge Python API-Binding 2.1.24 [(Info)](https://www.tinkerforge.com/en/doc/Software/Bricklets/LCD20x4_Bricklet_Python.html)
* Python 3.7.3, GCC 8.2.0
* The versions for developing this plugin are subject to change.

## Quick Steps
For implementing the Plugin on the Domoticz Server running on the Raspberry Pi.
See also Python Plugin Code (well documented) **plugin.py**.

## Test Setup
For testing this plugin, the test setup has a Master Brick with LCD 20x4 Bricklet connected to port B.
On the Raspberry Pi, it is mandatory to install the Tinkerforge Brick Daemon and Brick Viewer following [these](https://www.tinkerforge.com/en/doc/Embedded/Raspberry_Pi.html) installation instructions (for Raspian armhf).
Start the Brick Viewer and action:
* Update the devices firmware
* Obtain the UID of the LCD 20x4 Bricklet as required by the plugin (i.e. BHN).

## Domoticz Web GUI
Open windows GUI Setup > Hardware, GUI Setup > Log, GUI Setup > Devices
This is required to add the new hardware with its device and monitor if the plugin code is running without errors.
It is imporant, that the GUI > Setup > Hardware accepts new devices!

## Create folder
The folder name is the same as the key property of the plugin (i.e. plugin key="tflcd20x4").
```
cd /home/pi/domoticz/plugins/tflcd20x4
```

## Create the plugin
The Python plugin has a mandatory filename **plugin.py** located in the created plugin folder.
Domoticz Python Plugin Source Code: see file **plugin.py**.
In addition to the plugin file, the custom character file **customchar.json** is required.

### Plugin Pseudo Code
```
Define imports and amend path

Define constants for the devices (Units)

Define class BasePlugin:
	Init
		define debug flag & connection vars
	onStart
		If first time, create the device Type General, SubType Text
		Get the device UID
		Make IP connection
		Configure the bricklet backlight on, cursor off, blink off = [function set_bricklet_configuration()]
		Register callbacks for the button pressed & released
	onCommand(self, Unit)
		Handle button pressed & released [functions set_button_device_state(button, state),onButtonPressedCallback(button),onButtonReleasedCallback(button)]
	onDeviceModified(self, Unit)
		Handle text changes for the unit (the text device with JSON formatted string)
		UNITJSON = [function write_lines(unit)]
```

### Communication
Bricklet communication is on request = connect, execute function and disconnect from the Master Brick.
There is no ongoing connection between the plugin and Domoticz, as no callback used.
The plugin function onHeartbeat (every 10s) is not used.

### Write Lines
The text to be written to the display is defined in a JSON formatted string hold by the Domotiz Text device (default name Hardware - JSON, i.e. LCD20x4 - JSON).
The JSON string is an array with up-to 4 line items - at least 1 line must be defined.
```
[{"line":1,"position":n,"clear":n,"text":"Text"},{"line":2,"position":n,"clear":n,"text":"Text"},{"line":3,"position":n,"clear":n,"text":"Text"},{"line":4,"position":n,"clear":n,"text":"Text"}] 
```
Each line item has the **key:value pairs**:
"line":0-3 - Integer with line index 0 to 3.
"position":0-19 - Integer with position index 0 - 19.
"clear":1-2 - Integer to clear the line (1) or clear the display (2) prior writing the text to the line.
"Text":"Text string" - The text to be displayed.

#### Example Single Line
JSON string writing "Hello World" to line index 1 at position 9 and clearing the display prior writing.
```
[{"line":1,"position":9,"clear":2,"text":"Hello World"}] 
```

**Lua**
Define the JSON string and update the Domotiz device (General/Text,idx=84) which triggers writing to the LCD display.
```
IDXJSON = 84
local line = '[{"line":%d,"position":%d,"clear":2,"text":"%s"}]'
line = string.format(line, 1, 9, "Hello World" )
domoticz.devices(IDXJSON).updateText(line)
```

**API**
Send via HTTP API REST request, the JSON string for the device with idx=84.
This is a fast way to test the plugin.
In the URL, the special characters are escaped: "=%22, space=%20.
Do not embed the JSON array in "", i.e. "[{}]", but leave the "" out, i.e. [{}]
```
http://domoticz-ip-address:8080/json.htm?type=command&param=udevice&idx=84&nvalue=0&svalue=[{%22line%22:1,%22position%22:9,%22clear%22:2,%22text%22:%22Hello%20World!%22}]
```
with HTTP response:
```
{"status" : "OK","title" : "Update Device"}
```
and Domoticz Log:
```
2020-02-14 16:08:36.002 (LCD) Pushing 'CPluginMessageBase' on to queue 
2020-02-14 16:08:36.015 (LCD) Processing 'CPluginMessageBase' message 
2020-02-14 16:08:36.016 (LCD) Calling message handler 'onDeviceModified'. 
2020-02-14 16:08:36.016 (LCD) onDeviceModified called Unit:1 (LCD20x4 - JSON),nValue=0,sValue=[{"line":1,"position":9,"clear":2,"text":"Hello World!"}] 
2020-02-14 16:08:36.017 (LCD) write_lines: Unit=1,ID=84,JSON=[{"line":1,"position":9,"clear":2,"text":"Hello World!"}] 
2020-02-14 16:08:36.029 (LCD) write_lines: Lines: 1 
2020-02-14 16:08:36.030 (LCD) write_lines: Line=1,Position=9,Text=Hello World! 
2020-02-14 16:08:36.134 (LCD) write_lines: OK
```

#### Example All Lines
JSON string writing all 4 lines and clear the lines prior writing.
Basically some data to monitor the Raspberry Pi Domoticz System is displayed.
```
[
{"line":1,"position":0,"clear":1,"text":"CPU 43.5 \u00DFC"},
{"line":2,"position":0,"clear":1,"text":"RAM 29.42 %"},
{"line":3,"position":0,"clear":1,"text":"DISC 69.08 %"},
{"line":0,"position":14,"clear":1,"text":"\u000909:37"}
] 
```

### Custom Characters
Custom Characters are defined as an JSON array in an external file  located in the plugin folder.
The content is parsed and assigned to the Tinkerforge character set during plugin start.
Set Custom Characters with index 0-7 as max 8 custom characters can be defined.
JSON format example with some characters.
The id has a range 0-7, name is to know what character is defined, char is the 8 bit definition as decimals.
```
[
{"id":0,"name":"battery","char":"14,27,17,17,17,17,17,31"},
{"id":1,"name":"clock","char":"31,17,10,4,14,31,31,0"},
{"id":2,"name":"arrowdown","char":"0,4,4,4,31,14,4,0"},
{"id":3,"name":"arrowup","char":"0,4,14,31,4,4,4,0"},
{"id":4,"name":"nochange","char":"0,0,31,0,31,0,0,0"}
]
```

_Python_
Ensure to write in Unicode \u00NN and NOT \xNN.
Example using the device object:
lcdDev.write_line(0, 0, "Battery: " + "\u0008")

_Lua_
Ensure to escape the backslash \ character.
Example using string format to define a line with custom character clock, which has index 1(id:1) and unicode format \u0009:
local line0 = string.format('{"line":1,"position":0,"clear":1,"text":"Clock  %s  \\u0009"}', timenow )

### LCD Table Characters
To display a character from the LCD, use the same approach as for custom characters.
Example displaying the degree character, which is at position DF. Displayed is °C.
local line0 = string.format('{"line":1,"position":0,"clear":1,"text":"CPU  %s  \\u00DFC"}', cputemp )

### Hints
#### Clear Display
To clear the display, define a JSON string with empty text and clear = 2 at line = 0, position = 0.
```
[{"line":0,"position":0,"clear":2,"text":""}]
```

#### Bricklet Disconnected
If the LCD 20x4 bricklet is disconnected and connected again to the Domoticz system, the plugin must be updated (GUI > Setup > Hardware > select plugin).

## Install the Tinkerforge Python API
There are two options.

### 1) sudo pip3 install tinkerforge
Advantage: in case of binding updates, only a single folder must be updated.
Check if a subfolder tinkerforge is created in folder /usr/lib/python3/dist-packages.
**Note**
Check the version of "python3" in the folder path. This could also be python 3.7 or other = see below.

**If for some reason the bindings are not installed**
Unzip the Tinkerforge Python Binding into the folder /usr/lib/python3/dist-packages.
_Example_
Create subfolder Tinkerforge holding the Tinkerforge Python Library
```
cd /home/pi/tinkerforge
```
Unpack the latest python bindings into folder /home/pi/tinkerforge
Copy /home/pi/tinkerforge to the Python3 dist-packges
```
sudo cp -r /home/pi/tinkerforge /usr/lib/python3/dist-packages/
```

In the Python Plugin code amend the import path to enable using the Tinkerforge libraries
```
from os import path
import sys
sys.path
sys.path.append('/usr/local/lib/python3.7/dist-packages')
```

### 2) Install the Tinkerforge Python Bindings in a subfolder of the plugin and copy the binding content.
Disadvantage: Every Python plugin using the Tinkerforge bindings must have a subfolder tinkerforge.
In case of binding updates,each of the tinkerforge plugin folders must be updated.
/home/pi/domoticz/plugins/...

There is no need to amend the path as for option 1.

For either ways, the bindings are used like:
```
import tinkerforge
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_lcd_20x4 import BrickletLCD20x4
```
**Note**
Add more bindings depending Tinkerforge bricks & bricklets used.

Ensure to update the files in case of newer Tinkerforge Python Bindings.

## Make plugin.py executable
```
cd /home/pi/domoticz/plugins/tflcd20x4
chmod +x plugin.py
```

## Restart Domoticz
Restart Domoticz to find the plugin:
```
sudo systemctl restart domoticz.service
```

**Note**
When making changes to the Python plugin code, ensure to restart Domoticz and refresh any of the Domoticz Web GUI's.

## Domoticz Add Hardware Tinkerforge LCD 20x4 Bricklet
**IMPORTANT**
Prior adding, set GUI Stup > Settings > Hardware the option to allow new hardware.
If this option is not enabled, no new devices are created assigned to this hardware.
Check in the Domoticz log as error message Python script at the line where the new device is used
(i.e. Domoticz.Debug("Device created: "+Devices[1].Name))

In the GUI Setup > Hardware add the new hardware "Tinkerforge LCD 20x4 Bricklet".

## Add Hardware - Check the Domoticz Log
After adding,ensure to check the Domoticz Log (GUI Setup > Log)

### Example Domoticz Log Entry Adding Hardware with Debug=True
```
2020-02-15 11:10:33.464 Status: Startup Path: /home/pi/domoticz/ 
2020-02-15 11:10:33.617 Status: PluginSystem: Started, Python version '3.7.3'. 
2020-02-15 11:11:05.879 Status: (LCD) Started. 
2020-02-15 11:11:06.299 (LCD) Debug logging mask set to: PYTHON PLUGIN QUEUE IMAGE DEVICE CONNECTION MESSAGE ALL 
2020-02-15 11:11:06.299 (LCD) 'HardwareID':'11' 
2020-02-15 11:11:06.299 (LCD) 'HomeFolder':'/home/pi/domoticz/plugins/tflcd20x4/' 
2020-02-15 11:11:06.299 (LCD) 'StartupFolder':'/home/pi/domoticz/' 
2020-02-15 11:11:06.299 (LCD) 'UserDataFolder':'/home/pi/domoticz/' 
2020-02-15 11:11:06.299 (LCD) 'Database':'/home/pi/domoticz/domoticz.db' 
2020-02-15 11:11:06.299 (LCD) 'Language':'en' 
2020-02-15 11:11:06.299 (LCD) 'Version':'0.8.0' 
2020-02-15 11:11:06.299 (LCD) 'Author':'rwbL' 
2020-02-15 11:11:06.299 (LCD) 'Name':'LCD' 
2020-02-15 11:11:06.299 (LCD) 'Address':'127.0.0.1' 
2020-02-15 11:11:06.299 (LCD) 'Port':'4223' 
2020-02-15 11:11:06.299 (LCD) 'Key':'tflcd20x4' 
2020-02-15 11:11:06.299 (LCD) 'Mode1':'BHN' 
2020-02-15 11:11:06.299 (LCD) 'Mode6':'Debug' 
2020-02-15 11:11:06.300 (LCD) 'DomoticzVersion':'4.11674' 
2020-02-15 11:11:06.300 (LCD) 'DomoticzHash':'91c3475ac' 
2020-02-15 11:11:06.300 (LCD) 'DomoticzBuildTime':'2020-02-09 10:00:09' 
2020-02-15 11:11:06.300 (LCD) Device count: 0 
2020-02-15 11:11:06.300 (LCD) Creating devices 
2020-02-15 11:11:06.300 (LCD) Creating device 'JSON'. 
2020-02-15 11:11:06.301 (LCD) Device created: LCD - JSON 
2020-02-15 11:11:06.301 (LCD) Creating device 'Backlight'. 
2020-02-15 11:11:06.303 (LCD - Backlight) Updating device from 0:'' to have values 1:''. 
2020-02-15 11:11:06.315 (LCD) Device created: LCD - Backlight 
2020-02-15 11:11:06.316 (LCD) Creating device 'Cursor'. 
2020-02-15 11:11:06.317 (LCD) Device created: LCD - Cursor 
2020-02-15 11:11:06.317 (LCD) Creating device 'Blinking'. 
2020-02-15 11:11:06.318 (LCD) Device created: LCD - Blinking 
2020-02-15 11:11:06.318 (LCD) Creating device 'Button 0'. 
2020-02-15 11:11:06.319 (LCD) Device created: LCD - Button 0 
2020-02-15 11:11:06.319 (LCD) Creating device 'Button 1'. 
2020-02-15 11:11:06.321 (LCD) Device created: LCD - Button 1 
2020-02-15 11:11:06.321 (LCD) Creating device 'Button 2'. 
2020-02-15 11:11:06.322 (LCD) Device created: LCD - Button 2 
2020-02-15 11:11:06.322 (LCD) Creating device 'Button 3'. 
2020-02-15 11:11:06.323 (LCD) Device created: LCD - Button 3 
2020-02-15 11:11:06.323 (LCD) Creating device: OK 
2020-02-15 11:11:06.326 (LCD) IP Connection - OK 
2020-02-15 11:11:06.327 (LCD) set_configuration. IP-Connected: 1 
2020-02-15 11:11:06.327 (LCD) set_backlight: Change state=On 
2020-02-15 11:11:06.327 (LCD - Backlight) Updating device from 1:'' to have values 1:''. 
2020-02-15 11:11:06.339 (LCD) set_backlight: OK 
2020-02-15 11:11:06.339 (LCD) set_cursor: Change state=Off 
2020-02-15 11:11:06.341 (LCD - Cursor) Updating device from 0:'' to have values 0:''. 
2020-02-15 11:11:06.359 (LCD) set_cursor: OK 
2020-02-15 11:11:06.359 (LCD) set_blinking: Change state=Off 
2020-02-15 11:11:06.366 (LCD - Blinking) Updating device from 0:'' to have values 0:''. 
2020-02-15 11:11:06.379 (LCD) set_blinking: OK 
2020-02-15 11:11:06.380 (LCD) Customchar: characters: 5 
2020-02-15 11:11:06.380 (LCD) Customchar: Index=0,Name=battery,Char=14,27,17,17,17,17,17,31 
2020-02-15 11:11:06.381 (LCD) Customchar: Index=1,Name=clock,Char=31,17,10,4,14,31,31,0 
2020-02-15 11:11:06.381 (LCD) Customchar: Index=2,Name=arrowdown,Char=0,4,4,4,31,14,4,0 
2020-02-15 11:11:06.381 (LCD) Customchar: Index=3,Name=arrowup,Char=0,4,14,31,4,4,4,0 
2020-02-15 11:11:06.381 (LCD) Customchar: Index=4,Name=nochange,Char=0,0,31,0,31,0,0,0 
2020-02-15 11:11:06.382 (LCD) set_configuration OK 
2020-02-15 11:11:06.296 Status: (LCD) Entering work loop. 
2020-02-15 11:11:06.296 Status: (LCD) Initialized version 0.8.0, author 'rwbL' 
```

### Domoticz Log Switch Backlight

#### Backlight Off
```
2020-02-15 11:12:51.302 (LCD) Pushing 'onCommandCallback' on to queue 
2020-02-15 11:12:51.321 (LCD) Processing 'onCommandCallback' message 
2020-02-15 11:12:51.321 (LCD) Calling message handler 'onCommand'. 
2020-02-15 11:12:51.321 (LCD) onCommand called for Unit 2: Parameter 'Off', Level: 0', Hue: 
2020-02-15 11:12:51.321 (LCD) set_backlight: Change state=Off 
2020-02-15 11:12:51.321 (LCD - Backlight) Updating device from 1:'' to have values 0:''. 
2020-02-15 11:12:51.351 (LCD) set_backlight: OK 
2020-02-15 11:12:51.302 Status: User: Admin initiated a switch command (86/LCD - Backlight/Off) 
```

#### Backlight On
```
2020-02-15 11:12:54.118 (LCD) Pushing 'onCommandCallback' on to queue 
2020-02-15 11:12:54.156 (LCD) Processing 'onCommandCallback' message 
2020-02-15 11:12:54.156 (LCD) Calling message handler 'onCommand'. 
2020-02-15 11:12:54.157 (LCD) onCommand called for Unit 2: Parameter 'On', Level: 0', Hue: 
2020-02-15 11:12:54.157 (LCD) set_backlight: Change state=On 
2020-02-15 11:12:54.158 (LCD - Backlight) Updating device from 0:'' to have values 1:''. 
2020-02-15 11:12:54.197 (LCD) set_backlight: OK 
2020-02-15 11:12:54.117 Status: User: Admin initiated a switch command (86/LCD - Backlight/On) 
```

## dzVents Lua Automation Script Examples

### Hello World
```
-- Tinkerforge LCD20x4  Bricklet Plugin - Test Script
-- dzVents Automation Script: tflcd20x4_hello_world
-- Display the text "Hello World".
-- A JSON array with a single entry is used to set the text.
-- To avoid spoiling the log of the text device, the log is cleared at every time update - using function openURL
-- 20200114 by rwbL

-- Idx of the text device for JSON text.
IDXJSON = 84    -- LCD line&position set by JSON string array

return {
	on = {
		timer = {
			'every minute',
	   },
    },
	execute = function(domoticz, timer)
        local line = '[' ..
                        '{"line":%d,"position":%d,"clear":2,"text":"%s"}' ..
                     ']'
        line = string.format(line, 1, 9, "Hello World" )
        domoticz.devices(IDXJSON).updateText(line)
        -- Clear the device log
        domoticz.openURL('http://localhost:8080/json.htm?type=command&param=clearlightlog&idx=' .. IDXJSON)
    end
}
```

### Clock
```
-- Tinkerforge LCD20x4  Bricklet Plugin - Test Script Clock
-- dzVents Automation Script: tflcd20x4_clock
-- Display clock CHH:MM - C is the custom character (index1, \u0009) clock symbol.
-- The time, updated every minute, position is randomly on the LCD display at one of the 4 lines 0-3 and at positions 0-13 (=19 - length time characters 6).
-- A JSON array with a single entry is used to set the time.
-- To avoid spoiling the log of the text device, the log is cleared at every time update - using function openURL
-- 20200109 by rwbL

-- Idx of the text device for JSON text.
IDXJSON = 84    -- LCD line&position set by JSON string array

-- NOTE
-- In the plugin, the function onDeviceModified handles new text from the text units (devices). The text is in property Devices[Unit].sValue
-- def onDeviceModified(self, Unit):
--  # for json format the unit IDXJSON is used.
--  WriteLCDFromJSON(Unit)

-- split a string by delimiter
-- return array, i.e. array[1], array[2]
function splitstring(s, delimiter)
    result = {};
    for match in (s..delimiter):gmatch("(.-)"..delimiter) do
        table.insert(result, match);
    end
    return result;
end

-- get the current time from the domoticz instance with time object
-- return time now, i.e. 09:09
function isnowhhmm(domoticz)
    timearray = splitstring(domoticz.time.rawTime, ':')
    return timearray[1] .. ':' .. timearray[2]
end

return {
	on = {
		timer = {
			'every minute',
	   },
    },
	execute = function(domoticz, timer)
		domoticz.log('Timer event was triggered by ' .. timer.trigger, domoticz.LOG_INFO)

        -- JSON
        -- The JSON array has a single entry to set the CHH:MM at line, position
        -- Use string format for only line 3 and clear the display prior writing text
        -- Special character is writte prior time - \u0009 is the second special character (index 1).
        -- Ensure to escape \ and DO NOT USE hex format \xNN as not supported by json.load = use unicode format \uNNNN
        local line = '[' ..
                        '{"line":%d,"position":%d,"clear":2,"text":"%s%s"}' ..
                     ']'
        -- Random line and position
        local l = math.floor(math.random(0,3))
        local p = math.floor(math.random(0,14))
        line = string.format(line, l, p, "\\u0009", isnowhhmm(domoticz) )
        domoticz.devices(IDXJSON).updateText(line)
            
        -- Clear the device log
        domoticz.openURL('http://localhost:8080/json.htm?type=command&param=clearlightlog&idx=' .. IDXJSON)
    end
}
```

### Raspberry Pi Monitor (dzVents Lua Automation Script)
```
-- Tinkerforge LCD20x4  Bricklet Plugin - Test Script 
-- dzVents Automation Script: tflcd20x4_rpi_monitor
-- Display the CPU Temperature, RAM & Disc usage and the time (update every minute).
-- The text is defined by using JSON string writing to virtualdevice type: General, subtype: Text.
-- To display special characters use unicode \uNNNNN and NOT hex \xNN.
-- 20200112 by rwbL

-- Idx devices.
IDXRPICPUTEMP = 2
IDXRPIRAMUSAGE = 3
IDXRPIDISCUSAGE = 8
IDXLCDJSON = 84    -- LCD line 0-3 set by JSON string array

-- split a string by delimiter
-- return array, i.e. array[1], array[2]
function splitstring(s, delimiter)
    result = {};
    for match in (s..delimiter):gmatch("(.-)"..delimiter) do
        table.insert(result, match)
    end
    return result
end

-- get the current time from the domoticz instance with time object
-- return time now, i.e. 09:09:00
function isnowtime(domoticz)
    return domoticz.time.rawTime
end

-- get the current time from the domoticz instance with time object
-- return time now, i.e. 09:09
function isnowhhmm(domoticz)
    timearray = splitstring(domoticz.time.rawTime, ':')
    return timearray[1] .. ':' .. timearray[2]
end

return {
	on = {
		timer = {
			'every minute',
	   },
    },
	execute = function(domoticz, timer)
		domoticz.log('Timer event was triggered by ' .. timer.trigger, domoticz.LOG_INFO)

    	-- All 4 lines defined
    	local cputemp = domoticz.devices(IDXRPICPUTEMP).sValue
        local ramusage = domoticz.devices(IDXRPIRAMUSAGE).sValue
        local discusage = domoticz.devices(IDXRPIDISCUSAGE).sValue

        -- The time is displayed line 0 at the right with special character time symbol (index 1 = \u0009)
        local line3 = string.format('{"line":0,"position":14,"clear":1,"text":"\\u0009%s"}', isnowhhmm(domoticz) )
        -- To display degree C use the unicode hex value for ° character which is \u00DF (see LCD character table)
        local line0 = string.format('{"line":1,"position":0,"clear":1,"text":"CPU  %s  \\u00DFC"}', cputemp )
        -- The % character needs to be escaped with % to %%
        local line1 = string.format('{"line":2,"position":0,"clear":1,"text":"RAM  %s %%"}', ramusage )
        local line2 = string.format('{"line":3,"position":0,"clear":1,"text":"DISC %s %%"}', discusage )

	   	local line = string.format('[%s,%s,%s,%s]', line0,line1,line2,line3)
		-- domoticz.log('Line: ' .. line, domoticz.LOG_INFO)
        domoticz.devices(IDXLCDJSON).updateText(line)

        -- Clear the device log
        domoticz.openURL('http://localhost:8080/json.htm?type=command&param=clearlightlog&idx=' .. IDXLCDJSON)
    end
}
```

#### Example Log (Plugin debug option True)
```
2020-02-14 10:44:00.357 (LCD) Pushing 'CPluginMessageBase' on to queue 
2020-02-14 10:44:00.383 (LCD) Processing 'CPluginMessageBase' message 
2020-02-14 10:44:00.386 (LCD) Calling message handler 'onDeviceModified'. 
2020-02-14 10:44:00.386 (LCD) onDeviceModified called: Unit 1, LCD20x4 - JSON 
2020-02-14 10:44:00.386 (LCD) nValue=0,sValue=[{"line":1,"position":0,"clear":1,"text":"CPU 44.0 \u00DFC"},{"line":2,"position":0,"clear":1,"text":"RAM 29.18 %"},{"line":3,"position":0,"clear":1,"text":"DISC 69.08 %"},{"line":0,"position":14,"clear":1,"text":"\u000910:44"}] 
2020-02-14 10:44:00.386 (LCD) write_lines: Unit=1,ID=84,JSON=[{"line":1,"position":0,"clear":1,"text":"CPU 44.0 \u00DFC"},{"line":2,"position":0,"clear":1,"text":"RAM 29.18 %"},{"line":3,"position":0,"clear":1,"text":"DISC 69.08 %"},{"line":0,"position":14,"clear":1,"text":"\u000910:44"}] 
2020-02-14 10:44:00.391 (LCD) JSON line items: 4 
2020-02-14 10:44:00.391 (LCD) Items (l,p,t,c): 1,0,CPU 44.0 ßC,1 
2020-02-14 10:44:00.393 (LCD) LCD line written=1,0:CPU 44.0 ßC 
2020-02-14 10:44:00.393 (LCD) Items (l,p,t,c): 2,0,RAM 29.18 %,1 
2020-02-14 10:44:00.394 (LCD) LCD line written=2,0:RAM 29.18 % 
2020-02-14 10:44:00.394 (LCD) Items (l,p,t,c): 3,0,DISC 69.08 %,1 
2020-02-14 10:44:00.395 (LCD) LCD line written=3,0:DISC 69.08 % 
2020-02-14 10:44:00.395 (LCD) Items (l,p,t,c): 0,14, 10:44,1 
2020-02-14 10:44:00.396 (LCD) LCD line written=0,14: 10:44 
2020-02-14 10:44:00.498 (LCD) write_lines: OK 
2020-02-14 10:44:00.322 Status: dzVents: Info: ------ Start internal script: tflcd20x4_rpi_monitor:, trigger: every minute 
2020-02-14 10:44:00.322 Status: dzVents: Info: Timer event was triggered by every minute 
2020-02-14 10:44:00.350 Status: dzVents: Info: ------ Finished tflcd20x4_rpi_monitor 
2020-02-14 10:44:00.350 Status: EventSystem: Script event triggered: /home/pi/domoticz/dzVents/runtime/dzVents.lua 
```
