import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkcalendar import Calendar
from datetime import datetime
import requests

# Цветовая схема
BG_COLOR = "#f5f5f5"
ACCENT_COLOR = "#3a506b"  # Тёмно-синий
TEXT_COLOR = "#1c2541"    # Тёмно-синий текст
BUTTON_COLOR = "#3a506b"
BUTTON_HOVER = "#2b3a55"
LIGHT_ACCENT = "#5bc0be"  # Светло-бирюзовый
SELECTION_COLOR = "#d6e4ff"  # Светло-голубой для выделения
SELECTION_TEXT = "#1c2541"   # Тёмный текст для выделения

class OpenRouterAI:
    def __init__(self):
        self.API_KEY = "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"
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "meta-llama/llama-3-70b-instruct"  
    
    def generate_tasks(self, prompt):
        """Генерация задач через OpenRouter API с обязательным русским языком"""
        headers = {
            "Authorization": f"Bearer {self.API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://your-site.com",  # Обязательные заголовки
            "X-Title": "Task Manager"
        }
        
        payload = {
            "model": self.model,
            "messages": [{
                "role": "user", 
                "content": f"Сгенерируй 3 конкретные задачи на русском языке по теме: '{prompt}'. "\
                          f"Формат строго: '1. Заголовок: Описание\\n2. Заголовок: Описание'. "\
                          f"Используй только русский язык, избегай английских слов."
            }],
            "max_tokens": 500
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=15
            )
            
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                raise ValueError(f"Ошибка API ({response.status_code}): {response.text}")
                
        except Exception as e:
            raise ValueError(f"Ошибка соединения: {str(e)}")

class TaskManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager Pro")
        self.root.geometry("1000x700")
        self.root.configure(bg=BG_COLOR)
        
        self.setup_styles()
        self.ai = OpenRouterAI()
        self.tasks = {}
        self.task_id = 0
        self.current_filter = "Все"
        
        self.create_widgets()
    
    def setup_styles(self):
        """Настройка стилей элементов"""
        style = ttk.Style()
        style.theme_use("clam")
        
        # Общие стили
        style.configure(".", background=BG_COLOR, foreground=TEXT_COLOR, font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 14, "bold"))
        style.configure("Section.TLabelframe.Label", font=("Segoe UI", 10, "bold"))
        
        # Стили кнопок
        style.configure("Accent.TButton", 
                        background=BUTTON_COLOR, 
                        foreground="white",
                        font=("Segoe UI", 9, "bold"),
                        borderwidth=0)
        style.map("Accent.TButton",
                 background=[("active", BUTTON_HOVER), ("pressed", BUTTON_HOVER)])
        
        # Стили полей ввода
        style.configure("TEntry", fieldbackground="white", padding=5)
        style.configure("TCombobox", fieldbackground="white")
        
        # Стили списка задач
        style.configure("Treeview", 
                       background="white", 
                       fieldbackground="white",
                       rowheight=35,
                       font=("Segoe UI", 9),
                       foreground=TEXT_COLOR)
        
        style.configure("Treeview.Heading", 
                       background=ACCENT_COLOR, 
                       foreground="white",
                       font=("Segoe UI", 9, "bold"),
                       padding=(5, 3))
        
        style.map("Treeview", 
                  background=[("selected", SELECTION_COLOR)],
                  foreground=[("selected", SELECTION_TEXT)])
    
    def create_widgets(self):
        # Главный контейнер
        main_frame = ttk.Frame(self.root, padding=(20, 15))
        main_frame.pack(fill="both", expand=True)
        
        # Заголовок приложения
        ttk.Label(main_frame, text="Task Manager Pro", style="Title.TLabel").pack(pady=(0, 15))
        
        # Панель добавления задач
        self.create_input_panel(main_frame)
        
        # Панель управления
        self.create_control_panel(main_frame)
        
        # Список задач
        self.create_task_list(main_frame)
    
    def create_input_panel(self, parent):
        """Создает панель для ввода новых задач"""
        input_frame = ttk.LabelFrame(parent, text="Добавить задачу", padding=(15, 10))
        input_frame.pack(fill="x", pady=(0, 15))
        input_frame.columnconfigure(1, weight=1)
        
        # Поля ввода
        ttk.Label(input_frame, text="Заголовок:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.title_entry = ttk.Entry(input_frame, width=50, style="TEntry")
        self.title_entry.grid(row=0, column=1, padx=5, pady=5, sticky="we")
        
        ttk.Label(input_frame, text="Описание:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.desc_entry = ttk.Entry(input_frame, width=50, style="TEntry")
        self.desc_entry.grid(row=1, column=1, padx=5, pady=5, sticky="we")
        
        ttk.Label(input_frame, text="Приоритет:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.priority_var = tk.StringVar()
        self.priority_combobox = ttk.Combobox(input_frame, 
                                            textvariable=self.priority_var,
                                            values=["Низкий", "Средний", "Высокий"],
                                            state="readonly",
                                            style="TCombobox")
        self.priority_combobox.current(0)
        self.priority_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(input_frame, text="Дата выполнения:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        date_frame = ttk.Frame(input_frame)
        date_frame.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        self.due_date_entry = ttk.Entry(date_frame, width=12, style="TEntry")
        self.due_date_entry.pack(side="left")
        
        ttk.Button(date_frame, text="Выбрать", command=self.show_calendar, style="Accent.TButton").pack(side="left", padx=5)
        
        ttk.Button(input_frame, text="Добавить задачу", 
                  command=self.add_task, 
                  style="Accent.TButton").grid(row=4, column=1, pady=10, sticky="e")
    
    def create_control_panel(self, parent):
        """Создает панель управления с фильтрами и кнопками"""
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill="x", pady=(0, 15))
        
        # Левая часть (фильтры)
        left_control = ttk.Frame(control_frame)
        left_control.pack(side="left", fill="x", expand=True)
        
        ttk.Label(left_control, text="Фильтр:").pack(side="left", padx=(0, 5))
        self.filter_var = tk.StringVar()
        filter_combobox = ttk.Combobox(left_control, 
                                      textvariable=self.filter_var,
                                      values=["Все", "Текущие", "Выполненные"],
                                      state="readonly",
                                      width=12,
                                      style="TCombobox")
        filter_combobox.current(0)
        filter_combobox.pack(side="left")
        filter_combobox.bind("<<ComboboxSelected>>", self.apply_filter)
        
        # Правая часть (кнопки действий)
        right_control = ttk.Frame(control_frame)
        right_control.pack(side="right")
        
        buttons = [
            ("AI-генерация", self.generate_with_ai),
            ("Редактировать", self.edit_task),
            ("Отметить выполненной", self.mark_completed),
            ("Удалить", self.delete_task)
        ]
        
        for text, command in buttons:
            ttk.Button(right_control, text=text, command=command, style="Accent.TButton").pack(side="left", padx=3)
    
    def create_task_list(self, parent):
        """Создает список задач с прокруткой"""
        columns = ("ID", "Заголовок", "Описание", "Приоритет", "Дата", "Статус")
        
        self.task_list = ttk.Treeview(
            parent, 
            columns=columns, 
            show="headings",
            selectmode="extended",
            style="Treeview"
        )
        
        # Настройка колонок
        for col in columns:
            self.task_list.heading(col, text=col, anchor="center")
            
        # Ширина колонок
        self.task_list.column("ID", width=50, stretch=False, anchor="center")
        self.task_list.column("Заголовок", width=200, minwidth=100, stretch=True)
        self.task_list.column("Описание", width=300, minwidth=100, stretch=True)
        self.task_list.column("Приоритет", width=80, stretch=False, anchor="center")
        self.task_list.column("Дата", width=100, stretch=False, anchor="center")
        self.task_list.column("Статус", width=100, stretch=False, anchor="center")
        
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.task_list.yview)
        self.task_list.configure(yscrollcommand=scrollbar.set)
        
        # Размещение элементов
        self.task_list.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def show_calendar(self):
        """Показывает календарь для выбора даты"""
        top = tk.Toplevel(self.root)
        top.title("Выберите дату")
        top.geometry("300x300")
        top.transient(self.root)
        top.grab_set()
        top.configure(bg=BG_COLOR)
        
        cal = Calendar(top, selectmode="day", date_pattern="yyyy-mm-dd", 
                      background=LIGHT_ACCENT, foreground=TEXT_COLOR,
                      headersbackground=ACCENT_COLOR, headersforeground="white",
                      normalbackground="white", weekendbackground="#f0f0f0")
        cal.pack(pady=10, padx=10, fill="both", expand=True)
        
        btn_frame = ttk.Frame(top)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Выбрать", 
                  command=lambda: self.set_due_date(cal.get_date(), top),
                  style="Accent.TButton").pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="Отмена", command=top.destroy).pack(side="left", padx=5)
    
    def set_due_date(self, date, window):
        """Устанавливает выбранную дату в поле ввода"""
        self.due_date_entry.delete(0, tk.END)
        self.due_date_entry.insert(0, date)
        window.destroy()
    
    def add_task(self):
        """Добавляет новую задачу в список"""
        title = self.title_entry.get()
        description = self.desc_entry.get()
        priority = self.priority_var.get()
        due_date = self.due_date_entry.get()
        
        if not title:
            messagebox.showwarning("Ошибка", "Введите заголовок задачи!")
            return
            
        # Проверка формата даты
        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Ошибка", "Неправильный формат даты! Используйте ГГГГ-ММ-ДД.")
                return
            
        self.task_id += 1
        self.tasks[self.task_id] = {
            "title": title,
            "description": description,
            "priority": priority,
            "due_date": due_date,
            "status": "Не выполнено"
        }
        
        self.update_task_list()
        self.clear_inputs()
    
    def update_task_list(self):
        """Обновляет список задач в соответствии с текущим фильтром"""
        self.task_list.delete(*self.task_list.get_children())
        
        for task_id, task in self.tasks.items():
            if (self.current_filter == "Все" or
                (self.current_filter == "Текущие" and task["status"] == "Не выполнено") or
                (self.current_filter == "Выполненные" and task["status"] == "Выполнено")):
                
                # Цвет строки в зависимости от статуса
                tags = ("completed",) if task["status"] == "Выполнено" else ()
                
                self.task_list.insert("", "end", iid=task_id, tags=tags,
                                    values=(task_id, task["title"], task["description"],
                                            task["priority"], task["due_date"], task["status"]))
        
        # Настройка цветов для выполненных задач
        self.task_list.tag_configure("completed", background="#f0f0f0", foreground="#777777")
    
    def clear_inputs(self):
        """Очищает поля ввода после добавления задачи"""
        self.title_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.due_date_entry.delete(0, tk.END)
        self.priority_combobox.current(0)
    
    def apply_filter(self, event=None):
        """Применяет выбранный фильтр к списку задач"""
        self.current_filter = self.filter_var.get()
        self.update_task_list()
    
    def mark_completed(self):
        """Отмечает выбранные задачи как выполненные"""
        selected = self.task_list.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите задачу!")
            return
            
        for task_id in selected:
            self.tasks[int(task_id)]["status"] = "Выполнено"
        self.update_task_list()
    
    def delete_task(self):
        """Удаляет выбранные задачи"""
        selected = self.task_list.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите задачу!")
            return
            
        confirm = messagebox.askyesno("Подтверждение", f"Удалить {len(selected)} задач(у)?")
        if not confirm:
            return
            
        for task_id in selected:
            del self.tasks[int(task_id)]
        self.update_task_list()
    
    def edit_task(self):
        """Открывает окно редактирования выбранной задачи"""
        selected = self.task_list.selection()
        if not selected or len(selected) > 1:
            messagebox.showwarning("Ошибка", "Выберите ОДНУ задачу!")
            return
            
        task_id = int(selected[0])
        task = self.tasks[task_id]
        
        edit_win = tk.Toplevel(self.root)
        edit_win.title("Редактирование задачи")
        edit_win.geometry("500x400")
        edit_win.transient(self.root)
        edit_win.grab_set()
        edit_win.configure(bg=BG_COLOR)
        
        # Контейнер для элементов
        container = ttk.Frame(edit_win, padding=(20, 15))
        container.pack(fill="both", expand=True)
        
        # Заголовок окна
        ttk.Label(container, text="Редактирование задачи", style="Title.TLabel").grid(row=0, column=0, columnspan=2, pady=(0, 15))
        
        # Заголовок
        ttk.Label(container, text="Заголовок:").grid(row=1, column=0, sticky="w", pady=(0, 5))
        title_entry = ttk.Entry(container, width=40, style="TEntry")
        title_entry.grid(row=1, column=1, padx=5, pady=(0, 5), sticky="we")
        title_entry.insert(0, task["title"])
        
        # Описание
        ttk.Label(container, text="Описание:").grid(row=2, column=0, sticky="nw", pady=(0, 5))
        
        desc_frame = ttk.Frame(container)
        desc_frame.grid(row=2, column=1, padx=5, pady=(0, 5), sticky="nsew")
        
        desc_text = tk.Text(desc_frame, width=40, height=6, wrap="word", font=("Segoe UI", 9))
        scrollbar = ttk.Scrollbar(desc_frame, command=desc_text.yview)
        desc_text.config(yscrollcommand=scrollbar.set)
        
        desc_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        desc_text.insert("1.0", task["description"])
        
        # Приоритет
        ttk.Label(container, text="Приоритет:").grid(row=3, column=0, sticky="w", pady=(0, 5))
        priority_var = tk.StringVar(value=task["priority"])
        priority_combobox = ttk.Combobox(container, 
                                       textvariable=priority_var,
                                       values=["Низкий", "Средний", "Высокий"],
                                       state="readonly",
                                       style="TCombobox")
        priority_combobox.grid(row=3, column=1, padx=5, pady=(0, 5), sticky="w")
        
        # Дата выполнения
        ttk.Label(container, text="Дата выполнения:").grid(row=4, column=0, sticky="w", pady=(0, 5))
        date_frame = ttk.Frame(container)
        date_frame.grid(row=4, column=1, padx=5, pady=(0, 5), sticky="w")
        
        due_date_entry = ttk.Entry(date_frame, width=12, style="TEntry")
        due_date_entry.pack(side="left")
        due_date_entry.insert(0, task["due_date"])
        
        ttk.Button(date_frame, text="Выбрать", 
                  command=lambda: self.show_calendar_for_edit(due_date_entry), 
                  style="Accent.TButton").pack(side="left", padx=5)
        
        # Кнопки
        btn_frame = ttk.Frame(container)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Сохранить", 
                  command=lambda: self.save_edited_task(
                      task_id,
                      title_entry.get(),
                      desc_text.get("1.0", "end-1c"),
                      priority_var.get(),
                      due_date_entry.get(),
                      edit_win
                  ), style="Accent.TButton").pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="Отмена", command=edit_win.destroy).pack(side="left", padx=5)
        
        # Настройка растягивания
        container.columnconfigure(1, weight=1)
        container.rowconfigure(2, weight=1)
    
    def show_calendar_for_edit(self, entry_widget):
        """Показывает календарь для редактирования даты"""
        top = tk.Toplevel(self.root)
        top.title("Выберите дату")
        top.geometry("300x300")
        top.transient(self.root)
        top.grab_set()
        top.configure(bg=BG_COLOR)
        
        cal = Calendar(top, selectmode="day", date_pattern="yyyy-mm-dd", 
                      background=LIGHT_ACCENT, foreground=TEXT_COLOR,
                      headersbackground=ACCENT_COLOR, headersforeground="white",
                      normalbackground="white", weekendbackground="#f0f0f0")
        cal.pack(pady=10, padx=10, fill="both", expand=True)
        
        btn_frame = ttk.Frame(top)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Выбрать", 
                  command=lambda: self.set_due_date_for_edit(cal.get_date(), top, entry_widget),
                  style="Accent.TButton").pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="Отмена", command=top.destroy).pack(side="left", padx=5)
    
    def set_due_date_for_edit(self, date, window, entry_widget):
        """Устанавливает дату для редактируемой задачи"""
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, date)
        window.destroy()
    
    def save_edited_task(self, task_id, title, description, priority, due_date, window):
        """Сохраняет изменения в задаче"""
        if not title:
            messagebox.showwarning("Ошибка", "Заголовок не может быть пустым!")
            return
            
        # Проверка формата даты
        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Ошибка", "Неправильный формат даты! Используйте ГГГГ-ММ-ДД.")
                return
            
        self.tasks[task_id] = {
            "title": title,
            "description": description,
            "priority": priority,
            "due_date": due_date,
            "status": self.tasks[task_id]["status"]
        }
        
        self.update_task_list()
        window.destroy()
        messagebox.showinfo("Успех", "Задача обновлена!")
    
    def generate_with_ai(self):
        """Генерирует задачи с помощью ИИ"""
        prompt = simpledialog.askstring("AI Генератор задач", 
                                      "О чем создать задачи? Например: 'подготовка к экзамену'",
                                      parent=self.root)
        if not prompt:
            return

        try:
            generated_text = self.ai.generate_tasks(prompt)
            
            if not generated_text:
                messagebox.showwarning("Ошибка", "AI не вернул результаты")
                return
            
            generated_count = 0
            for line in generated_text.split("\n"):
                if line.strip() and ":" in line:
                    try:
                        # Обработка строки с задачей
                        clean_line = line.split(".", 1)[-1].strip()
                        title, desc = clean_line.split(":", 1)
                        title = title.strip()
                        desc = desc.strip()
                        
                        # Проверка на русский язык
                        if any(c.lower() in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя' for c in title+desc):
                            self.title_entry.delete(0, tk.END)
                            self.title_entry.insert(0, title)
                            self.desc_entry.delete(0, tk.END)
                            self.desc_entry.insert(0, desc)
                            self.add_task()
                            generated_count += 1
                            
                    except Exception as e:
                        continue

            if generated_count == 0:
                messagebox.showwarning("Предупреждение", 
                                     "Не удалось распознать русскоязычные задачи в ответе AI.\n"
                                     "Попробуйте изменить формулировку запроса.")
            else:
                messagebox.showinfo("Успех", f"Добавлено {generated_count} задач!")

        except Exception as e:
            messagebox.showerror("AI Ошибка", f"Ошибка генерации: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManager(root)
    root.mainloop()
