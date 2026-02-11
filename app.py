import threading
import tkinter as tk
from tkinter import ttk, messagebox

from config_loader import load_imap_config, save_config, PersonalConfig, CorporateConfig
from email_code_fetcher import get_auth_code_from_email, get_auth_code_from_sms, PLATFORM_OTP_SUBJECT_MARKERS


def run_in_thread(func, on_done):
    def run():
        try:
            result = func()
        except Exception as e:
            result = str(e)
        if on_done:
            root = tk._default_root
            if root:
                root.after(0, lambda: on_done(result))

    threading.Thread(target=run, daemon=True).start()


class SettingsWindow:
    def __init__(self, parent, on_save):
        self.on_save = on_save
        self.win = tk.Toplevel(parent)
        self.win.title("Настройки")
        self.win.transient(parent)
        self.win.geometry("400x320")
        self.win.resizable(True, True)

        f = ttk.Frame(self.win, padding=10)
        f.pack(fill=tk.BOTH, expand=True)

        row = 0
        ttk.Label(f, text="Личная почта (email):").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.personal_email = ttk.Entry(f, width=38)
        self.personal_email.grid(row=row, column=1, sticky=tk.EW, pady=2, padx=(8, 0))
        row += 1
        ttk.Label(f, text="Личная почта (пароль):").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.personal_password = ttk.Entry(f, width=38, show="*")
        self.personal_password.grid(row=row, column=1, sticky=tk.EW, pady=2, padx=(8, 0))
        row += 1
        ttk.Label(f, text="Папка с кодами (личная):").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.personal_folder = ttk.Entry(f, width=38)
        self.personal_folder.grid(row=row, column=1, sticky=tk.EW, pady=2, padx=(8, 0))
        row += 1

        ttk.Separator(f, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=2, sticky=tk.EW, pady=8)
        row += 1
        ttk.Label(f, text="Корпоративная почта (email):").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.corporate_email = ttk.Entry(f, width=38)
        self.corporate_email.grid(row=row, column=1, sticky=tk.EW, pady=2, padx=(8, 0))
        row += 1
        ttk.Label(f, text="Корпоративная почта (пароль):").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.corporate_password = ttk.Entry(f, width=38, show="*")
        self.corporate_password.grid(row=row, column=1, sticky=tk.EW, pady=2, padx=(8, 0))
        row += 1

        ttk.Separator(f, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=2, sticky=tk.EW, pady=8)
        row += 1
        self.copy_to_clipboard_var = tk.BooleanVar()
        ttk.Checkbutton(f, text="Копировать результат в буфер обмена", variable=self.copy_to_clipboard_var).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=2
        )
        row += 1
        self.always_on_top_var = tk.BooleanVar()
        ttk.Checkbutton(f, text="Окно поверх всех окон", variable=self.always_on_top_var).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=2
        )
        row += 1

        f.columnconfigure(1, weight=1)
        btn_f = ttk.Frame(f)
        btn_f.grid(row=row, column=0, columnspan=2, pady=12)
        ttk.Button(btn_f, text="Сохранить", command=self._save).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_f, text="Отмена", command=self.win.destroy).pack(side=tk.LEFT, padx=4)

    def load(self, host: str, port: int, personal: PersonalConfig, corporate: CorporateConfig, ui: dict):
        self._imap_host = host
        self._imap_port = port
        self.personal_email.delete(0, tk.END)
        self.personal_email.insert(0, personal.email)
        self.personal_password.delete(0, tk.END)
        self.personal_password.insert(0, personal.password)
        self.personal_folder.delete(0, tk.END)
        self.personal_folder.insert(0, personal.folder)
        self.corporate_email.delete(0, tk.END)
        self.corporate_email.insert(0, corporate.email)
        self.corporate_password.delete(0, tk.END)
        self.corporate_password.insert(0, corporate.password)
        self.copy_to_clipboard_var.set(ui.get("copy_to_clipboard", True))
        self.always_on_top_var.set(ui.get("always_on_top", False))

    def _save(self):
        personal = PersonalConfig(
            email=self.personal_email.get().strip(),
            password=self.personal_password.get(),
            folder=(self.personal_folder.get().strip() or "INBOX"),
        )
        corporate = CorporateConfig(
            email=self.corporate_email.get().strip(),
            password=self.corporate_password.get(),
        )
        save_config(
            host=self._imap_host,
            port=self._imap_port,
            personal=personal,
            corporate=corporate,
            copy_to_clipboard=self.copy_to_clipboard_var.get(),
            always_on_top=self.always_on_top_var.get(),
        )
        self.on_save(personal, corporate)
        self.win.destroy()


def copy_to_clipboard(root: tk.Tk, text: str):
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update_idletasks()


