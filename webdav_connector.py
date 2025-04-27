# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import subprocess
import os
import sys
import json

from pathlib import Path
import locale

# Konfigurationsdateien
ENV_FILE = "pfade.env"
HISTORY_FILE = "history.json"
MAX_HISTORY = 10

# Sicherstellen, dass stdout auf UTF-8 gestellt ist (für Konsolenausgaben)
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    # Python < 3.7 unterstützt reconfigure nicht
    pass

# Optional: Windows Konsole auf UTF-8 schalten
if os.name == 'nt':
    os.system('chcp 65001')

# WebDAV-Pfade laden
def validate_env_file(filename):
    env_path = Path(filename)
    if not env_path.exists():
        raise FileNotFoundError(f"Die Datei '{filename}' wurde nicht gefunden.")

    with open(env_path, "r", encoding="utf-8") as file:
        for lineno, line in enumerate(file, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue  # Kommentare und leere Zeilen ignorieren
            if '=' not in line:
                raise ValueError(f"Fehler in Zeile {lineno}: Kein '=' gefunden.")
            key, value = line.split('=', 1)
            key = key.strip()
            if ' ' in key:
                raise ValueError(f"Fehler in Zeile {lineno}: Schlüssel '{key}' enthält Leerzeichen.")
            if not key.isidentifier():
                raise ValueError(f"Fehler in Zeile {lineno}: Ungültiger Schlüssel '{key}'. Nur Buchstaben, Zahlen, Unterstrich erlaubt.")

try:
    validate_env_file(ENV_FILE)
    from dotenv import dotenv_values
    pfade = dotenv_values(ENV_FILE)
except Exception as e:
    messagebox.showerror("Fehler beim Einlesen der .env-Datei", f"{str(e)}\n\nBitte prüfen Sie die Datei '{ENV_FILE}'!")
    sys.exit(1)

# History laden
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)
else:
    history = []

def save_history(config):
    if config not in history:
        history.insert(0, config)
    if len(history) > MAX_HISTORY:
        history.pop()
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

def get_active_drives():
    result = subprocess.run(
        ["net", "use"],
        capture_output=True,
        text=True,
        shell=True,
        encoding=locale.getpreferredencoding(False),
        errors="replace"
    )
    active = {}
    if result.stdout:
        lines = result.stdout.splitlines()
        for line in lines:
            line = line.strip()
            if line and ':' in line and ('\\' in line or '@SSL' in line):
                parts = line.split()
                if len(parts) >= 3 and parts[1].endswith(":"):
                    laufwerk = parts[1][:-1]
                    pfad = parts[2]
                    active[laufwerk] = pfad
    return active

def freie_laufwerksbuchstaben():
    alle = {chr(i) for i in range(68, 91)}  # D-Z
    belegt = set(get_active_drives().keys())
    return sorted(alle - belegt)

def verbinden(name, pfad, laufwerk, use_login_flag):
    active_drives = get_active_drives()
    if laufwerk in active_drives:
        messagebox.showerror("Fehler", f"Laufwerk {laufwerk}: ist bereits belegt!")
        return
    if not pfad.startswith("\\\\"):
        messagebox.showerror("Fehler", f"Ungültiger Pfad: {pfad}")
        return
    try:
        if use_login_flag:
            user = simpledialog.askstring("Benutzername eingeben", f"Benutzername für Verbindung '{name}' eingeben:")
            pw = simpledialog.askstring("Passwort eingeben", f"Passwort für Verbindung '{name}' eingeben:", show='*')
            if not user or not pw:
                messagebox.showerror("Fehler", "Benutzername und Passwort erforderlich!")
                return
            cmd = ['net', 'use', f'{laufwerk}:', pfad, '/user:' + user, pw]
        else:
            cmd = ['net', 'use', f'{laufwerk}:', pfad]

        subprocess.check_call(cmd, shell=True)
        messagebox.showinfo("Erfolg", f"Verbindung zu {name} auf {laufwerk}: hergestellt!")
        save_history({"name": name, "pfad": pfad, "laufwerk": laufwerk, "use_login": use_login_flag})
        refresh_history()
        update_laufwerke()
    except subprocess.CalledProcessError:
        messagebox.showerror("Fehler", f"Verbindung zu {pfad} fehlgeschlagen!")

