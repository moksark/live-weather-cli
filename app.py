import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def terjemahkan_kode_cuaca(kode):
    # Mengubah kode cuaca WMO menjadi teks bahasa Indonesia + Emoji
    if kode == 0:
        return "Cerah ☀️", "yellow"
    elif kode in [1, 2, 3]:
        return "Cerah Berawan ⛅", "cyan"
    elif kode in [45, 48]:
        return "Berkabut 🌫️", "white"
    elif kode in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
        return "Hujan 🌧️", "blue"
    elif kode in [95, 96, 99]:
        return "Hujan Petir ⛈️", "magenta"
    else:
        return "Berawan ☁️", "green"

def ambil_data_cuaca(nama_kota):
    try:
        # 1. Cari koordinat kota menggunakan Open-Meteo Geocoding API
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={nama_kota}&count=1&language=id&format=json"
        geo_res = requests.get(geo_url, timeout=10).json()
        
        if "results" not in geo_res or len(geo_res["results"]) == 0:
            return None
            
        lokasi = geo_res["results"][0]
        lat = lokasi["latitude"]
        lon = lokasi["longitude"]
        nama_resmi = lokasi["name"]
        negara = lokasi.get("country", "")
        
        # 2. Ambil data cuaca real-time berdasarkan koordinat
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
        )
        weather_res = requests.get(weather_url, timeout=10).json()
        current = weather_res["current"]
        
        kondisi_teks, warna = terjemahkan_kode_cuaca(current["weather_code"])
        
        return {
            "lokasi": f"{nama_resmi}, {negara}",
            "suhu": f"{current['temperature_2m']}°C",
            "kelembapan": f"{current['relative_humidity_2m']}%",
            "angin": f"{current['wind_speed_10m']} km/jam",
            "kondisi": kondisi_teks,
            "warna": warna
        }
    except requests.exceptions.RequestException:
        return "ERROR_JARINGAN"

def jalankan_aplikasi():
    console.print(Panel.fit(
        "[bold cyan]🌍 LIVE WEATHER CLI DASHBOARD[/bold cyan]\n[italic dim]Real-Time Data via Open-Meteo REST API[/italic dim]", 
        border_style="blue"
    ))
    
    while True:
        console.print("\n")
        kota_input = console.input("[bold green]Masukkan nama kota mana saja[/bold green] (ketik [bold red]'keluar'[/bold red]): ").strip()
        
        if kota_input.lower() == 'keluar':
            console.print("\n[bold cyan]Terima kasih telah menggunakan Live Weather CLI! 👋[/bold cyan]\n")
            break
            
        if not kota_input:
            continue

        # Menampilkan spinner saat mengambil data dari internet
        with console.status(f"[bold yellow]Menghubungi satelit cuaca untuk '{kota_input}'...", spinner="dots"):
            hasil = ambil_data_cuaca(kota_input)
            
        if hasil == "ERROR_JARINGAN":
            console.print("\n[bold red][!] Gagal terhubung ke internet. Periksa koneksi jaringan Anda.[/bold red]")
        elif hasil is None:
            console.print(f"\n[bold red][!] Kota '{kota_input}' tidak ditemukan di peta dunia.[/bold red]")
        else:
            table = Table(
                title=f"Laporan Cuaca Real-Time: {hasil['lokasi']}", 
                title_style="bold underline", 
                border_style=hasil['warna']
            )
            
            table.add_column("Parameter", style="cyan", justify="left")
            table.add_column("Data Terkini", style="bold white", justify="left")
            
            table.add_row("Kondisi Cuaca", hasil['kondisi'])
            table.add_row("Suhu Udara", hasil['suhu'])
            table.add_row("Kelembapan", hasil['kelembapan'])
            table.add_row("Kecepatan Angin", hasil['angin'])
            
            console.print(table)
            console.print("[dim]📡 Sumber: Open-Meteo Live Weather API[/dim]")

if __name__ == "__main__":
    jalankan_aplikasi()
