import customtkinter as ctk
from tkinter import filedialog, messagebox, Scrollbar
import re
import requests
import os

# Initialize App with Light Theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("BEN Image Downloader")

# Get screen dimensions and set dynamic scaling
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()

app.geometry(f"{int(screen_width * 0.5)}x{int(screen_height * .85)}")  # Adjusted to 85% of screen height
app.resizable(False, False)  # Prevent resizing

def scale_ui(widget, width_ratio, height_ratio):
    widget.configure(width=int(screen_width * width_ratio), height=int(screen_height * height_ratio))

# Define UI Components Before Scaling
text_html = ctk.CTkTextbox(app, corner_radius=10)
text_urls = ctk.CTkTextbox(app, corner_radius=10)
entry_folder = ctk.CTkEntry(app)
text_status = ctk.CTkTextbox(app, corner_radius=10)

# Apply scaling to key elements
scale_ui(text_html, 0.9, 0.25)  # HTML text box
scale_ui(text_urls, 0.9, 0.25)  # URL list box
scale_ui(entry_folder, 0.4, 0.05)  # Folder selection entry
scale_ui(text_status, 0.9, 0.15)  # Status box


# Global Variable for URLs
urls_to_download = []

def reset_ui():
    """Reset all fields except the destination folder."""
    text_html.delete("1.0", "end")
    text_urls.delete("1.0", "end")
    text_status.delete("1.0", "end")
    progress_bar.set(0)
    status_label.configure(text="Status: Waiting")

def extract_image_urls():
    """Extract image URLs from pasted HTML text, remove duplicates, and display count."""
    text_urls.delete("1.0", "end")
    global urls_to_download
    urls_to_download = []

    html_content = text_html.get("1.0", "end").strip()
    
    url_pattern = r"https?://[^\s\"'>]+"
    all_urls = re.findall(url_pattern, html_content)

    # Filter URLs that contain 'project_modules' and modify them
    image_extensions = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg")
    urls_filtered = [
        re.sub(r"(project_modules/)[^/]+", r"\1source", url)
        for url in all_urls if "project_modules" in url and url.lower().endswith(image_extensions)
    ]

    # Remove duplicates
    urls_to_download = list(set(urls_filtered))

    if urls_to_download:
        count_message = f"Total Unique Image Links: {len(urls_to_download)}\n"
        text_urls.insert("end", count_message + "\n".join(urls_to_download))  # Display image URLs and count
    else:
        text_urls.insert("end", "No image URLs found in the HTML text.")

def select_download_folder():
    """Choose folder for image downloads."""
    folder_path = filedialog.askdirectory()
    if folder_path:
        entry_folder.delete(0, "end")
        entry_folder.insert(0, folder_path)
        btn_download.configure(state="normal")

def download_images():
    """Download all extracted image URLs."""
    if not urls_to_download:
        messagebox.showerror("Error", "No valid image URLs to download!")
        return

    download_folder = entry_folder.get()
    os.makedirs(download_folder, exist_ok=True)

    progress_bar.set(0)
    status_label.configure(text="Downloading...")

    for index, url in enumerate(urls_to_download):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            image_name = url.split("/")[-1]
            image_path = os.path.join(download_folder, image_name)

            with open(image_path, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)

            progress_bar.set((index + 1) / len(urls_to_download))  # Update progress bar smoothly
            app.update_idletasks()
        except Exception as e:
            text_status.insert("end", f"Failed: {url} - {str(e)}\n")

    status_label.configure(text="Download Complete!")
    text_status.insert("end", "Download finished.\n")
    messagebox.showinfo("Success", "Images downloaded successfully.")

# UI Components
frame_top = ctk.CTkFrame(app, corner_radius=10)
frame_top.pack(pady=10)

btn_reset = ctk.CTkButton(frame_top, text="Clear & Reset", command=reset_ui)
btn_reset.pack(side="left", padx=5)

text_html = ctk.CTkTextbox(app, width=850, height=250, corner_radius=10)
text_html.pack(pady=10)

btn_extract = ctk.CTkButton(app, text="Extract Image URLs", command=extract_image_urls)
btn_extract.pack(pady=10)

# Scrollable Text Box for Image Links
frame_scroll = ctk.CTkFrame(app, corner_radius=10)
frame_scroll.pack(fill="both", expand=True, pady=10)

scrollbar = Scrollbar(frame_scroll)
scrollbar.pack(side="right", fill="y")

text_urls = ctk.CTkTextbox(frame_scroll, width=850, height=300, corner_radius=10)
text_urls.pack(fill="both", expand=True)
text_urls.configure(yscrollcommand=scrollbar.set)
scrollbar.config(command=text_urls.yview)

frame_folder = ctk.CTkFrame(app, corner_radius=10)
frame_folder.pack(pady=10)

entry_folder = ctk.CTkEntry(frame_folder, width=400)
entry_folder.pack(side="left", padx=5)

btn_select_folder = ctk.CTkButton(frame_folder, text="Download Destination", command=select_download_folder)
btn_select_folder.pack(side="left")

btn_download = ctk.CTkButton(app, text="Download Images", command=download_images, state="disabled")
btn_download.pack(pady=10)

frame_status = ctk.CTkFrame(app, corner_radius=10)
frame_status.pack(pady=10)

status_label = ctk.CTkLabel(frame_status, text="Status: Waiting", text_color="blue")
status_label.pack(side="left", padx=10)

progress_bar = ctk.CTkProgressBar(frame_status, width=300)
progress_bar.pack(side="left", padx=10)

text_status = ctk.CTkTextbox(app, width=850, height=100, corner_radius=10)
text_status.pack(pady=10)

# Run the application
app.mainloop()