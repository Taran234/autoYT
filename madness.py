import instaloader
import os
import datetime

# Initialize Instaloader
L = instaloader.Instaloader()
L.download_geotags = False
L.save_metadata = False
L.save_metadata_json = False
L.download_comments = False
L.download_thumbnail = False

# Prompt user for login credentials
username = input("Enter your Instagram username: ")
password = input("Enter your Instagram password: ")

# Login to your Instagram account
L.context.log("info", "Logging in...")
try:
    L.load_session_from_file(username)
    if not L.context.is_logged_in:
        raise Exception("Failed to log in using session file")
except (FileNotFoundError, Exception):
    L.context.log("info", "Session file does not exist or failed to load.")
    try:
        L.context.log("info", "Logging in with provided credentials...")
        L.context.login(username, password)
    except instaloader.exceptions.BadCredentialsException:
        L.context.log("info", "Invalid username or password provided.")
        exit()

# Get profile object
profile = instaloader.Profile.from_username(L.context, username)

# Calculate date 10 days ago
ten_days_ago = datetime.datetime.utcnow().date() - datetime.timedelta(days=10)

# Create directory for downloads
if not os.path.exists("dwl"):
    os.mkdir("dwl")

# Iterate through followed accounts and gather reels posted in the last 10 days
reels_to_download = []
for following_profile in profile.get_followees():
    L.context.log("info", f"Processing account {following_profile.username}...")
    for post in following_profile.get_posts():
        if post.is_video and post.date_local.date() >= ten_days_ago:
            # Construct filename
            filename = f"{post.date_local.date()}_{post.owner_username}_{post.shortcode}.mp4"
            # Add reel to list of reels to download
            reels_to_download.append((post, filename))
        # Limit the number of reels to download to a maximum of 25
        if len(reels_to_download) >= 25:
            break
    # Break out of the loop if the maximum number of reels has been reached
    if len(reels_to_download) >= 25:
        break

# Show list of reels to download
L.context.log("info", f"Gathering {len(reels_to_download)} reels to download...")
for post, filename in reels_to_download:
    L.context.log("info", f" - {post.owner_username}: {filename}")

# Download reels
for post, filename in reels_to_download:
    # Download reel with custom filename
    L.download_post(post, target=os.path.join("dwl", filename))

# Logout
L.context.log("info", "Logging out...")
L.close()
