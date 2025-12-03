# backend.py — Restored full-featured backend (copy this file content into backend.py)

import csv
import os
from datetime import datetime
from typing import List

FILE_DB = "data_kantin.csv"
FILE_ORDERS = "orders_history.csv"

# -------------------------
# MenuItem
# -------------------------
class MenuItem:
    def __init__(self, nama: str, harga: int, kategori: str, stok: int = 0):
        self.nama = str(nama)
        self.harga = int(harga)
        self.kategori = str(kategori)
        self.stok = int(stok)

    def reduce_stok(self, qty: int) -> bool:
        if qty <= self.stok:
            self.stok -= qty
            return True
        return False

    def increase_stok(self, qty: int):
        self.stok += int(qty)

    def to_row(self):
        return [self.nama, str(self.harga), self.kategori, str(self.stok)]

# -------------------------
# OrderItem & Order
# -------------------------
class OrderItem:
    def __init__(self, menu_item: MenuItem, qty: int):
        self.menu_item = menu_item
        self.qty = int(qty)

    @property
    def subtotal(self):
        return self.menu_item.harga * self.qty

class Order:
    TAX_RATE = 0.10

    def __init__(self, buyer_name: str, items: List[OrderItem]):
        self.buyer_name = buyer_name
        self.items = items[:]  # copy
        self.timestamp = datetime.now()
        self.status = "Selesai"

    @property
    def subtotal(self):
        return sum(item.subtotal for item in self.items)

    @property
    def pajak(self):
        return int(self.subtotal * Order.TAX_RATE)

    @property
    def total(self):
        return self.subtotal + self.pajak

    def to_row(self):
        items_ser = ";".join([f"{i.menu_item.nama}|{i.qty}|{i.menu_item.harga}" for i in self.items])
        return [self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                self.buyer_name,
                str(self.subtotal),
                str(self.pajak),
                str(self.total),
                self.status,
                items_ser]

# -------------------------
# Cart
# -------------------------
class CartItem:
    def __init__(self, menu_item: MenuItem, qty: int):
        self.menu_item = menu_item
        self.qty = int(qty)

    @property
    def subtotal(self):
        return self.menu_item.harga * self.qty

class Cart:
    def __init__(self):
        self.items: List[CartItem] = []

    def add(self, menu_item: MenuItem, qty: int):
        if qty <= 0:
            return False
        # check stock
        if qty > menu_item.stok:
            return False
        for it in self.items:
            if it.menu_item.nama == menu_item.nama:
                if it.qty + qty > menu_item.stok:
                    return False
                it.qty += qty
                return True
        self.items.append(CartItem(menu_item, qty))
        return True

    def remove(self, nama_menu: str):
        self.items = [it for it in self.items if it.menu_item.nama != nama_menu]

    def clear(self):
        self.items.clear()

    @property
    def subtotal(self):
        return sum(it.subtotal for it in self.items)

    @property
    def pajak(self):
        return int(self.subtotal * Order.TAX_RATE)

    @property
    def total(self):
        return self.subtotal + self.pajak

    def to_order_items(self):
        return [OrderItem(it.menu_item, it.qty) for it in self.items]

