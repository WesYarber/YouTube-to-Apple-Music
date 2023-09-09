import os
from sys import platform
import re
import shutil
from io import BytesIO
import getpass
import tkinter as tk
import requests
from PIL import Image, ImageTk
from pytube import YouTube, Playlist
from mutagen.mp4 import MP4, MP4Cover
from tempfile import NamedTemporaryFile
import customtkinter as ctk
import tkinter.filedialog as filedialog

# Initialize constants
thumbnail_width = 100

# Initialize globals
download_folder = os.getcwd()
video_details_widgets = []

# Set up paths based on the platform
if platform in ("linux", "linux2"):
    print("Linux platform is not yet configured to move the file to Apple Music.")
elif platform == "darwin":
    username = getpass.getuser()
    apple_music_path = f"/Users/{username}/Music/Music/Media.localized/Automatically Add to Music.localized"
elif platform == "win32":
    print("Windows platform is not yet configured to move the file to Apple Music.")

def get_video_urls(playlist_url):
    """Get all video URLs from a YouTube playlist."""
    playlist = Playlist(playlist_url)
    video_urls = list(playlist.video_urls)
    return video_urls

def make_safe_filename(s):
    """
    Create a safe filename by replacing invalid characters with underscores.

    Parameters:
    s (str): The original filename string

    Returns:
    str: A safe filename string
    """
    # Define a dictionary of invalid characters and their replacements
    invalid_char_replacements = {
        '/': '_',
        '\\': '_',
        ':': '_',
        '*': '_',
        '?': '_',
        '"': '_',
        '<': '_',
        '>': '_',
        '|': '_',
    }

    # Replace each invalid character with its replacement
    for invalid_char, replacement in invalid_char_replacements.items():
        s = s.replace(invalid_char, replacement)
    
    # Remove any other non-alphanumeric characters (excluding periods and spaces)
    s = re.sub(r'[^\w\.\s-]', '_', s)
    
    return s

def add_metadata_to_mp4(input_filepath, output_filepath, title, artist, album, cover_art_path):
    """
    Add metadata to an MP4 file.

    Args:
    input_filepath (str): The path to the input MP4 file.
    output_filepath (str): The path to save the output MP4 file with metadata.
    title (str): The title metadata to add to the file.
    artist (str): The artist metadata to add to the file.
    album (str): The album metadata to add to the file.
    cover_art_path (str): The path to the cover art image file to add to the MP4 file.

    Returns:
    None
    """
    
    # Open the output file with mutagen
    audio = MP4(input_filepath)
    
    # Set the metadata
    audio["\xa9nam"] = title  # Title
    audio["\xa9ART"] = artist  # Artist
    audio["\xa9alb"] = album  # Album

    # Add cover art (assuming it's in JPEG format, use MP4Cover.FORMAT_PNG for PNG)
    with open(cover_art_path, 'rb') as f:
        audio["covr"] = [MP4Cover(f.read(), imageformat=MP4Cover.FORMAT_JPEG)]

    # Save the changes
    audio.save()
    # Copy the input file to the output file path
    
    shutil.copy2(input_filepath, output_filepath)

def select_download_folder():
    global download_folder
    # Open a dialog to select a download folder and set the selected folder as the value of a variable
    selected_folder = filedialog.askdirectory(initialdir=download_folder)  # This line opens the directory selection dialog
    if selected_folder:  # Only update if a folder was selected (i.e., the user didn't cancel the dialog)
        download_folder = selected_folder

def start_video_download():
    start_download(audio_only=False)

def start_audio_download():
    start_download(audio_only=True)

