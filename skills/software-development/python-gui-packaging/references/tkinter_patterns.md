# tkinter Common Patterns

## Treeview (Data Table)

```python
cols = ("序号", "名称", "状态")
tree = ttk.Treeview(root, columns=cols, show="headings", height=10)
for c in cols:
    tree.heading(c, text=c)
tree.column("序号", width=40, anchor="center")

# Scrollbar
scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)

# Insert data
tree.insert("", "end", values=(1, "item name", "active"))

# Selection handling
def on_select(event):
    sel = tree.selection()
    if sel:
        item = tree.item(sel[0])
        values = item["values"]  # tuple of column values
tree.bind("<<TreeviewSelect>>", on_select)
```

## Modal Dialog

```python
class Dialog:
    def __init__(self, parent):
        self.win = tk.Toplevel(parent)
        self.win.transient(parent)
        self.win.grab_set()  # Modal: blocks parent
        self.win.wait_window()  # Blocks until closed
```

## Thread-Safe UI Updates

```python
# WRONG (blocks UI):
def _task(self):
    result = do_work()
    self.label.config(text=result)  # May crash!

# RIGHT:
def _task(self):
    result = do_work()
    self.root.after(0, lambda: self.label.config(text=result))

# For multiple updates in lambda, use a helper function:
def _update_ui(self, text):
    self.label.config(text=text)
    self.btn.config(state="normal")
self.root.after(0, lambda: self._update_ui("done"))
```

## Radiobutton Tab Switching

```python
self.tab_var = tk.StringVar(value="tab1")
for text, val in [("Tab 1", "tab1"), ("Tab 2", "tab2")]:
    rb = tk.Radiobutton(frame, text=text, variable=self.tab_var,
                         value=val, command=self._switch,
                         indicatoron=False, relief=tk.RAISED)
    rb.pack(side=tk.LEFT, padx=2)

self.frames = {"tab1": tk.Frame(root), "tab2": tk.Frame(root)}

def _switch(self):
    for f in self.frames.values():
        f.pack_forget()
    self.frames[self.tab_var.get()].pack(fill=tk.BOTH, expand=True)
```

## Combobox (Dropdown)

```python
self.platform_var = tk.StringVar(value="Option1")
ttk.Combobox(frame, textvariable=self.platform_var,
             values=["Option1", "Option2"], state="readonly", width=15)
```

## Image Display

```python
from PIL import Image, ImageTk

img = Image.open("path.png")
photo = ImageTk.PhotoImage(img)
label = tk.Label(root, image=photo)
label.image = photo  # MUST keep reference!
```
