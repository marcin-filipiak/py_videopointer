import cv2
import numpy as np
import tkinter as tk
from tkinter import messagebox, colorchooser, ttk
from PIL import Image, ImageTk

# Video parameters
video_path = "input.mp4"
cap = cv2.VideoCapture(video_path)
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
fps = int(cap.get(cv2.CAP_PROP_FPS))

# OpenCV fonts
font_options = {
    "Hershey Simplex": cv2.FONT_HERSHEY_SIMPLEX,
    "Hershey Plain": cv2.FONT_HERSHEY_PLAIN,
    "Hershey Duplex": cv2.FONT_HERSHEY_DUPLEX,
    "Hershey Complex": cv2.FONT_HERSHEY_COMPLEX,
    "Hershey Triplex": cv2.FONT_HERSHEY_TRIPLEX,
    "Hershey Script Simplex": cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,
    "Hershey Script Complex": cv2.FONT_HERSHEY_SCRIPT_COMPLEX
}
selected_font = cv2.FONT_HERSHEY_SIMPLEX

# Create Tkinter window
root = tk.Tk()
root.title("Video Text - Interface")
root.geometry("1400x500")

# Point tracking parameters
lk_params = dict(winSize=(15, 15), maxLevel=2, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
tracking = False
point = None
prev_gray = None
prev_point = None
text_color = (0, 255, 0)  # Default green color

# Create frames
image_frame = tk.Frame(root)
image_frame.grid(row=0, column=0, padx=10, pady=10)
form_frame = tk.Frame(root)
form_frame.grid(row=0, column=1, padx=10, pady=10)

def choose_color():
    global text_color
    color_code = colorchooser.askcolor(title="Choose text color")[0]
    if color_code:
        text_color = tuple(int(c) for c in color_code)
        color_label.config(text=f"Color: {text_color}")

def select_font(event):
    global selected_font
    selected_font = font_options[font_combo.get()]

def resize_image(image, max_width):
    img_height, img_width = image.shape[:2]
    aspect_ratio = img_width / img_height
    new_width = max_width
    new_height = int(new_width / aspect_ratio)
    return cv2.resize(image, (new_width, new_height))

def show_image(image):
    resized_image = resize_image(image, 800)
    image_rgb = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)
    photo = ImageTk.PhotoImage(image=Image.fromarray(image_rgb))
    canvas.create_image(0, 0, image=photo, anchor=tk.NW)
    canvas.image = photo

def start_rendering():
    global point, prev_gray, prev_point, text_entry, text_color
    if point is None:
        messagebox.showerror("Error", "You must select a point on the frame!")
        return
    text = text_entry.get()
    if not text:
        messagebox.showerror("Error", "You must enter text!")
        return
    cap = cv2.VideoCapture(video_path)  # Reopen file    
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    ret, first_frame = cap.read()
    if not ret:
        messagebox.showerror("Error", "Failed to load video.")
        return
    prev_gray = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)
    prev_point = point
    out = cv2.VideoWriter('output.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        new_point, status, _ = cv2.calcOpticalFlowPyrLK(prev_gray, gray, prev_point, None, **lk_params)
        if status[0] == 1:
            x, y = new_point.ravel()
            cv2.putText(frame, text, (int(x), int(y)), selected_font, 1, text_color[::-1], 2)
            prev_point = new_point
        prev_gray = gray
        out.write(frame)
    cap.release()
    out.release()
    messagebox.showinfo("Completed", "Rendering finished! Video saved as output.mp4.")

def select_point(event):
    global point
    aspect_ratio = frame_width / frame_height
    new_width = 800
    new_height = int(new_width / aspect_ratio)
    real_x = int((frame_width * event.x) / 800)
    real_y = int((frame_height * event.y) / new_height)
    point = np.array([[real_x, real_y]], dtype=np.float32)
    point_label.config(text=f'Coordinates: ({real_x}, {real_y})')

def start_gui():
    global canvas, text_entry, point_label, color_label, font_combo
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    ret, first_frame = cap.read()
    if not ret:
        messagebox.showerror("Error", "Failed to load video.")
        return
    canvas = tk.Canvas(image_frame, width=800, height=500)
    canvas.pack()
    show_image(first_frame)
    tk.Label(form_frame, text="Enter text:").grid(row=0, column=1)
    text_entry = tk.Entry(form_frame)
    text_entry.grid(row=0, column=2, padx=10)
    point_label = tk.Label(form_frame, text="Coordinates: (x, y)")
    point_label.grid(row=1, column=2, pady=5)
    tk.Button(form_frame, text="Choose color", command=choose_color).grid(row=2, column=1, pady=10)
    color_label = tk.Label(form_frame, text=f"Color: {text_color}")
    color_label.grid(row=2, column=2, pady=5)
    tk.Label(form_frame, text="Choose font:").grid(row=3, column=1)
    font_combo = ttk.Combobox(form_frame, values=list(font_options.keys()))
    font_combo.grid(row=3, column=2, pady=5)
    font_combo.current(0)
    font_combo.bind("<<ComboboxSelected>>", select_font)
    tk.Button(form_frame, text="Start rendering", command=start_rendering).grid(row=4, column=1, pady=10)
    canvas.bind("<Button-1>", select_point)
    root.mainloop()

start_gui()
