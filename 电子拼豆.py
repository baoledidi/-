#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🟣 电子拼豆 — Digital Perler Bead Studio
用 Python + Tkinter 实现的拼豆图纸编辑器
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import json
import os
import math
from datetime import datetime

# ═══════════════════════════════════════
#  拼豆颜色板（真实色号）
# ═══════════════════════════════════════
PALETTES = {
    "Perler 标准色": [
        ("#FFFFFF", "白色 White"),
        ("#D1D1D1", "浅灰 Light Grey"),
        ("#8E8E8E", "灰色 Grey"),
        ("#555555", "深灰 Dark Grey"),
        ("#000000", "黑色 Black"),
        ("#FFB7C5", "树莓 Raspberry"),
        ("#FF0000", "红色 Red"),
        ("#C40004", "深红 Dark Red"),
        ("#8B0000", "栗色 Maroon"),
        ("#FFA500", "橙色 Orange"),
        ("#FFDB00", "黄色 Yellow"),
        ("#FFF200", "浅黄 Light Yellow"),
        ("#94DE00", "柠檬绿 Lime Green"),
        ("#00B200", "绿色 Green"),
        ("#006A44", "深绿 Dark Green"),
        ("#00BFFF", "浅蓝 Light Blue"),
        ("#0076FF", "蓝色 Blue"),
        ("#003DA5", "深蓝 Dark Blue"),
        ("#260080", "紫色 Purple"),
        ("#A653FF", "浅紫 Light Purple"),
        ("#FF00FF", "品红 Magenta"),
        ("#DC82B4", "粉色 Pink"),
        ("#FFCAB6", "蜜桃 Peach"),
        ("#FFAF80", "棕褐 Tan"),
        ("#B67134", "棕色 Brown"),
        ("#FFCC00", "金色 Gold"),
    ],
    "Hama 标准色": [
        ("#FFFFFF", "白色 White"),
        ("#DCDCDC", "浅灰 Light Grey"),
        ("#A0A0A0", "灰色 Grey"),
        ("#505050", "深灰 Dark Grey"),
        ("#000000", "黑色 Black"),
        ("#FF0000", "红色 Red"),
        ("#B4001E", "深红 Dark Red"),
        ("#FF9600", "橙色 Orange"),
        ("#FFE600", "黄色 Yellow"),
        ("#B4E600", "柠檬 Lime"),
        ("#00A000", "绿色 Green"),
        ("#005028", "深绿 Dark Green"),
        ("#00C8C8", "青色 Cyan"),
        ("#0078FF", "蓝色 Blue"),
        ("#0028A0", "深蓝 Dark Blue"),
        ("#7800C8", "紫色 Purple"),
        ("#C850FF", "浅紫 Light Purple"),
        ("#FF0096", "粉色 Pink"),
        ("#FFB4B4", "浅粉 Light Pink"),
        ("#FFC88C", "蜜桃 Peach"),
        ("#C88232", "棕色 Brown"),
        ("#8C5028", "深棕 Dark Brown"),
        ("#FFDC64", "金色 Gold"),
        ("#C8C864", "橄榄 Olive"),
    ],
    "Artkal 方块色": [
        ("#FFFFFF", "白色 White"),
        ("#D7D7D7", "浅灰 Lt Grey"),
        ("#8C8C8C", "灰色 Grey"),
        ("#464646", "深灰 Dk Grey"),
        ("#000000", "黑色 Black"),
        ("#FF3232", "红色 Red"),
        ("#C80014", "深红 Dk Red"),
        ("#FFA000", "橙色 Orange"),
        ("#FFE600", "黄色 Yellow"),
        ("#82E600", "柠檬 Lime"),
        ("#00B400", "绿色 Green"),
        ("#005A32", "深绿 Dk Green"),
        ("#00C8DC", "青色 Cyan"),
        ("#0082FF", "蓝色 Blue"),
        ("#0032B4", "深蓝 Dk Blue"),
        ("#6400DC", "紫色 Purple"),
        ("#B43CFF", "浅紫 Lt Purple"),
        ("#FF00B4", "粉色 Pink"),
        ("#FFC8C8", "浅粉 Lt Pink"),
        ("#FFD296", "蜜桃 Peach"),
        ("#BE6E32", "棕色 Brown"),
        ("#783C1E", "深棕 Dk Brown"),
        ("#FFD200", "金色 Gold"),
        ("#B4B43C", "橄榄 Olive"),
        ("#FF8282", "珊瑚 Coral"),
        ("#B4DCFF", "天蓝 Sky"),
        ("#DCBEFF", "薰衣草 Lavender"),
        ("#FFC882", "杏色 Apricot"),
    ],
}


