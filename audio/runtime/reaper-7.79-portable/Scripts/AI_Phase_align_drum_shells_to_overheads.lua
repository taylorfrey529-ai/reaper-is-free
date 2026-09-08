-- AI Phase Align Drum Shells to Overheads
-- REAPER 7.79 ReaScript (Lua)
--
-- Purpose:
--   Time-align close-miked drum shells (kick/snare/toms) to their own acoustic
--   arrivals in the stereo overheads. The overhead tracks are never moved.
--   Tom 1 is self-anchored: Tom 1 close-mic transients define the search windows,
--   and only the corresponding local transient in OH L/R is used for alignment.
--
-- Method:
--   1. Detect overhead tracks by name.
--   2. Detect close shell tracks by name, or use selected shell tracks.
--   3. Find strong, spaced transients on each shell track.
--   4. For each shell hit, search only a local +/-25 ms region in OH L/R.
--   5. Coarse-match transient energy, then fine-match waveform derivative.
--   6. Median/reject outliers and apply a dedicated non-destructive JSFX offset.
--
-- Positive offset delays the shell to meet the later overhead arrival.
-- Negative offset uses REAPER PDC to advance the shell if needed.

local FX_NAME = "JS: utility/AI_Drum_Shell_Phase_Align"
local LOG_NAME = "phase-align-last-run.txt"

local SCAN_SR = 2000
local SCAN_BIN_SEC = 0.005
local SCAN_CHUNK_SEC = 20.0
local MAX_SCAN_SEC = 900.0
local MAX_EVENTS = 8
local MIN_EVENT_GAP_SEC = 0.120

local COARSE_SR = 8000
local COARSE_PRE_SEC = 0.006
local COARSE_POST_SEC = 0.024
local SEARCH_SEC = 0.025

local FINE_SR = 96000
local FINE_PRE_SEC = 0.004
local FINE_POST_SEC = 0.010
local FINE_RADIUS_SEC = 0.0008

local MAX_ABS_OFFSET_SEC = 0.050
local MIN_ACCEPTED_SCORE = 0.035

