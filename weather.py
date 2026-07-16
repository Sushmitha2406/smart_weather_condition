import tkinter as tk
from tkinter import messagebox
import requests
from PIL import Image, ImageTk
from dotenv import load_dotenv
import os

# ---------------- LOAD .ENV FILE ----------------
load_dotenv()

# ---------------- API KEY ----------------
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise ValueError("API_KEY not found in .env file")

# ---------------- MAIN WINDOW ----------------
root = tk.Tk()
root.title("Smart Weather Forecast Application")
root.geometry("750x700")
root.config(bg="white")

# ---------------- LOAD PNG ICONS ----------------
sun_icon = ImageTk.PhotoImage(Image.open("sun.png").resize((35,35)))
cloud_icon = ImageTk.PhotoImage(Image.open("cloud.png").resize((35,35)))
rain_icon = ImageTk.PhotoImage(Image.open("rain.png").resize((35,35)))
storm_icon = ImageTk.PhotoImage(Image.open("storm.png").resize((35,35)))
fog_icon = ImageTk.PhotoImage(Image.open("fog.png").resize((35,35)))

# ---------------- WEATHER ICON FUNCTION ----------------
def get_weather_icon(condition):
    condition = condition.lower()

    if "sunny" in condition or "clear" in condition:
        return sun_icon
    elif "cloud" in condition:
        return cloud_icon
    elif "rain" in condition or "drizzle" in condition:
        return rain_icon
    elif "storm" in condition or "thunder" in condition:
        return storm_icon
    elif "mist" in condition or "fog" in condition:
        return fog_icon
    else:
        return cloud_icon

# ---------------- TITLE ----------------
title_frame = tk.Frame(root, bg="lightblue", height=70)
title_frame.pack(fill="x")
title_frame.pack_propagate(False)

# Center frame
center_frame = tk.Frame(title_frame, bg="lightblue")
center_frame.place(relx=0.5, rely=0.5, anchor="center")

# Load title icon
title_icon = ImageTk.PhotoImage(
    Image.open("weather.png").resize((50,50))
)

# Icon
icon_label = tk.Label(
    center_frame,
    image=title_icon,
    bg="lightblue"
)
icon_label.pack(side="left", padx=(0,10))

# Title
title = tk.Label(
    center_frame,
    text="Smart Weather Forecast App",
    font=("Arial",20,"bold"),
    bg="lightblue",
    fg="darkblue"
)
title.pack(side="left")

# ---------------- SEARCH FRAME ----------------
search_frame = tk.Frame(root, bg="white")
search_frame.pack(pady=10)

city_entry = tk.Entry(
    search_frame,
    font=("Arial",13),
    width=30
)
city_entry.grid(row=0, column=0, padx=10)

search_btn = tk.Button(
    search_frame,
    text="Get Weather",
    bg="lightgreen",
    font=("Arial",11,"bold")
)
search_btn.grid(row=0, column=1)

# ---------------- TODAY WEATHER FRAME ----------------
today_frame = tk.LabelFrame(
    root,
    text="Today's Weather",
    font=("Arial",12,"bold"),
    bg="white",
    padx=10,
    pady=10
)
today_frame.pack(fill="x", padx=15, pady=10)

today_icon = tk.Label(today_frame, bg="white")
today_icon.grid(row=0, column=0, rowspan=5, padx=15)

city_label = tk.Label(
    today_frame,
    text="",
    font=("Arial",12),
    bg="white"
)
city_label.grid(row=0, column=1, sticky="w")

temp_label = tk.Label(
    today_frame,
    text="",
    font=("Arial",12),
    bg="white"
)
temp_label.grid(row=1, column=1, sticky="w")

humidity_label = tk.Label(
    today_frame,
    text="",
    font=("Arial",12),
    bg="white"
)
humidity_label.grid(row=2, column=1, sticky="w")

wind_label = tk.Label(
    today_frame,
    text="",
    font=("Arial",12),
    bg="white"
)
wind_label.grid(row=3, column=1, sticky="w")

condition_label = tk.Label(
    today_frame,
    text="",
    font=("Arial",12),
    bg="white"
)
condition_label.grid(row=4, column=1, sticky="w")
# ---------------- SCROLLABLE FORECAST ----------------
canvas = tk.Canvas(root, bg="white", highlightthickness=0)
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)

