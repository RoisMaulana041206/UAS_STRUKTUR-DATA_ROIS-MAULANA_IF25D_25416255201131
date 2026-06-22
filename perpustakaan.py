# SISTEM PERPUSTAKAAN SEDERHANA
# Struktur Data: Hash Map (dict), Sorting, Searching, Queue (deque)
# Database: 1 file CSV (perpustakaan.csv)
# Kolom CSV: tipe, f1, f2, f3, f4, f5
#   tipe=buku    -> f1=kode, f2=judul,     f3=penulis, f4=tahun, f5=stok
#   tipe=anggota -> f1=id,   f2=nama,      f3=no_hp,   f4=,      f5=
#   tipe=antrian -> f1=kode_buku, f2=id_anggota, f3=, f4=, f5=

import csv
import os
from collections import deque

FILE_DB = "perpustakaan.csv"
HEADER  = ["tipe", "f1", "f2", "f3", "f4", "f5"]

# ─── FILE INIT ────────────────────────────────────────────────────────────────
def init_file():
    if not os.path.exists(FILE_DB):
        with open(FILE_DB, "w", newline="") as f:
            csv.writer(f).writerow(HEADER)

# ─── BACA / TULIS ─────────────────────────────────────────────────────────────
def baca_semua():
    with open(FILE_DB, newline="") as f:
        return list(csv.DictReader(f))

def tulis_semua(rows):
    with open(FILE_DB, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADER)
        writer.writeheader()
        writer.writerows(rows)

# ─── KONVERSI ─────────────────────────────────────────────────────────────────
def row_ke_buku(r):
    return {"kode": r["f1"], "judul": r["f2"], "penulis": r["f3"],
            "tahun": r["f4"], "stok": int(r["f5"])}

def buku_ke_row(b):
    return {"tipe": "buku", "f1": b["kode"], "f2": b["judul"],
            "f3": b["penulis"], "f4": b["tahun"], "f5": str(b["stok"])}

def row_ke_anggota(r):
    return {"id": r["f1"], "nama": r["f2"], "no_hp": r["f3"]}

def anggota_ke_row(a):
    return {"tipe": "anggota", "f1": a["id"], "f2": a["nama"],
            "f3": a["no_hp"], "f4": "", "f5": ""}

def row_ke_antrian(r):
    return (r["f1"], r["f2"])  # (kode_buku, id_anggota)

def antrian_ke_row(kode, id_a):
    return {"tipe": "antrian", "f1": kode, "f2": id_a, "f3": "", "f4": "", "f5": ""}

# ─── HASH MAP : BUKU ──────────────────────────────────────────────────────────
def muat_buku():
    hm = {}
    for r in baca_semua():
        if r["tipe"] == "buku":
            b = row_ke_buku(r)
            hm[b["kode"]] = {k: v for k, v in b.items() if k != "kode"}
    return hm

def simpan_buku(hm):
    rows = [r for r in baca_semua() if r["tipe"] != "buku"]
    rows += [buku_ke_row({"kode": k, **v}) for k, v in hm.items()]
    tulis_semua(rows)

# ─── HASH MAP : ANGGOTA ───────────────────────────────────────────────────────
def muat_anggota():
    hm = {}
    for r in baca_semua():
        if r["tipe"] == "anggota":
            a = row_ke_anggota(r)
            hm[a["id"]] = {k: v for k, v in a.items() if k != "id"}
    return hm

def simpan_anggota(hm):
    rows = [r for r in baca_semua() if r["tipe"] != "anggota"]
    rows += [anggota_ke_row({"id": k, **v}) for k, v in hm.items()]
    tulis_semua(rows)

# ─── QUEUE : ANTRIAN ──────────────────────────────────────────────────────────
def muat_antrian():
    return deque(row_ke_antrian(r) for r in baca_semua() if r["tipe"] == "antrian")

def simpan_antrian(q):
    rows = [r for r in baca_semua() if r["tipe"] != "antrian"]
    rows += [antrian_ke_row(k, a) for k, a in q]
    tulis_semua(rows)

# ─── SORTING ───────────────────────────────────────────────────────────────
def sorting(data, key):
    if len(data) <= 1:
        return data
    mid = len(data) // 2
    L = sorting(data[:mid], key)
    R = sorting(data[mid:], key)
    hasil, i, j = [], 0, 0
    while i < len(L) and j < len(R):
        if L[i][key].lower() <= R[j][key].lower():
            hasil.append(L[i]); i += 1
        else:
            hasil.append(R[j]); j += 1
    return hasil + L[i:] + R[j:]

