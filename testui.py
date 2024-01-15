import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import pandas as pd
from ultralytics import YOLO
from tracker import*
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import api
from math import dist

class VideoPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1120x600")
        self.root.title("Traffic Management")

        self.video_path = tk.StringVar()
        self.video_path.set("")
        self.sender = tk.StringVar()
        self.sender.set("")

        # Entry widget to get video path
        self.entry = tk.Entry(root, textvariable=self.video_path, width=40)
        self.entry.grid(row=0, column=0, padx=10, pady=10)

        self.entry = tk.Entry(root, textvariable=self.sender, width=40)
        self.entry.grid(row=1, column=0, padx=10, pady=10)

        # Button to browse for a video file
        self.browse_button = tk.Button(root, text="Browse", command=self.browse_video)
        self.browse_button.grid(row=0, column=1, padx=10, pady=10)

        # Button to play the video
        self.play_button = tk.Button(root, text="Run", command=self.play_video)
        self.play_button.grid(row=1, column=1, columnspan=2, pady=10)

        # Canvas to display video frames
        self.canvas = tk.Canvas(root)
        self.canvas.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    def browse_video(self):
        video_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mkv")])
        self.video_path.set(video_path)

    def play_video(self):
        video_path = self.video_path.get()
        sender = self.sender.get()
        import main
        main.detect()
        if video_path:
            if video_path == "self":
                cap = cv2.VideoCapture(0)  # Webcam
            else:
                cap = cv2.VideoCapture(video_path)

            # Get video properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # Set up the canvas for displaying frames
            self.canvas.config(width=width, height=height)

            # Read and display video frames
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Convert OpenCV BGR image to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Convert the frame to ImageTk format
                img_tk = ImageTk.PhotoImage(Image.fromarray(frame_rgb))

                # Update the canvas with the new frame
                self.canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)

                # Display each frame for 30 milliseconds (adjust as needed)
                self.root.update_idletasks()
                self.root.update()
                self.root.after(30)

            cap.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoPlayerApp(root)
    root.mainloop()
