# main.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import customtkinter as ctk
from backend import KantinManager, Order, OrderItem, Cart
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# Colors
COLOR_BG_MAIN = "#0F172A"
COLOR_SIDEBAR = "#1E293B"
COLOR_CARD = "#334155"
COLOR_PRIMARY = "#3B82F6"
COLOR_SUCCESS = "#10B981"
COLOR_WARNING = "#F59E0B"
COLOR_DANGER = "#EF4444"

# ====================================================
# LOGIN PAGE
# ====================================================
class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Login Sistem - Kantin Digital")
        self.geometry("900x600")
        self.minsize(850, 550)
        self.resizable(True, True)
        self.manager = KantinManager()

        frame = ctk.CTkFrame(self, fg_color=COLOR_CARD)
        frame.pack(expand=True, padx=40, pady=40)

        ctk.CTkLabel(frame, text="Login Admin Kantin", font=("Arial", 22, "bold")).pack(pady=10)

        self.entry_user = ctk.CTkEntry(frame, placeholder_text="Username", width=280)
        self.entry_user.pack(pady=6)

        self.entry_pass = ctk.CTkEntry(frame, placeholder_text="Password", width=280, show="*")
        self.entry_pass.pack(pady=6)

        ctk.CTkButton(frame, text="Login", fg_color=COLOR_PRIMARY, width=200,
                      command=self.try_login).pack(pady=10)

        ctk.CTkButton(frame, text="Masuk Tanpa Login", fg_color=COLOR_SUCCESS, width=200,
                      command=self.guest_mode).pack(pady=5)

    def try_login(self):
        user = self.entry_user.get()
        pwd = self.entry_pass.get()
        if self.manager.cek_login(user, pwd):
            self.destroy()
            app = AplikasiKantin(is_admin=True)
            app.mainloop()
        else:
            messagebox.showerror("Gagal", "Username atau password salah!")

    def guest_mode(self):
        self.destroy()
        app = AplikasiKantin(is_admin=False)
        app.mainloop()


