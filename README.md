# Proyek Analisis Data: Bike Sharing Dataset 🚲

Analisis data penyewaan sepeda Capital Bikeshare (Washington D.C., 2011–2012) beserta dashboard interaktif
berbasis Streamlit.

## Pertanyaan Bisnis
1. Berapa selisih rata-rata jumlah penyewaan sepeda per hari antara **hari kerja** dan **hari libur** untuk pengguna
   *casual* dan *registered* sepanjang 2011–2012, serta pada jam berapa puncak penyewaan terjadi?
2. Pada **kategori suhu** dan **kondisi cuaca** apa rata-rata penyewaan harian paling tinggi selama 2011–2012, dan berapa
   persen penurunannya saat hujan/salju ringan dibandingkan cuaca cerah?

## Struktur Direktori
```
submissionfinal
├── dashboard
│   ├── main_data.csv      # data harian yang sudah bersih (dipakai dashboard)
│   ├── hour_data.csv      # data per jam yang sudah bersih (dipakai dashboard)
│   └── dashboard.py       # kode dashboard Streamlit
├── data
│   ├── day.csv            # dataset asli (harian)
│   └── hour.csv           # dataset asli (per jam)
├── notebook.ipynb         # proses analisis data lengkap (dijalankan di Google Colab)
├── README.md
├── requirements.txt
└── url.txt                # tautan dashboard di Streamlit Cloud (format: streamlit = <tautan>)
```

## Menjalankan Notebook (Google Colab)
Notebook ini disusun untuk dijalankan di **Google Colab** dan membaca dataset dari Google Drive.

1. Unggah seluruh folder `submissionfinal` ke **My Drive** di Google Drive, sehingga dataset berada di
   `MyDrive/submissionfinal/data/day.csv` dan `MyDrive/submissionfinal/data/hour.csv`.
   (Path ini ditulis pada sel 11 notebook: `DATA_DIR = '/content/drive/MyDrive/submissionfinal/data/'`.
   Jika folder Anda berada di lokasi atau memiliki nama lain, ubah nilai `DATA_DIR` tersebut.)
2. Buka `notebook.ipynb` dengan Google Colab (klik kanan berkas di Drive > Open with > Google Colaboratory).
3. Jalankan seluruh sel (**Runtime > Run all**). Pada sel pertama bagian *Gathering Data*, Colab akan meminta izin
   mengakses Google Drive; pilih akun lalu izinkan.
4. Di akhir notebook, data bersih disimpan ke folder `dashboard/` pada penyimpanan sementara Colab
   (`/content/dashboard/main_data.csv` dan `/content/dashboard/hour_data.csv`). Berkas hasil run yang sama sudah
   tersedia di folder `dashboard` pada submission ini. Untuk memperbaruinya, unduh kedua berkas itu dari panel
   *Files* Colab lalu timpa isi folder `dashboard`.

> Catatan: untuk menjalankan notebook di komputer sendiri (tanpa Colab), hapus sel `drive.mount` (sel 10) dan ubah
> `DATA_DIR` menjadi `'data'`.

## Setup Environment (Dashboard)
Dashboard dijalankan di komputer sendiri. Pastikan Python 3.10 atau lebih baru terpasang.

### Menggunakan virtual environment (venv)
```shell
cd submissionfinal
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### Menggunakan Anaconda
```shell
conda create --name bike-sharing python=3.11
conda activate bike-sharing
pip install -r requirements.txt
```

## Menjalankan Dashboard
Jalankan perintah berikut dari folder utama submission (`submissionfinal`):
```shell
streamlit run dashboard/dashboard.py
```
Dashboard akan terbuka otomatis di browser (biasanya `http://localhost:8501`). Gunakan filter **Rentang tanggal** dan
**Musim** pada sidebar untuk memperbarui seluruh grafik dan ringkasan.

## Deploy ke Streamlit Community Cloud
1. Unggah folder proyek ke repositori GitHub (tanpa folder `venv`).
2. Masuk ke [share.streamlit.io](https://share.streamlit.io) dengan akun GitHub.
3. Pilih **New app**, lalu isi repositori, branch, dan **Main file path** dengan `dashboard/dashboard.py`.
4. Setelah berhasil, salin tautan aplikasi ke berkas `url.txt` dengan format
   `streamlit = https://nama-app-anda.streamlit.app`.

## Sumber Data
Fanaee-T, H. & Gama, J. (2013). *Event labeling combining ensemble detectors and background knowledge.*
Progress in Artificial Intelligence, 1–15. doi:10.1007/s13748-013-0040-3.
Dataset: [Bike Sharing Dataset (Kaggle)](https://www.kaggle.com/datasets/lakshmi25npathi/bike-sharing-dataset)
