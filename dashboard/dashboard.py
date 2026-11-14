"""Dashboard Analisis Bike Sharing (Capital Bikeshare, Washington D.C., 2011-2012).

Cara menjalankan (dari folder utama submission):
    streamlit run dashboard/dashboard.py
"""
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

# ----------------------------------------------------------------------
# Konfigurasi halaman & gaya visualisasi
# ----------------------------------------------------------------------
st.set_page_config(page_title="Dashboard Bike Sharing", page_icon="🚲", layout="wide")

sns.set_theme(style="whitegrid")
plt.rcParams.update({
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titleweight": "bold",
    "axes.titlesize": 12,
    "axes.labelsize": 10,
    "axes.grid.axis": "y",
})

COLOR_CASUAL = "#E69F00"
COLOR_REGISTERED = "#0072B2"
COLOR_HIGHLIGHT = "#D55E00"
COLOR_NEUTRAL = "#B8B8B8"

DAY_TYPES = ["Hari Kerja", "Hari Libur"]
SEASON_ORDER = ["Musim Semi", "Musim Panas", "Musim Gugur", "Musim Dingin"]
TEMP_ORDER = ["Dingin (<10°C)", "Sejuk (10–20°C)", "Hangat (20–28°C)", "Panas (≥28°C)"]
WEATHER_ORDER = ["Cerah", "Berkabut/Berawan", "Hujan/Salju Ringan"]
HOUR_ORDER = ["Dini Hari (00–05)", "Pagi (06–09)", "Siang (10–15)", "Sore (16–19)", "Malam (20–23)"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ----------------------------------------------------------------------
# Fungsi bantu
# ----------------------------------------------------------------------
def fmt_id(x, digits=0):
    """Format angka dengan pemisah ribuan, contoh: 1,371 (sama dengan format pada notebook)."""
    return f"{x:,.{digits}f}"


def fmt_pct(x, digits=1):
    """Format persentase bertanda, contoh: -63.0% atau +126.0%."""
    return f"{x:+,.{digits}f}%"


def format_yaxis(ax):
    ax.yaxis.set_major_formatter("{x:,.0f}")


@st.cache_data
def load_data():
    day = pd.read_csv(os.path.join(BASE_DIR, "main_data.csv"), parse_dates=["dteday"])
    hour = pd.read_csv(os.path.join(BASE_DIR, "hour_data.csv"), parse_dates=["dteday"])
    day["temp_category"] = pd.Categorical(day["temp_category"], categories=TEMP_ORDER, ordered=True)
    hour["hour_group"] = pd.Categorical(hour["hour_group"], categories=HOUR_ORDER, ordered=True)
    return day, hour


# ----------------------------------------------------------------------
# Fungsi visualisasi
# ----------------------------------------------------------------------
def plot_daily_by_type(day):
    g = day.groupby("day_type")[["casual", "registered"]].mean().reindex(DAY_TYPES).fillna(0)
    n = day["day_type"].value_counts().reindex(DAY_TYPES).fillna(0).astype(int)

    fig, ax = plt.subplots(figsize=(7, 4.6))
    x = np.arange(len(DAY_TYPES))
    width = 0.36
    bars_c = ax.bar(x - width / 2, g["casual"], width, color=COLOR_CASUAL, label="Casual")
    bars_r = ax.bar(x + width / 2, g["registered"], width, color=COLOR_REGISTERED, label="Registered")
    ax.bar_label(bars_c, labels=[fmt_id(v) for v in g["casual"]], padding=3)
    ax.bar_label(bars_r, labels=[fmt_id(v) for v in g["registered"]], padding=3)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{t}\n({n[t]} hari)" for t in DAY_TYPES])
    ax.set_ylim(0, max(g["registered"].max(), g["casual"].max(), 1) * 1.18)
    ax.set_ylabel("Rata-rata penyewaan per hari (sepeda)")
    format_yaxis(ax)
    ax.set_title("Rata-rata penyewaan harian: hari kerja vs hari libur", loc="left")
    ax.legend(title="Jenis pengguna", frameon=False, loc="upper right")
    fig.tight_layout()
    return fig


def plot_hourly(hour):
    h = hour.groupby(["day_type", "hour"])[["casual", "registered"]].mean()
    ymax = max(float(h.max().max()) if len(h) else 1.0, 1.0) * 1.15

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.4), sharey=True)
    for ax, day_type in zip(axes, DAY_TYPES):
        ax.set_title(day_type, loc="left")
        ax.set_xlabel("Jam dalam sehari (00–23)")
        ax.set_xticks(range(0, 24, 3))
        ax.set_ylim(0, ymax)
        if day_type not in h.index.get_level_values(0):
            ax.text(0.5, 0.5, "Tidak ada data pada filter ini", ha="center", va="center",
                    transform=ax.transAxes, color="gray")
            continue
        sub = h.loc[day_type]
        ax.plot(sub.index, sub["registered"], color=COLOR_REGISTERED, lw=2.3, label="Registered")
        ax.plot(sub.index, sub["casual"], color=COLOR_CASUAL, lw=2.3, label="Casual")
        for user, color in [("registered", COLOR_REGISTERED), ("casual", COLOR_CASUAL)]:
            hr = int(sub[user].idxmax())
            val = sub.loc[hr, user]
            ax.scatter(hr, val, color=color, s=50, zorder=3)
            left = hr >= 15
            ax.annotate(f"Puncak {hr:02d}:00 ({fmt_id(val)})", (hr, val), textcoords="offset points",
                        xytext=(-10, 7) if left else (10, 7), ha="right" if left else "left",
                        fontsize=8.5, color=color, fontweight="bold")
        if day_type == "Hari Kerja":
            morning = sub[sub.index < 12]["registered"]
            if len(morning):
                hr = int(morning.idxmax())
                ax.scatter(hr, morning.max(), color=COLOR_REGISTERED, s=50, zorder=3)
                ax.annotate(f"Puncak {hr:02d}:00 ({fmt_id(morning.max())})", (hr, morning.max()),
                            textcoords="offset points", xytext=(-10, 7), ha="right",
                            fontsize=8.5, color=COLOR_REGISTERED, fontweight="bold")
    axes[0].set_ylabel("Rata-rata penyewaan per jam (sepeda)")
    format_yaxis(axes[0])
    for ax in reversed(axes):   # legend di panel kanan (jika ada data) agar tidak menimpa anotasi
        if ax.get_legend_handles_labels()[0]:
            ax.legend(title="Jenis pengguna", frameon=False, loc="upper right")
            break
    fig.tight_layout()
    return fig