# -------------------------
# KantinManager
# -------------------------
class KantinManager:
    def __init__(self):
        self.daftar_menu: List[MenuItem] = []
        self.orders_history: List[Order] = []
        self._ensure_files()
        self.load_data_awal()
        self.load_orders_history()

    def _ensure_files(self):
        if not os.path.exists(FILE_DB):
            # create with sample data
            with open(FILE_DB, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Nama","Harga","Kategori","Stok"])
                writer.writerow(["Nasi Goreng Spesial","18000","Makanan","10"])
                writer.writerow(["Ayam Geprek","15000","Makanan","15"])
                writer.writerow(["Es Teh Manis","4000","Minuman","30"])
            # leave orders file creation to when needed

    # -------------------------
    # Data menu
    # -------------------------
    def load_data_awal(self):
        self.daftar_menu = []
        if os.path.exists(FILE_DB):
            try:
                with open(FILE_DB, newline='', mode='r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    next(reader, None)
                    for row in reader:
                        if len(row) >= 4:
                            nama,harga,kategori,stok = row[0], row[1], row[2], row[3]
                            try:
                                self.tambah_menu(nama, int(harga), kategori, int(stok))
                            except Exception:
                                continue
            except Exception:
                # fallback sample
                self._load_sample()
        else:
            self._load_sample()
            self.export_ke_csv()

    def _load_sample(self):
        self.daftar_menu = []
        self.tambah_menu("Nasi Goreng Spesial", 18000, "Makanan", 10)
        self.tambah_menu("Ayam Geprek", 15000, "Makanan", 15)
        self.tambah_menu("Es Teh Manis", 4000, "Minuman", 30)
        self.tambah_menu("Kopi Susu Gula Aren", 12000, "Minuman", 20)
        self.tambah_menu("Kentang Goreng", 8000, "Snack", 12)

    def tambah_menu(self, nama: str, harga: int, kategori: str, stok: int = 0):
        self.daftar_menu.append(MenuItem(nama, harga, kategori, stok))

    def edit_menu(self, nama_lama: str, nama_baru: str, harga_baru: int, kategori_baru: str, stok_baru: int) -> bool:
        for m in self.daftar_menu:
            if m.nama == nama_lama:
                m.nama = nama_baru
                m.harga = int(harga_baru)
                m.kategori = kategori_baru
                m.stok = int(stok_baru)
                return True
        return False

    def hapus_menu(self, nama_menu: str):
        self.daftar_menu = [m for m in self.daftar_menu if m.nama != nama_menu]

    def cari_menu(self, kata_kunci: str) -> List[MenuItem]:
        return [m for m in self.daftar_menu if kata_kunci.strip().lower() in m.nama.lower()]

    def filter_kategori(self, kategori: str) -> List[MenuItem]:
        if kategori.lower() == "semua":
            return self.daftar_menu
        return [m for m in self.daftar_menu if m.kategori.lower() == kategori.lower()]

    def get_semua_menu(self) -> List[MenuItem]:
        return self.daftar_menu

    # -------------------------
    # export/import
    # -------------------------
    def export_ke_csv(self, filename: str = FILE_DB) -> bool:
        try:
            with open(filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Nama", "Harga", "Kategori", "Stok"])
                for m in self.daftar_menu:
                    writer.writerow([m.nama, m.harga, m.kategori, m.stok])
            return True
        except Exception as e:
            print("Export error:", e)
            return False

    # -------------------------
    # simple auth
    # -------------------------
    def cek_login(self, username: str, password: str) -> bool:
        return username == "admin" and password == "123"

    # -------------------------
    # orders & history
    # -------------------------
    def load_orders_history(self):
        self.orders_history = []
        if os.path.exists(FILE_ORDERS):
            try:
                with open(FILE_ORDERS, newline='', mode='r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    next(reader, None)
                    for row in reader:
                        if len(row) >= 7:
                            timestamp_s, buyer, subtotal_s, pajak_s, total_s, status, items_ser = row[:7]
                            items = []
                            for it in items_ser.split(";"):
                                parts = it.split("|")
                                if len(parts) == 3:
                                    nama, qty_s, harga_s = parts
                                    menu_ref = next((x for x in self.daftar_menu if x.nama == nama), None)
                                    if menu_ref:
                                        items.append(OrderItem(menu_ref, int(qty_s)))
                            if items:
                                ord_obj = Order(buyer, items)
                                # try parse timestamp
                                try:
                                    ord_obj.timestamp = datetime.strptime(timestamp_s, "%Y-%m-%d %H:%M:%S")
                                except:
                                    ord_obj.timestamp = datetime.now()
                                ord_obj.status = status
                                self.orders_history.append(ord_obj)
            except Exception:
                pass

    def simpan_order(self, order: Order) -> bool:
        # check stock
        for it in order.items:
            if it.qty > it.menu_item.stok:
                return False
        # reduce
        for it in order.items:
            it.menu_item.reduce_stok(it.qty)
        # append & save
        self.orders_history.append(order)
        self._append_order_to_csv(order)
        self.export_ke_csv()
        return True

    def _append_order_to_csv(self, order: Order):
        header_needed = not os.path.exists(FILE_ORDERS)
        try:
            with open(FILE_ORDERS, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if header_needed:
                    writer.writerow(["Timestamp", "Buyer", "Subtotal", "Pajak", "Total", "Status", "Items"])
                writer.writerow(order.to_row())
        except Exception as e:
            print("Order save error:", e)

    # -------------------------
    # proses checkout (dari Cart)
    # -------------------------
    def proses_checkout(self, buyer_name: str, cart: Cart) -> Order | None:
        if not cart.items:
            return None
        # check stock
        for c in cart.items:
            if c.qty > c.menu_item.stok:
                return None
        # create order
        order = Order(buyer_name, cart.to_order_items())
        # save via simpan_order
        if not self.simpan_order(order):
            return None
        return order

    # -------------------------
    # struk
    # -------------------------
    def generate_struk(self, order: Order) -> str:
        lines = []
        lines.append("======= STRUK PEMBELIAN =======")
        lines.append(f"Nama Pembeli : {order.buyer_name}")
        lines.append(f"Waktu        : {order.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("--------------------------------")
        for item in order.items:
            lines.append(f"{item.menu_item.nama} x{item.qty}  = Rp{item.subtotal:,}".replace(",","."))

        lines.append("--------------------------------")
        lines.append(f"Subtotal : Rp{order.subtotal:,}".replace(",","."))
        lines.append(f"Pajak    : Rp{order.pajak:,}".replace(",","."))
        lines.append(f"TOTAL    : Rp{order.total:,}".replace(",","."))
        lines.append("================================")
        return "\n".join(lines)

    # -------------------------
    # laporan
    # -------------------------
    def hitung_total_penjualan(self):
        total_orders = len(self.orders_history)
        total_revenue = int(sum(o.total for o in self.orders_history))
        return {"total_orders": total_orders, "total_revenue": total_revenue}

    def get_orders_history(self) -> List[Order]:
        return sorted(self.orders_history, key=lambda x: x.timestamp, reverse=True)

    def get_data_grafik(self):
        data = {}
        for m in self.daftar_menu:
            data[m.kategori] = data.get(m.kategori, 0) + 1
        return data
