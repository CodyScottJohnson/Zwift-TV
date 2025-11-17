-- gym-controller/hammerspoon/init.lua

local apps   = require("apps")
local layout = require("layout")
local media  = require("media")
local state  = require("state")

hs.ipc = require("hs.ipc")

-- Expose functions for hs CLI / Python to call
function controlApp(key, action, jsonArg)
  apps.controlApp(key, action, jsonArg)
end

function listApps()
  apps.searchInstalledApps()
end

function focusAppForControl(key)
  layout.focusAppForControl(key)
end

function restoreSplitLayout()
  layout.restoreSplitLayout()
end

function splitWorkoutWith(serviceKey)
  layout.splitWorkoutWith(serviceKey)
end

function openMedia(serviceKey)
  media.openService(serviceKey)
end

function printStatusJSON()
  hs.printf(state.statusJSON())
end