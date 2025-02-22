import sys

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
except ModuleNotFoundError:
    print("Ошибка: модуль 'tkinter' не установлен. Приложение будет работать в консольном режиме.")
    tk = None

import paramiko


def execute_commands(username, password, command, ip_list, port):
    report = []
    for ip in ip_list:
        try:
            print(f"Подключение к {ip}:{port}...")
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, port=port, username=username, password=password, timeout=10)

            stdin, stdout, stderr = ssh.exec_command(command)
            output = stdout.read().decode()
            error_output = stderr.read().decode()
            ssh.close()

            if error_output:
                report.append(f"{ip}:{port}: Ошибка - {error_output.strip()}")
            else:
                report.append(f"{ip}:{port}: Успешно - {output.strip()}")
        except Exception as e:
            report.append(f"{ip}:{port}: Ошибка подключения - {e}")

    return report


if tk:
    class RouterApp:
        def __init__(self, root):
            self.root = root
            self.root.title("RouterOS SSH Executor K*UT")
            self.root.geometry("500x450")

            tk.Label(root, text="Логин: ").pack(pady=5)
            self.username_entry = tk.Entry(root, width=30)
            self.username_entry.pack(pady=5)

            tk.Label(root, text="Пароль: ").pack(pady=5)
            self.password_entry = tk.Entry(root, width=30, show="*")
            self.password_entry.pack(pady=5)

            tk.Label(root, text="Порт SSH: ").pack(pady=5)
            self.port_entry = tk.Entry(root, width=10)
            self.port_entry.insert(0, "22")
            self.port_entry.pack(pady=5)

            tk.Label(root, text="Команда: ").pack(pady=5)
            self.command_entry = tk.Entry(root, width=50)
            self.command_entry.pack(pady=5)

            tk.Button(root, text="Загрузить список IP", command=self.load_file).pack(pady=10)
            self.file_label = tk.Label(root, text="Файл не выбран")
            self.file_label.pack(pady=5)

            tk.Button(root, text="Выполнить команду", command=self.execute_commands).pack(pady=20)

            tk.Label(root, text="Лог выполнения:").pack(pady=5)
            self.log_text = tk.Text(root, height=10, width=60)
            self.log_text.pack(pady=5)

            self.ip_list = []

        def load_file(self):
            file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
            if file_path:
                self.file_label.config(text=f"Загружено: {file_path}")
                try:
                    with open(file_path, "r") as file:
                        self.ip_list = [line.strip() for line in file.readlines()]
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось прочитать файл: {e}")

        def execute_commands(self):
            username = self.username_entry.get()
            password = self.password_entry.get()
            command = self.command_entry.get()
            port = self.port_entry.get()

            if not username or not password or not command or not self.ip_list:
                messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля и загрузите список IP.")
                return

            try:
                port = int(port)
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректный номер порта.")
                return

            report = execute_commands(username, password, command, self.ip_list, port)
            self.log_text.delete("1.0", tk.END)
            self.log_text.insert(tk.END, "\n".join(report))
            messagebox.showinfo("Готово", "Команда выполнена на всех роутерах! Отчет доступен в логах.")


    if __name__ == "__main__":
        try:
            root = tk.Tk()
            app = RouterApp(root)
            root.mainloop()
        except Exception as e:
            print(f"Ошибка при запуске приложения: {e}")
else:
    if __name__ == "__main__":
        try:
            username = input("Введите логин: ")
            password = input("Введите пароль: ")
            command = input("Введите команду: ")
            port = input("Введите порт SSH (по умолчанию 22): ")
            file_path = input("Введите путь к файлу с IP-адресами: ")

            ip_list = []
            with open(file_path, "r") as file:
                ip_list = [line.strip() for line in file.readlines()]

            try:
                port = int(port) if port else 22
            except ValueError:
                print("Ошибка: Некорректный номер порта.")
                sys.exit(1)

            report = execute_commands(username, password, command, ip_list, port)
            print("\nОтчет о выполнении:")
            print("\n".join(report))
        except FileNotFoundError:
            print("Ошибка: файл не найден.")
        except ValueError:
            print("Ошибка: некорректные данные в файле.")
        except Exception as e:
            print(f"Ошибка: {e}")
