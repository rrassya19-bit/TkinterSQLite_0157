import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
DB_NAME = "prediksi_diabetes.db"

def run_query(sql, params=()):
    conn = sqlite3.connect(DB_NAME)
    try:
        with conn:
            return conn.execute(sql, params).fetchall()
    finally:
        conn.close()

def init_db():
    run_query(
        """CREATE TABLE IF NOT EXISTS pasien (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama_pasien TEXT NOT NULL, 
        usia INTEGER, gula_darah INTEGER,
        bmi REAL, 
        riwayat_ortu TEXT, 
        hasil_prediksi TEXT
        )"""
    )

def add_pasien(nama, usia, gula, bmi, riwayat, hasil):
    run_query("INSERT INTO pasien (nama_pasien, usia, gula_darah, bmi, riwayat_ortu, hasil_prediksi) VALUES (?, ?, ?, ?, ?, ?)",
              (nama, usia, gula, bmi, riwayat, hasil))

def get_pasien():
    return run_query("SELECT id, nama_pasien, usia, gula_darah, bmi, riwayat_ortu, hasil_prediksi FROM pasien ORDER BY id")

def hitung_risiko(gula, bmi, riwayat):
    if gula >= 200:
        if riwayat == "Ya":
            return "Sangat Tinggi"
        else:
            return "Tinggi"
    elif gula >= 140:
        if bmi >= 30 or riwayat == "Ya":
            return "Tinggi"
        else:
            return "Sedang"
    else:
        if bmi >= 30:
            if riwayat == "Ya":
                return "Sedang"
            else:
                return "Waspada"
        else:
            if riwayat == "Ya":
                return "Waspada"
            else:
                return "Rendah"

def read_form():
    nama = entries["Nama"].get().strip()
    usia = entries["Usia"].get().strip()
    gula = entries["Gula Darah"].get().strip()
    bmi = entries["BMI"].get().strip()
    bmi = bmi.replace(",", ".")
    riwayat = combo_riwayat.get()
    if not nama or not usia or not gula or not bmi or not riwayat:
        messagebox.showwarning("Missing data", "Semua data harus diisi.")
        return None
    if not nama.replace(" ", "").isalpha():
        messagebox.showwarning("Invalid name", "Nama hanya boleh berisi huruf.")
        return None
    if not usia.isdigit() or int(usia) < 1 or int(usia) > 120:
        messagebox.showwarning("Invalid age", "Usia harus angka 1 sampai 120.")
        return None
    if not gula.isdigit() or int(gula) < 20 or int(gula) > 600:
        messagebox.showwarning("Invalid glucose", "Gula darah harus angka 20 sampai 600 mg/dL.")
        return None
    if not bmi.replace(".", "", 1).isdigit() or float(bmi) < 10 or float(bmi) > 60:
        messagebox.showwarning("Invalid BMI", "BMI harus angka 10 sampai 60.")
        return None
    return nama, int(usia), int(gula), float(bmi), riwayat

def on_prediksi():
    data = read_form()
    if data:
        nama, usia, gula, bmi, riwayat = data
        hasil = hitung_risiko(gula, bmi, riwayat)
        add_pasien(nama, usia, gula, bmi, riwayat, hasil)
        label_hasil.config(text="Risiko Diabetes: " + hasil, fg=warna[hasil])
        clear_form()

def refresh():
    tree.delete(*tree.get_children())
    for row in get_pasien():
        tree.insert("", tk.END, values=row)

def clear_form():
    for e in entries.values():
        e.delete(0, tk.END)
    combo_riwayat.set("")

warna = {"Rendah": "#15803d", "Waspada": "#a16207", "Sedang": "#c2410c",
         "Tinggi": "#dc2626", "Sangat Tinggi": "#7f1d1d"}

init_db()
root = tk.Tk()
root.title("Prediksi Risiko Diabetes")

# ===== Style =====
BG = "#eef2f7"
CARD = "#ffffff"
BORDER = "#d8e0ea"
TEXT = "#1f2937"
MUTED = "#64748b"
ACCENT = "#0f766e"
FONT = ("Segoe UI", 10)

