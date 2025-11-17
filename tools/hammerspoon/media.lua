-- media.lua
local M = {}
local json = hs.json

local MEDIA_URLS = {
  netflix = "https://www.netflix.com/browse",
  disney  = "https://www.disneyplus.com/home",
  youtube = "https://www.youtube.com/",
}

local currentService = nil

function safariKiosk()
    local safari = hs.application.find("Safari")
    if not safari then return end
    safari:activate()

    -- Safari fullscreen (removes URL bar, toolbars, etc.)
    hs.eventtap.keyStroke({"cmd", "ctrl"}, "f", 0)  -- Safari fullscreen toggle

    -- Give it a moment to adjust
    hs.timer.doAfter(0.5, function()
        local win = safari:mainWindow()
        if win then
            -- Force kiosk-style window inside the current space
            win:setFullScreen(false)  -- remove macOS “space” fullscreen
            win:maximize()
        end
    end)
end



local function safariMediaOpen(url)
  hs.application.launchOrFocus("Safari")
  hs.applescript(string.format([[
    tell application "Safari"
      activate
      if (count of windows) = 0 then
        make new document with properties {URL:"%s"}
      else
        tell window 1
          if (count of tabs) = 0 then
            make new tab with properties {URL:"%s"}
          else
            set URL of current tab to "%s"
          end if
        end tell
      end if
    end tell
  ]], url, url, url))
end

local function safariKioskRight()
  local safari = hs.application.find("Safari")
  if not safari then return end
  safari:activate()
  -- Toggle Safari fullscreen, then maximize/resnap
  hs.eventtap.keyStroke({"cmd", "ctrl"}, "f", 0)

  hs.timer.doAfter(0.7, function()
    local win = safari:mainWindow()
    if win then
      win:setFullScreen(false)
      win:moveToUnit(hs.layout.right50)
    end
  end)
end

function M.openService(key)
  local url = MEDIA_URLS[key]
  if not url then return end
  safariMediaOpen(url)
  currentService = key
  hs.timer.doAfter(0.5, safariKiosk)
end

function M.currentService()
  return currentService
end

return M