# ─── SEARCHING ────────────────────────────────────────────────────────────
def searching(data_terurut, judul):
    lo, hi = 0, len(data_terurut) - 1
    judul = judul.lower()
    while lo <= hi:
        mid = (lo + hi) // 2
        j = data_terurut[mid]["judul"].lower()
        if j == judul:
            return data_terurut[mid]
        elif j < judul:
            lo = mid + 1
        else:
            hi = mid - 1
    return None

# ─── PROSES ANTRIAN ───────────────────────────────────────────────────────────
def proses_antrian(kode, hm_buku):
    q = muat_antrian()
    sisa = deque()
    dilayani = False
    while q:
        k, a = q.popleft()
        if k == kode and not dilayani and hm_buku[kode]["stok"] > 0:
            hm_buku[kode]["stok"] -= 1
            print(f">> Antrian: anggota {a} otomatis pinjam '{kode}' (sisa stok {hm_buku[kode]['stok']})")
            dilayani = True
        else:
            sisa.append((k, a))
    simpan_antrian(sisa)
    simpan_buku(hm_buku)

# ─── CRUD BUKU ────────────────────────────────────────────────────────────────
def cetak_buku(daftar):
    print(f"\n{'KODE':<8}{'JUDUL':<22}{'PENULIS':<16}{'TAHUN':<7}{'STOK':<5}")
    print("-" * 58)
    for b in daftar:
        print(f"{b['kode']:<8}{b['judul']:<22}{b['penulis']:<16}{b['tahun']:<7}{b['stok']:<5}")

def tambah_buku():
    hm = muat_buku()
    kode = input("Kode   : ").strip()
    if kode in hm:
        print("!! Kode sudah ada."); return
    judul   = input("Judul  : ").strip()
    penulis = input("Penulis: ").strip()
    tahun   = input("Tahun  : ").strip()
    stok    = input("Stok   : ").strip()
    if not (tahun.isdigit() and stok.isdigit()):
        print("!! Tahun/stok harus angka."); return
    hm[kode] = {"judul": judul, "penulis": penulis, "tahun": tahun, "stok": int(stok)}
    simpan_buku(hm)
    print(">> Buku ditambahkan.")

def lihat_buku():
    hm = muat_buku()
    if not hm:
        print("Belum ada buku."); return
    daftar = [{"kode": k, **v} for k, v in hm.items()]
    cetak_buku(sorting(daftar, "judul"))

def cari_buku():
    hm = muat_buku()
    if not hm:
        print("Belum ada buku."); return
    daftar  = [{"kode": k, **v} for k, v in hm.items()]
    terurut = sorting(daftar, "judul")
    judul   = input("Judul yang dicari: ").strip()
    hasil   = searching(terurut, judul)
    if hasil:
        cetak_buku([hasil])
    else:
        print(">> Tidak ditemukan.")

def ubah_buku():
    hm = muat_buku()
    kode = input("Kode buku: ").strip()
    if kode not in hm:
        print("!! Tidak ditemukan."); return
    b = hm[kode]
    judul   = input(f"Judul ({b['judul']}): ").strip()
    penulis = input(f"Penulis ({b['penulis']}): ").strip()
    tahun   = input(f"Tahun ({b['tahun']}): ").strip()
    stok    = input(f"Stok ({b['stok']}): ").strip()
    if judul:         b["judul"]   = judul
    if penulis:       b["penulis"] = penulis
    if tahun.isdigit(): b["tahun"] = tahun
    if stok.isdigit():  b["stok"]  = int(stok)
    simpan_buku(hm)
    print(">> Buku diperbarui.")

def hapus_buku():
    hm = muat_buku()
    kode = input("Kode buku: ").strip()
    if kode not in hm:
        print("!! Tidak ditemukan."); return
    if input(f"Hapus '{hm[kode]['judul']}'? (y/n): ").lower() == "y":
        del hm[kode]
        simpan_buku(hm)
        print(">> Dihapus.")

# ─── CRUD ANGGOTA ─────────────────────────────────────────────────────────────
def tambah_anggota():
    hm = muat_anggota()
    id_a = input("ID    : ").strip()
    if id_a in hm:
        print("!! ID sudah ada."); return
    nama = input("Nama  : ").strip()
    hp   = input("No HP : ").strip()
    hm[id_a] = {"nama": nama, "no_hp": hp}
    simpan_anggota(hm)
    print(">> Anggota ditambahkan.")

