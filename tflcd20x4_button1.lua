-- Tinkerforge LCD20x4  Bricklet Plugin - Test Script Clock
-- dzVents Automation Script: tflcd20x4_button1
-- If button 1 is pressed, turn the backlight on or off depending state
-- To avoid spoiling the log of devices, the log is cleared at every time update - using function openURL
-- 20200115 by rwbL

-- Idx of the devices used
-- text device for JSON text.
IDXJSON = 85    -- LCD line&position set by JSON string array
IDXBUTTON1 = 90
IDXBACKLIGHT = 86

return {
	on = {
		devices = {
			IDXBUTTON1
		}
	},
	execute = function(domoticz, device)
		domoticz.log('Device ' .. device.name .. ' was changed to state ' .. device.state, domoticz.LOG_INFO)
        -- Check the state of the button 1
		if (device.state == 'On') then
            -- Get the backlight state and switch on or off depending state
            if (domoticz.devices(IDXBACKLIGHT).state == 'On') then
                domoticz.devices(IDXBACKLIGHT).switchOff()
            else            
                domoticz.devices(IDXBACKLIGHT).switchOn()
            end

            -- Clear the device log
            domoticz.openURL('http://localhost:8080/json.htm?type=command&param=clearlightlog&idx=' .. IDXBUTTON1)
            domoticz.openURL('http://localhost:8080/json.htm?type=command&param=clearlightlog&idx=' .. IDXBACKLIGHT)
            
        else
            domoticz.devices(IDXBUTTON0).switchOff()
		end
    end
}