def peak_table(hour):
    h = hour.groupby(["day_type", "hour"])[["casual", "registered"]].mean()
    rows = []
    for day_type in DAY_TYPES:
        if day_type not in h.index.get_level_values(0):
            continue
        sub = h.loc[day_type]
        for user, label in [("casual", "Casual"), ("registered", "Registered")]:
            rows.append({
                "Tipe Hari": day_type,
                "Jenis Pengguna": label,
                "Jam Puncak": f"{int(sub[user].idxmax()):02d}:00",
                "Rata-rata Penyewaan per Jam": round(float(sub[user].max())),
            })
    return pd.DataFrame(rows)


def plot_temp_weather(day):
    temp = day.groupby("temp_category", observed=True)["cnt"].agg(["mean", "count"]).reindex(TEMP_ORDER)
    weather = day.groupby("weather")["cnt"].agg(["mean", "count"]).reindex(WEATHER_ORDER)
    temp_mean, temp_n = temp["mean"].fillna(0), temp["count"].fillna(0).astype(int)
    w_mean, w_n = weather["mean"].fillna(0), weather["count"].fillna(0).astype(int)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))

    ax = axes[0]
    top = temp_mean.max()
    colors = [COLOR_HIGHLIGHT if (top > 0 and v >= 0.95 * top) else COLOR_NEUTRAL for v in temp_mean]
    bars = ax.bar(range(len(temp_mean)), temp_mean.values, color=colors)
    ax.bar_label(bars, labels=[fmt_id(v) if v > 0 else "" for v in temp_mean.values], padding=3)
    ax.set_xticks(range(len(temp_mean)))
    ax.set_xticklabels([f"{lbl.replace(' (', chr(10) + '(')}\n{n} hari" for lbl, n in zip(TEMP_ORDER, temp_n)])
    ax.set_ylim(0, max(top, 1) * 1.15)
    ax.set_ylabel("Rata-rata penyewaan per hari (sepeda)")
    format_yaxis(ax)
    ax.set_title("(a) Menurut kategori suhu", loc="left")

    ax = axes[1]
    base = w_mean.get("Cerah", 0)
    lowest = w_mean[w_n > 0].min() if (w_n > 0).any() else None
    w_colors = [COLOR_HIGHLIGHT if (lowest is not None and v == lowest and w_n[c] > 0) else COLOR_NEUTRAL
                for c, v in w_mean.items()]
    bars = ax.bar(range(len(w_mean)), w_mean.values, color=w_colors)
    labels = []
    for cond, v in w_mean.items():
        if w_n[cond] == 0:
            labels.append("")
        elif cond == "Cerah" or base <= 0:
            labels.append(fmt_id(v))
        else:
            labels.append(f"{fmt_id(v)}\n({fmt_pct((v / base - 1) * 100)} vs cerah)")
    ax.bar_label(bars, labels=labels, padding=3)
    ax.set_xticks(range(len(w_mean)))
    ax.set_xticklabels([f"{c}\n{n} hari" for c, n in zip(WEATHER_ORDER, w_n)])
    ax.set_ylim(0, max(w_mean.max(), 1) * 1.28)
    ax.set_ylabel("Rata-rata penyewaan per hari (sepeda)")
    format_yaxis(ax)
    ax.set_title("(b) Menurut kondisi cuaca", loc="left")
    fig.tight_layout()
    return fig