# ====================================================
# MAIN APPLICATION
# ====================================================
class AplikasiKantin(ctk.CTk):
    def __init__(self, is_admin=True):
        super().__init__()
        self.is_admin = is_admin
        role = "Administrator" if is_admin else "Mode Tamu"
        self.title(f"Dashboard {role} - Kantin Digital")
        self.geometry("1200x750")
        self.configure(fg_color=COLOR_BG_MAIN)

        self.manager = KantinManager()

        # === Fitur Baru dari backend ===
        self.cart = Cart()
        self.buyer_name = ""

        # Layout grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ====================================================
        # SIDEBAR
        # ====================================================
        self.sidebar = ctk.CTkFrame(self, width=220, fg_color=COLOR_SIDEBAR, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nswe")

        ctk.CTkLabel(self.sidebar, text="KANTIN DIGITAL",
                     font=("Montserrat", 22, "bold"),
                     text_color=COLOR_PRIMARY).pack(pady=(30, 20))

        self.btn_order = ctk.CTkButton(self.sidebar, text="🛒 Pemesanan",
                                       command=self.show_pemesanan,
                                       width=200, fg_color="transparent", anchor="w")
        self.btn_order.pack(pady=6)

        if self.is_admin:
            self.btn_kelola = ctk.CTkButton(self.sidebar, text="📝 Kelola Menu",
                                            command=self.show_kelola,
                                            width=200, fg_color="transparent", anchor="w")
            self.btn_kelola.pack(pady=6)

            self.btn_riwayat = ctk.CTkButton(self.sidebar, text="📜 Riwayat",
                                             command=self.show_riwayat,
                                             width=200, fg_color="transparent", anchor="w")
            self.btn_riwayat.pack(pady=6)

            self.btn_laporan = ctk.CTkButton(self.sidebar, text="📊 Laporan",
                                             command=self.show_laporan,
                                             width=200, fg_color="transparent", anchor="w")
            self.btn_laporan.pack(pady=6)

        self.dark_var = tk.BooleanVar(value=True)
        ctk.CTkSwitch(self.sidebar, text="Dark Mode",
                      variable=self.dark_var,
                      command=self.toggle_theme).pack(side="bottom", pady=30)

        ctk.CTkButton(self.sidebar, text="Log Out", fg_color=COLOR_DANGER,
                      command=self.logout, width=160).pack(side="bottom", pady=10)

        # main content area
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

        # Instances
        self.frame_pemesanan = None
        self.frame_kelola = None
        self.frame_riwayat = None
        self.frame_laporan = None

        self.show_pemesanan()

    # ====================================================
    # CLEAR MAIN PAGE
    # ====================================================
    def clear_main(self):
        for w in self.main_area.winfo_children():
            w.destroy()

    # ====================================================
    # PEMESANAN PAGE
    # ====================================================
    def show_pemesanan(self):
        self.clear_main()
        frame = ctk.CTkFrame(self.main_area, fg_color=COLOR_CARD, corner_radius=12)
        frame.pack(fill="both", expand=True)

        ctk.CTkLabel(frame, text="Pemesanan", font=("Arial", 18, "bold")).pack(anchor="w", padx=20, pady=10)

        ctrl = ctk.CTkFrame(frame, fg_color="transparent")
        ctrl.pack(fill="x", padx=20)

        search_entry = ctk.CTkEntry(ctrl, placeholder_text="🔍 Cari menu...", width=300)
        search_entry.grid(row=0, column=0, padx=10)

        kat_list = ["Semua"] + list({m.kategori for m in self.manager.get_semua_menu()})
        kat_filter = ctk.CTkComboBox(ctrl, values=kat_list, width=180)
        kat_filter.grid(row=0, column=1, padx=10)
        kat_filter.set("Semua")

        # ====================================================
        # CART PANEL
        # ====================================================
        cart_frame = ctk.CTkFrame(frame, fg_color=COLOR_CARD)
        cart_frame.pack(side="right", fill="y", padx=20, pady=20)

        ctk.CTkLabel(cart_frame, text="Keranjang Belanja",
                     font=("Arial", 15, "bold")).pack(pady=8)

        self.listbox_cart = tk.Listbox(cart_frame, bg=COLOR_SIDEBAR,
                                       fg="white", width=30, font=("Arial", 12))
        self.listbox_cart.pack(pady=6)

        self.label_cart_total = ctk.CTkLabel(cart_frame, text="Total: Rp 0",
                                             font=("Arial", 14, "bold"), text_color=COLOR_SUCCESS)
        self.label_cart_total.pack(pady=10)

        ctk.CTkButton(cart_frame, text="Bersihkan Keranjang",
                      fg_color=COLOR_WARNING,
                      command=self.clear_cart).pack(fill="x", pady=4)

        ctk.CTkButton(cart_frame, text="Checkout",
                      fg_color=COLOR_PRIMARY,
                      command=self.checkout).pack(fill="x", pady=4)

        # ====================================================
        # MENU LIST
        # ====================================================
        canvas = tk.Canvas(frame, bg=COLOR_CARD, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind("<Configure>",
                          lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="left", fill="y")

        # Render function
        def populate_cards(kat="Semua", keyword=""):
            for w in scroll_frame.winfo_children():
                w.destroy()

            menus = self.manager.get_semua_menu()

            if kat != "Semua":
                menus = [m for m in menus if m.kategori == kat]

            if keyword:
                menus = [m for m in menus if keyword.lower() in m.nama.lower()]

            for m in menus:
                card = ctk.CTkFrame(scroll_frame, fg_color="#111827", corner_radius=10)
                card.pack(fill="x", pady=6, padx=10)

                ctk.CTkLabel(card, text=m.nama, font=("Arial", 14, "bold")).grid(
                    row=0, column=0, sticky="w", padx=10, pady=(8, 0))

                ctk.CTkLabel(card, text=f"Rp {m.harga:,}".replace(",", "."),
                             font=("Arial", 12)).grid(row=1, column=0, sticky="w", padx=10)

                ctk.CTkLabel(card, text=f"Stok: {m.stok}",
                             font=("Arial", 11)).grid(row=1, column=1, sticky="e", padx=10)

                qty_spin = tk.Spinbox(card, from_=1, to=max(1, m.stok), width=5)
                qty_spin.grid(row=0, column=1, padx=10)

                def add_to_cart(menu=m, spin=qty_spin):
                    try:
                        qty = int(spin.get())
                    except:
                        qty = 1

                    if qty > menu.stok:
                        messagebox.showerror("Stok Kurang",
                                             f"Stok {menu.nama} tidak cukup.")
                        return

                    self.cart.add(menu, qty)
                    self.refresh_cart()

                ctk.CTkButton(card, text="Tambah",
                              command=add_to_cart,
                              fg_color=COLOR_PRIMARY, width=80).grid(
                                  row=0, column=2, rowspan=2, padx=10, pady=10)

        populate_cards()

        search_entry.bind("<KeyRelease>",
                          lambda e: populate_cards(kat_filter.get(), search_entry.get()))
        kat_filter.configure(
            command=lambda v: populate_cards(v, search_entry.get())
        )

        self.frame_pemesanan = frame

    # ====================================================
    # CART FUNCTIONS
    # ====================================================
    def refresh_cart(self):
        self.listbox_cart.delete(0, "end")

        for item in self.cart.items:
            self.listbox_cart.insert(
                "end",
                f"{item.menu_item.nama} x{item.qty} = Rp {item.subtotal:,}".replace(",", ".")
            )

        self.label_cart_total.configure(
            text=f"Total: Rp {self.cart.total:,}".replace(",", ".")
        )

    def clear_cart(self):
        if messagebox.askyesno("Konfirmasi", "Kosongkan keranjang?"):
            self.cart.clear()
            self.refresh_cart()

    def checkout(self):
        if not self.cart.items:
            messagebox.showwarning("Kosong", "Keranjang masih kosong.")
            return

        buyer = simpledialog.askstring("Nama Pembeli", "Masukkan nama pembeli:")
        if not buyer:
            return

        hasil = self.manager.proses_checkout(buyer, self.cart)

        if isinstance(hasil, str):
            messagebox.showerror("Gagal", hasil)
            return

        order = hasil
        struk = self.manager.generate_struk(order)

        messagebox.showinfo("Sukses", f"Order berhasil!\n\n{struk}")

        self.cart.clear()
        self.refresh_cart()
        self.show_pemesanan()

    # ====================================================
    # PAGE: KELOLA MENU
    # ====================================================
    def show_kelola(self):
        self.clear_main()
        frame = ctk.CTkFrame(self.main_area, fg_color=COLOR_CARD)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="Kelola Menu",
                     font=("Arial", 18, "bold")).pack(anchor="w", padx=20, pady=10)

        tree = ttk.Treeview(frame, columns=("harga", "kategori", "stok"), show="headings")
        tree.heading("harga", text="Harga")
        tree.heading("kategori", text="Kategori")
        tree.heading("stok", text="Stok")
        tree.pack(fill="both", expand=True, padx=20, pady=10)

        for m in self.manager.get_semua_menu():
            tree.insert("", "end", iid=m.nama,
                        values=(m.harga, m.kategori, m.stok))

        def tambah():
            nama = simpledialog.askstring("Nama", "Masukkan nama menu:")
            harga = simpledialog.askinteger("Harga", "Masukkan harga:")
            kategori = simpledialog.askstring("Kategori", "Masukkan kategori:")
            stok = simpledialog.askinteger("Stok", "Masukkan stok awal:")
            if nama and harga and kategori and stok is not None:
                self.manager.tambah_menu(nama, harga, kategori, stok)
                self.manager.export_ke_csv()
                self.show_kelola()

        def edit():
            selected = tree.focus()
            if not selected:
                return
            m = next((x for x in self.manager.daftar_menu if x.nama == selected), None)
            if not m:
                return

            nama_baru = simpledialog.askstring("Nama Baru", "Nama Baru:", initialvalue=m.nama)
            harga_baru = simpledialog.askinteger("Harga Baru", "Harga Baru:", initialvalue=m.harga)
            kategori_baru = simpledialog.askstring("Kategori Baru", "Kategori Baru:", initialvalue=m.kategori)
            stok_baru = simpledialog.askinteger("Stok Baru", "Stok Baru:", initialvalue=m.stok)

            if nama_baru and harga_baru and kategori_baru and stok_baru is not None:
                self.manager.edit_menu(m.nama, nama_baru, harga_baru, kategori_baru, stok_baru)
                self.manager.export_ke_csv()
                self.show_kelola()

        def hapus():
            selected = tree.focus()
            if selected and messagebox.askyesno("Hapus", "Hapus menu ini?"):
                self.manager.hapus_menu(selected)
                self.manager.export_ke_csv()
                self.show_kelola()

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="Tambah Menu", fg_color=COLOR_PRIMARY,
                      command=tambah).grid(row=0, column=0, padx=10)
        ctk.CTkButton(btn_frame, text="Edit", fg_color=COLOR_WARNING,
                      command=edit).grid(row=0, column=1, padx=10)
        ctk.CTkButton(btn_frame, text="Hapus", fg_color=COLOR_DANGER,
                      command=hapus).grid(row=0, column=2, padx=10)

        self.frame_kelola = frame

    # ====================================================
    # PAGE: RIWAYAT ORDER
    # ====================================================
    def show_riwayat(self):
        self.clear_main()
        frame = ctk.CTkFrame(self.main_area, fg_color=COLOR_CARD)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="Riwayat Transaksi",
                     font=("Arial", 18, "bold")).pack(anchor="w", padx=20, pady=10)

        tree = ttk.Treeview(frame, columns=("waktu", "nama", "total"), show="headings")
        tree.heading("waktu", text="Waktu")
        tree.heading("nama", text="Pembeli")
        tree.heading("total", text="Total")
        tree.pack(fill="both", expand=True, padx=20, pady=20)

        for o in self.manager.get_orders_history():
            tree.insert("", "end",
                        values=(o.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                                o.buyer_name, f"Rp {o.total:,}".replace(",", ".")))

        self.frame_riwayat = frame

    # ====================================================
    # PAGE: LAPORAN
    # ====================================================
    def show_laporan(self):
        self.clear_main()
        frame = ctk.CTkFrame(self.main_area, fg_color=COLOR_CARD)
        frame.pack(fill="both", expand=True)

        ctk.CTkLabel(frame, text="Laporan Penjualan",
                     font=("Arial", 20, "bold")).pack(pady=20)

        ringkas = self.manager.ringkasan_laporan()

        info = ctk.CTkFrame(frame, fg_color="#1E293B")
        info.pack(fill="x", padx=40, pady=10)

        ctk.CTkLabel(info, text=f"Total Menu: {ringkas['total_menu']}",
                     font=("Arial",14)).pack(pady=5)
        ctk.CTkLabel(info, text=f"Total Transaksi: {ringkas['total_orders']}",
                     font=("Arial",14)).pack(pady=5)
        ctk.CTkLabel(info, text=f"Total Pendapatan: Rp {ringkas['total_revenue']:,}".replace(",", "."),
                     font=("Arial",14)).pack(pady=5)

        # Grafik kategori menu
        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)

        kategori = list(ringkas["menu_per_kategori"].keys())
        jumlah = list(ringkas["menu_per_kategori"].values())

        ax.bar(kategori, jumlah)
        ax.set_title("Jumlah Menu per Kategori")

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=20)

        self.frame_laporan = frame

    # ====================================================
    # THEME + LOGOUT
    # ====================================================
    def toggle_theme(self):
        if self.dark_var.get():
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")

    def logout(self):
        self.destroy()
        LoginWindow().mainloop()


# ====================================================
# RUN APP
# ====================================================
if __name__ == "__main__":
    LoginWindow().mainloop()
