-- the `options` command shows all the available options along with help for them
-- You can also see them in https://neovim.io/doc/user/options.html

local opt = vim.opt -- Saves vim options in a local variable

-- line numbers
opt.relativenumber = true
opt.number = true

-- tabs
opt.tabstop = 4
opt.shiftwidth = 4
opt.expandtab = true
opt.autoindent = true

-- line wrap
opt.wrap = false

-- searching
opt.ignorecase = true
opt.smartcase = true

-- cursor
opt.cursorline = true

-- appearance
opt.termguicolors = true
opt.background = "dark"
opt.signcolumn = "yes"

-- backspace
opt.backspace = "indent,eol,start"

-- clipboard
opt.clipboard:append("unnamedplus") -- use the default system clipboard on yanking

-- split windows
opt.splitright = true
opt.splitbelow = true