def plot_heatmap(day):
    mean = day.pivot_table(index="temp_category", columns="weather", values="cnt",
                           aggfunc="mean", observed=True).reindex(index=TEMP_ORDER, columns=WEATHER_ORDER)
    cnt = day.pivot_table(index="temp_category", columns="weather", values="cnt",
                          aggfunc="count", observed=True).reindex(index=TEMP_ORDER, columns=WEATHER_ORDER)
    annot = mean.copy().astype(object)
    for r in mean.index:
        for c in mean.columns:
            annot.loc[r, c] = "" if pd.isna(mean.loc[r, c]) else f"{fmt_id(mean.loc[r, c])}\n(n={int(cnt.loc[r, c])})"

    fig, ax = plt.subplots(figsize=(7.5, 4.4))
    if mean.notna().any().any():
        sns.heatmap(mean, annot=annot, fmt="", cmap="Blues", linewidths=1, linecolor="white",
                    cbar_kws={"label": "Rata-rata penyewaan per hari"}, ax=ax)
    else:
        ax.text(0.5, 0.5, "Tidak ada data pada filter ini", ha="center", va="center",
                transform=ax.transAxes, color="gray")
    for i, r in enumerate(mean.index):
        for j, c in enumerate(mean.columns):
            if pd.isna(mean.loc[r, c]):
                ax.text(j + 0.5, i + 0.5, "tidak ada\ndata", ha="center", va="center", color="gray", fontsize=8)
    ax.grid(False)
    ax.set_xlabel("Kondisi cuaca")
    ax.set_ylabel("Kategori suhu")
    ax.set_title("Kombinasi suhu x cuaca (n = jumlah hari)", loc="left")
    fig.tight_layout()
    return fig


def hour_group_share(hour):
    total = hour.groupby(["day_type", "hour_group"], observed=True)[["casual", "registered"]].sum()
    return total.div(total.groupby(level=0).transform("sum")) * 100