def main():
    root = tk.Tk()
    root.title("Коды")
    root.geometry("170x360")
    root.resizable(False, False)
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=0)
    root.columnconfigure(2, weight=1)
    root.rowconfigure(0, weight=0)
    root.rowconfigure(1, weight=1)

    imap_host, imap_port, personal, corporate, ui = load_imap_config()
    root.attributes("-topmost", bool(ui.get("always_on_top", False)))

    def apply_after_save(new_personal: PersonalConfig, new_corporate: CorporateConfig):
        nonlocal personal, corporate, ui
        _, _, personal, corporate, ui = load_imap_config()
        root.attributes("-topmost", bool(ui.get("always_on_top", False)))

    # Центральная колонка (кнопки + результат)
    center = ttk.Frame(root)
    center.grid(row=0, column=1, rowspan=2, sticky=tk.N)
    center.columnconfigure(0, weight=0)
    center.rowconfigure(0, weight=0)
    center.rowconfigure(1, weight=1)

    # Кнопки в один столбик
    btn_frame = ttk.Frame(center, padding=8)
    btn_frame.grid(row=0, column=0, sticky=tk.N)
    btn_frame.columnconfigure(0, weight=0)

    buttons_config = [
        ("Настройки", None),
        ("Моя почта", "my"),
        ("uneco", "uneco"),
        ("eak", "eak"),
        ("sale", "sale"),
        ("svet1", "svet1"),
        ("sms", "sms"),
        ("autotest", "autotest"),
    ]

    last_result = [""]
    result_label = None

    def set_result(value: str):
        last_result[0] = value or ""
        if result_label:
            result_label.config(text=value or "")
        if value and ui.get("copy_to_clipboard", True):
            copy_to_clipboard(root, value)

    def do_fetch(mode: str):
        if mode == "my":
            if not personal.email or not personal.password:
                set_result("")
                messagebox.showwarning("Настройки", "Укажите личную почту и пароль в настройках.")
                return
            def task():
                return get_auth_code_from_email(
                    recipient_email=personal.email,
                    folder=personal.folder,
                    imap_user=personal.email,
                    imap_password=personal.password,
                    imap_host=imap_host,
                    imap_port=imap_port,
                    subject_contains=PLATFORM_OTP_SUBJECT_MARKERS,
                )
        else:
            if not corporate.email or not corporate.password:
                set_result("")
                messagebox.showwarning("Настройки", "Укажите корпоративную почту и пароль в настройках.")
                return
            if mode == "sms":
                def task():
                    return get_auth_code_from_sms(
                        imap_user=corporate.email,
                        imap_password=corporate.password,
                        imap_host=imap_host,
                        imap_port=imap_port,
                        folder="sms",
                    )
            else:
                folder = mode
                def task():
                    return get_auth_code_from_email(
                        recipient_email=corporate.email,
                        folder=folder,
                        imap_user=corporate.email,
                        imap_password=corporate.password,
                        imap_host=imap_host,
                        imap_port=imap_port,
                        subject_contains=PLATFORM_OTP_SUBJECT_MARKERS,
                    )

        set_result("… ожидание кода …")

        def on_done(res):
            if res is None:
                set_result("(код не найден)")
                if mode == "my":
                    root.after(0, lambda: messagebox.showinfo(
                        "Моя почта",
                        f"В указанной папке «{personal.folder}» не найдено подходящих писем.\n\nПроверьте папку (тема: пароль для входа или код подтверждения почты на Платформе).",
                    ))
                elif mode == "sms":
                    root.after(0, lambda: messagebox.showinfo(
                        "SMS",
                        "В папке «sms» не найдено подходящих писем.\n\nКод берётся из тела письма (тема — номер телефона).",
                    ))
                else:
                    root.after(0, lambda: messagebox.showinfo(
                        "Корпоративная почта",
                        f"В папке «{mode}» не найдено подходящих писем.\n\nПроверьте папку (тема: пароль для входа или код подтверждения почты на Платформе).",
                    ))
            elif isinstance(res, str) and not res.isdigit() and len(res) > 10:
                set_result(f"Ошибка: {res[:200]}")
            else:
                set_result(str(res) if res is not None else "(код не найден)")

        run_in_thread(task, on_done)

    def open_settings():
        _, _, p, c, u = load_imap_config()
        sw = SettingsWindow(root, on_save=apply_after_save)
        sw.load(imap_host, imap_port, p, c, u)
        sw.win.grab_set()

    def make_sep_row(parent, row):
        f = ttk.Frame(parent)
        f.grid(row=row, column=0, sticky=tk.EW, pady=5)
        ttk.Separator(f, orient=tk.HORIZONTAL).pack(fill=tk.X)
        parent.columnconfigure(0, weight=0)

    buttons = []
    row = 0
    for label, mode in buttons_config:
        if mode is None:
            btn = ttk.Button(btn_frame, text=label, command=open_settings)
        else:
            btn = ttk.Button(btn_frame, text=label, command=lambda m=mode: do_fetch(m))
        btn.grid(row=row, column=0, padx=0, pady=2, sticky=tk.EW)
        buttons.append(btn)
        row += 1
        if mode is None:
            make_sep_row(btn_frame, row)
            row += 1

    make_sep_row(btn_frame, row)
    row += 1

    # Результат: блок под кнопками, визуально отделён разделителем, тот же фон
    result_frame = ttk.Frame(center, padding=(8, 0))
    result_frame.grid(row=1, column=0, sticky=tk.NSEW)
    result_frame.columnconfigure(0, weight=1)
    sep_f = ttk.Frame(result_frame)
    sep_f.grid(row=0, column=0, sticky=tk.EW, pady=(5, 5))
    ttk.Separator(sep_f, orient=tk.HORIZONTAL).pack(fill=tk.X)
    style_center = ttk.Style()
    style_center.configure("Center.TLabel", anchor=tk.CENTER)
    result_label = ttk.Label(result_frame, text="", font=("Consolas", 11), padding=(8, 6), style="Center.TLabel")
    result_label.grid(row=1, column=0, sticky=tk.EW)
    result_frame.rowconfigure(1, weight=1)

    copy_btn = ttk.Button(btn_frame, text="Копировать", command=lambda: copy_to_clipboard(root, last_result[0]))
    copy_btn.grid(row=row, column=0, padx=0, pady=3, sticky=tk.EW)
    buttons.append(copy_btn)

    root.mainloop()


if __name__ == "__main__":
    main()
