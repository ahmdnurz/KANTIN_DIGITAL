import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import customtkinter as ctk
from backend import KantinManager, Order, OrderItem
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

# initial appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")
#KONTANTA (nilai tetap yang tidak berubah selama program berjalan)(14-36)
# palettes for dark and light
PALETTE = {
    #TIPE DATA STING Tipe data menentukan jenis nilai yang disimpan dalam variabel(16-37)
    "Dark": {
        "BG_MAIN": "#0F172A",
        "SIDEBAR": "#1E293B",
        "CARD": "#334155",
        "PRIMARY": "#3B82F6",
        "SUCCESS": "#10B981",
        "WARNING": "#F59E0B",
        "DANGER": "#EF4444",
        "TEXT": "white",
        "SUBTEXT": "gray"
    },
    "Light": {
        "BG_MAIN": "#FFFFFF",
        "SIDEBAR": "#F1F5F9",
        "CARD": "#F8FAFC",
        "PRIMARY": "#2563EB",
        "SUCCESS": "#059669",
        "WARNING": "#D97706",
        "DANGER": "#DC2626",
        "TEXT": "#0B1220",
        "SUBTEXT": "#374151"
    }
}
#VARIABEL WARNA UNTUK MODE GELAP DAN TERANG(Variabel adalah tempat menyimpan nilai yang bisa berubah)(39-40)
#FUNGSI Fungsi adalah blok kode yang memiliki nama, dipanggil berkali-kali, dan membuat kode lebih rapi.(41-43)
def colors_for_mode(mode: str):
    return PALETTE.get(mode, PALETTE["Dark"])

# --------------- Login Window ---------------
#GUI CustomTkinter , Tkinter adalah tampilan visual yang berinteraksi dengan pengguna melalui tombol, input, label, dll.
class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Login Sistem - Kantin Digital")
        self.geometry("900x600")
        self.minsize(850, 550)
        self.resizable(True, True)
#VARIABEL MANAGER UNTUK MENGELOLA DATA KANTIN(51)
        self.manager = KantinManager()

        self._apply_palette()

        # ================= GRID UTAMA (PENTING) =================
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # =========== LEFT Branding Panel ===========
        left = ctk.CTkFrame(self, fg_color=self.COLORS["PRIMARY"], corner_radius=0)
        left.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(left, text="KANTIN\nDIGITAL",
                     font=("Montserrat", 32, "bold"),
                     justify="center",
                     text_color=self.COLORS["TEXT"]).pack(pady=(120, 20))

        ctk.CTkLabel(left, text="Sistem Manajemen\nMenu & Order",
                     font=("Roboto", 14),
                     text_color=self.COLORS["TEXT"]).pack()

        ctk.CTkLabel(left,
                     text="Created by Kelompok 3 & 4\nTeknik Komputer 2025",
                     font=("Arial", 10),
                     text_color=self.COLORS["TEXT"]).pack(side="bottom", pady=30)

        # =========== RIGHT Form Panel ===========
        right = ctk.CTkFrame(self, fg_color=self.COLORS["BG_MAIN"], corner_radius=0)
        right.grid(row=0, column=1, sticky="nsew")

        # membuat form berada di tengah vertikal & horizontal
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(0, weight=1)

        box = ctk.CTkFrame(right, fg_color="transparent")
        box.grid(row=0, column=0)

        # ========== Isi Kotak Login ==========
        ctk.CTkLabel(box, text="LOGIN ADMIN",
                     font=("Arial", 20, "bold"),
                     text_color=self.COLORS["TEXT"]).pack(pady=(0, 20))
