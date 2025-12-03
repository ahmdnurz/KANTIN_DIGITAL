# main.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import customtkinter as ctk
from backend import KantinManager, Order, OrderItem
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")
# KONSTANTA
# Colors
COLOR_BG_MAIN = "#0F172A"
COLOR_SIDEBAR = "#1E293B"
COLOR_CARD = "#334155"
COLOR_PRIMARY = "#3B82F6"
COLOR_SUCCESS = "#10B981"
COLOR_WARNING = "#F59E0B"
COLOR_DANGER = "#EF4444"
#VARIABEL LOGIN(MENYIMPANDATA LOGIN)
# --------------- Login Window ---------------
#OPP(LOGIN WINDOW)
class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Login Sistem - Kantin Digital")
        self.geometry("900x600")
        self.minsize(850, 550)
        self.resizable(True, True)
        self.manager = KantinManager()

        # ================= GRID UTAMA (PENTING) =================
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # =========== LEFT Branding Panel ===========
        left = ctk.CTkFrame(self, fg_color=COLOR_PRIMARY, corner_radius=0)
        left.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(left, text="KANTIN\nDIGITAL",
                     font=("Montserrat", 32, "bold"),
                     justify="center",
                     text_color="white").pack(pady=(120, 20))

        ctk.CTkLabel(left, text="Sistem Manajemen\nMenu & Order",
                     font=("Roboto", 14),
                     text_color="#DBEAFE").pack()

        ctk.CTkLabel(left,
                     text="Created by Kelompok 3 & 4\nTeknik Komputer 2025",
                     font=("Arial", 10),
                     text_color="#DBEAFE").pack(side="bottom", pady=30)

        # =========== RIGHT Form Panel ===========
        right = ctk.CTkFrame(self, fg_color=COLOR_BG_MAIN, corner_radius=0)
        right.grid(row=0, column=1, sticky="nsew")

        # membuat form berada di tengah vertikal & horizontal
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(0, weight=1)

        box = ctk.CTkFrame(right, fg_color="transparent")
        box.grid(row=0, column=0)

        # ========== Isi Kotak Login ==========
        ctk.CTkLabel(box, text="LOGIN ADMIN",
                     font=("Arial", 20, "bold"),
                     text_color="white").pack(pady=(0, 20))

        self.entry_user = ctk.CTkEntry(box, placeholder_text="Username",
                                       width=260, height=40)
        self.entry_user.pack(pady=10)

        self.entry_pass = ctk.CTkEntry(box, placeholder_text="Password",
                                       show="•", width=260, height=40)
        self.entry_pass.pack(pady=10)

        ctk.CTkButton(box, text="LOGIN",
                      command=self.aksi_login,
                      width=260, height=40,
                      fg_color=COLOR_PRIMARY).pack(pady=20)

        ctk.CTkButton(box, text="Lihat Menu Saja (Tamu)",
                      command=self.masuk_tamu,
                      width=260,
                      fg_color="transparent",
                      border_width=1,
                      text_color="white").pack(pady=5)

        ctk.CTkLabel(box, text="Silahkan login",
                     text_color="gray").pack()

        # Enter untuk login
        self.bind('<Return>', lambda e: self.aksi_login())

    # =================== LOGIN FUNCTION ===================    
    def aksi_login(self):
        if self.manager.cek_login(self.entry_user.get(), self.entry_pass.get()):
            self.destroy()
            buka_aplikasi_utama(is_admin=True)
        else:
            messagebox.showerror("Akses Ditolak", "Username atau Password salah!")

    def masuk_tamu(self):
        self.destroy()
        buka_aplikasi_utama(is_admin=False)
#VARIABEL CLASS(MENYIMOAN DATA APLIKASI)
# --------------- Main App ---------------
class AplikasiKantin(ctk.CTk):
    def __init__(self, is_admin=True):
        super().__init__()
        self.is_admin = is_admin
        role = "Administrator" if is_admin else "Mode Tamu"
        self.title(f"Dashboard {role} - Kantin Digital")
        self.geometry("1200x750")
        self.configure(fg_color=COLOR_BG_MAIN)
