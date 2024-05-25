vim.g.mapleader = " " --all keymaps will be prefixed by spaces

local keymap = vim.keymap

-- general keymaps
keymap.set("i", "jk", "<ESC>") -- in `i`nsert mode, `jk` acts as `ESC`

-- split & terminal
keymap.set("n", "<leader>sv", "<C-w>v")
keymap.set("n", "<leader>sh", "<C-w>s")
keymap.set("n", "tt", "<C-w>s:terminal<CR>i") -- open a terminal on a horizontal split
keymap.set("n", "<leader>se", "<C-w>=")
keymap.set("n", "<leader>sx", ":close<CR>")


-- tabs
keymap.set("n", "to", ":tabnew<CR>")
keymap.set("n", "tx", ":tabclose<CR>")
keymap.set("n", "tn", ":tabn<CR>")
keymap.set("n", "tp", ":tabp<CR>")

-- maximize splits with Maximizer
keymap.set("n", "<leader><leader>", ":MaximizerToggle<CR>")
keymap.set("n", "<C-b>", ":NvimTreeToggle<CR>")
