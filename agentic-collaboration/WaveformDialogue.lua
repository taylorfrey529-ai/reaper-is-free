-- WaveformDialogue.lua
-- Audio-native turn-taking protocol for Agent Musicians in REAPER.
-- A musical utterance is a waveform span; a pause is a listening/handoff span;
-- the following waveform is the collaborating agent's response.

local M = {}
M.VERSION = "0.1.0"

local function copy_table(t)
  local out = {}
  if t then
    for k, v in pairs(t) do out[k] = v end
  end
  return out
end

local function assert_number(name, value)
  assert(type(value) == "number", name .. " must be a number")
end

local function last_segment(dialogue)
  return dialogue.segments[#dialogue.segments]
end

function M.new(options)
  options = options or {}
  return {
    version = M.VERSION,
    min_pause_seconds = options.min_pause_seconds or 0.05,
    allow_self_response = options.allow_self_response or false,
    segments = {}
  }
end

function M.add_wave(dialogue, agent_id, start_time, end_time, payload)
  assert(type(dialogue) == "table" and type(dialogue.segments) == "table", "invalid dialogue")
  assert(type(agent_id) == "string" and agent_id ~= "", "agent_id is required")
  assert_number("start_time", start_time)
  assert_number("end_time", end_time)
  assert(end_time > start_time, "waveform end_time must be greater than start_time")

  local previous = last_segment(dialogue)
  if previous then
    assert(previous.kind == "pause", "adjacent waveform turns require an explicit pause")
    assert(start_time >= previous.end_time, "waveform may not begin before the pause ends")
  end

  dialogue.segments[#dialogue.segments + 1] = {
    kind = "wave",
    agent_id = agent_id,
    start_time = start_time,
    end_time = end_time,
    payload = copy_table(payload)
  }
  return dialogue
end

function M.add_pause(dialogue, start_time, end_time, metadata)
  assert(type(dialogue) == "table" and type(dialogue.segments) == "table", "invalid dialogue")
  assert_number("start_time", start_time)
  assert_number("end_time", end_time)
  assert(end_time > start_time, "pause end_time must be greater than start_time")
  assert((end_time - start_time) >= dialogue.min_pause_seconds,
    string.format("pause must be at least %.3f seconds", dialogue.min_pause_seconds))

  local previous = last_segment(dialogue)
  assert(previous and previous.kind == "wave", "a pause must follow a waveform turn")
  assert(start_time >= previous.end_time, "pause may not begin before the waveform ends")

  dialogue.segments[#dialogue.segments + 1] = {
    kind = "pause",
    start_time = start_time,
    end_time = end_time,
    metadata = copy_table(metadata)
  }
  return dialogue
end

function M.validate(dialogue)
  local errors = {}
  local segments = dialogue and dialogue.segments or nil
  if type(segments) ~= "table" or #segments == 0 then
    return false, { "dialogue contains no segments" }
  end

  if segments[1].kind ~= "wave" then
    errors[#errors + 1] = "dialogue must begin with a waveform"
  end

  for i, segment in ipairs(segments) do
    if segment.kind ~= "wave" and segment.kind ~= "pause" then
      errors[#errors + 1] = string.format("segment %d has invalid kind", i)
    end

    if i > 1 then
      local previous = segments[i - 1]
      if previous.kind == segment.kind then
        errors[#errors + 1] = string.format("segments %d and %d do not alternate", i - 1, i)
      end
      if previous.end_time and segment.start_time and segment.start_time < previous.end_time then
        errors[#errors + 1] = string.format("segments %d and %d overlap", i - 1, i)
      end
    end

    if segment.kind == "pause" then
      local duration = segment.end_time - segment.start_time
      if duration < dialogue.min_pause_seconds then
        errors[#errors + 1] = string.format("pause %d is shorter than minimum", i)
      end
    end
  end

  for i = 1, #segments - 2 do
    local a, pause, b = segments[i], segments[i + 1], segments[i + 2]
    if a.kind == "wave" and pause.kind == "pause" and b.kind == "wave" then
      if not dialogue.allow_self_response and a.agent_id == b.agent_id then
        errors[#errors + 1] = string.format(
          "self-response is disabled but %s owns both turns around segment %d",
          a.agent_id, i + 1)
      end
    end
  end

  return #errors == 0, errors
end

function M.handoffs(dialogue)
  local handoffs = {}
  local segments = dialogue.segments
  for i = 1, #segments - 2 do
    local a, pause, b = segments[i], segments[i + 1], segments[i + 2]
    if a.kind == "wave" and pause.kind == "pause" and b.kind == "wave" then
      handoffs[#handoffs + 1] = {
        from_agent = a.agent_id,
        to_agent = b.agent_id,
        pause_start = pause.start_time,
        pause_end = pause.end_time,
        pause_duration = pause.end_time - pause.start_time,
        previous_wave = a,
        response_wave = b
      }
    end
  end
  return handoffs
end

function M.timeline(dialogue)
  local lines = {}
  for _, segment in ipairs(dialogue.segments) do
    if segment.kind == "wave" then
      lines[#lines + 1] = string.format(
        "%.3f - %.3f  WAVE   %-12s %s",
        segment.start_time,
        segment.end_time,
        segment.agent_id,
        segment.payload.intent or "musical utterance")
    else
      lines[#lines + 1] = string.format(
        "%.3f - %.3f  PAUSE  handoff      %s",
        segment.start_time,
        segment.end_time,
        segment.metadata.intent or "listen / reconcile / respond")
    end
  end
  return table.concat(lines, "\n")
end

-- Optional REAPER integration. This does not create or alter audio items; it only
-- materializes ownership and handoff boundaries on the project timeline.
function M.materialize_reaper_markers(dialogue, project)
  if not reaper then
    return false, "REAPER API is not available"
  end

  project = project or 0
  local handoff_by_pause_start = {}
  for _, handoff in ipairs(M.handoffs(dialogue)) do
    handoff_by_pause_start[handoff.pause_start] = handoff
  end

  reaper.Undo_BeginBlock2(project)
  for _, segment in ipairs(dialogue.segments) do
    if segment.kind == "wave" then
      local intent = segment.payload.intent or "WAVE"
      local name = string.format("[AGENT:%s] %s", segment.agent_id, intent)
      reaper.AddProjectMarker2(project, true, segment.start_time, segment.end_time, name, -1, 0)
    else
      local handoff = handoff_by_pause_start[segment.start_time]
      local name = "[HANDOFF] listening pause"
      if handoff then
        name = string.format("[HANDOFF] %s -> %s", handoff.from_agent, handoff.to_agent)
      end
      reaper.AddProjectMarker2(project, false, segment.start_time, 0, name, -1, 0)
    end
  end
  reaper.Undo_EndBlock2(project, "Materialize Agent Musician waveform dialogue", -1)
  reaper.UpdateArrange()
  return true
end

-- Minimal executable example:
-- local d = M.new({ min_pause_seconds = 0.10 })
-- M.add_wave(d, "Drummer",   0.000, 2.400, { intent = "groove statement" })
-- M.add_pause(d,             2.400, 2.750, { intent = "listen to groove" })
-- M.add_wave(d, "Bassist",   2.750, 4.700, { intent = "rhythmic answer" })
-- M.add_pause(d,             4.700, 5.050, { intent = "listen to bass answer" })
-- M.add_wave(d, "Guitarist", 5.050, 7.300, { intent = "harmonic answer" })
-- local ok, errors = M.validate(d)
-- assert(ok, table.concat(errors, "; "))
-- print(M.timeline(d))

return M