#ARRAY
        self.manager = KantinManager()
        self.keranjang = []  # list of dict {menu:MenuItem, qty:int}
        self.buyer_name = ""

        # grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # sidebar
        self.sidebar = ctk.CTkFrame(self, width=220, fg_color=COLOR_SIDEBAR, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nswe")
        ctk.CTkLabel(self.sidebar, text="KANTIN", font=("Montserrat", 22, "bold"), text_color=COLOR_PRIMARY).pack(pady=(30,10))
        self.btn_order = ctk.CTkButton(self.sidebar, text="🛒 Pemesanan", command=self.show_pemesanan, width=200, fg_color="transparent", anchor="w")
        self.btn_order.pack(pady=6)
        if self.is_admin:
            self.btn_kelola = ctk.CTkButton(self.sidebar, text="📝 Kelola Menu", command=self.show_kelola, width=200, fg_color="transparent", anchor="w")
            self.btn_kelola.pack(pady=6)
            self.btn_riwayat = ctk.CTkButton(self.sidebar, text="📜 Riwayat", command=self.show_riwayat, width=200, fg_color="transparent", anchor="w")
            self.btn_riwayat.pack(pady=6)
            self.btn_laporan = ctk.CTkButton(self.sidebar, text="📊 Laporan", command=self.show_laporan, width=200, fg_color="transparent", anchor="w")
            self.btn_laporan.pack(pady=6)
        # theme switch
        self.dark_var = tk.BooleanVar(value=True)
        self.switch = ctk.CTkSwitch(self.sidebar, text="Dark Mode", command=self.toggle_theme, variable=self.dark_var)
        self.switch.pack(side="bottom", pady=30)

        ctk.CTkButton(self.sidebar, text="Log Out", command=self.logout, fg_color=COLOR_DANGER, width=160).pack(side="bottom", pady=10)

        # main area
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

        # container frames for pages
        self.frame_pemesanan = None
        self.frame_kelola = None
        self.frame_riwayat = None
        self.frame_laporan = None

        # default page
        self.show_pemesanan()
#PERCABANGAN
    def toggle_theme(self):
        if self.dark_var.get():
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")

    def clear_main(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()

    # ---------------- Pemesanan Page ----------------
    def show_pemesanan(self):
        self.clear_main()
        frame = ctk.CTkFrame(self.main_area, fg_color=COLOR_CARD, corner_radius=12)
        frame.pack(fill="both", expand=True)
        header = ctk.CTkLabel(frame, text="Pemesanan", font=("Arial", 18, "bold"))
        header.pack(anchor="w", padx=20, pady=10)

        # search + filter
        ctrl_frame = ctk.CTkFrame(frame, fg_color="transparent")
        ctrl_frame.pack(fill="x", padx=20)
        search_entry = ctk.CTkEntry(ctrl_frame, placeholder_text="🔍 Cari menu...", width=300)
        search_entry.grid(row=0, column=0, padx=10, pady=6)
        values = ["Semua"] + sorted(list({m.kategori for m in self.manager.get_semua_menu()}))
        combo_filter = ctk.CTkComboBox(ctrl_frame, values=values, width=200)
        combo_filter.grid(row=0, column=1, padx=10)
        combo_filter.set("Semua")

        # right: cart and checkout (for guest)
        right_frame = ctk.CTkFrame(frame, fg_color=COLOR_CARD)
        right_frame.pack(side="right", fill="y", padx=20, pady=10)

        ctk.CTkLabel(right_frame, text="Keranjang", font=("Arial", 14, "bold")).pack(padx=10, pady=(10,0))
        listbox = tk.Listbox(right_frame, height=10, bg=COLOR_SIDEBAR, fg="white", font=("Arial", 12))
        listbox.pack(padx=10, pady=6, fill="x")

        label_total = ctk.CTkLabel(right_frame, text="Total: Rp 0", font=("Arial", 14, "bold"), text_color=COLOR_SUCCESS)
        label_total.pack(padx=10, pady=(6,10))

        btn_clear = ctk.CTkButton(right_frame, text="Bersihkan Keranjang", fg_color=COLOR_WARNING, command=lambda: self.clear_cart(listbox, label_total))
        btn_clear.pack(padx=10, pady=4, fill="x")
        btn_checkout = ctk.CTkButton(right_frame, text="Checkout", fg_color=COLOR_PRIMARY, command=lambda: self.checkout(listbox, label_total))
        btn_checkout.pack(padx=10, pady=4, fill="x")

        # container for menu cards (scrollable)
        canvas = tk.Canvas(frame, bg=COLOR_CARD, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        canvas.create_window((0,0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=(20,0), pady=10)
        scrollbar.pack(side="left", fill="y")
#PERULANGAN(MENAMPILKAN MENU ATAU MENGISI KERANJANG)
#FUNGSI(DEF)
        # populate cards function
        def populate_cards(filter_kat="Semua", keyword=""):
            for w in scrollable_frame.winfo_children():
                w.destroy()
            menus = self.manager.get_semua_menu()
            if filter_kat != "Semua":
                menus = [m for m in menus if m.kategori == filter_kat]
            if keyword.strip():
                menus = [m for m in menus if keyword.lower() in m.nama.lower()]

            for m in menus:
                card = ctk.CTkFrame(scrollable_frame, fg_color="#0b1220", corner_radius=10)
                card.pack(fill="x", padx=10, pady=8)
                top = ctk.CTkLabel(card, text=m.nama, font=("Arial", 14, "bold"))
                top.grid(row=0, column=0, sticky="w", padx=10, pady=(8,0))
                price = ctk.CTkLabel(card, text=f"Rp {m.harga:,}".replace(",", "."), font=("Arial",12))
                price.grid(row=1, column=0, sticky="w", padx=10)
                kat = ctk.CTkLabel(card, text=f"Kategori: {m.kategori}", font=("Arial",11), text_color="gray")
                kat.grid(row=0, column=1, sticky="e", padx=10)
                stok_lbl = ctk.CTkLabel(card, text=f"Stok: {m.stok}", font=("Arial",11))
                stok_lbl.grid(row=1, column=1, sticky="e", padx=10)

                # qty spinbox and add button
                qty_var = tk.IntVar(value=1)
                spin = tk.Spinbox(card, from_=1, to=max(1, m.stok), width=5)
                spin.grid(row=0, column=2, rowspan=2, padx=10)
                def add_to_cart_local(menu_item=m, qty_spin=spin):
                    try:
                        qty = int(qty_spin.get())
                    except Exception:
                        qty = 1
                    # validate stok
                    if qty > menu_item.stok:
                        messagebox.showerror("Stok Habis", f"Stok untuk {menu_item.nama} tidak mencukupi.")
                        return
                    # check if already in cart
                    found = False
                    for entry in self.keranjang:
                        if entry["menu"].nama == menu_item.nama:
                            # if adding, ensure stok total not exceeded
                            if entry["qty"] + qty > menu_item.stok:
                                messagebox.showerror("Stok Habis", "Jumlah melebihi stok tersedia.")
                                return
                            entry["qty"] += qty
                            found = True
                            break
                    if not found:
                        self.keranjang.append({"menu": menu_item, "qty": qty})
                    self.refresh_cart_listbox(listbox, label_total)
                btn = ctk.CTkButton(card, text="Tambah", width=80, command=add_to_cart_local)
                btn.grid(row=0, column=3, rowspan=2, padx=10, pady=8)

        # initial render
        populate_cards()

        # bind search/filter
        def on_search(e):
            populate_cards(filter_kat=combo_filter.get(), keyword=search_entry.get())
        search_entry.bind("<KeyRelease>", on_search)
        combo_filter.configure(command=lambda v: populate_cards(filter_kat=v, keyword=search_entry.get()))

        # store references for later if needed
        self.frame_pemesanan = frame

    # cart helpers
    def refresh_cart_listbox(self, listbox_widget, label_total_widget):
        listbox_widget.delete(0, "end")
        total = 0
        for entry in self.keranjang:
            nama = entry["menu"].nama
            harga = entry["menu"].harga
            qty = entry["qty"]
            tamp = f"{nama} x{qty} - Rp {harga*qty:,}".replace(",", ".")
            listbox_widget.insert("end", tamp)
            total += harga * qty
        label_total_widget.configure(text=f"Total: Rp {total:,}".replace(",", "."))
        self.current_cart_total = total

    def clear_cart(self, listbox_widget, label_total_widget):
        if messagebox.askyesno("Konfirmasi", "Bersihkan seluruh keranjang?"):
            self.keranjang.clear()
            self.refresh_cart_listbox(listbox_widget, label_total_widget)

    def checkout(self, listbox_widget, label_total_widget):
        if not self.keranjang:
            messagebox.showwarning("Kosong", "Keranjang kosong.")
            return
        # request buyer name
        buyer = simpledialog.askstring("Nama Pembeli", "Masukkan nama pembeli:")
        if not buyer:
            messagebox.showwarning("Diperlukan", "Nama pembeli harus diisi.")
            return
        # build order items and validate stok again
        items = []
        for entry in self.keranjang:
            menu_item = entry["menu"]
            qty = entry["qty"]
            if qty > menu_item.stok:
                messagebox.showerror("Stok Tidak Cukup", f"Stok {menu_item.nama} tidak mencukupi.")
                return
            items.append(OrderItem(menu_item, qty))
        order = Order(buyer, items)
        # attempt to simpan order (reduksi stok & append)
        success = self.manager.simpan_order(order)
        if success:
            messagebox.showinfo("Sukses", f"Order berhasil. Total: Rp {order.total:,}".replace(",", "."))
            # clear cart
            self.keranjang.clear()
            self.refresh_cart_listbox(listbox_widget, label_total_widget)
            # if admin view open, refresh data etc.
        else:
            messagebox.showerror("Gagal", "Order gagal. Periksa stok item.")
        # refresh pemesanan page to update stok displayed
        self.show_pemesanan()

    # ---------------- Kelola Menu Page (Admin) ----------------
    def show_kelola(self):
        if not self.is_admin:
            return
        self.clear_main()
        frame = ctk.CTkFrame(self.main_area, fg_color=COLOR_CARD, corner_radius=12)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        header = ctk.CTkLabel(frame, text="Kelola Menu", font=("Arial", 18, "bold"))
        header.pack(anchor="w", padx=20, pady=10)

        # form top
        form = ctk.CTkFrame(frame, fg_color="transparent")
        form.pack(fill="x", padx=20)
        entry_nama = ctk.CTkEntry(form, placeholder_text="Nama Item", width=300)
        entry_nama.grid(row=0, column=0, padx=6, pady=6)
        entry_harga = ctk.CTkEntry(form, placeholder_text="Harga (Rp)", width=150)
        entry_harga.grid(row=0, column=1, padx=6)
        entry_stok = ctk.CTkEntry(form, placeholder_text="Stok", width=100)
        entry_stok.grid(row=0, column=2, padx=6)
        combo_kat = ctk.CTkComboBox(form, values=["Makanan", "Minuman", "Snack"], width=150)
        combo_kat.grid(row=0, column=3, padx=6)
        combo_kat.set("Makanan")

        btn_add = ctk.CTkButton(form, text="+ Tambah", fg_color=COLOR_SUCCESS, command=lambda: self.admin_add_menu(entry_nama, entry_harga, combo_kat, entry_stok))
        btn_add.grid(row=0, column=4, padx=6)
        btn_update = ctk.CTkButton(form, text="Update", fg_color=COLOR_WARNING, command=lambda: self.admin_update_menu(entry_nama, entry_harga, combo_kat, entry_stok))
        btn_update.grid(row=0, column=5, padx=6)
        btn_delete = ctk.CTkButton(form, text="Hapus", fg_color=COLOR_DANGER, command=lambda: self.admin_delete_menu(entry_nama))
        btn_delete.grid(row=0, column=6, padx=6)
        btn_export = ctk.CTkButton(form, text="Export CSV", fg_color=COLOR_PRIMARY, command=lambda: self.manager.export_ke_csv() and messagebox.showinfo("Export", "Data menu diexport ke CSV"))
        btn_export.grid(row=0, column=7, padx=6)

        # table
        cols = ("nama", "harga", "kategori", "stok")
        tree = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c.upper())
        tree.pack(fill="both", expand=True, padx=20, pady=10)

        def refresh_table():
            for item in tree.get_children():
                tree.delete(item)
            for m in self.manager.get_semua_menu():
                tree.insert("", "end", values=(m.nama, f"Rp {m.harga:,}".replace(",", "."), m.kategori, m.stok))
        refresh_table()

        def on_tree_select(event):
            sel = tree.selection()
            if not sel: return
            vals = tree.item(sel[0])["values"]
            entry_nama.delete(0, "end"); entry_nama.insert(0, vals[0])
            harga_int = int(str(vals[1]).replace("Rp ", "").replace(".", ""))
            entry_harga.delete(0, "end"); entry_harga.insert(0, str(harga_int))
            combo_kat.set(vals[2])
            entry_stok.delete(0, "end"); entry_stok.insert(0, vals[3])

        tree.bind("<<TreeviewSelect>>", on_tree_select)

        # helper admin CRUD implementations
        def safe_int(val, default=0):
            try:
                return int(val)
            except Exception:
                return default

        self._refresh_kelola_table = refresh_table  # store for external call
        self.frame_kelola = frame

    def admin_add_menu(self, entry_nama, entry_harga, combo_kat, entry_stok):
        nama = entry_nama.get().strip()
        try:
            harga = int(entry_harga.get())
        except:
            messagebox.showerror("Error", "Harga harus angka")
            return
        stok = 0
        try:
            stok = int(entry_stok.get())
        except:
            stok = 0
        if not nama:
            messagebox.showwarning("Diperlukan", "Nama menu harus diisi")
            return
        self.manager.tambah_menu(nama, harga, combo_kat.get(), stok)
        self.manager.export_ke_csv()
        messagebox.showinfo("Sukses", "Menu ditambahkan")
        # refresh views
        self.show_kelola()

    def admin_update_menu(self, entry_nama, entry_harga, combo_kat, entry_stok):
        selected_name = None
        # try to get selected from tree
        try:
            tree = self.frame_kelola.winfo_children()[-1]  # a bit hacky but tree is last child
            sel = tree.selection()
            if sel:
                selected_name = tree.item(sel[0])["values"][0]
        except Exception:
            pass
        if not selected_name:
            messagebox.showwarning("Pilih Item", "Pilih menu yang akan diupdate dari tabel")
            return
        nama_baru = entry_nama.get().strip()
        try:
            harga_baru = int(entry_harga.get())
        except:
            messagebox.showerror("Error", "Harga harus angka")
            return
        try:
            stok_baru = int(entry_stok.get())
        except:
            stok_baru = 0
        kat = combo_kat.get()
        if self.manager.edit_menu(selected_name, nama_baru, harga_baru, kat, stok_baru):
            self.manager.export_ke_csv()
            messagebox.showinfo("Sukses", "Menu diperbarui")
            self.show_kelola()
        else:
            messagebox.showerror("Gagal", "Tidak dapat menemukan menu")

    def admin_delete_menu(self, entry_nama):
        nama = entry_nama.get().strip()
        if not nama:
            messagebox.showwarning("Diperlukan", "Masukkan nama menu yang ingin dihapus")
            return
        if messagebox.askyesno("Konfirmasi", f"Hapus menu {nama}?"):
            self.manager.hapus_menu(nama)
            self.manager.export_ke_csv()
            messagebox.showinfo("Sukses", "Menu dihapus")
            self.show_kelola()

    # ---------------- Riwayat Page ----------------
    def show_riwayat(self):
        if not self.is_admin:
            return
        self.clear_main()

        frame = ctk.CTkFrame(self.main_area, fg_color=COLOR_CARD, corner_radius=12)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        header = ctk.CTkLabel(frame, text="Riwayat Pesanan", font=("Arial", 18, "bold"))
        header.pack(anchor="w", padx=20, pady=10)

        # ==============================
        # TABLE RIWAYAT
        # ==============================
        cols = ("waktu", "pembeli", "items", "total", "status")
        tree = ttk.Treeview(frame, columns=cols, show="headings")

        for c in cols:
            tree.heading(c, text=c.upper())

        tree.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        def refresh():
            for i in tree.get_children():
                tree.delete(i)

            for o in self.manager.get_orders_history():
                items_text = ", ".join([f"{it.menu_item.nama}x{it.qty}" for it in o.items])
                tree.insert(
                    "",
                    "end",
                    values=(
                        o.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        o.buyer_name,
                        items_text,
                        f"Rp {o.total:,}".replace(",", "."),
                        o.status
                    )
                )

        refresh()

        # ==============================
        # TOMBOL HAPUS RIWAYAT TERPILIH
        # ==============================
        def hapus_riwayat():
            from tkinter import messagebox

            # Ambil item terpilih
            selected = tree.focus()
            if not selected:
                messagebox.showwarning("Peringatan", "Pilih salah satu riwayat yang ingin dihapus!")
                return

            values = tree.item(selected, "values")
            waktu = values[0]

            confirm = messagebox.askyesno(
                "Konfirmasi",
                f"Yakin ingin menghapus riwayat pada waktu:\n{waktu}?"
            )
            if not confirm:
                return

            history = self.manager.orders_history

            for o in history[:]:
                if o.timestamp.strftime("%Y-%m-%d %H:%M:%S") == waktu:
                    history.remove(o)
                    break

            refresh()

        # === TOMBOL DITAMBAHKAN DI SINI ===
        btn_hapus = ctk.CTkButton(
            frame,
            text="Hapus Riwayat Terpilih",
            fg_color="red",
            hover_color="#A00000",
            text_color="white",
            command=hapus_riwayat
        )
        btn_hapus.pack(anchor="e", padx=20, pady=10)

        self.frame_riwayat = frame


    # ---------------- Laporan Page ----------------
    def show_laporan(self):
        if not self.is_admin:
            return
        self.clear_main()
        frame = ctk.CTkFrame(self.main_area, fg_color=COLOR_CARD, corner_radius=12)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        header = ctk.CTkLabel(frame, text="Laporan Penjualan", font=("Arial", 18, "bold"))
        header.pack(anchor="w", padx=20, pady=10)

        stats = self.manager.hitung_total_penjualan()
        ctk.CTkLabel(frame, text=f"Total Pesanan: {stats['total_orders']}", font=("Arial", 14)).pack(anchor="w", padx=20, pady=(10,0))
        ctk.CTkLabel(frame, text=f"Total Pendapatan (termasuk pajak): Rp {stats['total_revenue']:,}".replace(",", "."), font=("Arial", 14)).pack(anchor="w", padx=20, pady=(6,0))

        # grafik sederhana kategori
        data = self.manager.get_data_grafik()
        fig = Figure(figsize=(5,3), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(list(data.keys()), list(data.values()), color=['#3B82F6', '#10B981', '#F59E0B'])
        ax.set_title("Jumlah Item per Kategori")
        FigureCanvasTkAgg(fig, master=frame).get_tk_widget().pack(padx=10, pady=10)

        self.frame_laporan = frame

    # ---------------- misc ----------------
    def logout(self):
        if messagebox.askyesno("Logout", "Keluar dari sistem?"):
            self.destroy()
            buka_login_window()

# --------------- App launch helpers ---------------
def buka_login_window():
    app = LoginWindow()
    app.mainloop()

def buka_aplikasi_utama(is_admin=True):
    app = AplikasiKantin(is_admin=is_admin)
    app.mainloop()

if __name__ == "__main__":
    buka_login_window()
