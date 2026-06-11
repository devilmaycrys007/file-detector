import os
import sys
import shutil
import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
from pathlib import Path

CONFIG_FILE = os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__)), "file_detector_config.json")


class FileDetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文件检测与复制工具")
        self.root.geometry("900x680")
        self.root.resizable(True, True)
        self.root.minsize(800, 600)

        # 设置样式
        style = ttk.Style()
        style.theme_use("clam")

        # 加载配置
        self.config = self.load_config()

        # 存储匹配的文件信息列表，每个元素: {"path": ..., "filename": ..., "mtime": ..., "mtime_str": ...}
        self.matched_files = []

        self.create_widgets()
        self.load_config_to_ui()

        # 窗口关闭时保存配置
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_config(self):
        """加载配置文件"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "source_folder": "",
            "file_types": "",
            "target_folder": "",
            "last_file": ""
        }

    def save_config(self, source_folder=None, file_types=None, target_folder=None, last_file=None):
        """保存配置到文件"""
        if source_folder is not None:
            self.config["source_folder"] = source_folder
        if file_types is not None:
            self.config["file_types"] = file_types
        if target_folder is not None:
            self.config["target_folder"] = target_folder
        if last_file is not None:
            self.config["last_file"] = last_file
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def load_config_to_ui(self):
        """将配置加载到UI"""
        if self.config.get("source_folder"):
            self.source_var.set(self.config["source_folder"])
        if self.config.get("file_types"):
            self.types_var.set(self.config["file_types"])
        if self.config.get("target_folder"):
            self.target_var.set(self.config["target_folder"])
        if self.config.get("last_file"):
            self.last_file_var.set(self.config["last_file"])

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = ttk.Label(main_frame, text="文件检测与复制工具", font=("Microsoft YaHei", 16, "bold"))
        title_label.pack(pady=(0, 12))

        # 第一步：选择检测文件夹
        row1 = ttk.Frame(main_frame)
        row1.pack(fill=tk.X, pady=3)
        ttk.Label(row1, text="1. 检测文件夹：", width=21, anchor=tk.W).pack(side=tk.LEFT)
        self.source_var = tk.StringVar()
        source_entry = ttk.Entry(row1, textvariable=self.source_var)
        source_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(row1, text="浏览...", command=self.browse_source, width=8).pack(side=tk.RIGHT)

        # 第二步：输入文件类型
        row2 = ttk.Frame(main_frame)
        row2.pack(fill=tk.X, pady=3)
        ttk.Label(row2, text="2. 文件类型（逗号分隔）：", width=21, anchor=tk.W).pack(side=tk.LEFT)
        self.types_var = tk.StringVar()
        types_entry = ttk.Entry(row2, textvariable=self.types_var)
        types_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(row2, text="例：.docx,.doc,.zip,.xls", foreground="gray").pack(side=tk.RIGHT, padx=(5, 0))

        # 第三步：选择参照文件
        row3 = ttk.Frame(main_frame)
        row3.pack(fill=tk.X, pady=3)
        ttk.Label(row3, text="3. 参照文件（开始时间点）：", width=21, anchor=tk.W).pack(side=tk.LEFT)
        self.last_file_var = tk.StringVar()
        last_file_entry = ttk.Entry(row3, textvariable=self.last_file_var)
        last_file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(row3, text="浏览...", command=self.browse_last_file, width=8).pack(side=tk.RIGHT)

        # 第四步：选择目标文件夹
        row4 = ttk.Frame(main_frame)
        row4.pack(fill=tk.X, pady=3)
        ttk.Label(row4, text="4. 目标存储文件夹：", width=21, anchor=tk.W).pack(side=tk.LEFT)
        self.target_var = tk.StringVar()
        target_entry = ttk.Entry(row4, textvariable=self.target_var)
        target_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(row4, text="浏览...", command=self.browse_target, width=8).pack(side=tk.RIGHT)

        # 分隔线 + 检测按钮
        sep_frame = ttk.Frame(main_frame)
        sep_frame.pack(fill=tk.X, pady=(10, 5))
        ttk.Separator(sep_frame, orient=tk.HORIZONTAL).pack(fill=tk.X)

        self.run_btn = ttk.Button(main_frame, text="开始检测文件", command=self.run_detection)
        self.run_btn.pack(fill=tk.X, ipady=5, pady=(0, 5))

        # 进度条
        self.progress = ttk.Progressbar(main_frame, mode="indeterminate")

        # ---- 文件表格区域 ----
        table_frame = ttk.LabelFrame(main_frame, text="匹配文件列表", padding="3")
        table_frame.pack(fill=tk.BOTH, expand=True)

        # 表格工具栏
        toolbar = ttk.Frame(table_frame)
        toolbar.pack(fill=tk.X, pady=(0, 5))

        self.delete_btn = ttk.Button(toolbar, text="删除选中", command=self.delete_selected)
        self.delete_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.clear_btn = ttk.Button(toolbar, text="清空全部", command=self.clear_all)
        self.clear_btn.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        self.copy_btn = ttk.Button(toolbar, text="复制到目标文件夹", command=self.copy_files)
        self.copy_btn.pack(side=tk.LEFT, padx=(10, 0))

        self.select_all_btn = ttk.Button(toolbar, text="全选", command=self.select_all)
        self.select_all_btn.pack(side=tk.RIGHT, padx=(5, 0))
        self.deselect_btn = ttk.Button(toolbar, text="取消全选", command=self.deselect_all)
        self.deselect_btn.pack(side=tk.RIGHT)

        # Treeview 表格
        columns = ("filename", "mtime", "path")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="extended")

        self.tree.heading("filename", text="文件名", anchor=tk.W)
        self.tree.heading("mtime", text="修改时间", anchor=tk.W)
        self.tree.heading("path", text="文件路径", anchor=tk.W)

        self.tree.column("filename", width=220, minwidth=120)
        self.tree.column("mtime", width=160, minwidth=120)
        self.tree.column("path", width=400, minwidth=200)

        # 表格滚动条
        tree_scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        tree_scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # ---- 日志区域 ----
        log_frame = ttk.LabelFrame(main_frame, text="执行日志", padding="3")
        log_frame.pack(fill=tk.X, pady=(5, 0))

        self.log_text = tk.Text(log_frame, height=5, wrap=tk.WORD, font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)

        log_scroll = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.configure(yscrollcommand=log_scroll.set)

        # 底部状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding=(5, 2))
        status_bar.pack(fill=tk.X, pady=(5, 0))

        # 绑定键盘快捷键删除
        self.root.bind("<Delete>", lambda e: self.delete_selected())

    def browse_source(self):
        folder = filedialog.askdirectory(title="选择需要检测的文件夹")
        if folder:
            self.source_var.set(folder)
            self.save_config(source_folder=folder)

    def browse_last_file(self):
        file_path = filedialog.askopenfilename(title="选择参照文件（检测修改时间晚于该文件的文件）")
        if file_path:
            self.last_file_var.set(file_path)

    def browse_target(self):
        folder = filedialog.askdirectory(title="选择目标存储文件夹")
        if folder:
            self.target_var.set(folder)
            self.save_config(target_folder=folder)

    def log(self, message):
        """输出日志到文本框"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def clear_table(self):
        """清空表格"""
        for item in self.tree.get_children():
            self.tree.delete(item)

    def refresh_table(self):
        """用 self.matched_files 刷新表格"""
        self.clear_table()
        for file_info in self.matched_files:
            self.tree.insert("", tk.END, values=(
                file_info["filename"],
                file_info["mtime_str"],
                file_info["path"]
            ))
        self.update_table_count()

    def update_table_count(self):
        """更新状态栏中的表格计数"""
        total = len(self.matched_files)
        self.status_var.set(f"表格中共 {total} 个文件")

    def delete_selected(self):
        """删除表格中选中的行"""
        selected = self.tree.selection()
        if not selected:
            return
        # 获取选中行的路径集合
        paths_to_remove = set()
        for item in selected:
            values = self.tree.item(item, "values")
            if values:
                paths_to_remove.add(values[2])  # values[2] 是文件路径

        # 从匹配列表中移除
        self.matched_files = [f for f in self.matched_files if f["path"] not in paths_to_remove]
        self.refresh_table()
        self.log(f"已删除 {len(selected)} 个文件")

    def clear_all(self):
        """清空表格中所有文件"""
        if not self.matched_files:
            return
        if messagebox.askyesno("确认清空", f"确定要清空表格中全部 {len(self.matched_files)} 个文件吗？"):
            self.matched_files = []
            self.clear_table()
            self.update_table_count()
            self.log("已清空全部文件")

    def select_all(self):
        """全选表格行"""
        for item in self.tree.get_children():
            self.tree.selection_add(item)

    def deselect_all(self):
        """取消全选"""
        for item in self.tree.selection():
            self.tree.selection_remove(item)

    def run_detection(self):
        """执行文件检测"""
        source_folder = self.source_var.get().strip()
        file_types_str = self.types_var.get().strip()
        last_file = self.last_file_var.get().strip()
        target_folder = self.target_var.get().strip()

        # 验证输入
        if not source_folder:
            messagebox.showerror("错误", "请选择需要检测的文件夹！")
            return
        if not os.path.isdir(source_folder):
            messagebox.showerror("错误", "检测文件夹路径不存在！")
            return

        if not file_types_str:
            messagebox.showerror("错误", "请输入需要检测的文件类型！")
            return

        if not last_file:
            messagebox.showerror("错误", "请选择参照文件！")
            return
        if not os.path.isfile(last_file):
            messagebox.showerror("错误", "参照文件不存在！")
            return

        # 目标文件夹不强制校验，复制时才校验

        # 解析文件类型
        file_types = [t.strip() for t in file_types_str.replace("，", ",").split(",") if t.strip()]
        file_types_lower = [t.lower() for t in file_types]

        # 获取参照文件的修改时间
        ref_mtime = os.path.getmtime(last_file)
        ref_mtime_str = datetime.fromtimestamp(ref_mtime).strftime("%Y-%m-%d %H:%M:%S")
        self.log(f"参照文件修改时间: {ref_mtime_str}")

        # 禁用按钮，显示进度
        self.run_btn.config(state=tk.DISABLED, text="正在检测中...")
        self.progress.pack(fill=tk.X, pady=(0, 5))
        self.progress.start()
        self.status_var.set("正在扫描文件...")

        try:
            new_matched = []
            total_scanned = 0

            # 遍历源文件夹
            for root_dir, dirs, files in os.walk(source_folder):
                for filename in files:
                    total_scanned += 1
                    file_path = os.path.join(root_dir, filename)
                    file_ext = os.path.splitext(filename)[1].lower()

                    # 检查文件类型是否匹配
                    if file_ext not in file_types_lower:
                        continue

                    try:
                        file_mtime = os.path.getmtime(file_path)
                    except OSError:
                        continue

                    # 检查修改时间是否晚于参照文件
                    if file_mtime > ref_mtime:
                        new_matched.append({
                            "path": file_path,
                            "filename": filename,
                            "mtime": file_mtime,
                            "mtime_str": datetime.fromtimestamp(file_mtime).strftime("%Y-%m-%d %H:%M:%S")
                        })

                    # 每扫描1000个文件更新一次状态
                    if total_scanned % 1000 == 0:
                        self.status_var.set(f"已扫描 {total_scanned} 个文件，匹配 {len(new_matched)} 个...")
                        self.root.update_idletasks()

            self.log(f"扫描完成，共扫描 {total_scanned} 个文件，匹配 {len(new_matched)} 个文件")

            if new_matched:
                # 追加到现有列表（保留之前扫描但未删除的文件）
                existing_paths = {f["path"] for f in self.matched_files}
                added_count = 0
                for f in new_matched:
                    if f["path"] not in existing_paths:
                        self.matched_files.append(f)
                        added_count += 1

                # 按修改时间降序排列
                self.matched_files.sort(key=lambda x: x["mtime"], reverse=True)

                self.refresh_table()
                self.log(f"新增 {added_count} 个文件到表格（跳过了 {len(new_matched) - added_count} 个重复文件）")
            else:
                self.log("没有找到符合条件的文件（修改时间晚于参照文件且类型匹配）")
                self.update_table_count()

            # 保存配置（第1、2、4步）
            self.save_config(
                source_folder=source_folder,
                file_types=file_types_str,
                target_folder=target_folder
            )

        except Exception as e:
            self.log(f"发生错误: {e}")
            messagebox.showerror("错误", f"执行过程中发生错误:\n{e}")
        finally:
            self.progress.stop()
            self.progress.pack_forget()
            self.run_btn.config(state=tk.NORMAL, text="开始检测文件")

    def copy_files(self):
        """将表格中的文件复制到目标文件夹"""
        target_folder = self.target_var.get().strip()

        if not target_folder:
            messagebox.showerror("错误", "请先选择目标存储文件夹（步骤4）！")
            return
        if not os.path.isdir(target_folder):
            messagebox.showerror("错误", "目标存储文件夹路径不存在！")
            return

        files_to_copy = list(self.matched_files)  # 复制一份，避免迭代时修改
        if not files_to_copy:
            messagebox.showinfo("提示", "表格中没有文件可供复制。")
            return

        # 确认复制
        if not messagebox.askyesno("确认复制", f"确定要将表格中的 {len(files_to_copy)} 个文件复制到目标文件夹吗？"):
            return

        # 禁用按钮，显示进度
        self.copy_btn.config(state=tk.DISABLED, text="正在复制...")
        self.run_btn.config(state=tk.DISABLED)
        self.progress.pack(fill=tk.X, pady=(0, 5))
        self.progress.start()

        copied_count = 0
        failed_files = []
        self.status_var.set(f"正在复制 {len(files_to_copy)} 个文件...")

        try:
            for i, file_info in enumerate(files_to_copy):
                src_file = file_info["path"]
                filename = file_info["filename"]
                dst_file = os.path.join(target_folder, filename)

                # 如果目标文件已存在，添加序号避免覆盖
                if os.path.exists(dst_file):
                    name, ext = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(dst_file):
                        new_name = f"{name}_{counter}{ext}"
                        dst_file = os.path.join(target_folder, new_name)
                        counter += 1

                try:
                    shutil.copy2(src_file, dst_file)
                    copied_count += 1
                    self.log(f"已复制: {src_file} -> {dst_file}")
                except Exception as e:
                    failed_files.append((src_file, str(e)))
                    self.log(f"复制失败: {src_file} - {e}")

                if (i + 1) % 10 == 0:
                    self.status_var.set(f"复制进度: {i + 1}/{len(files_to_copy)}")
                    self.root.update_idletasks()

            # 保存配置：将表格中修改时间最晚的文件作为参照文件
            newest_file = None
            if self.matched_files:
                newest_file = max(self.matched_files, key=lambda x: x["mtime"])["path"]

            self.save_config(
                source_folder=self.source_var.get().strip(),
                file_types=self.types_var.get().strip(),
                target_folder=target_folder,
                last_file=newest_file if newest_file else self.last_file_var.get().strip()
            )

            # 更新第三步显示
            if newest_file:
                self.last_file_var.set(newest_file)
                self.log(f"已更新参照文件为表格中最晚修改时间的文件")

            result_msg = f"复制完成！\n\n表格文件数: {len(files_to_copy)}\n成功复制: {copied_count}"
            if failed_files:
                result_msg += f"\n复制失败: {len(failed_files)}"
            self.log(result_msg.replace("\n", " | "))
            self.status_var.set(f"完成 - 成功复制 {copied_count} 个文件")
            messagebox.showinfo("执行完成", result_msg)

        except Exception as e:
            self.log(f"发生错误: {e}")
            messagebox.showerror("错误", f"复制过程中发生错误:\n{e}")
        finally:
            self.progress.stop()
            self.progress.pack_forget()
            self.copy_btn.config(state=tk.NORMAL, text="复制到目标文件夹")
            self.run_btn.config(state=tk.NORMAL, text="开始检测文件")

    def on_closing(self):
        """窗口关闭事件"""
        # 保存配置：将表格中修改时间最晚的文件作为参照文件
        newest_file = None
        if self.matched_files:
            newest_file = max(self.matched_files, key=lambda x: x["mtime"])["path"]

        self.save_config(
            source_folder=self.source_var.get().strip(),
            file_types=self.types_var.get().strip(),
            target_folder=self.target_var.get().strip(),
            last_file=newest_file if newest_file else self.last_file_var.get().strip()
        )
        self.root.destroy()


def main():
    root = tk.Tk()
    app = FileDetectorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