local log_lines = {}
local function log(s)
  log_lines[#log_lines + 1] = tostring(s)
  reaper.ShowConsoleMsg(tostring(s) .. "\n")
end

local function write_log()
  local path = reaper.GetResourcePath() .. "/" .. LOG_NAME
  local f = io.open(path, "w")
  if f then
    f:write(table.concat(log_lines, "\n"), "\n")
    f:close()
  end
end

local function lower(s)
  return string.lower(s or "")
end

local function track_name(track)
  local _, name = reaper.GetTrackName(track)
  return name or ""
end

local function is_overhead_name(name)
  local n = lower(name)
  if n:find("overhead", 1, true) then return true end
  if n == "oh" or n:match("^oh[%s_%-]?") then return true end
  if n:match("[%s_%-]oh[%s_%-]?") then return true end
  return false
end

local function is_excluded_non_shell(name)
  local n = lower(name)
  local bad = {
    "overhead", "room", "ambient", "ambience", "cymbal", "hihat", "hi-hat",
    "hat ", "ride", "crash", "china", "splash", "shaker", "tamb", "perc",
    "drum bus", "drumbus", "drum master", "parallel", "crush", "verb", "reverb"
  }
  for _, p in ipairs(bad) do
    if n:find(p, 1, true) then return true end
  end
  if is_overhead_name(name) then return true end
  return false
end

local function is_shell_name(name)
  if is_excluded_non_shell(name) then return false end
  local n = lower(name)
  if n:find("kick", 1, true) or n:find("bass drum", 1, true) then return true end
  if n:find("snare", 1, true) then return true end
  if n:find("tom", 1, true) or n:find("floor", 1, true) or n:find("rack", 1, true) then return true end
  if n == "bd" or n:match("^bd[%s_%-]") then return true end
  if n == "sn" or n:match("^sn[%s_%-]") then return true end
  return false
end

local function is_tom1_name(name)
  local n = lower(name)
  return n:match("tom[%s_%-]*0*1([^0-9]?)") ~= nil or n:match("rack[%s_%-]*0*1([^0-9]?)") ~= nil
end

local function all_tracks()
  local t = {}
  for i = 0, reaper.CountTracks(0) - 1 do
    t[#t + 1] = reaper.GetTrack(0, i)
  end
  return t
end

local function selected_tracks()
  local t = {}
  for i = 0, reaper.CountSelectedTracks(0) - 1 do
    t[#t + 1] = reaper.GetSelectedTrack(0, i)
  end
  return t
end

local function find_overheads(tracks)
  local refs = {}
  for _, tr in ipairs(tracks) do
    if is_overhead_name(track_name(tr)) then refs[#refs + 1] = tr end
  end
  table.sort(refs, function(a, b) return lower(track_name(a)) < lower(track_name(b)) end)
  if #refs > 2 then
    -- Prefer obvious L/R or first stereo-labelled pair when many OH-related tracks exist.
    local preferred = {}
    for _, tr in ipairs(refs) do
      local n = lower(track_name(tr))
      if n:find(" left", 1, true) or n:match("[%s_%-]l$") or n:find(" right", 1, true) or n:match("[%s_%-]r$") then
        preferred[#preferred + 1] = tr
      end
    end
    if #preferred >= 2 then refs = { preferred[1], preferred[2] }
    else refs = { refs[1], refs[2] } end
  end
  return refs
end

local function find_shells(tracks)
  local selected = selected_tracks()
  local sel_shells = {}
  for _, tr in ipairs(selected) do
    if is_shell_name(track_name(tr)) then sel_shells[#sel_shells + 1] = tr end
  end
  if #sel_shells > 0 then return sel_shells, true end

  local shells = {}
  for _, tr in ipairs(tracks) do
    if is_shell_name(track_name(tr)) then shells[#shells + 1] = tr end
  end
  return shells, false
end

local function read_stereo(accessor, start_time, duration, sr)
  local frames = math.max(1, math.floor(duration * sr + 0.5))
  local arr = reaper.new_array(frames * 2)
  local rv = reaper.GetAudioAccessorSamples(accessor, sr, 2, start_time, frames, arr)
  if not rv or rv <= 0 then return nil, nil end
  local v = arr.table()
  local l, r = {}, {}
  for i = 1, frames do
    local j = (i - 1) * 2
    l[i] = v[j + 1] or 0.0
    r[i] = v[j + 2] or 0.0
  end
  return l, r
end

local function mono_from_stereo(l, r)
  if not l then return nil end
  local m = {}
  for i = 1, #l do m[i] = 0.5 * ((l[i] or 0.0) + (r[i] or 0.0)) end
  return m
end

local function read_shell_mono(accessor, start_time, duration, sr)
  local l, r = read_stereo(accessor, start_time, duration, sr)
  return mono_from_stereo(l, r)
end

local function read_overhead_channels(ref_accessors, start_time, duration, sr)
  if #ref_accessors == 1 then
    return read_stereo(ref_accessors[1], start_time, duration, sr)
  end
  local l1, r1 = read_stereo(ref_accessors[1], start_time, duration, sr)
  local l2, r2 = read_stereo(ref_accessors[2], start_time, duration, sr)
  if not l1 or not l2 then return nil, nil end
  return mono_from_stereo(l1, r1), mono_from_stereo(l2, r2)
end

local function derivative_abs(x)
  local y = {}
  if not x or #x < 2 then return y end
  y[1] = 0.0
  for i = 2, #x do y[i] = math.abs((x[i] or 0.0) - (x[i - 1] or 0.0)) end
  return y
end

local function derivative_signed(x)
  local y = {}
  if not x or #x < 2 then return y end
  y[1] = 0.0
  for i = 2, #x do y[i] = (x[i] or 0.0) - (x[i - 1] or 0.0) end
  return y
end

local function norm_corr(x, y, y_start)
  local n = #x
  if n < 4 or y_start < 1 or y_start + n - 1 > #y then return 0.0 end
  local xy, xx, yy = 0.0, 0.0, 0.0
  for i = 1, n do
    local a = x[i] or 0.0
    local b = y[y_start + i - 1] or 0.0
    xy = xy + a * b
    xx = xx + a * a
    yy = yy + b * b
  end
  local den = math.sqrt(xx * yy)
  if den < 1e-20 then return 0.0 end
  return xy / den
end

local function clamp(v, lo, hi)
  if v < lo then return lo end
  if v > hi then return hi end
  return v
end

local function median(values)
  if #values == 0 then return nil end
  local c = {}
  for i, v in ipairs(values) do c[i] = v end
  table.sort(c)
  local n = #c
  if n % 2 == 1 then return c[(n + 1) // 2] end
  return 0.5 * (c[n // 2] + c[n // 2 + 1])
end

local function detect_events(accessor)
  local astart = math.max(0.0, reaper.GetAudioAccessorStartTime(accessor) or 0.0)
  local aend = reaper.GetAudioAccessorEndTime(accessor) or reaper.GetProjectLength(0)
  local project_end = reaper.GetProjectLength(0)
  if project_end > 0 then aend = math.min(aend, project_end) end
  aend = math.min(aend, astart + MAX_SCAN_SEC)
  if aend <= astart then return {} end

  local candidates = {}
  local bin_frames = math.max(1, math.floor(SCAN_BIN_SEC * SCAN_SR + 0.5))
  local t = astart
  while t < aend do
    local dur = math.min(SCAN_CHUNK_SEC, aend - t)
    local m = read_shell_mono(accessor, t, dur, SCAN_SR)
    if m then
      local i = 1
      while i <= #m do
        local last = math.min(#m, i + bin_frames - 1)
        local maxamp, maxi = 0.0, i
        for j = i, last do
          local a = math.abs(m[j] or 0.0)
          if a > maxamp then maxamp, maxi = a, j end
        end
        if maxamp > 1e-6 then
          candidates[#candidates + 1] = { amp = maxamp, time = t + (maxi - 1) / SCAN_SR }
        end
        i = last + 1
      end
    end
    t = t + dur
  end

  table.sort(candidates, function(a, b) return a.amp > b.amp end)
  local chosen = {}
  for _, c in ipairs(candidates) do
    local far_enough = true
    for _, e in ipairs(chosen) do
      if math.abs(c.time - e.time) < MIN_EVENT_GAP_SEC then far_enough = false; break end
    end
    if far_enough then
      chosen[#chosen + 1] = c
      if #chosen >= MAX_EVENTS then break end
    end
  end
  table.sort(chosen, function(a, b) return a.time < b.time end)
  return chosen
end

local function best_lag_for_hit(shell_acc, ref_accs, hit_time)
  -- Coarse transient-energy correlation.
  local shell_start = hit_time - COARSE_PRE_SEC
  local shell_dur = COARSE_PRE_SEC + COARSE_POST_SEC
  local shell = read_shell_mono(shell_acc, shell_start, shell_dur, COARSE_SR)
  if not shell then return nil end
  local oh_start = shell_start - SEARCH_SEC
  local oh_dur = shell_dur + 2 * SEARCH_SEC
  local oh1, oh2 = read_overhead_channels(ref_accs, oh_start, oh_dur, COARSE_SR)
  if not oh1 or not oh2 then return nil end

  local sx = derivative_abs(shell)
  local oy1, oy2 = derivative_abs(oh1), derivative_abs(oh2)
  local search_n = math.floor(SEARCH_SEC * COARSE_SR + 0.5)
  local best_lag, best_score, best_ch = 0, -1.0, 1
  for lag = -search_n, search_n do
    local ys = search_n + lag + 1
    local c1 = norm_corr(sx, oy1, ys)
    local c2 = norm_corr(sx, oy2, ys)
    if c1 > best_score then best_lag, best_score, best_ch = lag, c1, 1 end
    if c2 > best_score then best_lag, best_score, best_ch = lag, c2, 2 end
  end

  -- Fine signed-derivative correlation around the coarse result.
  local coarse_sec = best_lag / COARSE_SR
  local fine_shell_start = hit_time - FINE_PRE_SEC
  local fine_shell_dur = FINE_PRE_SEC + FINE_POST_SEC
  local fine_shell = read_shell_mono(shell_acc, fine_shell_start, fine_shell_dur, FINE_SR)
  if not fine_shell then return coarse_sec, best_score, best_ch, 1 end

  local radius_n = math.floor(FINE_RADIUS_SEC * FINE_SR + 0.5)
  local center_n = math.floor(coarse_sec * FINE_SR + (coarse_sec >= 0 and 0.5 or -0.5))
  local fine_search_sec = math.abs(coarse_sec) + FINE_RADIUS_SEC + 2.0 / FINE_SR
  local fine_oh_start = fine_shell_start - fine_search_sec
  local fine_oh_dur = fine_shell_dur + 2 * fine_search_sec
  local foh1, foh2 = read_overhead_channels(ref_accs, fine_oh_start, fine_oh_dur, FINE_SR)
  if not foh1 or not foh2 then return coarse_sec, best_score, best_ch, 1 end

  local fsx = derivative_signed(fine_shell)
  local foy1, foy2 = derivative_signed(foh1), derivative_signed(foh2)
  local base_n = math.floor(fine_search_sec * FINE_SR + 0.5)
  local fbest_lag, fbest_abs, fbest_signed, fbest_ch = center_n, -1.0, 0.0, best_ch
  for lag = center_n - radius_n, center_n + radius_n do
    local ys = base_n + lag + 1
    local c1 = norm_corr(fsx, foy1, ys)
    local c2 = norm_corr(fsx, foy2, ys)
    if math.abs(c1) > fbest_abs then fbest_lag, fbest_abs, fbest_signed, fbest_ch = lag, math.abs(c1), c1, 1 end
    if math.abs(c2) > fbest_abs then fbest_lag, fbest_abs, fbest_signed, fbest_ch = lag, math.abs(c2), c2, 2 end
  end
  return fbest_lag / FINE_SR, fbest_abs, fbest_ch, (fbest_signed < 0 and -1 or 1)
end

local function estimate_offset(shell_acc, ref_accs)
  local events = detect_events(shell_acc)
  local measurements = {}
  for _, e in ipairs(events) do
    local lag, score, ch, polarity = best_lag_for_hit(shell_acc, ref_accs, e.time)
    if lag and math.abs(lag) <= MAX_ABS_OFFSET_SEC and score >= MIN_ACCEPTED_SCORE then
      measurements[#measurements + 1] = { lag = lag, score = score, ch = ch, polarity = polarity, time = e.time }
    end
  end
  if #measurements == 0 then return nil, events, measurements end

  local lags = {}
  for _, m in ipairs(measurements) do lags[#lags + 1] = m.lag end
  local med = median(lags)
  local devs = {}
  for _, v in ipairs(lags) do devs[#devs + 1] = math.abs(v - med) end
  local mad = median(devs) or 0.0
  local tol = math.max(0.00035, 3.0 * mad)

  local kept = {}
  for _, m in ipairs(measurements) do
    if math.abs(m.lag - med) <= tol then kept[#kept + 1] = m end
  end
  if #kept == 0 then kept = measurements end

  local kept_lags = {}
  for _, m in ipairs(kept) do kept_lags[#kept_lags + 1] = m.lag end
  return median(kept_lags), events, kept
end

local function find_or_add_alignment_fx(track)
  local idx = reaper.TrackFX_AddByName(track, FX_NAME, false, -1)
  if idx < 0 then idx = reaper.TrackFX_AddByName(track, FX_NAME, false, 0) end
  return idx
end

local function zero_existing_alignment_fx(track)
  local idx = reaper.TrackFX_AddByName(track, FX_NAME, false, -1)
  if idx >= 0 then reaper.TrackFX_SetParam(track, idx, 0, 0.0) end
end

local function apply_offset(track, offset_sec)
  local idx = find_or_add_alignment_fx(track)
  if idx < 0 then return false, "alignment JSFX not found" end
  local ms = clamp(offset_sec * 1000.0, -100.0, 100.0)
  reaper.TrackFX_SetParam(track, idx, 0, ms)
  reaper.TrackFX_SetEnabled(track, idx, true)
  reaper.GetSetMediaTrackInfo_String(track, "P_EXT:AI_DRUM_ALIGN_DELAY_MS", string.format("%.6f", ms), true)
  return true, ms
end

reaper.ClearConsole()
log("AI Drum Shell -> Overhead phase alignment")
log("-----------------------------------------")

local tracks = all_tracks()
local overheads = find_overheads(tracks)
if #overheads == 0 then
  log("STOP: No overhead/OH track was found by name. No audio was changed.")
  write_log()
  return
end

local shells, selected_only = find_shells(tracks)
if #shells == 0 then
  log("STOP: No kick/snare/tom shell tracks were found. No audio was changed.")
  write_log()
  return
end

log("OH reference: " .. table.concat((function()
  local n = {}; for _, tr in ipairs(overheads) do n[#n + 1] = track_name(tr) end; return n
end)(), " + "))
log(selected_only and "Shell scope: selected shell tracks" or "Shell scope: auto-detected shell tracks")

-- Make reruns idempotent: neutralize only this script's own prior alignment FX before measuring.
for _, tr in ipairs(shells) do zero_existing_alignment_fx(tr) end

local ref_accs = {}
for _, tr in ipairs(overheads) do ref_accs[#ref_accs + 1] = reaper.CreateTrackAudioAccessor(tr) end

reaper.Undo_BeginBlock()
local changed = 0
for _, tr in ipairs(shells) do
  local name = track_name(tr)
  local shell_acc = reaper.CreateTrackAudioAccessor(tr)
  local offset, events, kept = estimate_offset(shell_acc, ref_accs)
  reaper.DestroyAudioAccessor(shell_acc)

  if offset then
    local ok, ms_or_err = apply_offset(tr, offset)
    if ok then
      changed = changed + 1
      local ch_counts = {0, 0}
      local polarity_votes = 0
      local avg_score = 0.0
      for _, m in ipairs(kept) do
        ch_counts[m.ch] = (ch_counts[m.ch] or 0) + 1
        polarity_votes = polarity_votes + m.polarity
        avg_score = avg_score + m.score
      end
      avg_score = (#kept > 0) and (avg_score / #kept) or 0.0
      local dominant_ch = (ch_counts[2] or 0) > (ch_counts[1] or 0) and "R/2" or "L/1"
      local tag = is_tom1_name(name) and " [Tom 1 self-anchor]" or ""
      local polarity_note = polarity_votes < 0 and "; inverse-polarity correlation dominant (timing aligned, polarity not flipped)" or ""
      log(string.format("OK  %-24s %+8.3f ms | %d hit(s), OH %s, score %.3f%s%s",
        name, ms_or_err, #kept, dominant_ch, avg_score, tag, polarity_note))
    else
      log("ERR " .. name .. ": " .. tostring(ms_or_err))
    end
  else
    log(string.format("SKIP %-24s insufficient reliable shell->OH match (%d candidate hit(s))", name, #events))
  end
end

for _, acc in ipairs(ref_accs) do reaper.DestroyAudioAccessor(acc) end

reaper.TrackList_AdjustWindows(false)
reaper.UpdateArrange()
reaper.Undo_EndBlock("Phase align drum shells to stereo overheads", -1)
log("-----------------------------------------")
log(string.format("Applied non-destructive alignment to %d shell track(s). Overheads were not moved.", changed))
write_log()
