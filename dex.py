import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import sqlite3
import requests
from io import BytesIO

# ฟังก์ชันในการเชื่อมต่อฐานข้อมูล SQLite
def connect_db():
    conn = sqlite3.connect('purchase_history.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS purchases (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        coin_name TEXT,
                        purchase_price TEXT)''')
    conn.commit()
    return conn, cursor

# ฟังก์ชันในการเพิ่มรายการลงฐานข้อมูล
def save_purchase_history():
    coin_name = coin_name_entry.get()
    purchase_price = purchase_price_entry.get()

    # Check for empty input fields
    if not coin_name or not purchase_price:
        messagebox.showwarning("Warning", "Please enter both coin name and purchase price!")
        return

    try:
        # Connect to the database and insert the record
        conn, cursor = connect_db()
        cursor.execute("INSERT INTO purchases (coin_name, purchase_price) VALUES (?, ?)",
                       (coin_name, purchase_price))
        conn.commit()
        conn.close()

        # Add entry to the Listbox
        purchase_history_listbox.insert(tk.END, f"{coin_name} | {purchase_price}")

        # Clear the input fields
        coin_name_entry.delete(0, tk.END)
        purchase_price_entry.delete(0, tk.END)

    except sqlite3.Error as e:
        # Handle any SQLite error that occurs
        messagebox.showerror("Database Error", f"An error occurred while saving to the database: {e}")


# ฟังก์ชันในการลบรายการที่เลือกจาก Listbox และฐานข้อมูล
def delete_purchase_history():
    selected_index = purchase_history_listbox.curselection()

    if not selected_index:
        messagebox.showwarning("Warning", "Please select an item to delete!")
        return

    # ดึงข้อมูลจากรายการที่เลือก
    selected_item = purchase_history_listbox.get(selected_index)
    coin_name, purchase_price = selected_item.split(" | ")

    # ลบรายการจากฐานข้อมูล
    conn, cursor = connect_db()
    cursor.execute("DELETE FROM purchases WHERE coin_name = ? AND purchase_price = ?", 
                   (coin_name, purchase_price))
    conn.commit()
    conn.close()

    # ลบรายการจาก Listbox
    purchase_history_listbox.delete(selected_index)

# Function to fetch token data
def fetch_token_data(token_address):
    try:
        response = requests.get(f"https://api.dexscreener.com/latest/dex/tokens/{token_address}")
        data = response.json()
        if not data or 'pairs' not in data or not data['pairs']:
            raise ValueError("No data available for the specified token.")
        token_data = data['pairs'][0]
        base_token = token_data.get('baseToken', {})
        symbol = base_token.get('symbol', 'No Name')
        namecoin = base_token.get('name', 'No Name')
        market_cap = token_data.get('marketCap', 'Not Available')
        price_change_24h = token_data.get('priceChange', {}).get('h24', 'Not Available')
        price_current = token_data.get('priceUsd', 'Not Available')
        pic_info = token_data.get('info', {}).get('imageUrl', None)
        pic_banner = token_data.get('info', {}).get('header', None)

        return token_data, symbol, market_cap, price_change_24h, namecoin, pic_info,pic_banner, price_current
    except Exception as e:
        return f"Error: {e}", None, None, None, None, None, None, None

# Function to update token info in the GUI
def update_token_info():
    token_address = token_entry.get()
    if not token_address:
        messagebox.showwarning("Warning", "Please enter a token address!")
        return

    token_data, symbol, market_cap, price_change_24h, namecoin, pic_info,pic_banner, price_current = fetch_token_data(token_address)
    if isinstance(token_data, str):  # If an error string was returned
        token_info_label.config(text=f"Error: {token_data}")
        return

    # Update labels with token information
    symbol_label.config(text=f"Symbol: {symbol}")
    namecoin_label.config(text=f"Name: {namecoin}")
    market_cap_label.config(text=f"Market Cap: ${market_cap}")
    price_change_label.config(text=f"24h Change: {price_change_24h}%")
    price_current_label.config(text=f"Current Price: ${price_current}")

    # Set the Coin Name entry field to the fetched name
    coin_name_entry.delete(0, tk.END)  # Clear any existing text
    coin_name_entry.insert(0, namecoin)  # Insert the fetched name
    purchase_price_entry.insert(0, price_current)  # Insert the fetched name

    # Fetch and display the image
    if pic_info:
        try:
            response = requests.get(pic_info)
            img_data = BytesIO(response.content)
            img = Image.open(img_data)
            img = img.resize((100, 100))  # Resize image to fit
            img_tk = ImageTk.PhotoImage(img)
            pic_label.config(image=img_tk)
            pic_label.image = img_tk  # Keep a reference to avoid garbage collection
        except Exception as e:
            pic_label.config(text="Unable to load image")
    else:
        pic_label.config(text="No image available")
    # Fetch and display the image
    if pic_banner:
        try:
            response = requests.get(pic_banner)
            img_data = BytesIO(response.content)
            img = Image.open(img_data)

            # ไม่ทำการปรับขนาดให้เป็นขนาดจริง
            img_tk = ImageTk.PhotoImage(img)
            pic2_label.config(image=img_tk)
            pic2_label.image = img_tk  # เก็บการอ้างอิงเพื่อหลีกเลี่ยงการเก็บข้อมูลใน garbage collection
        except Exception as e:
            pic2_label.config(text="Unable to load image")
    else:
        pic2_label.config(text="No image available")

# ฟังก์ชันในการเปลี่ยนพื้นหลัง
def change_background(bg_number):
    try:
        bg_image = Image.open(f"bg{bg_number}.jpg")  # ใช้ชื่อไฟล์พื้นหลังที่ต่างกัน
        bg_image = bg_image.resize((1100, 1200), Image.Resampling.LANCZOS)
        bg_tk = ImageTk.PhotoImage(bg_image)

        background_label.config(image=bg_tk)
        background_label.image = bg_tk  # เก็บการอ้างอิงเพื่อหลีกเลี่ยงการเก็บข้อมูลใน garbage collection
    except Exception as e:
        messagebox.showwarning("Error", f"Unable to load background image: {e}")

# Function to save the selected token address back to the token entry field
def save_token_address():
    selected_index = purchase_history_listbox.curselection()

    if not selected_index:
        messagebox.showwarning("Warning", "Please select a token address to save!")
        return

    # ดึงข้อมูลจากรายการที่เลือก
    selected_item = purchase_history_listbox.get(selected_index)
    coin_name, purchase_price = selected_item.split(" | ")

    # Place the selected token address back into the token entry field
    token_entry.delete(0, tk.END)
    token_entry.insert(0, coin_name)  # Insert the coin name as the token address
# Function to clear the token entry field.

def clear_token_entry():
    token_entry.delete(0, tk.END)

# ฟังก์ชันเปิดหน้าต่างใหม่เพื่อแสดงข้อมูลทั้งหมด
def show_all_data():
    # สร้างหน้าต่างใหม่
    new_window = tk.Toplevel(root)
    new_window.title("All Data")

    # Listbox แสดงข้อมูลทั้งหมด
    all_data_listbox = tk.Listbox(new_window, width=90, height=40)
    all_data_listbox.pack(pady=10)

    # ดึงข้อมูลทั้งหมดจากฐานข้อมูล
    conn, cursor = connect_db()
    cursor.execute("SELECT coin_name, purchase_price FROM purchases")
    rows = cursor.fetchall()
    for row in rows:
        all_data_listbox.insert(tk.END, f"{row[0]} | {row[1]}")
    conn.close()


    
# GUI Setup
root = tk.Tk()
root.title("Token Info Viewer #PUKUMPee V.3.0")
# Set the background color of the root window (optional)
root.configure(bg="black")

# Background Image
background_image = Image.open("bg1.jpg")  # เริ่มต้นที่พื้นหลังแรก
background_image = background_image.resize((1100, 1200), Image.Resampling.LANCZOS)
background_tk = ImageTk.PhotoImage(background_image)

background_label = tk.Label(root, image=background_tk)
background_label.place(relwidth=1, relheight=1)  # Cover the entire window

# ปุ่มสำหรับเปลี่ยนพื้นหลัง
bg_button_frame = tk.Frame(root)
bg_button_frame.pack(pady=10)

bg_buttons = []

# Image Display
pic2_label = tk.Label(root, text="Image will appear here", font=("Arial", 12))
pic2_label.pack(pady=10)



bg_button_frame = tk.Frame(root)
bg_button_frame.pack(pady=10)
for i in range(1, 6):
    tk.Button(bg_button_frame, text=f"Background {i}", command=lambda i=i: change_background(i)).grid(row=0, column=i-1, padx=5)

token_frame = tk.Frame(root)
token_frame.pack(pady=10)
tk.Label(token_frame, text="Enter Token Address:").grid(row=0, column=0)
token_entry = tk.Entry(token_frame, width=50)
token_entry.grid(row=0, column=1)

tk.Button(token_frame, text="Clear", command=clear_token_entry).grid(row=0, column=3)


# Token Info Display
info_frame = tk.Frame(root, bg="black")
info_frame.pack(pady=10)

# Label for Symbol with adjusted font size and padding
symbol_label = tk.Label(info_frame, text="Symbol: ", bg="white", font=("Arial", 14), width=20, anchor="w")
symbol_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)

# Label for Name with adjusted font size and padding
namecoin_label = tk.Label(info_frame, text="Name: ", bg="white", font=("Arial", 14), width=20, anchor="w")
namecoin_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)

# Label for Market Cap with adjusted font size and padding
market_cap_label = tk.Label(info_frame, text="Market Cap: ", bg="white", font=("Arial", 14), width=20, anchor="w")
market_cap_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)

# Label for 24h Change with adjusted font size and padding
price_change_label = tk.Label(info_frame, text="24h Change: ", bg="white", font=("Arial", 14), width=20, anchor="w")
price_change_label.grid(row=3, column=0, sticky="w", padx=10, pady=5)

# Label for Current Price with adjusted font size and padding
price_current_label = tk.Label(info_frame, text="Current Price: ", bg="white", font=("Arial", 14), width=20, anchor="w")
price_current_label.grid(row=4, column=0, sticky="w", padx=10, pady=5)

# Purchase History Frame
purchase_frame = tk.Frame(root)
purchase_frame.pack(pady=10)

# Labels
pic_label = tk.Label(purchase_frame, text="Token image will appear here", font=("Arial", 12))
pic_label.grid(row=0, column=0, padx=5)
coin_name_label = tk.Label(purchase_frame, text="Pic of Coin:", font=("Arial", 12))
coin_name_label.grid(row=1, column=0, padx=5)
coin_name_entry = tk.Entry(purchase_frame, width=25)
coin_name_entry.grid(row=0, column=1, padx=5)

purchase_price_label = tk.Label(purchase_frame, text="Purchase Price:", font=("Arial", 12))
purchase_price_label.grid(row=2, column=0, padx=5)
purchase_price_entry = tk.Entry(purchase_frame, width=25)
purchase_price_entry.grid(row=1, column=1, padx=5)

# Listbox for showing purchase history
purchase_history_listbox = tk.Listbox(purchase_frame, height=5, width=50)
purchase_history_listbox.grid(row=2, columnspan=2, pady=10)



# Add and Delete Buttons
save_button = tk.Button(purchase_frame, text="Save Purchase", command=save_purchase_history)
save_button.grid(row=4, column=0, padx=5, pady=10, sticky="w")
# Add Save Token Address Button
tk.Button(purchase_frame, text="Show All data", command=show_all_data).grid(row=4, column=0, columnspan=2, pady=10)
# โหลดข้อมูลการซื้อจากฐานข้อมูลและแสดงใน Listbox
delete_button = tk.Button(purchase_frame, text="Delete Selected", command=delete_purchase_history)
delete_button.grid(row=4, column=1, padx=5, pady=10, sticky="e")

# Fetch Token Address and Get Token Info Buttons
fetch_button = tk.Button(purchase_frame, text="Fetch Token Address", command=save_token_address)
fetch_button.grid(row=5, column=0, padx=5, pady=10, sticky="w")

tk.Button(purchase_frame, text="Get Token Info", command=update_token_info).grid(row=5, column=1, padx=5, pady=10, sticky="e")



def load_purchase_history():
    conn, cursor = connect_db()
    cursor.execute("SELECT coin_name, purchase_price FROM purchases")
    rows = cursor.fetchall()
    for row in rows:
        purchase_history_listbox.insert(tk.END, f"{row[0]} | {row[1]}")
    conn.close()
# โหลดข้อมูลเมื่อเริ่มโปรแกรม
load_purchase_history()
root.mainloop()