root.configure(bg=BG)
root.resizable(False, False)
W, H = 1000, 730
X = (root.winfo_screenwidth() - W) // 2
Y = max(0, (root.winfo_screenheight() - H) // 2)
root.geometry(f"{W}x{H}+{X}+{Y}")
root.option_add("*TCombobox*Listbox.font", "Segoe UI 10")

style = ttk.Style(root)
style.theme_use("clam")
style.configure("TCombobox", font=FONT, padding=6, fieldbackground=CARD,
                background=CARD, foreground=TEXT, arrowcolor=ACCENT,
                bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER)
style.map("TCombobox", fieldbackground=[("readonly", CARD)],
          selectbackground=[("readonly", CARD)], selectforeground=[("readonly", TEXT)])
style.configure("Treeview", font=FONT, rowheight=30, background=CARD,
                fieldbackground=CARD, foreground=TEXT, borderwidth=0)
style.map("Treeview", background=[("selected", "#ccfbf1")],
          foreground=[("selected", "#0f172a")])
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"),
                background=ACCENT, foreground="white", relief="flat", padding=8)
style.map("Treeview.Heading", background=[("active", "#115e59")])
style.configure("Vertical.TScrollbar", background="#cbd5e1", troughcolor=CARD,
                bordercolor=CARD, arrowcolor=MUTED, width=14)

# ===== Layout =====
tk.Label(root, text="Prediksi Risiko Diabetes", font=("Segoe UI", 20, "bold"),
         bg=BG, fg=ACCENT).pack(pady=(20, 12))

main = tk.Frame(root, bg=BG)
main.pack(fill="both", expand=True, padx=30, pady=(0, 20))

form = tk.Frame(main, bg=CARD, highlightthickness=1, highlightbackground=BORDER,
                padx=28, pady=16)
form.pack(fill="x")
form.grid_columnconfigure(1, weight=1)

entries = {}
fields = ["Nama", "Usia", "Gula Darah", "BMI"]
teks = ["Nama Pasien", "Usia (tahun)", "Gula Darah (mg/dL)", "BMI (contoh: 24.5)"]
for i, field in enumerate(fields):
    tk.Label(form, text=teks[i], font=FONT, bg=CARD, fg=TEXT,
             anchor="w").grid(row=i, column=0, sticky="w", padx=(0, 20), pady=7)
    entries[field] = tk.Entry(form, width=34, font=FONT, bg="#f8fafc", fg=TEXT,
                              relief="flat", highlightthickness=1,
                              highlightbackground=BORDER, highlightcolor=ACCENT,
                              insertbackground=TEXT, selectbackground=ACCENT,
                              selectforeground="white")
    entries[field].grid(row=i, column=1, sticky="ew", pady=7, ipady=5)

tk.Label(form, text="Riwayat Diabetes Orang Tua", font=FONT, bg=CARD, fg=TEXT,
         anchor="w").grid(row=4, column=0, sticky="w", padx=(0, 20), pady=7)
combo_riwayat = ttk.Combobox(form, values=["Ya", "Tidak"], state="readonly", width=32, font=FONT)
combo_riwayat.grid(row=4, column=1, sticky="ew", pady=7)

btns = tk.Frame(form, bg=CARD)
btns.grid(row=5, column=0, columnspan=2, pady=(14, 6))
tombol_gaya = [("#0f766e", "white", "#0d9488"), ("#e2e8f0", "#0f172a", "#cbd5e1"),
               ("#e2e8f0", "#0f172a", "#cbd5e1")]
for i, (text, cmd) in enumerate([("Prediksi", on_prediksi), ("Lihat Data", refresh),
                                 ("Clear", clear_form)]):
    bg_tombol, fg_tombol, bg_aktif = tombol_gaya[i]
    tk.Button(btns, text=text, width=12, command=cmd, font=("Segoe UI", 10, "bold"),
              bg=bg_tombol, fg=fg_tombol, activebackground=bg_aktif,
              activeforeground=fg_tombol, relief="flat", bd=0, cursor="hand2",
              padx=8, pady=6).pack(side="left", padx=5)

label_hasil = tk.Label(form, text="Hasil prediksi akan tampil di sini",
                       font=("Segoe UI", 13, "bold"), bg=CARD, fg=MUTED)
label_hasil.grid(row=6, column=0, columnspan=2, pady=(12, 2))

tabel = tk.Frame(main, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
tabel.pack(fill="both", expand=True, pady=(14, 0))
tabel.grid_rowconfigure(0, weight=1)
tabel.grid_columnconfigure(0, weight=1)

cols = ("id", "nama_pasien", "usia", "gula_darah", "bmi", "riwayat_ortu", "hasil_prediksi")
tree = ttk.Treeview(tabel, columns=cols, show="headings", height=8)
for c in cols:
    tree.heading(c, text=c.replace("_", " ").title())
    tree.column(c, width=100, anchor="center")
tree.column("id", width=55)
tree.column("nama_pasien", width=165, anchor="w")
scroll = ttk.Scrollbar(tabel, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scroll.set)
tree.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=10)
scroll.grid(row=0, column=1, sticky="ns", padx=(2, 8), pady=10)

root.mainloop()