def plot_hour_group(hour):
    share = hour_group_share(hour)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.4), sharey=True)
    x = np.arange(len(HOUR_ORDER))
    width = 0.38
    for ax, day_type in zip(axes, DAY_TYPES):
        ax.set_title(day_type, loc="left")
        ax.set_xticks(x)
        ax.set_xticklabels([lbl.replace(" (", "\n(") for lbl in HOUR_ORDER])
        ax.set_ylim(0, 65)
        if day_type not in share.index.get_level_values(0):
            ax.text(0.5, 0.5, "Tidak ada data pada filter ini", ha="center", va="center",
                    transform=ax.transAxes, color="gray")
            continue
        sub = share.loc[day_type].reindex(HOUR_ORDER).fillna(0)
        bars_c = ax.bar(x - width / 2, sub["casual"], width, color=COLOR_CASUAL, label="Casual")
        bars_r = ax.bar(x + width / 2, sub["registered"], width, color=COLOR_REGISTERED, label="Registered")
        ax.bar_label(bars_c, labels=[f"{v:.0f}%" for v in sub["casual"]], padding=2, fontsize=8.5)
        ax.bar_label(bars_r, labels=[f"{v:.0f}%" for v in sub["registered"]], padding=2, fontsize=8.5)
    axes[0].set_ylabel("% dari total penyewaan jenis pengguna tsb")
    for ax in reversed(axes):   # legend di panel kanan (jika ada data) agar tidak menimpa anotasi
        if ax.get_legend_handles_labels()[0]:
            ax.legend(title="Jenis pengguna", frameon=False, loc="upper left")
            break
    fig.tight_layout()
    return fig


# ----------------------------------------------------------------------
# Ringkasan insight dinamis (mengikuti filter yang dipilih)
# ----------------------------------------------------------------------
def insight_q1(day):
    g = day.groupby("day_type")[["casual", "registered", "cnt"]].mean()
    if not set(DAY_TYPES).issubset(g.index):
        return "Pilih rentang tanggal yang mencakup hari kerja **dan** hari libur untuk membandingkan keduanya."
    k, l = g.loc["Hari Kerja"], g.loc["Hari Libur"]
    return (
        f"**Pengguna casual** {fmt_pct((l['casual'] / k['casual'] - 1) * 100, 0)} pada hari libur "
        f"({fmt_id(k['casual'])} → {fmt_id(l['casual'])} sepeda/hari), sedangkan **pengguna registered** "
        f"{fmt_pct((l['registered'] / k['registered'] - 1) * 100, 0)} "
        f"({fmt_id(k['registered'])} → {fmt_id(l['registered'])}). "
        f"Total harian berubah {fmt_pct((l['cnt'] / k['cnt'] - 1) * 100)}."
    )


def insight_q2(day):
    weather = day.groupby("weather")["cnt"].mean()
    temp = day.groupby("temp_category", observed=True)["cnt"].mean()
    parts = []
    if len(temp):
        parts.append(f"Penyewaan harian tertinggi pada kategori suhu **{temp.idxmax()}** "
                     f"({fmt_id(temp.max())} sepeda/hari).")
    if "Cerah" in weather.index and "Hujan/Salju Ringan" in weather.index:
        drop = (weather["Hujan/Salju Ringan"] / weather["Cerah"] - 1) * 100
        parts.append(f"Hujan/salju ringan menurunkan penyewaan **{fmt_id(abs(drop), 1)}%** dibanding cuaca cerah "
                     f"({fmt_id(weather['Hujan/Salju Ringan'])} vs {fmt_id(weather['Cerah'])} sepeda/hari).")
    return " ".join(parts) if parts else "Tidak ada data pada filter ini."


# ----------------------------------------------------------------------
# Tampilan utama
# ----------------------------------------------------------------------
day_all, hour_all = load_data()

