# backend.py
import csv
import os
from datetime import datetime
from typing import List, Dict

FILE_DB = "data_kantin.csv"
FILE_ORDERS = "orders_history.csv"

# -------------------------
# OOP: MenuItem (encapsulation)
# -------------------------
class MenuItem:
    def __init__(self, nama: str, harga: int, kategori: str, stok: int = 0):
        # private attributes
        self._nama = str(nama)
        self._harga = int(harga)
        self._kategori = str(kategori)
        self._stok = int(stok)

    # getters / setters (encapsulation)
    @property
    def nama(self):
        return self._nama

    @nama.setter
    def nama(self, v):
        self._nama = str(v)

    @property
    def harga(self):
        return self._harga

    @harga.setter
    def harga(self, v):
        self._harga = int(v)

    @property
    def kategori(self):
        return self._kategori

    @kategori.setter
    def kategori(self, v):
        self._kategori = str(v)

    @property
    def stok(self):
        return self._stok

    @stok.setter
    def stok(self, v):
        self._stok = int(v)

    def reduce_stok(self, qty: int) -> bool:
        """Kurangi stok jika cukup, kembalikan True jika berhasil"""
        if qty <= self._stok:
            self._stok -= qty
            return True
        return False

    def increase_stok(self, qty: int):
        self._stok += int(qty)

    def to_row(self):
        return [self._nama, str(self._harga), self._kategori, str(self._stok)]

# -------------------------
# OOP: OrderItem & Order
# -------------------------
class OrderItem:
    def __init__(self, menu_item: MenuItem, qty: int):
        self.menu_item = menu_item
        self.qty = int(qty)

    @property
    def subtotal(self):
        return self.menu_item.harga * self.qty

    def to_dict(self):
        return {"nama": self.menu_item.nama, "harga": self.menu_item.harga, "qty": self.qty, "subtotal": self.subtotal}

class Order:
    TAX_RATE = 0.10

    def __init__(self, buyer_name: str, items: List[OrderItem]):
        self.buyer_name = buyer_name
        self.items = items  # list of OrderItem
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
        # store as: timestamp, buyer, total, pajak, status, items_serialized
        items_ser = ";".join([f"{i.menu_item.nama}|{i.qty}|{i.menu_item.harga}" for i in self.items])
        return [self.timestamp.strftime("%Y-%m-%d %H:%M:%S"), self.buyer_name, str(self.subtotal), str(self.pajak), str(self.total), self.status, items_ser]

# -------------------------
# KantinManager
# -------------------------
class KantinManager:
    def __init__(self):
        self.daftar_menu: List[MenuItem] = []
        self.orders_history: List[Order] = []
        self.load_data_awal()
        self.load_orders_history()

    # --------------- data menu ---------------
    def load_data_awal(self):
        if os.path.exists(FILE_DB):
            try:
                with open(FILE_DB, newline='', mode='r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    header = next(reader, None)
                    for row in reader:
                        # expect: nama,harga,kategori,stok
                        if len(row) >= 4:
                            nama, harga, kategori, stok = row[0], row[1], row[2], row[3]
                            try:
                                self.tambah_menu(nama, int(harga), kategori, int(stok))
                            except Exception:
                                continue
            except Exception:
                self.buat_data_dummy()
        else:
            self.buat_data_dummy()
            self.export_ke_csv()

    def buat_data_dummy(self):
        self.daftar_menu = []
        self.tambah_menu("Nasi Goreng Spesial", 18000, "Makanan", 10)
        self.tambah_menu("Ayam Geprek", 15000, "Makanan", 15)
        self.tambah_menu("Es Teh Manis", 4000, "Minuman", 30)
        self.tambah_menu("Kopi Susu Gula Aren", 12000, "Minuman", 20)
        self.tambah_menu("Kentang Goreng", 8000, "Snack", 12)
        self.export_ke_csv()

    def tambah_menu(self, nama: str, harga: int, kategori: str, stok: int = 0):
        self.daftar_menu.append(MenuItem(nama, int(harga), kategori, int(stok)))

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
        return [m for m in self.daftar_menu if m.kategori.lower() == kategori.lower()]

    def get_semua_menu(self) -> List[MenuItem]:
        return self.daftar_menu

    # --------------- export/import ---------------
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

    # --------------- login sederhana ---------------
    def cek_login(self, username: str, password: str) -> bool:
        # placeholder simple auth
        return username == "admin" and password == "123"

    # --------------- orders & history ---------------
    def load_orders_history(self):
        self.orders_history = []
        if os.path.exists(FILE_ORDERS):
            try:
                with open(FILE_ORDERS, newline='', mode='r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    next(reader, None)
                    for row in reader:
                        # row: timestamp, buyer, subtotal, pajak, total, status, items_ser
                        if len(row) >= 7:
                            # reconstruct Order object (basic)
                            timestamp_s, buyer, subtotal_s, pajak_s, total_s, status, items_ser = row[:7]
                            # parse items
                            items = []
                            for it in items_ser.split(";"):
                                parts = it.split("|")
                                if len(parts) == 3:
                                    nama, qty_s, harga_s = parts
                                    # find menu by name to get MenuItem reference (stok may differ)
                                    menu_ref = next((x for x in self.daftar_menu if x.nama == nama), None)
                                    if menu_ref:
                                        items.append(OrderItem(menu_ref, int(qty_s)))
                            if items:
                                ord_obj = Order(buyer, items)
                                ord_obj.timestamp = datetime.strptime(timestamp_s, "%Y-%m-%d %H:%M:%S")
                                ord_obj.status = status
                                self.orders_history.append(ord_obj)
            except Exception:
                pass

    def simpan_order(self, order: Order) -> bool:
        # reduce stok atomically (check first)
        for it in order.items:
            if it.qty > it.menu_item.stok:
                return False  # stok tidak cukup

        # jika semua cukup, kurangi stok
        for it in order.items:
            it.menu_item.reduce_stok(it.qty)

        # simpan order ke history list dan file CSV
        self.orders_history.append(order)
        self._append_order_to_csv(order)
        # update master menu csv
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

    # --------------- laporan ---------------
    def hitung_total_penjualan(self) -> Dict[str, int]:
        total_orders = len(self.orders_history)
        total_revenue = sum(o.total for o in self.orders_history)
        return {"total_orders": total_orders, "total_revenue": int(total_revenue)}

    def get_orders_history(self) -> List[Order]:
        # latest first
        return sorted(self.orders_history, key=lambda x: x.timestamp, reverse=True)

    # --------------- util ---------------
    def get_data_grafik(self):
        data = {}
        for menu in self.daftar_menu:
            data[menu.kategori] = data.get(menu.kategori, 0) + 1
        return data
