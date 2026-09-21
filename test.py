import customtkinter as ctk

# Inicializácia aplikácie
app = ctk.CTk()
app.title("Výber z možností")
app.geometry("400x350")

# Zoznam možností pre naše menu
ovocie_moznosti = ["Jablko", "Banan", "Pomaranc", "Jahoda"]

# 1. FUNKCIA PRE CTkOptionMenu
def zmena_option_menu(vybrana_moznost):
    label_option.configure(text=f"Z OptionMenu vybrané: {vybrana_moznost}")

# 2. FUNKCIA PRE CTkComboBox
def zmena_combo_box(vybrana_moznost):
    label_combo.configure(text=f"Z ComboBoxu vybrané: {vybrana_moznost}")

# --- SEKCIA 1: CTkOptionMenu ---
label_title1 = ctk.CTkLabel(app, text="CTkOptionMenu (Iba pevný výber):", font=("Arial", 12, "bold"))
label_title1.pack(pady=(20, 5))

option_menu = ctk.CTkOptionMenu(
    app, 
    values=ovocie_moznosti, 
    command=zmena_option_menu
)
option_menu.pack(pady=5)
option_menu.set("Vyber si ovocie") # Nastaví predvolený text

label_option = ctk.CTkLabel(app, text="Zatiaľ nič nevybrané", font=("Arial", 11, "italic"))
label_option.pack(pady=(0, 20))


# --- SEKCIA 2: CTkComboBox ---
label_title2 = ctk.CTkLabel(app, text="CTkComboBox (Výber alebo vlastné dopísanie):", font=("Arial", 12, "bold"))
label_title2.pack(pady=(10, 5))

combo_box = ctk.CTkComboBox(
    app, 
    values=ovocie_moznosti, 
    command=zmena_combo_box
)
combo_box.pack(pady=5)
combo_box.set("Napíš alebo vyber") # Nastaví predvolený text

label_combo = ctk.CTkLabel(app, text="Zatiaľ nič nevybrané", font=("Arial", 11, "italic"))
label_combo.pack(pady=(0, 20))


# Spustenie aplikácie
app.mainloop()
