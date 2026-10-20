# verifikasi.py
# Program untuk menguji fungsi pada bersihkan_data.py

from pathlib import Path
from bersihkan_data import (
    baca_data,
    bersihkan_data,
    seragamkan_satuan,
    seragamkan_tanggal,
)


def verifikasi():
    print("=" * 60)
    print("VERIFIKASI PEMBERSIHAN DATA")
    print("=" * 60)

    lulus = 0
    total = 0

    # Lokasi file dihitung dari lokasi script, bukan folder terminal.
    folder_kode = Path(__file__).resolve().parent
    file_data = folder_kode.parent / "data" / "data_produksi_kotor.csv"

    # Uji 1: Penyeragaman satuan
    total += 1
    hasil = seragamkan_satuan("Kilogram")
    status = hasil == "kg"
    if status:
        lulus += 1
    print(
        f" Uji 1: seragamkan_satuan('Kilogram') = '{hasil}' "
        f"-> {'LULUS' if status else 'GAGAL'}"
    )

    # Uji 2: Penyeragaman satuan 'kilo'
    total += 1
    hasil = seragamkan_satuan("kilo")
    status = hasil == "kg"
    if status:
        lulus += 1
    print(
        f" Uji 2: seragamkan_satuan('kilo') = '{hasil}' "
        f"-> {'LULUS' if status else 'GAGAL'}"
    )

    # Uji 3: Penyeragaman tanggal
    total += 1
    hasil = seragamkan_tanggal("01/01/2025")
    status = hasil == "2025-01-01"
    if status:
        lulus += 1
    print(
        f" Uji 3: seragamkan_tanggal('01/01/2025') = '{hasil}' "
        f"-> {'LULUS' if status else 'GAGAL'}"
    )

    # Uji 4: Penyeragaman tanggal format ISO
    total += 1
    hasil = seragamkan_tanggal("2025-01-05")
    status = hasil == "2025-01-05"
    if status:
        lulus += 1
    print(   
        f" Uji 4: seragamkan_tanggal('2025-01-05') = '{hasil}' "
        f"-> {'LULUS' if status else 'GAGAL'}"
    )

    # Uji 5 dan 6: Hasil pembersihan data dan jumlah log
    total += 1
    if not file_data.exists():
        print(f" Uji 5: File data tidak ditemukan: {file_data} -> GAGAL")
        print(" Uji 6: Jumlah log tidak dapat diperiksa karena file data tidak ada -> GAGAL")
        total += 1
    else:
        data_kotor = baca_data(file_data)
        log = []
        data_bersih = bersihkan_data(data_kotor, log)

        status = len(data_bersih) == 16
        if status:
            lulus += 1
        print(
            f" Uji 5: Jumlah data bersih = {len(data_bersih)} "
            f"(diharapkan 16) -> {'LULUS' if status else 'GAGAL'}"
        )

        total += 1
        status = len(log) == 8
        if status:
            lulus += 1
        print(
            f" Uji 6: Jumlah log = {len(log)} "
            f"(diharapkan 8) -> {'LULUS' if status else 'GAGAL'}"
        )

    print(f"\nTotal: {total} uji, Lulus: {lulus}, Gagal: {total - lulus}")
    persentase = (lulus / total * 100) if total else 0
    print(f"Persentase kelulusan: {persentase:.1f}%")


if __name__ == "__main__":
    verifikasi()