def alle_verbindungen_trennen():
    active = get_active_drives()
    if not active:
        messagebox.showinfo("Info", "Es sind keine aktiven Verbindungen vorhanden.")
        return
    for laufwerk in list(active.keys()):
        try:
            subprocess.check_call(['net', 'use', f'{laufwerk}:', '/delete', '/yes'], shell=True)
        except subprocess.CalledProcessError:
            pass
    messagebox.showinfo("Erfolg", "Alle aktiven Verbindungen wurden getrennt.")
    update_laufwerke()

def neue_verbindung():
    new_window = tk.Toplevel(root)
    new_window.title("Neue Verbindung herstellen")
    new_window.geometry("600x300")

    ttk.Label(new_window, text="Pfad auswählen:").pack(pady=5)
    pfad_var = tk.StringVar(new_window)

    # Liste aller vergebenen Pfade aus der gespeicherten History
    vergebene_pfade = {entry['pfad'] for entry in history}

    # Nur Pfade anzeigen, die NICHT in der History sind
    freie_pfade = {key: value for key, value in pfade.items() if value not in vergebene_pfade}

    if not freie_pfade:
        messagebox.showinfo("Info", "Alle Pfade sind bereits einer Verbindung zugeordnet!")
        new_window.destroy()
        return

    anzeigeeintraege = [f"{key} ➔ {value}" for key, value in freie_pfade.items()]
    pfad_dropdown = ttk.Combobox(new_window, textvariable=pfad_var, values=anzeigeeintraege, state="readonly", width=80)
    pfad_dropdown.pack(pady=5)

    ttk.Label(new_window, text="Freier Laufwerksbuchstabe wählen:").pack(pady=5)
    laufwerk_var = tk.StringVar(new_window)
    freie_lw = freie_laufwerksbuchstaben()
    laufwerk_dropdown = ttk.Combobox(new_window, textvariable=laufwerk_var, values=freie_lw, state="readonly")
    laufwerk_dropdown.pack(pady=5)
    if freie_lw:
        laufwerk_dropdown.set(freie_lw[0])

    use_login = tk.BooleanVar()
    ttk.Checkbutton(new_window, text="Benutzername/Passwort verwenden", variable=use_login).pack(pady=5)

    def verbinde():
        if pfad_var.get() and laufwerk_var.get():
            gewaehlt = pfad_var.get()
            name = gewaehlt.split(" ➔ ")[0]
            pfad_sel = freie_pfade[name]
            verbinden(name, pfad_sel, laufwerk_var.get(), use_login.get())
            new_window.destroy()
        else:
            messagebox.showerror("Fehler", "Bitte Pfad und Laufwerksbuchstabe auswählen!")

    ttk.Button(new_window, text="Verbinden", command=verbinde).pack(pady=10)

def verbindung_loeschen():
    selected_indices = history_listbox.curselection()
    if not selected_indices:
        messagebox.showerror("Fehler", "Bitte eine oder mehrere Verbindungen auswählen!")
        return
    for idx in reversed(selected_indices):
        eintrag = history[idx]
        laufwerk = eintrag.get("laufwerk")
        active_drives = get_active_drives()
        if laufwerk and laufwerk in active_drives:
            try:
                subprocess.check_call(['net', 'use', f'{laufwerk}:', '/delete', '/yes'], shell=True)
            except subprocess.CalledProcessError:
                pass
        del history[idx]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)
    refresh_history()
    update_laufwerke()

