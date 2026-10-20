# bersihkan_data.py
# Modul untuk membaca dan membersihkan data produksi.

import csv
from datetime import datetime
from pathlib import Path

# Lokasi proyek otomatis ditentukan dari posisi file ini.
# Struktur yang disarankan:
# pertemuan_05/
# ├── data/data_produksi_kotor.csv
# ├── kode/bersihkan_data.py
# └── laporan/
LOKASI_KODE = Path(__file__).resolve().parent
if LOKASI_KODE.name.lower() == "kode":
    FOLDER_PROYEK = LOKASI_KODE.parent
else:
    FOLDER_PROYEK = LOKASI_KODE

FOLDER_DATA = FOLDER_PROYEK / "data"
FOLDER_LAPORAN = FOLDER_PROYEK / "laporan"
FILE_DATA_KOTOR = FOLDER_DATA / "data_produksi_kotor.csv"
FILE_DATA_BERSIH = FOLDER_DATA / "data_produksi_bersih.csv"
FILE_LOG = FOLDER_LAPORAN / "log_pembersihan.txt"


def baca_data(nama_berkas: Path) -> list[dict]:
    """Membaca data produksi dari berkas CSV."""
    if not nama_berkas.is_file():
        raise FileNotFoundError(
            f"Berkas tidak ditemukan: {nama_berkas}\n"
            "Pastikan file data_produksi_kotor.csv berada di folder data."
        )

    with nama_berkas.open(mode="r", encoding="utf-8-sig", newline="") as berkas:
        pembaca = csv.DictReader(berkas)
        if not pembaca.fieldnames:
            raise ValueError(f"Berkas CSV kosong atau tidak memiliki header: {nama_berkas}")
        # Hilangkan spasi dari nama kolom agar pencocokan kolom lebih aman.
        pembaca.fieldnames = [nama.strip().lower() for nama in pembaca.fieldnames]
        data = []
        for baris in pembaca:
            data.append({(k.strip().lower() if k else k): (v or "") for k, v in baris.items()})
    return data


def seragamkan_satuan(satuan: str) -> str:
    """Menyeragamkan satuan menjadi 'kg' atau 'liter'."""
    satuan_asli = (satuan or "").strip()
    nilai = satuan_asli.lower()
    if nilai in ("kg", "kilogram", "kilograms", "kilo", "kilos"):
        return "kg"
    if nilai in ("l", "liter", "litre", "liters", "litres"):
        return "liter"
    return satuan_asli


