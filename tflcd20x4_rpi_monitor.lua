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
