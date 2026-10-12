import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import sys
from datetime import datetime

PROJECT_PATH = r'C:\Users\jialo\Documents\Codex\2026-09-02\ni\rag_project'
sys.path.insert(0, PROJECT_PATH)


class DeltaForceApp:
    def __init__(self, root):
        self.root = root
        self.root.title('三角洲行动 - 彦祖情报系统 v3.0')
        self.root.geometry('1100x750')
        self.root.minsize(900, 600)
        self.root.configure(bg='#0a0e1a')

        self.kb_loaded = False
        self._create_ui()
        # ✅ 确保这行在 _create_ui 之后调用
        self._show_welcome()

    def _create_ui(self):
        # 顶部标题栏
        header = tk.Frame(self.root, bg='#1a1f3a', height=80)
        header.pack(fill='x')
        header.pack_propagate(False)

        title_frame = tk.Frame(header, bg='#1a1f3a')
        title_frame.pack(side='left', padx=30, pady=15)

        tk.Label(title_frame, text='🎯', font=('Microsoft YaHei', 28),
                 bg='#1a1f3a', fg='#FF6B35').pack()
        tk.Label(title_frame, text='三角洲行动', font=('Microsoft YaHei', 20, 'bold'),
                 bg='#1a1f3a', fg='#FF6B35').pack()
        tk.Label(title_frame, text='彦祖情报系统 v3.0', font=('Microsoft YaHei', 11),
                 bg='#1a1f3a', fg='#8892b0').pack()

        self.status_var = tk.StringVar(value='● 待机中')
        status_frame = tk.Frame(header, bg='#1a1f3a')
        status_frame.pack(side='right', padx=30, pady=15)
        tk.Label(status_frame, textvariable=self.status_var,
                 font=('Microsoft YaHei', 12), bg='#1a1f3a', fg='#00ff88').pack()

        # 主内容区
        main = tk.Frame(self.root, bg='#0a0e1a')
        main.pack(fill='both', expand=True, padx=20, pady=15)

        # 左侧对话区
        left_frame = tk.Frame(main, bg='#111827', relief='solid', bd=1)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 15))

        chat_header = tk.Frame(left_frame, bg='#1a1f3a', height=45)
        chat_header.pack(fill='x')
        chat_header.pack_propagate(False)
        tk.Label(chat_header, text='💬 情报咨询终端', font=('Microsoft YaHei', 13, 'bold'),
                 bg='#1a1f3a', fg='#FF6B35').pack(side='left', padx=20, pady=10)

        # ✅ 对话文本框
        self.chat_text = scrolledtext.ScrolledText(
            left_frame, font=('Microsoft YaHei', 11),
            bg='#0d1117', fg='#c9d1d9', insertbackground='#c9d1d9',
            wrap='word', state='disabled', bd=0
        )
        self.chat_text.pack(fill='both', expand=True, padx=15, pady=15)

        # 右侧控制区
        right_frame = tk.Frame(main, width=280, bg='#111827', relief='solid', bd=1)
        right_frame.pack(side='right', fill='y')
        right_frame.pack_propagate(False)
        right_frame.configure(height=640)

        control_title = tk.Frame(right_frame, bg='#1a1f3a', height=45)
        control_title.pack(fill='x')
        control_title.pack_propagate(False)
        tk.Label(control_title, text='⚙️ 作战控制台', font=('Microsoft YaHei', 13, 'bold'),
                 bg='#1a1f3a', fg='#FF6B35').pack(pady=10)

        kb_card = tk.Frame(right_frame, bg='#1a1f3a', height=100)
        kb_card.pack(fill='x', padx=15, pady=10)
        tk.Label(kb_card, text='📦 知识库状态', font=('Microsoft YaHei', 10),
                 bg='#1a1f3a', fg='#8892b0').pack(anchor='w', padx=15, pady=(10, 5))
        self.kb_status_var = tk.StringVar(value='状态: 未加载')
        tk.Label(kb_card, textvariable=self.kb_status_var, font=('Microsoft YaHei', 14, 'bold'),
                 bg='#1a1f3a', fg='#00ff88').pack(anchor='w', padx=15, pady=5)

        btn_frame = tk.Frame(right_frame, bg='#111827')
        btn_frame.pack(fill='x', padx=15, pady=20)

        tk.Button(btn_frame, text='📥 加载情报库', font=('Microsoft YaHei', 11),
                  bg='#FF6B35', fg='white', activebackground='#e85a2b',
                  relief='flat', padx=20, pady=12, cursor='hand2',
                  command=self.load_knowledge).pack(fill='x', pady=5)

        tk.Button(btn_frame, text='🗑️ 清空对话', font=('Microsoft YaHei', 11),
                  bg='#2d3748', fg='#e2e8f0', activebackground='#4a5568',
                  relief='flat', padx=20, pady=12, cursor='hand2',
                  command=self.clear_chat).pack(fill='x', pady=5)

        tip_card = tk.Frame(right_frame, bg='#1a1f3a', height=80)
        tip_card.pack(fill='x', padx=15, pady=10)
        tk.Label(tip_card, text='💡 快速提示', font=('Microsoft YaHei', 10),
                 bg='#1a1f3a', fg='#FF6B35').pack(anchor='w', padx=15, pady=(10, 5))
        tk.Label(tip_card, text='• 输入枪械型号查询\n• 支持模糊匹配\n• 秒级响应',
                 font=('Microsoft YaHei', 9), bg='#1a1f3a', fg='#8892b0',
                 justify='left').pack(anchor='w', padx=15, pady=5)

        # 底部输入区
        input_section = tk.Frame(self.root, bg='#1a1f3a', height=90)
        input_section.pack(fill='x', padx=20, pady=(0, 20))
        input_section.pack_propagate(False)

        input_container = tk.Frame(input_section, bg='#111827', relief='solid', bd=1)
        input_container.pack(side='left', fill='x', expand=True, padx=(0, 10), pady=15)

        self.input_entry = tk.Entry(
            input_container, font=('Microsoft YaHei', 12),
            bg='#0d1117', fg='#c9d1d9', insertbackground='#c9d1d9',
            relief='flat', bd=0
        )
        self.input_entry.pack(fill='x', expand=True, padx=20, pady=10)
        self.input_entry.insert(0, '🔍 输入查询内容，如: M14改枪码、M7步枪...')
        self.input_entry.bind('<FocusIn>', self._on_enter_focus)
        self.input_entry.bind('<Return>', lambda e: self.send_message())

        tk.Button(input_section, text='🚀 发送', font=('Microsoft YaHei', 12, 'bold'),
                  bg='#FF6B35', fg='white', activebackground='#e85a2b',
                  relief='flat', padx=30, pady=15, cursor='hand2',
                  command=self.send_message).pack(side='right', pady=15)

    def _show_welcome(self):
        """显示欢迎消息 - 确保这个方法被调用"""
        welcome_msg = '🎖️ 指挥官，欢迎回到三角洲行动情报中心！\n\n我是彦祖，你的专属情报分析助手。'
        print(f"调用 _show_welcome，消息: {welcome_msg}")  # 调试输出
        self._add_message('情报中心', welcome_msg, is_system=False)

    def _on_enter_focus(self, event):
        if self.input_entry.get() == '🔍 输入查询内容，如: M14改枪码、M7步枪...':
            self.input_entry.delete(0, 'end')

    def load_knowledge(self):
        self.status_var.set('● 加载中...')
        self.root.update()
        try:
            from rag_engine import engine
            engine.load_knowledge()
            self.kb_loaded = True
            self.status_var.set('● 已连接')
            self.kb_status_var.set('状态: ✅ 已加载')
            messagebox.showinfo('情报系统', '✅ 情报库加载成功！')
        except Exception as e:
            self.status_var.set('● 错误')
            messagebox.showerror('错误', f'❌ 加载失败: {e}')

    def send_message(self):
        question = self.input_entry.get().strip()
        if not question or question == '🔍 输入查询内容，如: M14改枪码、M7步枪...':
            return
        self._add_message('指挥官', question, is_user=True)
        self.input_entry.delete(0, 'end')
        self._add_message('系统', '🔍 正在分析情报...', is_system=True)
        self.root.update()
        threading.Thread(target=self._process, args=(question,), daemon=True).start()

    def _process(self, question):
        try:
            from rag_engine import engine
            if not self.kb_loaded:
                engine.load_knowledge()
                self.kb_loaded = True
            answer, sources = engine.ask(question)
            self.chat_text.config(state='normal')
            content = self.chat_text.get('1.0', 'end-1c')
            lines = [l for l in content.split('\n') if '正在分析' not in l]
            self.chat_text.delete('1.0', 'end')
            self.chat_text.insert('1.0', '\n'.join(lines))
            self.chat_text.config(state='disabled')
            self._add_message('情报中心', answer, is_system=False)
        except Exception as e:
            self._add_message('系统', f'❌ 查询失败: {e}', is_system=True)

    def _add_message(self, sender, message, is_user=False, is_system=False):
        print(f"_add_message called: sender={sender}, message={message[:30]}...")  # 调试输出
        self.chat_text.config(state='normal')
        t = datetime.now().strftime('%H:%M:%S')
        if is_system:
            self.chat_text.insert('end', f'\n[{t}] {sender}: {message}\n')
        elif is_user:
            self.chat_text.insert('end', f'\n[{t}] 指挥官: {message}\n')
        else:
            self.chat_text.insert('end', f'\n[{t}] {sender}:\n{message}\n\n')
        self.chat_text.see('end')
        self.chat_text.config(state='disabled')

    def clear_chat(self):
        self.chat_text.config(state='normal')
        self.chat_text.delete('1.0', 'end')
        self.chat_text.config(state='disabled')


if __name__ == '__main__':
    root = tk.Tk()
    app = DeltaForceApp(root)
    root.mainloop()