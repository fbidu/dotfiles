local status, _ = pcall(vim.cmd, "colorscheme nightfly")

if not status then
    print("🚨 Missing Nightfly colorscheme")
end
