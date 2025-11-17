-- layout.lua
local M = {}

local apps = require("apps")

local savedLayout = nil
local layoutMode  = "unknown"   -- "split", "focus", etc.
local focusKey    = nil

local function mainWindow(app)
  if not app then return nil end
  return app:mainWindow()
end

local function saveLayout()
  savedLayout = {}
  for _, key in ipairs(apps.allAppKeys()) do
    local app = apps.appForKey(key)
    local win = mainWindow(app)
    if win then
      savedLayout[key] = win:frame()
    end
  end
end

local function restoreLayout()
  if not savedLayout then return end

  for key, frame in pairs(savedLayout) do
    local app = apps.appForKey(key)
    local win = mainWindow(app)
    if win then
      win:setFrame(frame)
      app:unhide()
    end
  end

  savedLayout = nil
end

-- Public state getters (for state.lua)
function M.currentLayoutMode() return layoutMode end
function M.currentFocusKey()   return focusKey end

function M.focusAppForControl(key)
  local app = apps.appForKey(key)
  if not app then return end

  -- Only save once when entering focus mode the first time
  if layoutMode ~= "focus" then
    saveLayout()
  end

  local win = mainWindow(app)
  if win then
    app:activate(true)
    win:maximize()
  end

  -- Hide Safari/media so only the app is visible
  local safari = hs.application.find("Safari")
  if safari then safari:hide() end

  layoutMode = "focus"
  focusKey   = key
end

function M.restoreSplitLayout()
  if savedLayout then
    restoreLayout()
  end
  layoutMode = "split"
  focusKey   = nil
end

-- Called when you first set up the split (Zwift left, Safari right)
function M.setInitialSplit(appKeyForLeft)
  -- This assumes Safari is your media window on the right
  local leftApp   = apps.appForKey(appKeyForLeft)
  local safari    = hs.application.find("Safari")

  if leftApp then
    local win = mainWindow(leftApp)
    if win then win:moveToUnit(hs.layout.left50) end
  end

  if safari then
    local swin = mainWindow(safari)
    if swin then swin:moveToUnit(hs.layout.right50) end
  end

  layoutMode = "split"
  focusKey   = nil
  savedLayout = nil
end

-- Combined helper: ensure split with specific service
function M.splitWorkoutWith(serviceKey)
  -- For simplicity, assume Zwift for now; you can make this smarter
  M.setInitialSplit("zwift")
  -- media.openService(serviceKey) will be called separately usually
  layoutMode = "split"
end

return M