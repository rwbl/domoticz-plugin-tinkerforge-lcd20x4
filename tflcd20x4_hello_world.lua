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
