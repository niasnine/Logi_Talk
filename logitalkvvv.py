import threading  # для створення потоків (отримання повідомлень)
import socket      # для мережевого з'єднання
from customtkinter import *  # графічна бібліотека (оновлений Tkinter)

class LogiTalk(CTk):  # головне вікно програми
   def __init__(self):
       super().__init__()
       self.geometry("800x500")  # розмір вікна
       self.title("LogiTalk")    # заголовок вікна

       set_appearance_mode("System")  # система теми: світла/темна

       self.username = None  # ім'я користувача
       self.sock = None      # сокет для з'єднання з сервером

       self.login_frame = None  # екран авторизації
       self.create_login_ui()   # показати екран входу

   def create_login_ui(self):
       self.login_frame = CTkFrame(self)  # контейнер для входу
       self.login_frame.pack(expand=True)

       # Текст "Введіть ваше ім’я"
       CTkLabel(self.login_frame, text="Введіть ваше ім’я", font=("Arial", 18)).pack(pady=10)

       # Поле для введення імені
       self.name_entry = CTkEntry(self.login_frame, placeholder_text="Ім’я користувача")
       self.name_entry.pack(pady=10)

       # Кнопка "Увійти"
       CTkButton(self.login_frame, text="Увійти", command=self.open_chat).pack(pady=10)

   def open_chat(self):
       name = self.name_entry.get().strip()  # отримати ім'я
       if name:
           self.username = name  # зберігаємо ім’я
           self.login_frame.destroy()  # прибираємо екран входу
           self.create_main_ui()  # створюємо основне вікно
           self.connect_to_server()  # підключення до сервера
       else:
           # Якщо ім’я не введено, показати попередження
           CTkLabel(self.login_frame, text="⚠️ Введіть ім’я!", text_color="red").pack(pady=5)

   def create_main_ui(self):
       # Бічна панель (меню)
       self.menu_panel = CTkFrame(self, width=150)
       self.menu_panel.pack(side="left", fill="y", padx=10, pady=10)

       # Відображення імені користувача
       CTkLabel(self.menu_panel, text=f"👤 {self.username}", font=("Arial", 16)).pack(pady=10)

       # Кнопки: налаштування та вихід
       CTkButton(self.menu_panel, text="Налаштування", command=self.open_settings).pack(pady=5)
       CTkButton(self.menu_panel, text="Вийти", command=self.destroy).pack(pady=5)

       # Центральна панель
       self.center_panel = CTkFrame(self)
       self.center_panel.pack(expand=True, fill="both", padx=10, pady=10)

       # Поле для перегляду повідомлень (чат)
       self.textbox = CTkTextbox(self.center_panel, state="disabled")
       self.textbox.pack(expand=True, fill="both", padx=10, pady=(10, 5))

       # Нижня панель (введення повідомлення)
       self.bottom_panel = CTkFrame(self.center_panel)
       self.bottom_panel.pack(fill="x", padx=10, pady=(0, 10))

       # Поле для введення повідомлення
       self.entry = CTkEntry(self.bottom_panel, placeholder_text="Введіть повідомлення...")
       self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

       # Кнопка "Надіслати"
       self.send_btn = CTkButton(self.bottom_panel, text="Надіслати", command=self.send_message)
       self.send_btn.pack(side="right")

       # Надсилання по Enter
       self.entry.bind("<Return>", lambda event: self.send_message())

   def send_message(self):
       msg = self.entry.get().strip()  # беремо текст з поля
       if msg:
           self.entry.delete(0, END)  # очищаємо поле після відправки
           self.display_message(f"{self.username}: {msg}")  # показуємо в чаті
           try:
               # Формуємо повідомлення і надсилаємо на сервер
               self.sock.sendall(f"TEXT@{self.username}@{msg}\n".encode('utf-8'))
           except:
               self.display_message("⚠️ Відправка не вдалася (сервер недоступний).")
    def connect_to_server(self):
       try:
           self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # створюємо сокет
           self.sock.connect(('localhost', 8080))  # підключення до сервера
           hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався(лась) до чату!\n"
           self.sock.sendall(hello.encode('utf-8'))  # надсилаємо привітання

           # Запускаємо окремий потік для прийому повідомлень
           threading.Thread(target=self.receive_messages, daemon=True).start()
       except Exception as e:
           self.display_message(f"❌ Не вдалося підключитися до сервера: {e}")

   def receive_messages(self):
       buffer = ""  # буфер для збирання рядків
       while True:
           try:
               chunk = self.sock.recv(4096)  # отримуємо дані
               if not chunk:
                   break
               buffer += chunk.decode("utf-8")
               while "\n" in buffer:  # поки є повідомлення — обробляємо
                   line, buffer = buffer.split("\n", 1)
                   self.process_message(line.strip())
           except:
               break
       self.sock.close()  # закриваємо сокет після завершення

   def process_message(self, line):
       if not line:
           return
       parts = line.split("@", 3)  # розбиваємо повідомлення
       if len(parts) >= 3 and parts[0] == "TEXT":
           author = parts[1]
           msg = parts[2]
           if author != self.username:  # не показуємо свої повідомлення повторно
               self.display_message(f"{author}: {msg}")

   def display_message(self, message):
       self.textbox.configure(state="normal")  # вмикаємо редагування
       self.textbox.insert("end", message + "\n")  # додаємо текст
       self.textbox.configure(state="disabled")  # блокуємо редагування
       self.textbox.see("end")  # прокручуємо вниз

   def open_settings(self):
       # Вікно налаштувань теми
       settings_window = CTkToplevel(self)
       settings_window.title("Налаштування")
       settings_window.geometry("300x150")
       settings_window.resizable(False, False)

       CTkLabel(settings_window, text="Оберіть тему:", font=("Arial", 14)).pack(pady=10)

       def change_theme(choice):
           set_appearance_mode(choice)  # зміна теми

       theme_option = StringVar(value=get_appearance_mode())

       # Випадаючий список тем
       theme_menu = CTkOptionMenu(settings_window, variable=theme_option,
                                  values=["Light", "Dark"],
                                  command=change_theme)
       theme_menu.pack(pady=10)

       CTkButton(settings_window, text="Закрити", command=settings_window.destroy).pack(pady=10)


if name == "__main__":
   app = LogiTalk()  # створення екземпляра програми
   app.mainloop()    # запуск головного циклу