st.sidebar.header("Filter Data")
min_date, max_date = day_all["dteday"].min().date(), day_all["dteday"].max().date()
date_range = st.sidebar.date_input(
    "Rentang tanggal", value=(min_date, max_date), min_value=min_date, max_value=max_date
)
seasons = st.sidebar.multiselect("Musim", options=SEASON_ORDER, default=SEASON_ORDER)
st.sidebar.caption(
    "Hari Libur = akhir pekan + libur nasional. "
    "Kategori suhu: Dingin <10°C, Sejuk 10–20°C, Hangat 20–28°C, Panas ≥28°C."
)

if not (isinstance(date_range, (tuple, list)) and len(date_range) == 2):
    st.info("Pilih tanggal akhir pada filter rentang tanggal untuk menampilkan dashboard.")
    st.stop()
if not seasons:
    st.warning("Pilih minimal satu musim pada filter.")
    st.stop()

start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
day = day_all[(day_all["dteday"] >= start) & (day_all["dteday"] <= end) & day_all["season"].isin(seasons)]
hour = hour_all[(hour_all["dteday"] >= start) & (hour_all["dteday"] <= end) & hour_all["season"].isin(seasons)]

if day.empty:
    st.warning("Tidak ada data pada filter yang dipilih.")
    st.stop()

st.title("🚲 Dashboard Analisis Bike Sharing")
st.caption("Capital Bikeshare, Washington D.C. · Data harian & per jam 2011–2012")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Penyewaan", fmt_id(day["cnt"].sum()))
c2.metric("Rata-rata per Hari", fmt_id(day["cnt"].mean()))
c3.metric("Rata-rata Casual / Hari", fmt_id(day["casual"].mean()))
c4.metric("Rata-rata Registered / Hari", fmt_id(day["registered"].mean()))

tab1, tab2, tab3 = st.tabs([
    "1. Hari Kerja vs Hari Libur",
    "2. Suhu & Cuaca",
    "3. Analisis Lanjutan (Jam Operasional)",
])

with tab1:
    st.subheader("Seberapa berbeda penyewaan hari kerja dan hari libur, dan kapan puncaknya?")
    st.info(insight_q1(day))
    left, right = st.columns([1, 1])
    with left:
        fig = plot_daily_by_type(day)
        st.pyplot(fig)
        plt.close(fig)
    with right:
        st.markdown("**Jam puncak penyewaan**")
        st.dataframe(peak_table(hour))
        st.caption("Registered memuncak di jam komuter hari kerja (pagi & sore), "
                   "sedangkan casual memuncak di siang hari libur.")
    st.markdown("**Pola rata-rata penyewaan per jam**")
    fig = plot_hourly(hour)
    st.pyplot(fig)
    plt.close(fig)

with tab2:
    st.subheader("Pada suhu dan cuaca apa penyewaan tertinggi, dan seberapa besar penurunannya saat hujan?")
    st.info(insight_q2(day))
    fig = plot_temp_weather(day)
    st.pyplot(fig)
    plt.close(fig)
    st.markdown("**Kombinasi kategori suhu x kondisi cuaca**")
    fig = plot_heatmap(day)
    st.pyplot(fig)
    plt.close(fig)
    st.caption("Sel dengan n kecil (< 10 hari) perlu ditafsirkan hati-hati.")

with tab3:
    st.subheader("Manual grouping: sebaran penyewaan per periode operasional")
    st.markdown(
        "Jam 0–23 dikelompokkan menjadi 5 periode (Dini Hari, Pagi, Siang, Sore, Malam) agar tim operasional "
        "dapat menentukan kapan perlu menambah sepeda, melakukan *rebalancing*, atau perawatan."
    )
    if hour.empty:
        st.warning("Tidak ada data per jam pada filter yang dipilih.")
    else:
        fig = plot_hour_group(hour)
        st.pyplot(fig)
        plt.close(fig)

with st.expander("Lihat data harian (sesuai filter)"):
    st.dataframe(day)

st.caption(
    "Sumber data: Fanaee-T, H. & Gama, J. (2013). Event labeling combining ensemble detectors and background "
    "knowledge. Progress in Artificial Intelligence."
)
