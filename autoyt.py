import os
import instaloader
from moviepy.editor import *

# Initialize Instaloader
L = instaloader.Instaloader()
L.download_geotags = False
L.save_metadata = False
L.save_metadata_json = False
L.download_comments = False
L.download_thumbnail = False

# Login to your Instagram account
L.context.log("info", "Logging in...")
L.load_session_from_file("ex1m9966")
if not L.context.is_logged_in:
    L.context.log("info", "Session file does not exist or failed to load.")
    L.interactive_login("ex1m9966")

# Get profile object
profile = instaloader.Profile.from_username(L.context, "ex1m9966")

# Create directory for downloads
if not os.path.exists("dwl"):
    os.mkdir("dwl")

# Create directory for edited videos
if not os.path.exists("tmp"):
    os.mkdir("tmp")

# Set duration of stickers to 3 seconds
sticker_duration = 3

# Iterate through followed accounts and gather reels posted in the last week
reels_to_download = []
for following_profile in profile.get_followees():
    L.context.log("info", f"Processing account {following_profile.username}...")
    for post in following_profile.get_posts():
        if post.is_video and post.date_local >= one_week_ago:
            # Construct filename
            filename = f"{post.date_local.date()}_{post.owner_username}_{post.shortcode}.mp4"
            # Add reel to list of reels to download
            reels_to_download.append((post, filename))

# Show list of reels to download
L.context.log("info", f"Gathering {len(reels_to_download)} reels to download...")
for post, filename in reels_to_download:
    L.context.log("info", f" - {post.owner_username}: {filename}")

# Download reels
for post, filename in reels_to_download:
    # Download reel with custom filename
    L.download_post(post, target=os.path.join("dwl", filename))

    # Load the video clip
    clip = VideoFileClip(os.path.join("dwl", filename))

    # Get the duration of the clip
    duration = clip.duration

    # Load the two image files as stickers and resize them
    fgimg1 = ImageClip("fgimg1.png").resize(width=clip.w)
    fgimg2 = ImageClip("fgimg2.png").resize(width=clip.w)

    # Set the position of the stickers on the video clip
    fgimg1_pos = lambda t: (clip.w/2 - fgimg1.w/2, 0)
    fgimg2_pos = lambda t: (clip.w/2 - fgimg2.w/2, clip.h - fgimg2.h )

    # Add the stickers to the video clip
    clip_with_stickers = CompositeVideoClip([
        clip.set_duration(duration),
        fgimg1.set_position(fgimg1_pos).set_duration(sticker_duration),
        fgimg2.set_position(fgimg2_pos).set_duration(sticker_duration)
    ])

    # Define the output file path and write the output video file
    output_path = os.path.join("tmp", filename)
    clip_with_stickers.write_videofile(output_path)

    # Close the clip to free up memory
    clip.close()

# Logout
L.context.log("info", "Logging out...")
L.close()