def start_download(audio_only, opt_url='none'):
    if opt_url == 'none':
        ytLink = link.get()
    else:
        ytLink = opt_url

    if "playlist" in ytLink:
        video_urls = get_video_urls(ytLink)
        for url in video_urls:
            start_download(audio_only, url)
        return()
    
    try:
        audio_save_path = apple_music_path
        ytObject = YouTube(ytLink, on_progress_callback=on_progress)
        finishLabel.configure(text="")
        display_youtube_video_details(ytLink, audio_only)
        
        # Creating a temporary file to store the downloaded audio/video
        temp_file = NamedTemporaryFile(delete=False, suffix=".mp4")  
        
        show_progress_frame()
        show_progress_bar()
        if audio_only:
            stream = ytObject.streams.filter(only_audio=True).first()
            stream.download(output_path=os.path.dirname(temp_file.name), filename=os.path.basename(temp_file.name))
            
            # Get video details to fetch metadata and cover art path
            video_details = get_youtube_video_details(ytLink)
            
            # Prepare the final save path with filename
            if download_folder != os.getcwd():
                audio_save_path_with_filename = os.path.join(download_folder, f"{make_safe_filename(ytObject.title)}.mp4")
            else:
                audio_save_path_with_filename = os.path.join(audio_save_path, f"{make_safe_filename(ytObject.title)}.mp4")
            
            # Add metadata to the downloaded file and save it to the final destination
            add_metadata_to_mp4(
                temp_file.name,
                audio_save_path_with_filename,
                title=video_details['title'],
                artist=video_details['uploader'],  # Assuming uploader as the artist here, adjust as necessary
                album="YouTube",  # Album info is not available from YouTube data, keeping it empty
                cover_art_path=video_details['thumbnail_path']
            )
        else:
            stream = ytObject.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            stream.download(output_path=download_folder)  # Use the download_folder variable here
        
        # Delete temporary files
        os.unlink(temp_file.name)
        os.unlink(video_details['thumbnail_path'])
        
        hide_progress_bar()
        link.delete(0, ctk.END)
        finishLabel.configure(text="Download complete.", text_color="white")
    except Exception as error:
        # print(error)
        if str(error).startswith("regex_search"):
            error = "Invalid link"
        show_progress_frame()
        hide_progress_bar()
        
        finishLabel.configure(text=f"Download Error: {error}", text_color="red")

def get_youtube_video_details(video_url):
    yt = YouTube(video_url)
    video_details = {
        "title": yt.title,
        "uploader": yt.author,
        "views": yt.views,
        "thumbnail_url": yt.thumbnail_url,
    }

    # Download and save the thumbnail as a temp file
    response = requests.get(video_details["thumbnail_url"])
    temp_thumbnail = NamedTemporaryFile(delete=False, suffix=".jpg")  # Creating a temp file with .jpg extension
    temp_thumbnail.write(response.content)
    temp_thumbnail.close()  # Close the file to allow other functions to use it

    video_details["thumbnail_path"] = temp_thumbnail.name  # Storing the temp file path
    # print(video_details)

    return video_details

def display_youtube_video_details(link, audio_only):
    # Destroy any existing widgets from a previous call to this function
    # for widget in video_details_widgets:
    #     widget.destroy()
    # video_details_widgets.clear()
    
    # Fetch the thumbnail image from the URL
    video_details = get_youtube_video_details(link)
    
    response = requests.get(video_details["thumbnail_url"])
    img_data = BytesIO(response.content)
    img = Image.open(img_data)
    aspect_ratio = img.width / img.height
    new_width = thumbnail_width
    new_height = int(new_width / aspect_ratio)
    img = img.resize((new_width, new_height), Image.LANCZOS)
    img_tk = ImageTk.PhotoImage(img)
    
    # Create a new frame to hold both the image and text details
    details_frame = tk.Frame(app)
    details_frame.pack(fill="x", padx=10, expand=True)  # Make the frame expand horizontally
    video_details_widgets.append(details_frame)
    
    # Create a label to hold the image
    label_img = tk.Label(details_frame, image=img_tk)
    label_img.img = img_tk
    label_img.grid(row=0, column=0, pady=2, sticky='nsew') # Adjusted the sticky parameter
    video_details_widgets.append(label_img)

    # Create a new frame to hold the text details
    text_details_frame = tk.Frame(details_frame)
    text_details_frame.grid(row=0, column=1, padx=10, sticky='nsew')  # Make the frame expand in both directions
    details_frame.grid_columnconfigure(1, weight=1)  # Allow the second column to expand
    video_details_widgets.append(text_details_frame)
    
    # Create labels for text details and add them to the text_details_frame
    label_title = tk.Label(text_details_frame, text=f"Title: {video_details['title']}", wraplength=315, font=('default',10))
    label_uploader = tk.Label(text_details_frame, text=f"Uploader: {video_details['uploader']}", font=('default',10))
    label_title.grid(row=0, column=0, sticky="w")
    label_uploader.grid(row=1, column=0, sticky="w")
    
    # Display whether audio or video was downloaded
    if audio_only:
        file_format = "Audio"
    else:
        file_format = "Video"
    label_format = tk.Label(text_details_frame, text=f"Format: {file_format}", font=('default',10))
    label_format.grid(row=2, column=0, sticky="w")

    text_details_frame.columnconfigure(0, weight=1)  # Allow the first column to expand

    video_details_widgets.extend([label_title, label_uploader, label_format])

