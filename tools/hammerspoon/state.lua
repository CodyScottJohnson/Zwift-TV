-- state.lua
local M      = {}
local apps   = require("apps")
local layout = require("layout")
local media  = require("media")
local json   = hs.json

local function appStatusForKey(key)
  local app = apps.appForKey(key)
  local info = {
    key        = key,
    appName    = nil,
    running    = false,
    frontmost  = false,
    fullscreen = false,
    frame      = nil,
  }

  if not app then
    return info
  end

  info.appName   = app:name()
  info.running   = app:isRunning()
  info.frontmost = app:isFrontmost()

  local win = app:mainWindow()
  if win then
    info.frame      = win:frame()
    info.fullscreen = win:isFullScreen()
  end

  return info
end

function M.statusTable()
  local appStatuses = {}
  for _, key in ipairs(apps.allAppKeys()) do
    appStatuses[key] = appStatusForKey(key)
  end

  local activeApp = nil
  local frontmost = hs.window.frontmostWindow()
  if frontmost then
    local fApp = frontmost:application()
    if fApp then
      activeApp = fApp:name()
    end
  end

  return {
    apps        = appStatuses,
    layoutMode  = layout.currentLayoutMode(),
    focusKey    = layout.currentFocusKey(),
    media       = {
      service = media.currentService()
    },
    activeApp   = activeApp,
    timestamp   = hs.timer.localTime()
  }
end

function M.statusJSON()
  return json.encode(M.statusTable(), true)
end

return M