-- apps.lua
local M = {}

local json = hs.json
local spotlight = require("hs.spotlight")


-- Map your logical keys to macOS app names
local APP_MAP = {
    zwift       = "Zwift",
    systm       = "SYSTM", -- or "Wahoo SYSTM" if that's the name
    trainerroad = "TrainerRoad",
    safari      = "Safari",
}

local function appNameForKey(key)
    return APP_MAP[key]
end

local function getApp(appName)
    return hs.application.find(appName)
end

function M.searchInstalledApps()
    local results = {}
    local done = false
    local query = spotlight.new()
        :callbackMessages({ "didFinish" }) -- only fire callback when done
        :setCallback(function(obj, msg, info)
            if msg == "didFinish" then
                -- obj is the spotlightObject; you can use #obj and obj[i]
                print("Found " .. #obj .. " apps:")
                for i = 1, #obj do
                    local item = obj[i] -- hs.spotlight.item
                    -- attribute access via metamethods
                    local name = item.kMDItemDisplayName or "<no name>"
                    local path = item.kMDItemPath or "<no path>"
                    print(name, path,item:attributes())
                    print(hs.spotlight:valueLists())
                end
            end
            done = true
        end)

    -- Set the query string and start the query
    query:queryString([[ kMDItemContentType == "com.apple.application-bundle" ]])
    query:start()
   
end

function M.controlApp(key, action, jsonArg)
    local appName = appNameForKey(key)
    if not appName then return end

    local arg = nil
    if jsonArg and #jsonArg > 0 then
        arg = json.decode(jsonArg)
    end

    if action == "launch" then
        hs.application.launchOrFocus(appName)
    elseif action == "quit" then
        local app = getApp(appName)
        if app then app:kill() end
    elseif action == "focus" then
        local app = getApp(appName)
        if app then app:activate(true) end
    elseif action == "fullscreen" then
        local app = getApp(appName)
        if app then
            local win = app:mainWindow()
            if win then win:maximize() end
        end
    elseif action == "keystroke" and arg then
        local mods = arg.mods or {}
        local key = arg.key
        if key then
            hs.eventtap.keyStroke(mods, key, 0)
        end
    end
end

function M.appForKey(key)
    local name = appNameForKey(key)
    if not name then return nil end
    return getApp(name)
end

function M.allAppKeys()
    local keys = {}
    for k, _ in pairs(APP_MAP) do
        table.insert(keys, k)
    end
    return keys
end

return M
