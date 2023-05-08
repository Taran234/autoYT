import os
from moviepy.editor import *

# Define the path to the "saved" folder
saved_path = "saved/"

# Define the path to the "tmp" folder
tmp_path = "tmp/"

# Loop through all video files in the "saved" folder
for filename in os.listdir(saved_path):
    if filename.endswith(".mp4"):
        # Load the video clip
        clip = VideoFileClip(os.path.join(saved_path, filename))

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
            fgimg1.set_position(fgimg1_pos).set_duration(duration),
            fgimg2.set_position(fgimg2_pos).set_duration(duration)
        ])

        # Define the output file path and write the output video file
        output_path = os.path.join(tmp_path, filename)
        clip_with_stickers.write_videofile(output_path)

        # Close the clip to free up memory
        clip.close()