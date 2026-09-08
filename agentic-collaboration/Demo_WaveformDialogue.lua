-- Demo_WaveformDialogue.lua
-- Drop beside WaveformDialogue.lua and run this file from REAPER's Action List.
-- It creates regions/markers showing Agent Musicians taking turns on the timeline.

local script_path = debug.getinfo(1, "S").source:sub(2)
local script_dir = script_path:match("^(.*[/\\])") or ""
local Dialogue = dofile(script_dir .. "WaveformDialogue.lua")

local d = Dialogue.new({ min_pause_seconds = 0.10 })

Dialogue.add_wave(d, "Drummer", 0.000, 2.400, {
  intent = "groove statement"
})
Dialogue.add_pause(d, 2.400, 2.750, {
  intent = "Bassist listens and prepares response"
})
Dialogue.add_wave(d, "Bassist", 2.750, 4.700, {
  intent = "rhythmic answer"
})
Dialogue.add_pause(d, 4.700, 5.050, {
  intent = "Guitarist listens to the rhythm section"
})
Dialogue.add_wave(d, "Guitarist", 5.050, 7.300, {
  intent = "harmonic answer"
})

local ok, errors = Dialogue.validate(d)
if not ok then
  reaper.ShowMessageBox(table.concat(errors, "\n"), "Waveform Dialogue validation failed", 0)
  return
end

reaper.ShowConsoleMsg("Agent Musician dialogue:\n" .. Dialogue.timeline(d) .. "\n")
local materialized, err = Dialogue.materialize_reaper_markers(d, 0)
if not materialized then
  reaper.ShowMessageBox(err, "Waveform Dialogue", 0)
end