forecast_frame = tk.Frame(canvas, bg="white")

forecast_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas_window = canvas.create_window(
    (0, 0),
    window=forecast_frame,
    anchor="nw"
)

def resize_canvas(event):
    canvas.itemconfig(canvas_window, width=event.width)

canvas.bind("<Configure>", resize_canvas)
canvas.configure(yscrollcommand=scrollbar.set)

def on_mousewheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

canvas.bind_all("<MouseWheel>", on_mousewheel)

canvas.pack(
    side="left",
    fill="both",
    expand=True,
    padx=10,
    pady=10
)

scrollbar.pack(side="right", fill="y")


# ---------------- GET WEATHER FUNCTION ----------------
def get_weather():
    city = city_entry.get().strip()

    if city == "":
        messagebox.showerror("Error", "Please enter city name")
        return

    url = (
        f"http://api.weatherapi.com/v1/forecast.json"
        f"?key={API_KEY}&q={city}&days=10&aqi=no&alerts=no"
    )

    try:
        response = requests.get(url)
        data = response.json()

        if "error" in data:
            messagebox.showerror(
                "Error",
                data["error"]["message"]
            )
            return

        # Remove previous forecast labels
        for widget in forecast_frame.winfo_children():
            widget.destroy()

        location = data["location"]
        current = data["current"]

        icon = get_weather_icon(
            current["condition"]["text"]
        )

        today_icon.config(image=icon)
        today_icon.image = icon

        city_label.config(
            text=f"City : {location['name']}"
        )

        temp_label.config(
            text=f"Temperature : {current['temp_c']} °C"
        )

        humidity_label.config(
            text=f"Humidity : {current['humidity']} %"
        )

        wind_label.config(
            text=f"Wind : {current['wind_kph']} km/h"
        )

        condition_label.config(
            text=f"Condition : {current['condition']['text']}"
        )

        # Forecast heading
        tk.Label(
            forecast_frame,
            text="10-Day Forecast",
            font=("Arial", 15, "bold"),
            fg="darkgreen",
            bg="white"
        ).pack(pady=5)

        # 10-Day Forecast Loop
        for day in data["forecast"]["forecastday"]:

            icon = get_weather_icon(
                day["day"]["condition"]["text"]
            )

            day_frame = tk.Frame(
                forecast_frame,
                bd=1,
                relief="solid",
                padx=10,
                pady=10,
                bg="white"
            )

            day_frame.pack(
                fill="x",
                padx=10,
                pady=5
            )

            img = tk.Label(
                day_frame,
                image=icon,
                bg="white"
            )

            img.image = icon
            img.grid(
                row=0,
                column=0,
                rowspan=5,
                padx=10
            )

            tk.Label(
                day_frame,
                text=f"Date : {day['date']}",
                font=("Arial", 11, "bold"),
                bg="white"
            ).grid(
                row=0,
                column=1,
                sticky="w"
            )

            tk.Label(
                day_frame,
                text=f"Temperature : {day['day']['avgtemp_c']} °C",
                bg="white"
            ).grid(
                row=1,
                column=1,
                sticky="w"
            )

            tk.Label(
                day_frame,
                text=f"Humidity : {day['day']['avghumidity']} %",
                bg="white"
            ).grid(
                row=2,
                column=1,
                sticky="w"
            )
            tk.Label(
                day_frame,
                text=f"Wind : {day['day']['maxwind_kph']} km/h",
                bg="white"
            ).grid(
                row=3,
                column=1,
                sticky="w"
            )

            tk.Label(
                day_frame,
                text=f"Condition : {day['day']['condition']['text']}",
                bg="white"
            ).grid(
                row=4,
                column=1,
                sticky="w"
            )

        # Update scroll region
        forecast_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    except requests.exceptions.ConnectionError:
        messagebox.showerror(
            "Connection Error",
            "Please check your internet connection."
        )

    except Exception as e:
        messagebox.showerror(
            "Error",
            str(e)
        )


# ---------------- BUTTON COMMAND ----------------
search_btn.config(command=get_weather)

# Press Enter key to search
city_entry.bind("<Return>", lambda event: get_weather())

# ---------------- RUN APPLICATION ----------------
root.mainloop()