def on_progress (stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_of_compeletion = bytes_downloaded / total_size * 100
    per = str(int(percentage_of_compeletion))
    progress_label.configure(text=per + '%')
    progress_label.update() 
    # Update progress bar
    progress_bar.set(int(percentage_of_compeletion) / 100)
    progress_bar.update() 

def resize_window_to_fit_contents():
    app.update_idletasks()
    app.wm_geometry("")

def hide_progress_frame():
    progress_frame.grid_remove()  
    progress_bar.set(0)

def show_progress_frame():
    progress_frame.grid(row=2, column=0, padx=10, pady=(5,5))
    
def hide_progress_bar():
    progress_label.pack_forget()
    progress_bar.pack_forget()
    hide_progress_frame()
    finishLabel.grid(row=2, column=0, padx=10, pady=(0,5))

def show_progress_bar():
    finishLabel.grid_remove()
    progress_label.pack(padx=(10,0), side="left")
    progress_bar.pack(padx=10, side="left")

if __name__ == "__main__":
    ctk.set_appearance_mode("Syste m")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.geometry("1x1")
    app.title("Youtube to Apple Music")

    # Download frame
    download_frame = ctk.CTkFrame(app)
    download_frame.pack(padx=10, pady=10)

    link_frame = ctk.CTkFrame(download_frame)
    link_frame.grid(row=0, column=0, padx=10, pady=(10,5))
    button_frame = ctk.CTkFrame(download_frame)
    button_frame.grid(row=1, column=0, padx=10, pady=(5,10), sticky="ew")

    # Configure the column weights to distribute extra space equally
    button_frame.columnconfigure(0, weight=1)
    button_frame.columnconfigure(1, weight=1)
    button_frame.columnconfigure(2, weight=1)  # Create an extra column to hold the additional space

    progress_frame = ctk.CTkFrame(download_frame)
    progress_frame.grid(row=2, column=0, padx=10, pady=(5,5))

    # Link text
    link = ctk.CTkEntry(link_frame, width=400, height=25, placeholder_text="Paste YouTube link here")
    link.pack(fill="x", padx=10, pady=10, side='left')
    # Progress bar
    progress_label = ctk.CTkLabel(progress_frame, text="0%")
    progress_label.pack(padx=(10,0), side="left")
    progress_bar = ctk.CTkProgressBar(progress_frame, width=415)
    progress_bar.set(0)
    progress_bar.pack(padx=10, side="left")
    # Download buttons
    video_download_button = ctk.CTkButton(button_frame, text="Download Video", command=start_video_download)
    video_download_button.grid(row=0, column=0, padx=(10,0), pady=10, sticky="ew")
    audio_download_button = ctk.CTkButton(button_frame, text="Download Audio", command=start_audio_download)
    audio_download_button.grid(row=0, column=2, padx=(0,10), pady=10, sticky="ew")

    # Create a button to open the folder selection dialog
    button_size = 15
    folder_icon_path = '/Users/w0y01ne/Desktop/YouTube Downloader/folder_icon.png'
    folder_icon = ctk.CTkImage(Image.open(folder_icon_path), size=(button_size, button_size))
    select_folder_button = ctk.CTkButton(link_frame, image=folder_icon, text="", command=select_download_folder, width=button_size, height=button_size)
    select_folder_button.pack(fill="x", padx=(0,10), pady=10, side='left')

    # Finished DownLoading
    finishLabel = ctk.CTkLabel(download_frame, text="")

    hide_progress_frame()

    # Run app
    resize_window_to_fit_contents()
    app.mainloop()