def lihat_anggota():
    hm = muat_anggota()
    if not hm:
        print("Belum ada anggota."); return
    print(f"\n{'ID':<8}{'NAMA':<18}{'NO HP':<14}")
    print("-" * 40)
    for id_a, a in hm.items():
        print(f"{id_a:<8}{a['nama']:<18}{a['no_hp']:<14}")

def ubah_anggota():
    hm = muat_anggota()
    id_a = input("ID anggota: ").strip()
    if id_a not in hm:
        print("!! Tidak ditemukan."); return
    a    = hm[id_a]
    nama = input(f"Nama ({a['nama']}): ").strip()
    hp   = input(f"No HP ({a['no_hp']}): ").strip()
    if nama: a["nama"]  = nama
    if hp:   a["no_hp"] = hp
    simpan_anggota(hm)
    print(">> Anggota diperbarui.")

def hapus_anggota():
    hm = muat_anggota()
    id_a = input("ID anggota: ").strip()
    if id_a not in hm:
        print("!! Tidak ditemukan."); return
    if input(f"Hapus '{hm[id_a]['nama']}'? (y/n): ").lower() == "y":
        del hm[id_a]
        simpan_anggota(hm)
        print(">> Dihapus.")

# ─── PEMINJAMAN ───────────────────────────────────────────────────────────────
def pinjam_buku():
    hm_buku    = muat_buku()
    hm_anggota = muat_anggota()
    kode = input("Kode buku  : ").strip()
    id_a = input("ID anggota : ").strip()
    if kode not in hm_buku or id_a not in hm_anggota:
        print("!! Kode buku / ID anggota tidak ditemukan."); return
    if hm_buku[kode]["stok"] > 0:
        hm_buku[kode]["stok"] -= 1
        simpan_buku(hm_buku)
        print(f">> Dipinjam. Sisa stok: {hm_buku[kode]['stok']}")
    else:
        q = muat_antrian()
        q.append((kode, id_a))
        simpan_antrian(q)
        print(">> Stok kosong, dimasukkan ke antrian.")

def kembalikan_buku():
    hm_buku = muat_buku()
    kode    = input("Kode buku: ").strip()
    if kode not in hm_buku:
        print("!! Tidak ditemukan."); return
    hm_buku[kode]["stok"] += 1
    simpan_buku(hm_buku)
    print(f">> Dikembalikan. Stok: {hm_buku[kode]['stok']}")
    proses_antrian(kode, hm_buku)

def lihat_antrian():
    q = muat_antrian()
    if not q:
        print("Antrian kosong."); return
    print(f"\n{'NO':<4}{'KODE BUKU':<12}{'ID ANGGOTA':<12}")
    print("-" * 28)
    for i, (k, a) in enumerate(q, 1):
        print(f"{i:<4}{k:<12}{a:<12}")

# ─── MENU ─────────────────────────────────────────────────────────────────────
def menu_buku():
    while True:
        print("\n-- MENU BUKU --")
        print("1.Tambah  2.Lihat  3.Cari  4.Ubah  5.Hapus  0.Kembali")
        p = input("Pilih: ").strip()
        if   p == "1": tambah_buku()
        elif p == "2": lihat_buku()
        elif p == "3": cari_buku()
        elif p == "4": ubah_buku()
        elif p == "5": hapus_buku()
        elif p == "0": break
        else: print("!! Tidak valid.")

def menu_anggota():
    while True:
        print("\n-- MENU ANGGOTA --")
        print("1.Tambah  2.Lihat  3.Ubah  4.Hapus  0.Kembali")
        p = input("Pilih: ").strip()
        if   p == "1": tambah_anggota()
        elif p == "2": lihat_anggota()
        elif p == "3": ubah_anggota()
        elif p == "4": hapus_anggota()
        elif p == "0": break
        else: print("!! Tidak valid.")

def menu_peminjaman():
    while True:
        print("\n-- MENU PEMINJAMAN --")
        print("1.Pinjam  2.Kembalikan  3.Lihat Antrian  0.Kembali")
        p = input("Pilih: ").strip()
        if   p == "1": pinjam_buku()
        elif p == "2": kembalikan_buku()
        elif p == "3": lihat_antrian()
        elif p == "0": break
        else: print("!! Tidak valid.")

def main():
    init_file()
    while True:
        print("\n=== SISTEM PERPUSTAKAAN ===")
        print("1.Data Buku  2.Data Anggota  3.Peminjaman  0.Keluar")
        p = input("Pilih: ").strip()
        if   p == "1": menu_buku()
        elif p == "2": menu_anggota()
        elif p == "3": menu_peminjaman()
        elif p == "0": print("Sampai jumpa."); break
        else: print("!! Tidak valid.")

if __name__ == "__main__":
    main()
