# main.py — Complete final fixed
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import customtkinter as ctk
from backend import KantinManager, Order, OrderItem
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# --------------------------
# THEMES
# --------------------------
THEMES = {
    "dark": {
        "bg": "#0F172A",
        "sidebar": "#1E293B",
        "card": "#334155",
        "menucard": "#0b1220",
        "text": "white"
    },
    "light": {
        "bg": "#F8FAFC",
        "sidebar": "#FFFFFF",
        "card": "#F1F5F9",
        "menucard": "#FFFFFF",
        "text": "black"
    }
}

# --------------------------
# Local Cart helper (keamanan - tidak tergantung backend)
# --------------------------
class Cart:
    """
    Simple Cart container that stores OrderItem-like objects.
    Uses backend.MenuItem references as menu_item.
    """
    def __init__(self):
        self.items = []  # list of OrderItem (from backend)

    def add(self, menu_item, qty: int) -> bool:
        # validate stok
        if qty <= 0:
            return False
        # check current qty in cart
        existing = next((it for it in self.items if it.menu_item.nama == menu_item.nama), None)
        current = existing.qty if existing else 0
        if current + qty > menu_item.stok:
            return False
        if existing:
            existing.qty += qty
        else:
            self.items.append(OrderItem(menu_item, qty))
        return True

    def clear(self):
        self.items = []

    def to_order_items(self):
        # already OrderItem instances; return shallow copy
        return [OrderItem(it.menu_item, it.qty) for it in self.items]

    @property
    def subtotal(self):
        return sum(it.subtotal for it in self.items)


# --------------------------
# Login window
# --------------------------
class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.manager = KantinManager()

        self.title("Login Sistem - Kantin Digital")
        self.geometry("900x600")
        self.minsize(850, 550)
        ctk.set_appearance_mode("Dark")

        # layout grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(self, fg_color="#3B82F6")
        left.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(left, text="KANTIN\nDIGITAL",
                     font=("Montserrat", 32, "bold"),
                     justify="center",
                     text_color="white").pack(pady=(120, 20))
        ctk.CTkLabel(left, text="Sistem Manajemen Menu & Order",
                     font=("Roboto", 14),
                     text_color="white").pack()
        ctk.CTkLabel(left, text="Created by Kelompok",
                     font=("Arial", 10), text_color="white").pack(side="bottom", pady=20)

        right = ctk.CTkFrame(self, fg_color="#0F172A")
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(0, weight=1)

        box = ctk.CTkFrame(right, fg_color="transparent")
        box.grid(row=0, column=0)

        ctk.CTkLabel(box, text="LOGIN ADMIN", font=("Arial", 20, "bold")).pack(pady=(0, 20))
        self.entry_user = ctk.CTkEntry(box, placeholder_text="Username", width=260)
        self.entry_user.pack(pady=10)
        self.entry_pass = ctk.CTkEntry(box, placeholder_text="Password", width=260, show="•")
        self.entry_pass.pack(pady=10)

        ctk.CTkButton(box, text="LOGIN", command=self.aksi_login, width=260, fg_color="#3B82F6").pack(pady=20)
        ctk.CTkButton(box, text="Masuk sebagai Tamu", command=self.masuk_tamu, width=260, fg_color="transparent").pack(pady=5)

        self.bind("<Return>", lambda e: self.aksi_login())

    def aksi_login(self):
        if self.manager.cek_login(self.entry_user.get(), self.entry_pass.get()):
            self.destroy()
            # open main app as admin
            AplikasiKantin(is_admin=True).mainloop()
        else:
            messagebox.showerror("Akses Ditolak", "Username/Password salah.")

    def masuk_tamu(self):
        self.destroy()
        AplikasiKantin(is_admin=False).mainloop()


