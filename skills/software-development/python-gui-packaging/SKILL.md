---
name: python-gui-packaging
description: Build Python tkinter GUI applications and package as Windows EXE with PyInstaller. Use when user needs a desktop tool with GUI interface, or when porting existing projects (C++/other) to Python with a graphical frontend.
---

# Python GUI + PyInstaller Packaging

Build tkinter-based GUI applications and package them as standalone Windows EXEs.

## When to Use

- User asks for a tool/application and expects a GUI interface
- Porting an existing project (C++/other) to Python with GUI
- Need to distribute a Python app as a standalone EXE
- Building interactive desktop tools with account management, settings, etc.

## Workflow

### 1. Create Python Script with tkinter GUI

Use `tkinter` (built-in) + `ttk` for modern widgets. Key patterns:

```python
import tkinter as tk
from tkinter import ttk, messagebox

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("App Name")
        self.root.geometry("520x580")
        self._build_ui()
    
    def _build_ui(self):
        # Menu bar
        menubar = tk.Menu(self.root)
        # ... add menus
        self.root.config(menu=menubar)
        
        # Treeview for data tables
        cols = ("col1", "col2")
        self.tree = ttk.Treeview(self.root, columns=cols, show="headings")
        
        # Input fields
        self.var = tk.StringVar()
        tk.Entry(self.root, textvariable=self.var)
        
        # Buttons
        tk.Button(self.root, text="Action", command=self._do_action)
        
        # Checkboxes
        self.opt_var = tk.BooleanVar(value=True)
        tk.Checkbutton(self.root, text="Option", variable=self.opt_var)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN).pack(fill=tk.X, side=tk.BOTTOM)
```

### 2. Threading Pattern for Long Operations

NEVER block the main thread. Use `threading` + `root.after()` for UI updates:

```python
import threading

def _start_task(self):
    self.scanning = True
    threading.Thread(target=self._task_loop, daemon=True).start()

def _task_loop(self):
    while self.scanning:
        # ... do work
        # Update UI from thread:
        self.root.after(0, lambda: self.status_var.set("Status text"))
        self.root.after(0, lambda: messagebox.showinfo("Title", "Message"))
    self.root.after(0, self._task_done)

def _task_done(self):
    self.status_var.set("Done")
```

### 3. PyInstaller Packaging

#### Install
```bash
uv pip install pyinstaller
```

#### Basic Build
```bash
uv run pyinstaller --onefile --name AppName script.py
```

#### With Data Files (DLLs, configs)
```bash
uv run pyinstaller --onefile --name AppName \
  --add-data "path/to/file.dll;relative_dir" \
  script.py
```

The `;` separator: left = source path, right = destination in bundle.

### 4. Critical Pitfalls

#### pyzbar DLL Bundling
pyzbar requires `libiconv.dll` and `libzbar-64.dll`. Find them:
```bash
find .venv -name "libiconv*" -o -name "libzbar*"
```
Bundle with:
```bash
--add-data ".venv/Lib/site-packages/pyzbar/libiconv.dll;pyzbar" \
--add-data ".venv/Lib/site-packages/pyzbar/libzbar-64.dll;pyzbar"
```

#### Chinese Encoding on Windows
Add at script start:
```python
if sys.platform == "win32":
    import os
    os.system("")  # Enable ANSI escape codes
    sys.stdout.reconfigure(encoding="utf-8")
```

#### Windows Python Path Issues
If system Python has broken paths (SRE module mismatch), use uv venv:
```bash
cd project_dir
uv venv
uv pip install <dependencies>
.venv/Scripts/python.exe script.py
```

#### Double-Click Exits Immediately
GUI apps need to stay alive. If no args provided, show interactive UI instead of exiting. Add `input("Press Enter...")` at end if CLI, or ensure mainloop runs.

#### Porting: Match Original Functionality Exactly
CRITICAL pitfall when porting existing projects:
1. **Read ALL source code first** before writing any Python. Understand the complete workflow.
2. **Don't simplify or fake features.** If the original has account login via QR scan → API poll → token storage, implement that exact flow. Don't make a manual input form and call it "done."
3. **Don't skip UI.** If the original has a GUI, make a GUI. CLI-only is not acceptable when the user expects a desktop tool.
4. **Test the core flow** before packaging. Verify API calls work with real endpoints.

User feedback that triggered this pitfall:
- "你可能没理解代码吧" (you didn't understand the code)
- "你随便做一个假的忽悠谁啊" (you made a fake feature, who are you fooling)
- "你给人家设计个ui界面很难吗" (is it that hard to design a UI)

### 5. QR Code Generation in tkinter

When app needs to display QR codes (login flows, etc.), use `qrcode` + `PIL` + `ImageTk`:

```python
# Install: uv pip install qrcode[pil]
import qrcode
from PIL import Image, ImageTk

def create_qr_image(text, size=300):
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img = img.resize((size, size), Image.LANCZOS)
    return img

# Display in tkinter label:
photo = ImageTk.PhotoImage(img)
label.config(image=photo)
label.image = photo  # IMPORTANT: keep reference to prevent GC
```

### 6. tkinter Tab Switching (No Built-in Tabs)

tkinter lacks Qt's QTabWidget. Use Radiobuttons as tab selectors:

```python
self.tab_var = tk.StringVar(value="Tab1")
tabs_frame = tk.Frame(root)
for text in ["Tab1", "Tab2", "Tab3"]:
    rb = tk.Radiobutton(tabs_frame, text=text, variable=self.tab_var,
                         value=text, command=self._on_tab_change,
                         indicatoron=False, width=10, relief=tk.RAISED)
    rb.pack(side=tk.LEFT, padx=2)

# Content frames (one per tab, show/hide):
self.tab1_frame = tk.Frame(root)
self.tab2_frame = tk.Frame(root)

def _on_tab_change(self):
    for f in [self.tab1_frame, self.tab2_frame]:
        f.pack_forget()
    if self.tab_var.get() == "Tab1":
        self.tab1_frame.pack(fill=tk.BOTH, expand=True)
    else:
        self.tab2_frame.pack(fill=tk.BOTH, expand=True)
```

### 7. File Structure for EXE Projects

```
project/
├── script.py          # Main GUI script
├── api_defs.py        # API constants (if needed)
├── accounts.json      # User data (created at runtime)
├── .venv/             # Python venv
├── dist/
│   └── AppName.exe    # Built EXE
└── build/             # PyInstaller temp (delete after build)
```

## References

- `references/pyinstaller_tips.md` — Advanced PyInstaller options, DLL issues, hidden imports
- `references/tkinter_patterns.md` — Common tkinter patterns: Treeview, dialogs, threading, tabs, images
