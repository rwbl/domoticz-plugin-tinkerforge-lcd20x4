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