# --------------------------
# Main application
# --------------------------
class AplikasiKantin(ctk.CTk):
    def __init__(self, is_admin=True):
        super().__init__()

        self.theme = "dark"
        ctk.set_appearance_mode("Dark")

        self.is_admin = is_admin
        self.manager = KantinManager()
        self.cart = Cart()

        self.title("Kantin Digital")
        self.geometry("1200x750")
        self.configure(fg_color=THEMES["dark"]["bg"])

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=220, fg_color=THEMES[self.theme]["sidebar"])
        self.sidebar.grid(row=0, column=0, sticky="nswe")
        ctk.CTkLabel(self.sidebar, text="KANTIN", font=("Montserrat", 22, "bold"),
                     text_color="#3B82F6").pack(pady=(30, 10))

        # create buttons without direct command binding (safer)
        self.btn_order = ctk.CTkButton(self.sidebar, text="🛒 Pemesanan", fg_color="transparent", anchor="w")
        self.btn_order.pack(pady=6)

        # admin buttons placeholders
        self.btn_kelola = ctk.CTkButton(self.sidebar, text="📝 Kelola Menu", fg_color="transparent", anchor="w")
        self.btn_riwayat = ctk.CTkButton(self.sidebar, text="📜 Riwayat", fg_color="transparent", anchor="w")
        self.btn_laporan = ctk.CTkButton(self.sidebar, text="📊 Laporan", fg_color="transparent", anchor="w")

        if self.is_admin:
            self.btn_kelola.pack(pady=6)
            self.btn_riwayat.pack(pady=6)
            self.btn_laporan.pack(pady=6)

        self.dark_var = tk.BooleanVar(value=True)
        ctk.CTkSwitch(self.sidebar, text="Dark Mode", variable=self.dark_var, command=self.toggle_theme).pack(side="bottom", pady=30)

        ctk.CTkButton(self.sidebar, text="Logout", fg_color="#EF4444", command=self.logout).pack(side="bottom", pady=10)

        # main area
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

        # bind commands after init to ensure methods exist
        self.btn_order.configure(command=self.show_pemesanan)
        # schedule admin commands after initialization complete
        if self.is_admin:
            self.after(0, lambda: self.btn_kelola.configure(command=self.show_kelola))
            self.after(0, lambda: self.btn_riwayat.configure(command=self.show_riwayat))
            self.after(0, lambda: self.btn_laporan.configure(command=self.show_laporan))

        # show default page
        self.show_pemesanan()

    # --------------------------
    # theme
    # --------------------------
    def toggle_theme(self):
        self.theme = "dark" if self.dark_var.get() else "light"
        pal = THEMES[self.theme]
        ctk.set_appearance_mode("Dark" if self.theme == "dark" else "Light")
        self.configure(fg_color=pal["bg"])
        self.sidebar.configure(fg_color=pal["sidebar"])
        if hasattr(self, "current_page"):
            # re-render current page to apply theme
            self.current_page()

    def clear_main(self):
        for w in self.main_area.winfo_children():
            w.destroy()

    # --------------------------
    # Pemesanan page
    # --------------------------
    def show_pemesanan(self):
        self.clear_main()
        self.current_page = self.show_pemesanan
        pal = THEMES[self.theme]

        frame = ctk.CTkFrame(self.main_area, fg_color=pal["card"])
        frame.pack(fill="both", expand=True)

        ctk.CTkLabel(frame, text="Pemesanan", font=("Arial", 18, "bold"), text_color=pal["text"]).pack(anchor="w", padx=20, pady=10)

        # search & filter
        ctrl = ctk.CTkFrame(frame, fg_color="transparent")
        ctrl.pack(fill="x", padx=20)
        search = ctk.CTkEntry(ctrl, placeholder_text="Cari menu...", width=300)
        search.grid(row=0, column=0, padx=10, pady=6)
        kategori_list = ["Semua"] + sorted({m.kategori for m in self.manager.get_semua_menu()})
        filter_kat = ctk.CTkComboBox(ctrl, values=kategori_list, width=200)
        filter_kat.set("Semua")
        filter_kat.grid(row=0, column=1)

        # cart frame
        cart_frame = ctk.CTkFrame(frame, fg_color=pal["card"])
        cart_frame.pack(side="right", fill="y", padx=20, pady=10)
        ctk.CTkLabel(cart_frame, text="Keranjang", font=("Arial", 14, "bold"), text_color=pal["text"]).pack()
        self.list_cart = tk.Listbox(cart_frame, height=10, bg=pal["sidebar"], fg=pal["text"])
        self.list_cart.pack(padx=10, pady=6, fill="x")
        self.label_total = ctk.CTkLabel(cart_frame, text="Total: Rp 0", font=("Arial", 14, "bold"), text_color=pal["text"])
        self.label_total.pack(pady=6)
        ctk.CTkButton(cart_frame, text="Bersihkan Keranjang", fg_color="#F59E0B", command=self.clear_cart).pack(fill="x", padx=10, pady=4)
        ctk.CTkButton(cart_frame, text="Checkout", fg_color="#3B82F6", command=self.checkout).pack(fill="x", padx=10, pady=4)

        # menu list (scrollable)
        canvas = tk.Canvas(frame, bg=pal["card"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        container = ttk.Frame(canvas)
        container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, pady=10)
        scrollbar.pack(side="left", fill="y")

        def render_menu(kat="Semua", key=""):
            for w in container.winfo_children():
                w.destroy()
            menus = self.manager.get_semua_menu()
            if kat != "Semua":
                menus = [m for m in menus if m.kategori == kat]
            if key.strip():
                menus = [m for m in menus if key.lower() in m.nama.lower()]
            for m in menus:
                box = ctk.CTkFrame(container, fg_color=pal["menucard"], corner_radius=10)
                box.pack(fill="x", padx=10, pady=8)
                ctk.CTkLabel(box, text=m.nama, font=("Arial", 14, "bold"), text_color=pal["text"]).grid(row=0, column=0, sticky="w", padx=10)
                ctk.CTkLabel(box, text=f"Rp {m.harga:,}".replace(",", "."), font=("Arial", 12), text_color=pal["text"]).grid(row=1, column=0, sticky="w", padx=10)
                ctk.CTkLabel(box, text=f"Stok: {m.stok}", font=("Arial", 11), text_color=pal["text"]).grid(row=0, column=1, padx=10)
                spin = tk.Spinbox(box, from_=1, to=max(1, m.stok), width=5)
                spin.grid(row=0, column=2, rowspan=2)
                def add(menu_item=m, spinbox=spin):
                    try:
                        qty = int(spinbox.get())
                    except:
                        qty = 1
                    if not self.cart.add(menu_item, qty):
                        messagebox.showerror("Stok", "Jumlah melebihi stok.")
                        return
                    self.refresh_cart()
                ctk.CTkButton(box, text="Tambah", width=80, command=add).grid(row=0, column=3, rowspan=2, padx=10)

        render_menu()
        search.bind("<KeyRelease>", lambda e: render_menu(filter_kat.get(), search.get()))
        filter_kat.configure(command=lambda v: render_menu(v, search.get()))
        self.refresh_cart()

    # --------------------------
    # cart helpers
    # --------------------------
    def refresh_cart(self):
        pal = THEMES[self.theme]
        self.list_cart.delete(0, "end")
        total = 0
        for it in self.cart.items:
            self.list_cart.insert("end", f"{it.menu_item.nama} x{it.qty} - Rp {it.subtotal:,}".replace(",", "."))
            total += it.subtotal
        self.label_total.configure(text=f"Total: Rp {total:,}".replace(",", "."), text_color=pal["text"])

    def clear_cart(self):
        if messagebox.askyesno("Konfirmasi", "Kosongkan keranjang?"):
            self.cart.clear()
            self.refresh_cart()

    def checkout(self):
        if not self.cart.items:
            messagebox.showwarning("Kosong", "Keranjang kosong.")
            return
        buyer = simpledialog.askstring("Nama Pembeli", "Masukkan nama pembeli:")
        if not buyer:
            return
        # validate stock again and build Order
        for it in self.cart.items:
            if it.qty > it.menu_item.stok:
                messagebox.showerror("Stok", f"Stok untuk {it.menu_item.nama} tidak mencukupi.")
                return
        order = Order(buyer, self.cart.to_order_items())
        success = self.manager.simpan_order(order)
        if success:
            # build simple struk
            lines = [f"Struk - {order.timestamp.strftime('%Y-%m-%d %H:%M:%S')}", f"Pembeli: {order.buyer_name}", "-"*30]
            for it in order.items:
                lines.append(f"{it.menu_item.nama} x{it.qty} - Rp {it.subtotal:,}".replace(",", "."))
            lines.append("-"*30)
            lines.append(f"Subtotal: Rp {order.subtotal:,}".replace(",", "."))
            lines.append(f"Pajak: Rp {order.pajak:,}".replace(",", "."))
            lines.append(f"Total: Rp {order.total:,}".replace(",", "."))
            struk = "\n".join(lines)
            messagebox.showinfo("Struk Pembelian", struk)
            self.cart.clear()
            self.refresh_cart()
            # refresh listing (stok updated)
            self.show_pemesanan()
        else:
            messagebox.showerror("Gagal", "Gagal menyimpan order. Periksa stok.")

    # --------------------------
    # Kelola Menu (admin)
    # --------------------------
    def show_kelola(self):
        if not self.is_admin:
            return
        self.clear_main()
        self.current_page = self.show_kelola
        pal = THEMES[self.theme]

        frame = ctk.CTkFrame(self.main_area, fg_color=pal["card"])
        frame.pack(fill="both", expand=True)

        ctk.CTkLabel(frame, text="Kelola Menu", font=("Arial", 18, "bold"), text_color=pal["text"]).pack(anchor="w", padx=20, pady=10)

        form = ctk.CTkFrame(frame, fg_color="transparent")
        form.pack(fill="x", padx=20, pady=10)
        form.grid_columnconfigure(0, weight=2)
        form.grid_columnconfigure(1, weight=1)
        form.grid_columnconfigure(2, weight=1)
        form.grid_columnconfigure(3, weight=1)
        form.grid_columnconfigure(4, weight=0)
        form.grid_columnconfigure(5, weight=0)
        form.grid_columnconfigure(6, weight=0)

        en_nama = ctk.CTkEntry(form, placeholder_text="Nama")
        en_nama.grid(row=0, column=0, padx=6, pady=6, sticky="we")
        en_harga = ctk.CTkEntry(form, placeholder_text="Harga")
        en_harga.grid(row=0, column=1, padx=6, pady=6, sticky="we")
        en_stok = ctk.CTkEntry(form, placeholder_text="Stok")
        en_stok.grid(row=0, column=2, padx=6, pady=6, sticky="we")
        cmb_kat = ctk.CTkComboBox(form, values=["Makanan", "Minuman", "Snack"])
        cmb_kat.set("Makanan")
        cmb_kat.grid(row=0, column=3, padx=6, pady=6, sticky="we")

        def add():
            try:
                nama = en_nama.get().strip()
                harga = int(en_harga.get())
                stok = int(en_stok.get())
                kat = cmb_kat.get()
            except:
                messagebox.showerror("Error", "Data tidak valid!")
                return
            if not nama:
                messagebox.showerror("Error", "Nama tidak boleh kosong!")
                return
            self.manager.tambah_menu(nama, harga, kat, stok)
            self.manager.export_ke_csv()
            messagebox.showinfo("Sukses", "Menu ditambahkan")
            self.show_kelola()

        def update():
            sel = tree.focus()
            if not sel:
                messagebox.showwarning("Pilih", "Pilih item dahulu.")
                return
            try:
                nama = en_nama.get().strip()
                harga = int(en_harga.get())
                stok = int(en_stok.get())
                kat = cmb_kat.get()
            except:
                messagebox.showerror("Error", "Data tidak valid!")
                return
            if self.manager.edit_menu(sel, nama, harga, kat, stok):
                self.manager.export_ke_csv()
                messagebox.showinfo("Sukses", "Menu diperbarui")
                self.show_kelola()
            else:
                messagebox.showerror("Gagal", "Item tidak ditemukan")

        def delete():
            sel = tree.focus()
            if not sel:
                return
            if messagebox.askyesno("Hapus", "Yakin hapus item ini?"):
                self.manager.hapus_menu(sel)
                self.manager.export_ke_csv()
                self.show_kelola()

        ctk.CTkButton(form, text="+ Tambah", fg_color="#10B981", command=add).grid(row=0, column=4, padx=6, pady=6, sticky="we")
        ctk.CTkButton(form, text="Update", fg_color="#F59E0B", command=update).grid(row=0, column=5, padx=6, pady=6, sticky="we")
        ctk.CTkButton(form, text="Hapus", fg_color="#EF4444", command=delete).grid(row=0, column=6, padx=6, pady=6, sticky="we")

        cols = ("nama", "harga", "kategori", "stok")
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=12)
        for c in cols:
            tree.heading(c, text=c.upper())
        tree.pack(fill="both", expand=True, padx=20, pady=10)

        for m in self.manager.get_semua_menu():
            tree.insert("", "end", iid=m.nama, values=(m.nama, f"Rp {m.harga:,}".replace(",", "."), m.kategori, m.stok))

        def on_select(e):
            sel = tree.focus()
            if not sel:
                return
            vals = tree.item(sel)["values"]
            en_nama.delete(0, "end"); en_nama.insert(0, vals[0])
            en_harga.delete(0, "end"); en_harga.insert(0, int(str(vals[1]).replace("Rp ", "").replace(".", "")))
            cmb_kat.set(vals[2])
            en_stok.delete(0, "end"); en_stok.insert(0, vals[3])

        tree.bind("<<TreeviewSelect>>", on_select)

    # --------------------------
    # Riwayat
    # --------------------------
    def show_riwayat(self):
        if not self.is_admin:
            return
        self.clear_main()
        self.current_page = self.show_riwayat
        pal = THEMES[self.theme]

        frame = ctk.CTkFrame(self.main_area, fg_color=pal["card"])
        frame.pack(fill="both", expand=True)
        ctk.CTkLabel(frame, text="Riwayat Pesanan", font=("Arial", 18, "bold"), text_color=pal["text"]).pack(anchor="w", padx=20, pady=10)
        cols = ("waktu", "pembeli", "items", "total")
        tree = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c.upper())
        tree.pack(fill="both", expand=True, padx=20, pady=10)
        for o in self.manager.get_orders_history():
            items = ", ".join([f"{it.menu_item.nama}x{it.qty}" for it in o.items])
            tree.insert("", "end", values=(o.timestamp.strftime("%Y-%m-%d %H:%M:%S"), o.buyer_name, items, f"Rp {o.total:,}".replace(",", ".")))

    # --------------------------
    # Laporan
    # --------------------------
    def show_laporan(self):
        if not self.is_admin:
            return
        self.clear_main()
        self.current_page = self.show_laporan
        pal = THEMES[self.theme]
        frame = ctk.CTkFrame(self.main_area, fg_color=pal["card"])
        frame.pack(fill="both", expand=True)
        ctk.CTkLabel(frame, text="Laporan Penjualan", font=("Arial", 18, "bold"), text_color=pal["text"]).pack(anchor="w", padx=20, pady=10)
        stats = self.manager.hitung_total_penjualan()
        ctk.CTkLabel(frame, text=f"Total Pesanan: {stats['total_orders']}", font=("Arial", 14), text_color=pal["text"]).pack(anchor="w", padx=20)
        ctk.CTkLabel(frame, text=f"Pendapatan Total: Rp {stats['total_revenue']:,}".replace(",", "."), font=("Arial", 14), text_color=pal["text"]).pack(anchor="w", padx=20, pady=(0, 10))
        data = self.manager.get_data_grafik()
        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(list(data.keys()), list(data.values()))
        ax.set_title("Jumlah Menu per Kategori")
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)

    # --------------------------
    # Logout
    # --------------------------
    def logout(self):
        if messagebox.askyesno("Logout", "Keluar dari sistem?"):
            self.destroy()
            LoginWindow().mainloop()


# --------------------------
# Run
# --------------------------
if __name__ == "__main__":
    LoginWindow().mainloop()