#VARIABEL ENTRY UNTUK USERNAME DAN PASSWORD(94-101)
        self.entry_user = ctk.CTkEntry(box, placeholder_text="Username",
                                       width=260, height=40)
        self.entry_user.pack(pady=10)

        self.entry_pass = ctk.CTkEntry(box, placeholder_text="Password",
                                       show="•", width=260, height=40)
        self.entry_pass.pack(pady=10)

        ctk.CTkButton(box, text="LOGIN",
                      command=self.aksi_login,
                      width=260, height=40,
                      fg_color=self.COLORS["PRIMARY"]).pack(pady=20)

        ctk.CTkButton(box, text="Lihat Menu Saja (Tamu)",
                      command=self.masuk_tamu,
                      width=260,
                      fg_color="transparent",
                      border_width=1,
                      text_color=self.COLORS["TEXT"]).pack(pady=5)

        ctk.CTkLabel(box, text="Silahkan login",
                     text_color=self.COLORS["SUBTEXT"]).pack()

        # Enter untuk login
        self.bind('<Return>', lambda e: self.aksi_login())

    def _apply_palette(self):
        mode = ctk.get_appearance_mode() or "Dark"
        self.COLORS = colors_for_mode(mode)
        # set window bg accordingly
        try:
            self.configure(fg_color=self.COLORS["BG_MAIN"])
        except Exception:
            pass

    # =================== LOGIN FUNCTION ===================  
    # PERCABANGAN IF ELSE Percabangan adalah proses memilih jalur keputusan berdasarkan kondisi (132-137)
#FUNGSI PROSES LOGIN(134-143)
    def aksi_login(self):
        if self.manager.cek_login(self.entry_user.get(), self.entry_pass.get()):
            self.destroy()
            buka_aplikasi_utama(is_admin=True)
        else:
            messagebox.showerror("Akses Ditolak", "Username atau Password salah!")

    def masuk_tamu(self):
        self.destroy()
        buka_aplikasi_utama(is_admin=False)

# --------------- Main App ---------------
class AplikasiKantin(ctk.CTk):
    def __init__(self, is_admin=True):
        super().__init__()
        self.is_admin = is_admin
        role = "Administrator" if is_admin else "Mode Tamu"
        self.title(f"Dashboard {role} - Kantin Digital")
        self.geometry("1200x750")

        self.manager = KantinManager()
