-- REAPER 7.79 - vm-v1.1.0 live regression gate
-- Verify-only: never installs, downloads, repairs, substitutes models, or promotes a release.

local ROOT = os.getenv("SUNWELL_ROOT") or "/mnt/data/ubuntu-desktop-workspace"
local report_path = ROOT .. "/logs/vm-v1.1.0-reaper-regression.txt"
local pass, fail = 0, 0
local out = {}

local expected = {
  {"Drum Buss","FFF468"},{"Kick","0070DD"},{"Snare","00FF98"},{"Tom 1","F48CBA"},
  {"Tom 2","3FC7EB"},{"Tom 3","8788EE"},{"OH","FF7C0A"},{"Room","C69B6D"},
  {"Bass Buss","FFF468"},{"Bass DI","AAD372"},{"Bass Neural","AAD372"},
  {"Guitar Buss","FFF468"},{"L Guitar DI","C41E3A"},{"R Guitar DI","C41E3A"},
  {"L Guitar Neural","C41E3A"},{"R Guitar Neural","C41E3A"},{"Lead Buss","FFF468"},
  {"Lead Guitar DI","A330C9"},{"Lead Guitar Neural","A330C9"},{"Orchestra Buss","FFF468"},
  {"Strings High","33937F"},{"Strings Low","33937F"},{"Horns","33937F"}
}

