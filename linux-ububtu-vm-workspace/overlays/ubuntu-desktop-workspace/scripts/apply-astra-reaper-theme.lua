-- Load the native REAPER color theme used by Astra Workbench.
-- This runs inside an existing REAPER instance via `reaper -nonewinst`.
local theme = "/mnt/data/ubuntu-desktop-workspace/config/REAPER/ColorThemes/Astra_Workbench.ReaperThemeZip"
if reaper.file_exists(theme) then
  reaper.OpenColorThemeFile(theme)
  reaper.UpdateArrange()
  reaper.UpdateTimeline()
end