def verbindung_aktivieren():
    selected_indices = history_listbox.curselection()
    if not selected_indices:
        messagebox.showerror("Fehler", "Bitte eine oder mehrere Verbindungen auswählen!")
        return
    for idx in selected_indices:
        eintrag = history[idx]
        verbinden(
            eintrag['name'],
            eintrag['pfad'],
            eintrag['laufwerk'],
            eintrag.get('use_login', True)  # fallback: True
        )

def alle_verbindungen_aktivieren():
    if not history:
        messagebox.showerror("Fehler", "Keine gespeicherten Verbindungen vorhanden!")
        return
    for eintrag in history:
        verbinden(
            eintrag['name'],
            eintrag['pfad'],
            eintrag['laufwerk'],
            eintrag.get('use_login', True)  # fallback: True
        )
    messagebox.showinfo("Erfolg", "Alle Verbindungen wurden aktiviert!")

def verbindung_deaktivieren():
    selected_indices = history_listbox.curselection()
    if not selected_indices:
        messagebox.showerror("Fehler", "Bitte eine oder mehrere Verbindungen auswählen!")
        return
    active_drives = get_active_drives()
    for idx in selected_indices:
        eintrag = history[idx]
        laufwerk = eintrag.get('laufwerk')
        if laufwerk and laufwerk in active_drives:
            try:
                subprocess.check_call(['net', 'use', f'{laufwerk}:', '/delete', '/yes'], shell=True)
            except subprocess.CalledProcessError:
                pass
    update_laufwerke()

def beenden():
    root.destroy()

def refresh_history():
    history_listbox.delete(0, tk.END)
    for entry in history:
        history_listbox.insert(tk.END, f"{entry['laufwerk']}: {entry['name']} ({entry['pfad']})")

def update_laufwerke():
    laufwerke_text.configure(state="normal")
    laufwerke_text.delete(1.0, tk.END)
    active = get_active_drives()
    for lw, pfad in active.items():
        laufwerke_text.insert(tk.END, f"{lw}: {pfad}\n")
    laufwerke_text.configure(state="disabled")

# GUI Aufbau
root = tk.Tk()
root.title("WebDAV Connector")
root.geometry("800x750")

try:
    root.iconbitmap("icon.ico")
except Exception:
    pass  # Falls Icon fehlt, ignorieren

frame = ttk.Frame(root, padding=20)
frame.pack(fill="both", expand=True)

# Letzte Konfigurationen
ttk.Label(frame, text="Letzte Verbindungen:").pack(pady=5)
history_listbox = tk.Listbox(frame, height=10, selectmode="extended")
history_listbox.pack(fill="both", expand=True, pady=5)
refresh_history()

# Buttons logisch sortiert
ttk.Button(frame, text="Neue Verbindung herstellen", command=neue_verbindung).pack(pady=5)
ttk.Button(frame, text="Alle Verbindungen aktivieren", command=alle_verbindungen_aktivieren).pack(pady=5)
ttk.Button(frame, text="Ausgewählte Verbindungen aktivieren", command=verbindung_aktivieren).pack(pady=5)
ttk.Button(frame, text="Ausgewählte Verbindungen deaktivieren", command=verbindung_deaktivieren).pack(pady=5)
ttk.Button(frame, text="Ausgewählte Verbindungen löschen", command=verbindung_loeschen).pack(pady=5)
ttk.Button(frame, text="Alle aktiven Verbindungen deaktivieren", command=alle_verbindungen_trennen).pack(pady=5)
ttk.Button(frame, text="Aktualisieren", command=update_laufwerke).pack(pady=5)
ttk.Button(frame, text="Beenden", command=beenden).pack(pady=10)

# Aktive Laufwerke
ttk.Label(frame, text="Aktive Laufwerke:").pack(pady=5)
laufwerke_text = tk.Text(frame, height=7, state="normal")
laufwerke_text.pack(fill="both", expand=True, pady=5)

update_laufwerke()

root.mainloop()