local function emit(ok, label, detail)
  if ok then pass = pass + 1 else fail = fail + 1 end
  local s = string.format("[%s] %s", ok and "PASS" or "FAIL", label)
  if detail and detail ~= "" then s = s .. " - " .. detail end
  out[#out+1] = s
end

local function hex_to_rgb(h)
  local n = tonumber(h, 16)
  return (n >> 16) & 0xff, (n >> 8) & 0xff, n & 0xff
end

local function expected_native(h)
  local r,g,b = hex_to_rgb(h)
  return reaper.ColorToNative(r,g,b) & 0xffffff
end

local function track_name(t)
  local _, name = reaper.GetTrackName(t)
  return name or ""
end

local tracks = {}
local count = reaper.CountTracks(0)
emit(count == #expected, "exact track count", string.format("%d/%d", count, #expected))
for i=0,count-1 do
  local t = reaper.GetTrack(0,i)
  tracks[track_name(t)] = t
end

for i, spec in ipairs(expected) do
  local name, rgb = spec[1], spec[2]
  local t = reaper.GetTrack(0,i-1)
  local actual_name = t and track_name(t) or "<missing>"
  emit(actual_name == name, string.format("track %02d name", i), actual_name .. " / " .. name)
  if t then
    local c = math.floor(reaper.GetMediaTrackInfo_Value(t, "I_CUSTOMCOLOR")) & 0xffffff
    emit(c == expected_native(rgb), "color " .. name, "#" .. rgb)
  end
end

local function fx_names(t)
  local names = {}
  if not t then return names end
  for i=0,reaper.TrackFX_GetCount(t)-1 do
    local ok, n = reaper.TrackFX_GetFXName(t, i, "")
    if ok then names[#names+1] = n:lower() end
  end
  return names
end

local function has_fx(name, patterns)
  local t = tracks[name]
  if not t then emit(false, "FX role " .. name, "track missing"); return end
  local names = fx_names(t)
  local joined = table.concat(names, " | ")
  local ok = false
  for _,pat in ipairs(patterns) do
    if joined:find(pat:lower(), 1, true) then ok = true break end
  end
  emit(ok, "FX role " .. name, joined)
end

has_fx("Drum Buss", {"avldrums","avl drums","black pearl"})
has_fx("Bass DI", {"sforzando"})
has_fx("Bass Neural", {"neural amp modeler","nam"})
has_fx("L Guitar DI", {"sforzando"})
has_fx("R Guitar DI", {"sforzando"})
has_fx("Lead Guitar DI", {"sforzando"})
has_fx("L Guitar Neural", {"neural amp modeler","nam"})
has_fx("R Guitar Neural", {"neural amp modeler","nam"})
has_fx("Lead Guitar Neural", {"neural amp modeler","nam"})
has_fx("Strings High", {"sforzando"})
has_fx("Strings Low", {"sforzando"})
has_fx("Horns", {"sforzando"})

local function source_name_for_receive(dst, i)
  local src = reaper.GetTrackSendInfo_Value(dst, -1, i, "P_SRCTRACK")
  if src then return track_name(src) end
  return ""
end

local function has_receive(dst_name, src_name)
  local dst = tracks[dst_name]
  if not dst then emit(false, dst_name .. " receives " .. src_name, "destination missing"); return end
  local n = reaper.GetTrackNumSends(dst, -1)
  local ok = false
  for i=0,n-1 do
    if source_name_for_receive(dst, i) == src_name then ok = true break end
  end
  emit(ok, dst_name .. " receives " .. src_name, string.format("receives=%d", n))
end

has_receive("Bass Neural", "Bass DI")
has_receive("L Guitar Neural", "L Guitar DI")
has_receive("R Guitar Neural", "R Guitar DI")
has_receive("Lead Guitar Neural", "Lead Guitar DI")

for _,name in ipairs({"L Guitar DI","R Guitar DI","Lead Guitar DI"}) do
  local t = tracks[name]
  if t then
    emit(reaper.GetMediaTrackInfo_Value(t, "B_MAINSEND") == 0, name .. " parent send disabled")
    local pan = reaper.GetMediaTrackInfo_Value(t, "D_PAN")
    emit(math.abs(pan) < 0.000001, name .. " centered clean DI", string.format("pan=%.6f", pan))
  end
end

local function check_pan(name, expected_pan)
  local t = tracks[name]
  if not t then emit(false, name .. " pan", "track missing"); return end
  local p = reaper.GetMediaTrackInfo_Value(t, "D_PAN")
  emit(math.abs(p-expected_pan) < 0.000001, name .. " pan", string.format("%.6f", p))
end
check_pan("L Guitar Neural", -1.0)
check_pan("R Guitar Neural", 1.0)

local sentinels = {
  {"sforzando", ROOT .. "/home/.vst3/sforzando.vst3/Contents/x86_64-linux/sforzando.so"},
  {"AVLDrums", ROOT .. "/home/.lv2/avldrums.lv2/avldrums.so"},
  {"AVL Black Pearl", ROOT .. "/home/.lv2/avldrums.lv2/Black_Pearl_4_LV2.sf2"},
  {"Black & Blue Dark Black", ROOT .. "/instruments/Black-And-Blue-Basses-Upstream/Programs/01-darkblack_keysw.sfz"},
  {"Metal GTX Clean DI", ROOT .. "/instruments/Metal-GTX/Programs/03-METAL-GTX XTracking Clean DI.sfz"},
  {"NAM LV2", ROOT .. "/home/.lv2/neural_amp_modeler.lv2/neural_amp_modeler.so"},
  {"Obsidian NAM", ROOT .. "/nam-models/Obsidian.nam"},
}

for _,s in ipairs(sentinels) do
  local f = io.open(s[2], "rb")
  local ok = f ~= nil
  if f then f:close() end
  emit(ok, "VM sentinel " .. s[1], s[2])
end

local text = table.concat({
  "REAPER 7.79 - VM v1.1.0 LIVE REGRESSION",
  "Policy: verify-only / fail-closed / owner promotion required",
  table.concat(out, "\n"),
  string.format("SUMMARY pass=%d fail=%d", pass, fail),
  fail == 0 and "RESULT PASS" or "RESULT FAIL"
}, "\n") .. "\n"

local dir = ROOT .. "/logs"
os.execute("mkdir -p " .. string.format("%q", dir))
local f = io.open(report_path, "wb")
if f then f:write(text); f:close() end
reaper.ShowConsoleMsg(text)
reaper.SetExtState("SUNWELL_VM_V110", "last_result", fail == 0 and "PASS" or "FAIL", false)
reaper.SetExtState("SUNWELL_VM_V110", "last_report", report_path, false)

if fail ~= 0 then
  reaper.ShowMessageBox("vm-v1.1.0 regression gate failed. No repair or reinstall was attempted.\n\n" .. report_path,
    "Sunwell / REAPER 7.79", 0)
end