#ARRAY KERANJANG UNTUK MENYIMPAN ITEM YANG DIPESAN(154-155)
        self.keranjang = []  # list of dict {menu:MenuItem, qty:int}
        self.buyer_name = ""

        # initial palette & UI
        self._apply_palette_initial()

        # grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # sidebar
        self.sidebar = ctk.CTkFrame(self, width=220, fg_color=self.COLORS["SIDEBAR"], corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nswe")
        ctk.CTkLabel(self.sidebar, text="KANTIN", font=("Montserrat", 22, "bold"), text_color=self.COLORS["PRIMARY"]).pack(pady=(30,10))

        # always show Pemesanan for all users
        self.btn_order = ctk.CTkButton(self.sidebar, text=" Pemesanan", command=lambda: self.show_pemesanan("Semua"), width=200, fg_color="transparent", anchor="w")
        self.btn_order.pack(pady=6)

        # If admin show admin pages, guest will see category buttons below
#VARIABEL BUTTON UNTUK ADMIN DAN TAMU(172-186)
#PERCABANGAN IF ELSE Percabangan adalah proses memilih jalur keputusan berdasarkan kondisi (175-189)
        if self.is_admin:
            self.btn_kelola = ctk.CTkButton(self.sidebar, text="Kelola Menu", command=self.show_kelola, width=200, fg_color="transparent", anchor="w")
            self.btn_kelola.pack(pady=6)
            self.btn_riwayat = ctk.CTkButton(self.sidebar, text="Riwayat", command=self.show_riwayat, width=200, fg_color="transparent", anchor="w")
            self.btn_riwayat.pack(pady=6)
            self.btn_laporan = ctk.CTkButton(self.sidebar, text="Laporan", command=self.show_laporan, width=200, fg_color="transparent", anchor="w")
            self.btn_laporan.pack(pady=6)
        else:
            # for guest / tamu: show category quick buttons
            self.btn_makanan = ctk.CTkButton(self.sidebar, text="  Makanan", command=lambda: self.show_pemesanan("Makanan"), width=200, fg_color="transparent", anchor="w")
            self.btn_makanan.pack(pady=6)
            self.btn_minuman = ctk.CTkButton(self.sidebar, text="  Minuman", command=lambda: self.show_pemesanan("Minuman"), width=200, fg_color="transparent", anchor="w")
            self.btn_minuman.pack(pady=6)
            self.btn_snack = ctk.CTkButton(self.sidebar, text="  Snack", command=lambda: self.show_pemesanan("Snack"), width=200, fg_color="transparent", anchor="w")
            self.btn_snack.pack(pady=6)

        # theme switch
        self.dark_var = tk.BooleanVar(value=(ctk.get_appearance_mode() == "Dark"))
        self.switch = ctk.CTkSwitch(self.sidebar, text="Dark Mode", command=self.toggle_theme, variable=self.dark_var)
        self.switch.pack(side="bottom", pady=30)

        ctk.CTkButton(self.sidebar, text="Log Out", command=self.logout, fg_color=self.COLORS["DANGER"], width=160).pack(side="bottom", pady=10)

        # main area (made non-transparent to avoid blank visual on some systems)
        self.main_area = ctk.CTkFrame(self, fg_color=self.COLORS["BG_MAIN"])
        self.main_area.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

        # container frames for pages
        self.frame_pemesanan = None
        self.frame_kelola = None
        self.frame_riwayat = None
        self.frame_laporan = None

        # default page: show all menu
        self.show_pemesanan("Semua")

    def _apply_palette_initial(self):
        mode = ctk.get_appearance_mode() or "Dark"
        self.COLORS = colors_for_mode(mode)
        try:
            self.configure(fg_color=self.COLORS["BG_MAIN"])
        except Exception:
            pass

    def _apply_palette_runtime(self):
        """Apply current palette to main components (best-effort)."""
        mode = ctk.get_appearance_mode() or "Dark"
        self.COLORS = colors_for_mode(mode)
        try:
            self.configure(fg_color=self.COLORS["BG_MAIN"])
        except Exception:
            pass
        # update sidebar and main frames if exist
        try:
            if hasattr(self, "sidebar") and self.sidebar:
                self.sidebar.configure(fg_color=self.COLORS["SIDEBAR"])
            if hasattr(self, "main_area") and self.main_area:
                self.main_area.configure(fg_color=self.COLORS["BG_MAIN"])
            # update buttons/labels that use colors explicitly if present
            for btn in getattr(self, "sidebar").winfo_children():
                # if button uses fg_color stored earlier, let it remain; colors for new widgets will follow palette
                pass
        except Exception:
            pass
        # if there's a current page, refresh it so colors are used when widgets are recreated
        current = None
        if self.frame_pemesanan:
            current = "pemesanan"
        elif self.frame_kelola:
            current = "kelola"
        elif self.frame_riwayat:
            current = "riwayat"
        elif self.frame_laporan:
            current = "laporan"
        # re-show current to apply palette for page-specific widgets
        if current == "pemesanan":
            self.show_pemesanan("Semua")
        elif current == "kelola":
            self.show_kelola()
        elif current == "riwayat":
            self.show_riwayat()
        elif current == "laporan":
            self.show_laporan()

    def toggle_theme(self):
        # toggle appearance mode in customtkinter and re-apply palette
        if self.dark_var.get():
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")
        self._apply_palette_runtime()

    def clear_main(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()

    # ---------------- Pemesanan Page ----------------
    #GUI PEMESANAN UNTUK MENAMPILKAN MENU DAN KERANJANG(277-307)
    def show_pemesanan(self, filter_kategori="Semua"):
        from customtkinter import CTkScrollableFrame

        self.clear_main()
        # Use a card container with wider space for menu items
        container = ctk.CTkFrame(self.main_area, fg_color=self.COLORS["CARD"], corner_radius=12)
        container.pack(fill="both", expand=True)
        header = ctk.CTkLabel(container, text="Pemesanan", font=("Arial", 18, "bold"), text_color=self.COLORS["TEXT"])
        header.pack(anchor="w", padx=20, pady=10)

        # Top controls: search + kategori summary + meja (display) (meja input will be on checkout)
        ctrl = ctk.CTkFrame(container, fg_color="transparent")
        ctrl.pack(fill="x", padx=20, pady=(0,10))
        search_entry = ctk.CTkEntry(ctrl, placeholder_text="🔍 Cari menu...", width=420)
        search_entry.grid(row=0, column=0, padx=8, pady=6, sticky="w")
        combo = ctk.CTkComboBox(ctrl, values=["Semua", "Makanan", "Minuman", "Snack"], width=180)
        combo.grid(row=0, column=1, padx=8)
        combo.set(filter_kategori if filter_kategori else "Semua")

        # Right: cart panel
        cart_panel = ctk.CTkFrame(container, fg_color=self.COLORS["CARD"], width=280)
        cart_panel.pack(side="right", fill="y", padx=20, pady=10)
        ctk.CTkLabel(cart_panel, text="Keranjang", font=("Arial", 14, "bold"), text_color=self.COLORS["TEXT"]).pack(padx=10, pady=(10,6))
        listbox = tk.Listbox(cart_panel, height=12, bg=self.COLORS["SIDEBAR"], fg=self.COLORS["TEXT"], font=("Arial", 12))
        listbox.pack(padx=12, pady=6, fill="both")
        total_label = ctk.CTkLabel(cart_panel, text="Total: Rp 0", font=("Arial", 14, "bold"), text_color=self.COLORS["SUCCESS"])
        total_label.pack(padx=10, pady=(6,10))
        btn_clear = ctk.CTkButton(cart_panel, text="Bersihkan Keranjang", fg_color=self.COLORS["WARNING"], command=lambda: self.clear_cart(listbox, total_label))
        btn_clear.pack(padx=10, pady=6, fill="x")
        btn_checkout = ctk.CTkButton(cart_panel, text="Checkout", fg_color=self.COLORS["PRIMARY"], command=lambda: self.checkout(listbox, total_label))
        btn_checkout.pack(padx=10, pady=6, fill="x")

        # Scrollable list for menu (wider, uses CTkScrollableFrame so visuals follow theme)
        scroll_frame = CTkScrollableFrame(container, fg_color=container._fg_color)
        scroll_frame.pack(side="left", fill="both", expand=True, padx=(20,0), pady=10)

        # helper to refresh cart listbox
        def refresh_cartbox():
            listbox.delete(0, "end")
            total = 0
#PERULANGAN FOR Perulangan adalah proses pengulangan eksekusi kode tertentu berdasarkan kondisi yang ditentukan (313-319
            for entry in self.keranjang:
                nama = entry["menu"].nama
                harga = entry["menu"].harga
                qty = entry["qty"]
                listbox.insert("end", f"{nama} x{qty} - Rp {harga*qty:,}".replace(",", "."))
                total += harga * qty
            total_label.configure(text=f"Total: Rp {total:,}".replace(",", "."))
            self.current_cart_total = total

        # populate cards with optional filter & search
        def populate(kategori="Semua", keyword=""):
            # clear
            for w in scroll_frame.winfo_children():
                w.destroy()

            menus = self.manager.get_menu_by_kategori(kategori) if kategori and kategori != "Semua" else self.manager.get_semua_menu()
            if keyword.strip():
                kw = keyword.strip().lower()
                menus = [m for m in menus if kw in m.nama.lower()]

            # layout: vertical list of wide cards
            for m in menus:
                # choose a card background that's slightly different depending on mode
                card_bg = "#0b1220" if ctk.get_appearance_mode() == "Dark" else "#ffffff"
                card = ctk.CTkFrame(scroll_frame, fg_color=card_bg, corner_radius=10)
                card.pack(fill="x", padx=12, pady=8)

                # grid inside card: name/price/stok | qty | button
                card.grid_columnconfigure(0, weight=3)
                card.grid_columnconfigure(1, weight=1)
                card.grid_columnconfigure(2, weight=1)

                lbl_name = ctk.CTkLabel(card, text=m.nama, font=("Arial", 14, "bold"), text_color=self.COLORS["TEXT"])
                lbl_name.grid(row=0, column=0, sticky="w", padx=10, pady=(8,0))
                lbl_price = ctk.CTkLabel(card, text=f"Rp {m.harga:,}".replace(",", "."), font=("Arial", 12), text_color=self.COLORS["TEXT"])
                lbl_price.grid(row=1, column=0, sticky="w", padx=10)
                lbl_kat = ctk.CTkLabel(card, text=f"Kategori: {m.kategori}", font=("Arial", 11), text_color=self.COLORS["SUBTEXT"])
                lbl_kat.grid(row=0, column=1, sticky="e", padx=6)
                lbl_stok = ctk.CTkLabel(card, text=f"Stok: {m.stok}", font=("Arial", 11), text_color=self.COLORS["SUBTEXT"])
                lbl_stok.grid(row=1, column=1, sticky="e", padx=6)

                # qty spin & add button
                qty_spin = tk.Spinbox(card, from_=1, to=max(1, m.stok), width=4)
                qty_spin.grid(row=0, column=2, rowspan=2, padx=6, pady=8)
                def add_local(menu_item=m, spin=qty_spin):
                    try:
                        q = int(spin.get())
                    except:
                        q = 1
                    if q > menu_item.stok:
                        messagebox.showerror("Stok Habis", f"Stok untuk {menu_item.nama} tidak mencukupi.")
                        return
                    # merge into cart
                    found = False
                    for e in self.keranjang:
                        if e["menu"].nama == menu_item.nama:
                            if e["qty"] + q > menu_item.stok:
                                messagebox.showerror("Stok Habis", "Jumlah melebihi stok tersedia.")
                                return
                            e["qty"] += q
                            found = True
                            break
                    if not found:
                        self.keranjang.append({"menu": menu_item, "qty": q})
                    refresh_cartbox()

                btn_add = ctk.CTkButton(card, text="Tambah", width=100, command=add_local)
                btn_add.grid(row=0, column=3, rowspan=2, padx=10, pady=8)

        # initial populate using provided filter
        populate(filter_kategori if filter_kategori else "Semua")

        # bind search and combo
        search_entry.bind("<KeyRelease>", lambda e: populate(combo.get(), search_entry.get()))
        combo.configure(command=lambda v: populate(v, search_entry.get()))

        # store references
        self.frame_pemesanan = container

    # cart helpers (used by multiple pages)
    def refresh_cart_listbox(self, listbox_widget, label_total_widget):
        # kept for backward compatibility (not used directly since we have local refresh)
        listbox_widget.delete(0, "end")
        total = 0
        for entry in self.keranjang:
            nama = entry["menu"].nama
            harga = entry["menu"].harga
            qty = entry["qty"]
            listbox_widget.insert("end", f"{nama} x{qty} - Rp {harga*qty:,}".replace(",", ".")) 
            total += harga * qty
        label_total_widget.configure(text=f"Total: Rp {total:,}".replace(",", "."))
        self.current_cart_total = total

    def clear_cart(self, listbox_widget, label_total_widget):
        if messagebox.askyesno("Konfirmasi", "Bersihkan seluruh keranjang?"):
            self.keranjang.clear()
            listbox_widget.delete(0, "end")
            label_total_widget.configure(text="Total: Rp 0")

    def format_struk(self, order: Order) -> str:
        lines = []
        lines.append("====== STRUK KANTIN ======")
        lines.append(f"Tanggal : {order.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        # meja may exist on order (backend sets it); if not, show dash
        meja_val = getattr(order, "meja", "-")
        lines.append(f"Nomor Meja : {meja_val}")
        lines.append(f"Pembeli    : {order.buyer_name}")
        lines.append("--------------------------")
        for it in order.items:
            lines.append(f"{it.menu_item.nama} x{it.qty} - Rp {it.subtotal:,}".replace(",", "."))
        lines.append("--------------------------")
        lines.append(f"Subtotal : Rp {order.subtotal:,}".replace(",", "."))
        lines.append(f"Pajak 10%: Rp {order.pajak:,}".replace(",", "."))
        lines.append(f"Total    : Rp {order.total:,}".replace(",", "."))
        lines.append("==========================")
        return "\n".join(lines)

    def checkout(self, listbox_widget, label_total_widget):
        if not self.keranjang:
            messagebox.showwarning("Kosong", "Keranjang kosong.")
            return
        # ask for buyer name (optional). No meja input: backend akan generate meja
        buyer = simpledialog.askstring("Nama Pembeli", "Masukkan nama pembeli: ")
        # build OrderItems
        items = []
        for entry in self.keranjang:
            menu_item = entry["menu"]
            qty = entry["qty"]
            if qty > menu_item.stok:
                messagebox.showerror("Stok Tidak Cukup", f"Stok {menu_item.nama} tidak mencukupi.")
                return
            items.append(OrderItem(menu_item, qty))

        buyer_name = buyer.strip() if buyer and buyer.strip() else "Tamu"

        order = Order(buyer_name, items)
        # set meja attribute if backend does not (frontend can set placeholder), but backend is expected to generate meja
        if not hasattr(order, "meja"):
            # fallback meja: use timestamp seconds to make a small unique number
            order.meja = datetime.now().strftime("%H%M%S")
        success = self.manager.simpan_order(order)
        if success:
            # show struk to guest and admin will also see it in Riwayat
            struk = self.format_struk(order)
            messagebox.showinfo("Struk Pembelian", struk)
            # clear cart visuals
            self.keranjang.clear()
            listbox_widget.delete(0, "end")
            label_total_widget.configure(text="Total: Rp 0")
            # refresh pemesanan (stok updated)
            self.show_pemesanan("Semua")
        else:
            messagebox.showerror("Gagal", "Order gagal. Periksa stok item atau sistem.")

    # ---------------- Kelola Menu Page (Admin) ----------------
    def show_kelola(self):
        if not self.is_admin:
            return
        self.clear_main()
        frame = ctk.CTkFrame(self.main_area, fg_color=self.COLORS["CARD"], corner_radius=12)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        header = ctk.CTkLabel(frame, text="Kelola Menu", font=("Arial", 18, "bold"), text_color=self.COLORS["TEXT"])
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

        btn_add = ctk.CTkButton(form, text="+ Tambah", fg_color=self.COLORS["SUCCESS"], command=lambda: self.admin_add_menu(entry_nama, entry_harga, combo_kat, entry_stok))
        btn_add.grid(row=0, column=4, padx=6)
        btn_update = ctk.CTkButton(form, text="Update", fg_color=self.COLORS["WARNING"], command=lambda: self.admin_update_menu(entry_nama, entry_harga, combo_kat, entry_stok))
        btn_update.grid(row=0, column=5, padx=6)
        btn_delete = ctk.CTkButton(form, text="Hapus", fg_color=self.COLORS["DANGER"], command=lambda: self.admin_delete_menu(entry_nama))
        btn_delete.grid(row=0, column=6, padx=6)
        btn_export = ctk.CTkButton(form, text="Export CSV", fg_color=self.COLORS["PRIMARY"], command=lambda: self.manager.export_ke_csv() and messagebox.showinfo("Export", "Data menu diexport ke CSV"))
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
        try:
            tree = self.frame_kelola.winfo_children()[-1]
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
        frame = ctk.CTkFrame(self.main_area, fg_color=self.COLORS["CARD"], corner_radius=12)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        header = ctk.CTkLabel(frame, text="Riwayat Pesanan", font=("Arial", 18, "bold"), text_color=self.COLORS["TEXT"])
        header.pack(anchor="w", padx=20, pady=10)

        cols = ("waktu", "meja", "pembeli", "items", "total", "status")
        tree = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c.upper())
        tree.pack(fill="both", expand=True, padx=20, pady=10)

        # insert orders and use timestamp as iid (unique enough)
        for o in self.manager.get_orders_history():
            items_text = ", ".join([f"{it.menu_item.nama}x{it.qty}" for it in o.items])
            iid = o.timestamp.strftime("%Y%m%d%H%M%S")
            meja_display = getattr(o, "meja", "-")
            tree.insert("", "end", iid=iid, values=(o.timestamp.strftime("%Y-%m-%d %H:%M:%S"), meja_display, o.buyer_name, items_text, f"Rp {o.total:,}".replace(",", "."), o.status))

        def on_double_click(event):
            sel = tree.selection()
            if not sel:
                return
            iid = sel[0]
            # find order by matching timestamp string in iid
            try:
                ts = datetime.strptime(iid, "%Y%m%d%H%M%S")
            except Exception:
                # fallback: try reading value
                vals = tree.item(iid)["values"]
                ts_str = vals[0]
                try:
                    ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                except Exception:
                    ts = None
            target = None
            for ord_obj in self.manager.get_orders_history():
                if ts and ord_obj.timestamp.strftime("%Y%m%d%H%M%S") == iid:
                    target = ord_obj
                    break
            if not target:
                # fallback: use first selected row values to find by buyer+total+timestamp string
                vals = tree.item(iid)["values"]
                ts_val = vals[0]
                for ord_obj in self.manager.get_orders_history():
                    if ord_obj.timestamp.strftime("%Y-%m-%d %H:%M:%S") == ts_val:
                        target = ord_obj
                        break
            if target:
                struk = self.format_struk(target)
                # show in a scrollable popup
                top = tk.Toplevel(self)
                top.title(f"Struk - Meja {getattr(target, 'meja', '-')}")
                txt = tk.Text(top, width=60, height=20)
                txt.insert("1.0", struk)
                txt.configure(state="disabled")
                txt.pack(padx=10, pady=10)
                btn_close = ctk.CTkButton(top, text="Tutup", command=top.destroy)
                btn_close.pack(pady=(0,10))
        tree.bind("<Double-1>", on_double_click)

        self.frame_riwayat = frame

    # ---------------- Laporan Page ----------------
    def show_laporan(self):
        if not self.is_admin:
            return
        self.clear_main()
        frame = ctk.CTkFrame(self.main_area, fg_color=self.COLORS["CARD"], corner_radius=12)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        header = ctk.CTkLabel(frame, text="Laporan Penjualan", font=("Arial", 18, "bold"), text_color=self.COLORS["TEXT"])
        header.pack(anchor="w", padx=20, pady=10)

        stats = self.manager.hitung_total_penjualan()
        ctk.CTkLabel(frame, text=f"Total Pesanan: {stats['total_orders']}", font=("Arial", 14), text_color=self.COLORS["TEXT"]).pack(anchor="w", padx=20, pady=(10,0))
        ctk.CTkLabel(frame, text=f"Total Pendapatan (termasuk pajak): Rp {stats['total_revenue']:,}".replace(",", "."), font=("Arial", 14), text_color=self.COLORS["TEXT"]).pack(anchor="w", padx=20, pady=(6,0))

        # grafik sederhana kategori
        data = self.manager.get_data_grafik()
        fig = Figure(figsize=(5,3), dpi=100)
        ax = fig.add_subplot(111)
        keys = list(data.keys())
        vals = list(data.values())
        ax.bar(keys, vals)
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
