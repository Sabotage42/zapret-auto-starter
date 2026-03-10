import os
import sys
import subprocess
import winreg
import glob

AUTOSTART_NAME = "ZapretAutoStarter"

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def find_bat_files():
    base = get_base_path()
    pattern = os.path.join(base, "general*.bat")
    return glob.glob(pattern)

def choose_bat(bat_files):
    if not bat_files:
        return None
    if len(bat_files) == 1:
        return bat_files[0]
    print("Найдено несколько батников:")
    for i, f in enumerate(bat_files, 1):
        print(f"{i}. {os.path.basename(f)}")
    while True:
        try:
            choice = int(input("Выбери номер (или 0 для отмены): "))
            if choice == 0:
                return None
            if 1 <= choice <= len(bat_files):
                return bat_files[choice-1]
            else:
                print("Неверный номер.")
        except ValueError:
            print("Введи число.")

def is_admin():
    try:
        return os.getuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

def add_to_startup():
    script_path = os.path.abspath(sys.argv[0])
    python_dir = os.path.dirname(sys.executable)
    pythonw_path = os.path.join(python_dir, "pythonw.exe")
    if not os.path.exists(pythonw_path):
        pythonw_path = sys.executable
    command = f'"{pythonw_path}" "{script_path}"'
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Run",
                             0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, AUTOSTART_NAME, 0, winreg.REG_SZ, command)
        winreg.CloseKey(key)
        print("✅ Программа добавлена в автозагрузку")
    except Exception as e:
        print(f"❌ Ошибка автозагрузки: {e}")

def run_bat(bat_path):
    try:
        subprocess.Popen(
            [bat_path],
            shell=True,
            creationflags=subprocess.CREATE_NO_WINDOW,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print(f"✅ Запущен: {os.path.basename(bat_path)}")
        return True
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        return False

def main():
    print("=== Zapret Auto Starter ===")
    bat_files = find_bat_files()
    if not bat_files:
        print("❌ Нет файлов general*.bat в папке с программой")
        input("Нажми Enter...")
        return
    selected = choose_bat(bat_files)
    if not selected:
        print("Выход.")
        input("Нажми Enter...")
        return
    print(f"Выбран: {os.path.basename(selected)}")
    if not is_admin():
        print("⚠️ Рекомендуется запуск от администратора")
    add_to_startup()
    run_bat(selected)
    print("✅ Готово. При следующем входе запустится автоматически.")
    input("Нажми Enter...")

if __name__ == "__main__":
    main()