def seragamkan_tanggal(tanggal: str) -> str | None:
    """Mengubah format tanggal yang dikenal menjadi YYYY-MM-DD."""
    tanggal = (tanggal or "").strip()
    format_mungkin = (
        "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y",
        "%d %b %Y", "%d %B %Y", "%Y/%m/%d"
    )
    for fmt in format_mungkin:
        try:
            return datetime.strptime(tanggal, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return None


def bersihkan_data(data: list[dict], log: list[dict]) -> list[dict]:
    """Membersihkan satuan, tanggal, jumlah kosong/tidak valid, dan data ganda."""
    data_bersih = []
    kunci_terlihat = set()

    for nomor_baris, baris_asli in enumerate(data, start=1):
        baris = {
            kunci: nilai.strip() if isinstance(nilai, str) else nilai
            for kunci, nilai in baris_asli.items()
        }

        # 1. Seragamkan satuan.
        satuan_asli = baris.get("satuan", "")
        satuan_baru = seragamkan_satuan(satuan_asli)
        if satuan_asli != satuan_baru:
            log.append({
                "baris": nomor_baris,
                "masalah": f"Satuan tidak seragam: '{satuan_asli}'",
                "perlakuan": f"Diubah menjadi '{satuan_baru}'",
            })
            baris["satuan"] = satuan_baru

        # 2. Seragamkan tanggal.
        tanggal_asli = baris.get("tanggal", "")
        tanggal_baru = seragamkan_tanggal(tanggal_asli)
        if tanggal_baru is None:
            log.append({
                "baris": nomor_baris,
                "masalah": f"Format tanggal tidak dikenali: '{tanggal_asli}'",
                "perlakuan": "Baris dibuang",
            })
            continue
        if tanggal_asli != tanggal_baru:
            log.append({
                "baris": nomor_baris,
                "masalah": f"Format tanggal berbeda: '{tanggal_asli}'",
                "perlakuan": f"Diubah menjadi '{tanggal_baru}'",
            })
            baris["tanggal"] = tanggal_baru

        # 3. Validasi kolom jumlah.
        jumlah_asli = str(baris.get("jumlah", "")).strip()
        if jumlah_asli == "":
            log.append({
                "baris": nomor_baris,
                "masalah": "Nilai kosong pada kolom jumlah",
                "perlakuan": "Baris dibuang",
            })
            continue
        try:
            jumlah = int(jumlah_asli)
        except (TypeError, ValueError):
            log.append({
                "baris": nomor_baris,
                "masalah": f"Jumlah bukan bilangan: '{jumlah_asli}'",
                "perlakuan": "Baris dibuang",
            })
            continue

        # 4. Deteksi data ganda berdasarkan kolom yang tersedia.
        kunci = (
            baris.get("tanggal", ""),
            baris.get("liniproduksi", ""),
            baris.get("produk", ""),
            jumlah,
        )
        if kunci in kunci_terlihat:
            log.append({
                "baris": nomor_baris,
                "masalah": "Baris ganda",
                "perlakuan": "Baris dibuang",
            })
            continue
        kunci_terlihat.add(kunci)
        baris["jumlah"] = jumlah
        data_bersih.append(baris)

    return data_bersih


def simpan_data_bersih(data: list[dict], nama_berkas: Path) -> None:
    """Menyimpan hasil pembersihan ke CSV."""
    nama_berkas.parent.mkdir(parents=True, exist_ok=True)
    if not data:
        # Tetap buat file keluaran meskipun tidak ada baris data.
        nama_berkas.write_text("", encoding="utf-8")
        return
    with nama_berkas.open(mode="w", encoding="utf-8", newline="") as berkas:
        penulis = csv.DictWriter(berkas, fieldnames=list(data[0].keys()))
        penulis.writeheader()
        penulis.writerows(data)


def simpan_log(log: list[dict], nama_berkas: Path) -> None:
    """Menyimpan rincian setiap perlakuan pembersihan ke file teks."""
    nama_berkas.parent.mkdir(parents=True, exist_ok=True)
    with nama_berkas.open(mode="w", encoding="utf-8") as berkas:
        berkas.write("LOG PEMBERSIHAN DATA\n")
        berkas.write("=" * 60 + "\n")
        berkas.write(f"{'No':<4}{'Baris':<8}{'Masalah':<45}{'Perlakuan':<30}\n")
        berkas.write("-" * 90 + "\n")
        for i, catatan in enumerate(log, start=1):
            berkas.write(
                f"{i:<4}{catatan['baris']:<8}"
                f"{catatan['masalah']:<45}{catatan['perlakuan']:<30}\n"
            )


def main() -> None:
    print("=" * 60)
    print("PEMBERSIHAN DATA PRODUKSI")
    print("=" * 60)

    try:
        data_kotor = baca_data(FILE_DATA_KOTOR)
        print(f"Data kotor: {len(data_kotor)} baris")

        log: list[dict] = []
        data_bersih = bersihkan_data(data_kotor, log)
        print(f"Data bersih: {len(data_bersih)} baris")
        print(f"Perlakuan pembersihan: {len(log)} catatan")

        simpan_data_bersih(data_bersih, FILE_DATA_BERSIH)
        simpan_log(log, FILE_LOG)
        print(f"\nData bersih disimpan ke: {FILE_DATA_BERSIH.relative_to(FOLDER_PROYEK)}")
        print(f"Log pembersihan disimpan ke: {FILE_LOG.relative_to(FOLDER_PROYEK)}")

        print("\n" + "=" * 60)
        print("RINGKASAN PEMBERSIHAN")
        print("=" * 60)
        for i, catatan in enumerate(log, start=1):
            print(
                f" {i}. Baris {catatan['baris']}: {catatan['masalah']} "
                f"-> {catatan['perlakuan']}"
            )
    except (FileNotFoundError, ValueError, KeyError) as error:
        print(f"\nERROR: {error}")
        print("Periksa kembali lokasi file CSV dan nama kolomnya.")


if __name__ == "__main__":
    main()