class PerlerBeadStudio:
    """电子拼豆工作室"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🟣 电子拼豆 — Perler Bead Studio")
        self.root.configure(bg="#1a1a2e")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)

        # ── 状态变量 ──
        self.grid_rows = 29
        self.grid_cols = 29
        self.cell_size = 18
        self.current_color = "#FF0000"
        self.current_tool = "draw"
        self.show_grid = True
        self.show_numbers = False
        self.grid_data = {}        # (row, col) -> color_hex
        self.undo_stack = []
        self.redo_stack = []
        self.is_drawing = False
        self.last_cell = None
        self.palette_name = "Perler 标准色"
        self.zoom_level = 1.0

        # ── 历史颜色 ──
        self.recent_colors = []

        self._build_ui()
        self._build_canvas()
        self._bind_events()
        self._update_title()

        # 启动
        self.root.mainloop()

    # ═══════════════════════════════════════
    #  UI 构建
    # ═══════════════════════════════════════
    def _build_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#1a1a2e")
        style.configure("TLabel", background="#1a1a2e", foreground="#e0e0e0",
                        font=("Microsoft YaHei UI", 10))
        style.configure("TButton", font=("Microsoft YaHei UI", 9))
        style.configure("Header.TLabel", font=("Microsoft YaHei UI", 11, "bold"),
                        foreground="#a78bfa")
        style.configure("Small.TLabel", font=("Microsoft YaHei UI", 8),
                        foreground="#666")
        style.configure("TLabelframe", background="#1a1a2e", foreground="#a78bfa")
        style.configure("TLabelframe.Label", background="#1a1a2e", foreground="#a78bfa",
                        font=("Microsoft YaHei UI", 10, "bold"))

        # ── 菜单栏 ──
        menubar = tk.Menu(self.root, bg="#16213e", fg="#e0e0e0",
                         activebackground="#a78bfa", activeforeground="#000",
                         font=("Microsoft YaHei UI", 10))

        file_menu = tk.Menu(menubar, tearoff=0, bg="#16213e", fg="#e0e0e0",
                           activebackground="#a78bfa", activeforeground="#000",
                           font=("Microsoft YaHei UI", 10))
        file_menu.add_command(label="新建项目", command=self._new_project, accelerator="Ctrl+N")
        file_menu.add_command(label="保存项目", command=self._save_project, accelerator="Ctrl+S")
        file_menu.add_command(label="打开项目", command=self._open_project, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="导出 PNG", command=self._export_png)
        file_menu.add_command(label="导出颜色统计", command=self._export_stats)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        menubar.add_cascade(label="文件", menu=file_menu)

        view_menu = tk.Menu(menubar, tearoff=0, bg="#16213e", fg="#e0e0e0",
                           activebackground="#a78bfa", activeforeground="#000",
                           font=("Microsoft YaHei UI", 10))
        view_menu.add_command(label="放大", command=self._zoom_in, accelerator="Ctrl++")
        view_menu.add_command(label="缩小", command=self._zoom_out, accelerator="Ctrl+-")
        view_menu.add_command(label="重置缩放", command=self._zoom_reset)
        menubar.add_cascade(label="视图", menu=view_menu)

        help_menu = tk.Menu(menubar, tearoff=0, bg="#16213e", fg="#e0e0e0",
                           activebackground="#a78bfa", activeforeground="#000",
                           font=("Microsoft YaHei UI", 10))
        help_menu.add_command(label="使用帮助", command=self._show_help)
        help_menu.add_command(label="关于", command=self._show_about)
        menubar.add_cascade(label="帮助", menu=help_menu)

        self.root.config(menu=menubar)

        # ── 顶部工具栏 ──
        toolbar = tk.Frame(self.root, bg="#16213e", height=48)
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)

        btn_style = {"bg": "#1a1a2e", "fg": "#e0e0e0", "relief": "flat",
                     "padx": 12, "pady": 4, "font": ("Microsoft YaHei UI", 10),
                     "activebackground": "#a78bfa", "activeforeground": "#000",
                     "cursor": "hand2"}

        # 工具按钮
        tools = [
            ("✏️ 画笔", "draw"), ("🧹 橡皮", "erase"),
            ("🪣 填充", "fill"), ("💉 吸色", "eyedropper"),
        ]

        self.tool_buttons = {}
        for text, tool in tools:
            btn = tk.Button(toolbar, text=text, command=lambda t=tool: self._set_tool(t),
                          **btn_style)
            btn.pack(side=tk.LEFT, padx=2, pady=8)
            self.tool_buttons[tool] = btn

        # 分隔线
        sep = tk.Frame(toolbar, bg="#a78bfa", width=1)
        sep.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=10)

        # 网格设置
        tk.Label(toolbar, text="网格:", bg="#16213e", fg="#888",
                font=("Microsoft YaHei UI", 9)).pack(side=tk.LEFT, padx=(4, 2))

        self.size_var = tk.StringVar(value="29×29")
        size_combo = ttk.Combobox(toolbar, textvariable=self.size_var, width=8,
                                  state="readonly",
                                  values=["15×15", "20×20", "25×25", "29×29",
                                          "35×35", "40×40", "50×50", "60×60"])
        size_combo.pack(side=tk.LEFT, padx=4)
        size_combo.bind("<<ComboboxSelected>>", self._on_size_change)

        # 网格开关
        self.grid_var = tk.BooleanVar(value=True)
        tk.Checkbutton(toolbar, text="网格", variable=self.grid_var,
                      bg="#16213e", fg="#e0e0e0", selectcolor="#1a1a2e",
                      activebackground="#16213e", font=("Microsoft YaHei UI", 9),
                      command=self._toggle_grid).pack(side=tk.LEFT, padx=4)

        self.num_var = tk.BooleanVar(value=False)
        tk.Checkbutton(toolbar, text="编号", variable=self.num_var,
                      bg="#16213e", fg="#e0e0e0", selectcolor="#1a1a2e",
                      activebackground="#16213e", font=("Microsoft YaHei UI", 9),
                      command=self._toggle_numbers).pack(side=tk.LEFT, padx=4)

        # 分隔线
        sep2 = tk.Frame(toolbar, bg="#a78bfa", width=1)
        sep2.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=10)

        # 撤销/重做
        tk.Button(toolbar, text="↩ 撤销", command=self._undo, **btn_style).pack(side=tk.LEFT, padx=2, pady=8)
        tk.Button(toolbar, text="↪ 重做", command=self._redo, **btn_style).pack(side=tk.LEFT, padx=2, pady=8)
        tk.Button(toolbar, text="🗑 清空", command=self._clear_canvas, **btn_style).pack(side=tk.LEFT, padx=2, pady=8)

        # 右侧信息
        self.info_label = tk.Label(toolbar, text="0 颗珠子", bg="#16213e", fg="#a78bfa",
                                   font=("Microsoft YaHei UI", 10, "bold"))
        self.info_label.pack(side=tk.RIGHT, padx=16)

        # ── 主体区域 ──
        main_frame = tk.Frame(self.root, bg="#1a1a2e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # 左侧面板
        left_panel = tk.Frame(main_frame, bg="#16213e", width=260)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 4))
        left_panel.pack_propagate(False)

        # 当前颜色预览
        color_frame = tk.LabelFrame(left_panel, text="当前颜色", bg="#16213e",
                                    fg="#a78bfa", font=("Microsoft YaHei UI", 10, "bold"))
        color_frame.pack(fill=tk.X, padx=8, pady=(8, 4))

        self.color_preview = tk.Canvas(color_frame, height=40, bg="#FF0000",
                                       highlightthickness=1, highlightbackground="#333")
        self.color_preview.pack(fill=tk.X, padx=8, pady=8)
        self.color_preview.bind("<Button-1>", self._pick_custom_color)

        self.color_label = tk.Label(color_frame, text="#FF0000 — 红色 Red",
                                   bg="#16213e", fg="#aaa", font=("Consolas", 9))
        self.color_label.pack(padx=8, pady=(0, 8))

        # 色板选择
        pal_frame = tk.LabelFrame(left_panel, text="色板", bg="#16213e",
                                  fg="#a78bfa", font=("Microsoft YaHei UI", 10, "bold"))
        pal_frame.pack(fill=tk.X, padx=8, pady=4)

        self.pal_var = tk.StringVar(value="Perler 标准色")
        pal_combo = ttk.Combobox(pal_frame, textvariable=self.pal_var, state="readonly",
                                 values=list(PALETTES.keys()))
        pal_combo.pack(fill=tk.X, padx=8, pady=8)
        pal_combo.bind("<<ComboboxSelected>>", self._on_palette_change)

        # 颜色网格
        self.palette_frame = tk.Frame(left_panel, bg="#16213e")
        self.palette_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        pal_scroll = tk.Scrollbar(self.palette_frame)
        pal_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.palette_canvas = tk.Canvas(self.palette_frame, bg="#16213e",
                                        highlightthickness=0,
                                        yscrollcommand=pal_scroll.set)
        self.palette_canvas.pack(fill=tk.BOTH, expand=True)
        pal_scroll.config(command=self.palette_canvas.yview)

        self.palette_inner = tk.Frame(self.palette_canvas, bg="#16213e")
        self.palette_canvas.create_window((0, 0), window=self.palette_inner, anchor="nw")
        self.palette_inner.bind("<Configure>",
            lambda e: self.palette_canvas.configure(scrollregion=self.palette_canvas.bbox("all")))

        self._build_palette_colors()

        # 最近使用颜色
        recent_frame = tk.LabelFrame(left_panel, text="最近使用", bg="#16213e",
                                     fg="#a78bfa", font=("Microsoft YaHei UI", 10, "bold"))
        recent_frame.pack(fill=tk.X, padx=8, pady=4)

        self.recent_frame_inner = tk.Frame(recent_frame, bg="#16213e")
        self.recent_frame_inner.pack(fill=tk.X, padx=8, pady=8)

        # 右侧画布区域
        right_frame = tk.Frame(main_frame, bg="#0d0d1a")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 画布滚动条
        self.h_scroll = tk.Scrollbar(right_frame, orient=tk.HORIZONTAL)
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.v_scroll = tk.Scrollbar(right_frame, orient=tk.VERTICAL)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas = tk.Canvas(right_frame, bg="#0d0d1a", highlightthickness=0,
                                xscrollcommand=self.h_scroll.set,
                                yscrollcommand=self.v_scroll.set)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.h_scroll.config(command=self.canvas.xview)
        self.v_scroll.config(command=self.canvas.yview)

        # 底部状态栏
        self.status_bar = tk.Label(self.root, text="就绪", bg="#16213e", fg="#666",
                                   font=("Consolas", 9), anchor=tk.W, padx=10)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self._set_tool("draw")

    # ═══════════════════════════════════════
    #  色板渲染
    # ═══════════════════════════════════════
    def _build_palette_colors(self):
        for w in self.palette_inner.winfo_children():
            w.destroy()

        colors = PALETTES[self.palette_name]
        cols = 6

        for i, (hex_color, name) in enumerate(colors):
            r, c = divmod(i, cols)
            btn = tk.Button(self.palette_inner, bg=hex_color, width=3, height=1,
                           relief="flat", bd=0, cursor="hand2",
                           activebackground=hex_color,
                           command=lambda hc=hex_color, n=name: self._select_color(hc, n))
            btn.grid(row=r, column=c, padx=2, pady=2, sticky="nsew")

            # 深色背景上加边框
            brightness = self._get_brightness(hex_color)
            if brightness < 80:
                btn.configure(highlightbackground="#444", highlightthickness=1)

        for c in range(cols):
            self.palette_inner.columnconfigure(c, weight=1)

    def _get_brightness(self, hex_color):
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return r * 0.299 + g * 0.587 + b * 0.114

    # ═══════════════════════════════════════
    #  画布构建
    # ═══════════════════════════════════════
    def _build_canvas(self):
        self.canvas.delete("all")
        cs = self.cell_size
        w = self.grid_cols * cs + 1
        h = self.grid_rows * cs + 1
        self.canvas.configure(scrollregion=(0, 0, w + 40, h + 40))

        offset_x, offset_y = 20, 20

        # 绘制已有的珠子
        for (row, col), color in self.grid_data.items():
            x1 = offset_x + col * cs
            y1 = offset_y + row * cs
            x2 = x1 + cs
            y2 = y1 + cs
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color,
                                         outline="", tags="bead")

        # 网格线
        if self.show_grid:
            grid_color = "#2a2a4a"
            for r in range(self.grid_rows + 1):
                y = offset_y + r * cs
                self.canvas.create_line(offset_x, y, offset_x + self.grid_cols * cs, y,
                                        fill=grid_color, tags="grid")
            for c in range(self.grid_cols + 1):
                x = offset_x + c * cs
                self.canvas.create_line(x, offset_y, x, offset_y + self.grid_rows * cs,
                                        fill=grid_color, tags="grid")

        # 行列坐标
        if self.show_numbers:
            for r in range(self.grid_rows):
                self.canvas.create_text(offset_x - 10, offset_y + r * cs + cs / 2,
                                        text=str(r + 1), fill="#444",
                                        font=("Consolas", 7), anchor="e", tags="numbers")
            for c in range(self.grid_cols):
                self.canvas.create_text(offset_x + c * cs + cs / 2, offset_y - 10,
                                        text=str(c + 1), fill="#444",
                                        font=("Consolas", 7), anchor="s", tags="numbers")

        # 外边框
        self.canvas.create_rectangle(offset_x, offset_y,
                                     offset_x + self.grid_cols * cs,
                                     offset_y + self.grid_rows * cs,
                                     outline="#a78bfa", width=2, tags="border")

        self._update_info()

    # ═══════════════════════════════════════
    #  事件绑定
    # ═══════════════════════════════════════
    def _bind_events(self):
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Motion>", self._on_motion)
        self.canvas.bind("<Leave>", lambda e: self.status_bar.config(text="就绪"))

        # 鼠标滚轮缩放
        self.canvas.bind("<Control-MouseWheel>", self._on_mouse_zoom)
        self.canvas.bind("<Control-Button-4>", lambda e: self._zoom_in())
        self.canvas.bind("<Control-Button-5>", lambda e: self._zoom_out())

        # 快捷键
        self.root.bind("<Control-z>", lambda e: self._undo())
        self.root.bind("<Control-y>", lambda e: self._redo())
        self.root.bind("<Control-n>", lambda e: self._new_project())
        self.root.bind("<Control-s>", lambda e: self._save_project())
        self.root.bind("<Control-o>", lambda e: self._open_project())
        self.root.bind("<Control-plus>", lambda e: self._zoom_in())
        self.root.bind("<Control-minus>", lambda e: self._zoom_out())

    def _get_cell(self, event):
        """获取鼠标位置对应的格子坐标"""
        cs = self.cell_size
        offset_x, offset_y = 20, 20
        # 转换画布坐标
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        col = int((cx - offset_x) / cs)
        row = int((cy - offset_y) / cs)
        if 0 <= row < self.grid_rows and 0 <= col < self.grid_cols:
            return row, col
        return None

    def _on_click(self, event):
        cell = self._get_cell(event)
        if not cell:
            return
        self.is_drawing = True
        self._save_undo_state()

        if self.current_tool == "draw":
            self._paint_cell(cell)
        elif self.current_tool == "erase":
            self._erase_cell(cell)
        elif self.current_tool == "fill":
            self._fill_cells(cell)
        elif self.current_tool == "eyedropper":
            self._eyedrop(cell)

    def _on_drag(self, event):
        if not self.is_drawing:
            return
        cell = self._get_cell(event)
        if not cell or cell == self.last_cell:
            return

        if self.current_tool == "draw":
            self._paint_cell(cell)
        elif self.current_tool == "erase":
            self._erase_cell(cell)

    def _on_release(self, event):
        self.is_drawing = False
        self.last_cell = None

    def _on_motion(self, event):
        cell = self._get_cell(event)
        if cell:
            row, col = cell
            color = self.grid_data.get(cell)
            if color:
                name = self._get_color_name(color)
                self.status_bar.config(text=f"({row+1}, {col+1}) — {color} {name}")
            else:
                self.status_bar.config(text=f"({row+1}, {col+1}) — 空")
        else:
            self.status_bar.config(text="就绪")

    # ═══════════════════════════════════════
    #  绘图操作
    # ═══════════════════════════════════════
    def _paint_cell(self, cell):
        row, col = cell
        old = self.grid_data.get(cell)
        if old == self.current_color:
            return
        self.grid_data[cell] = self.current_color
        self.last_cell = cell
        self._draw_bead(row, col, self.current_color)
        self._add_recent_color(self.current_color)
        self._update_info()

    def _erase_cell(self, cell):
        if cell in self.grid_data:
            row, col = cell
            del self.grid_data[cell]
            self.last_cell = cell
            self._draw_bead(row, col, None)
            self._update_info()

    def _fill_cells(self, start):
        target_color = self.grid_data.get(start)
        if target_color == self.current_color:
            return

        to_fill = []
        visited = set()
        queue = [start]

        while queue:
            cell = queue.pop(0)
            if cell in visited:
                continue
            visited.add(cell)
            r, c = cell
            if self.grid_data.get(cell) != target_color:
                continue
            to_fill.append(cell)
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.grid_rows and 0 <= nc < self.grid_cols:
                    queue.append((nr, nc))

        for cell in to_fill:
            self.grid_data[cell] = self.current_color
            self._draw_bead(cell[0], cell[1], self.current_color)

        self._add_recent_color(self.current_color)
        self._update_info()

    def _eyedrop(self, cell):
        color = self.grid_data.get(cell)
        if color:
            self._select_color(color, self._get_color_name(color))

    def _draw_bead(self, row, col, color):
        cs = self.cell_size
        ox, oy = 20, 20
        x1 = ox + col * cs
        y1 = oy + row * cs
        x2 = x1 + cs
        y2 = y1 + cs

        # 删除该位置旧的珠子
        tag = f"cell_{row}_{col}"
        self.canvas.delete(tag)

        if color:
            self.canvas.create_rectangle(x1 + 1, y1 + 1, x2 - 1, y2 - 1,
                                         fill=color, outline="", tags=("bead", tag))

        # 重绘网格（如果开启）
        if self.show_grid:
            grid_color = "#2a2a4a"
            self.canvas.create_line(x1, y1, x2, y1, fill=grid_color, tags="grid")
            self.canvas.create_line(x1, y2, x2, y2, fill=grid_color, tags="grid")
            self.canvas.create_line(x1, y1, x1, y2, fill=grid_color, tags="grid")
            self.canvas.create_line(x2, y1, x2, y2, fill=grid_color, tags="grid")

    # ═══════════════════════════════════════
    #  工具切换
    # ═══════════════════════════════════════
    def _set_tool(self, tool):
        self.current_tool = tool
        for name, btn in self.tool_buttons.items():
            if name == tool:
                btn.configure(bg="#a78bfa", fg="#000")
            else:
                btn.configure(bg="#1a1a2e", fg="#e0e0e0")

        cursors = {"draw": "pencil", "erase": "circle", "fill": "crosshair",
                   "eyedropper": "crosshair"}
        try:
            self.canvas.configure(cursor=cursors.get(tool, "arrow"))
        except:
            self.canvas.configure(cursor="arrow")

    # ═══════════════════════════════════════
    #  颜色选择
    # ═══════════════════════════════════════
    def _select_color(self, hex_color, name=""):
        self.current_color = hex_color
        self.color_preview.configure(bg=hex_color)
        display_name = name if name else self._get_color_name(hex_color)
        self.color_label.configure(text=f"{hex_color} — {display_name}")
        self._set_tool("draw")

    def _pick_custom_color(self, event=None):
        color = colorchooser.askcolor(initialcolor=self.current_color,
                                      title="选择自定义颜色")
        if color[1]:
            self._select_color(color[1], "自定义 Custom")

    def _add_recent_color(self, hex_color):
        if hex_color in self.recent_colors:
            self.recent_colors.remove(hex_color)
        self.recent_colors.insert(0, hex_color)
        self.recent_colors = self.recent_colors[:12]
        self._update_recent_colors()

    def _update_recent_colors(self):
        for w in self.recent_frame_inner.winfo_children():
            w.destroy()
        for i, color in enumerate(self.recent_colors):
            btn = tk.Button(self.recent_frame_inner, bg=color, width=2, height=1,
                           relief="flat", bd=0, cursor="hand2",
                           command=lambda c=color: self._select_color(c))
            btn.grid(row=0, column=i, padx=2, pady=2)

    def _get_color_name(self, hex_color):
        for pal_colors in PALETTES.values():
            for hc, name in pal_colors:
                if hc.upper() == hex_color.upper():
                    return name
        return "自定义"

    # ═══════════════════════════════════════
    #  撤销 / 重做
    # ═══════════════════════════════════════
    def _save_undo_state(self):
        state = dict(self.grid_data)
        self.undo_stack.append(state)
        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)
        self.redo_stack.clear()

    def _undo(self):
        if not self.undo_stack:
            return
        self.redo_stack.append(dict(self.grid_data))
        self.grid_data = self.undo_stack.pop()
        self._build_canvas()

    def _redo(self):
        if not self.redo_stack:
            return
        self.undo_stack.append(dict(self.grid_data))
        self.grid_data = self.redo_stack.pop()
        self._build_canvas()

    # ═══════════════════════════════════════
    #  网格设置
    # ═══════════════════════════════════════
    def _on_size_change(self, event=None):
        size = self.size_var.get()
        r, c = size.split("×")
        self.grid_rows = int(r)
        self.grid_cols = int(c)
        self.grid_data.clear()
        self.undo_stack.clear()
        self.redo_stack.clear()
        self._build_canvas()
        self._update_title()

    def _toggle_grid(self):
        self.show_grid = self.grid_var.get()
        self._build_canvas()

    def _toggle_numbers(self):
        self.show_numbers = self.num_var.get()
        self._build_canvas()

    def _on_palette_change(self, event=None):
        self.palette_name = self.pal_var.get()
        self._build_palette_colors()

    # ═══════════════════════════════════════
    #  缩放
    # ═══════════════════════════════════════
    def _zoom_in(self):
        if self.cell_size < 40:
            self.cell_size += 2
            self._build_canvas()

    def _zoom_out(self):
        if self.cell_size > 6:
            self.cell_size -= 2
            self._build_canvas()

    def _zoom_reset(self):
        self.cell_size = 18
        self._build_canvas()

    def _on_mouse_zoom(self, event):
        if event.delta > 0:
            self._zoom_in()
        else:
            self._zoom_out()

    # ═══════════════════════════════════════
    #  清空
    # ═══════════════════════════════════════
    def _clear_canvas(self):
        if not self.grid_data:
            return
        if messagebox.askyesno("确认清空", "确定要清空画布吗？此操作不可撤销。"):
            self._save_undo_state()
            self.grid_data.clear()
            self._build_canvas()

    # ═══════════════════════════════════════
    #  新建
    # ═══════════════════════════════════════
    def _new_project(self):
        if self.grid_data:
            if not messagebox.askyesno("确认", "当前项目未保存，确定要新建吗？"):
                return
        self.grid_data.clear()
        self.undo_stack.clear()
        self.redo_stack.clear()
        self._build_canvas()
        self._update_title()
        self.status_bar.config(text="新项目已创建")

    # ═══════════════════════════════════════
    #  保存 / 打开项目
    # ═══════════════════════════════════════
    def _save_project(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pbd",
            filetypes=[("拼豆项目", "*.pbd"), ("JSON 文件", "*.json"), ("所有文件", "*.*")],
            title="保存拼豆项目"
        )
        if not filepath:
            return

        data = {
            "version": "1.0",
            "grid_rows": self.grid_rows,
            "grid_cols": self.grid_cols,
            "palette": self.palette_name,
            "beads": {f"{r},{c}": color for (r, c), color in self.grid_data.items()},
            "created": datetime.now().isoformat(),
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self.status_bar.config(text=f"已保存: {filepath}")

    def _open_project(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("拼豆项目", "*.pbd"), ("JSON 文件", "*.json"), ("所有文件", "*.*")],
            title="打开拼豆项目"
        )
        if not filepath:
            return

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.grid_rows = data.get("grid_rows", 29)
            self.grid_cols = data.get("grid_cols", 29)
            self.size_var.set(f"{self.grid_rows}×{self.grid_cols}")

            pal = data.get("palette", "Perler 标准色")
            if pal in PALETTES:
                self.palette_name = pal
                self.pal_var.set(pal)
                self._build_palette_colors()

            self.grid_data.clear()
            for key, color in data.get("beads", {}).items():
                r, c = key.split(",")
                self.grid_data[(int(r), int(c))] = color

            self.undo_stack.clear()
            self.redo_stack.clear()
            self._build_canvas()
            self._update_title()
            self.status_bar.config(text=f"已打开: {filepath}")

        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件: {e}")

    # ═══════════════════════════════════════
    #  导出
    # ═══════════════════════════════════════
    def _export_png(self):
        if not self.grid_data:
            messagebox.showinfo("提示", "画布为空，没有可导出的内容")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".ps",
            filetypes=[("PostScript 文件", "*.ps"), ("所有文件", "*.*")],
            title="导出图纸"
        )
        if not filepath:
            return

        # 使用 Canvas 的 postscript 功能
        try:
            self.canvas.postscript(file=filepath, colormode="color")
            self.status_bar.config(text=f"已导出: {filepath}")
            messagebox.showinfo("导出成功",
                f"已导出为 PostScript 文件。\n"
                f"如需 PNG 格式，可使用 ImageMagick 转换：\n"
                f"convert {filepath} output.png")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {e}")

    def _export_stats(self):
        if not self.grid_data:
            messagebox.showinfo("提示", "画布为空")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            title="导出颜色统计"
        )
        if not filepath:
            return

        # 统计颜色
        color_count = {}
        for color in self.grid_data.values():
            color_count[color] = color_count.get(color, 0) + 1

        sorted_colors = sorted(color_count.items(), key=lambda x: -x[1])

        total = sum(color_count.values())

        lines = [
            "═" * 50,
            "  拼豆图纸 — 颜色统计表",
            f"  网格大小: {self.grid_rows} × {self.grid_cols}",
            f"  总珠子数: {total}",
            f"  颜色种类: {len(color_count)}",
            "═" * 50,
            "",
            f"  {'编号':<6} {'颜色':<8} {'色名':<20} {'数量':<8}",
            "  " + "─" * 42,
        ]

        for i, (color, count) in enumerate(sorted_colors, 1):
            name = self._get_color_name(color)
            lines.append(f"  {i:<6} {color:<8} {name:<20} {count:<8}")

        lines.extend(["", "═" * 50])

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        self.status_bar.config(text=f"统计已导出: {filepath}")
        messagebox.showinfo("导出成功", f"颜色统计已保存到:\n{filepath}")

    # ═══════════════════════════════════════
    #  帮助 / 关于
    # ═══════════════════════════════════════
    def _show_help(self):
        messagebox.showinfo("使用帮助",
            "🟣 电子拼豆 — 使用指南\n\n"
            "基本操作:\n"
            "  ✏️ 画笔 — 左键点击或拖动绘制珠子\n"
            "  🧹 橡皮 — 左键点击或拖动擦除珠子\n"
            "  🪣 填充 — 左键点击填充相同颜色区域\n"
            "  💉 吸色 — 左键点击吸取该位置的颜色\n\n"
            "快捷键:\n"
            "  Ctrl+Z — 撤销\n"
            "  Ctrl+Y — 重做\n"
            "  Ctrl+S — 保存项目\n"
            "  Ctrl+O — 打开项目\n"
            "  Ctrl+N — 新建项目\n"
            "  Ctrl+滚轮 — 缩放画布\n\n"
            "色板:\n"
            "  左侧面板选择色板和颜色\n"
            "  点击颜色预览块可选择自定义颜色\n\n"
            "导出:\n"
            "  文件 → 导出颜色统计\n"
            "  获取每种颜色的珠子数量清单")

    def _show_about(self):
        messagebox.showinfo("关于",
            "🟣 电子拼豆 — Perler Bead Studio\n"
            "版本 1.0\n\n"
            "用 Python + Tkinter 制作\n"
            "一个帮助你设计拼豆图案的小工具\n\n"
            "支持 Perler / Hama / Artkal 三大品牌色板\n"
            "支持自定义网格大小、保存/加载项目\n"
            "支持导出颜色统计表")

    # ═══════════════════════════════════════
    #  界面更新
    # ═══════════════════════════════════════
    def _update_info(self):
        total = len(self.grid_data)
        colors = len(set(self.grid_data.values()))
        self.info_label.configure(text=f"{total} 颗 / {colors} 色")

    def _update_title(self):
        self.root.title(f"🟣 电子拼豆 — {self.grid_rows}×{self.grid_cols}")


# ═══════════════════════════════════════
#  启动
# ═══════════════════════════════════════
if __name__ == "__main__":
    PerlerBeadStudio()