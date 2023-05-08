import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import glob
import shutil
import instaloader

client_secrets_file = "client_secret_946594729018-s42q7i95i5lbulnqvai6b3bvmkftha01.apps.googleusercontent.com.json"
scopes = ['https://www.googleapis.com/auth/youtube.upload']
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
creds = flow.run_local_server()

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        raise Exception("The client secret file was not found or the credentials are invalid.")

service = googleapiclient.discovery.build('youtube', 'v3', credentials=creds)

video_folder = "saved"

L = instaloader.Instaloader()
L.download_geotags = false
L.save_metadata = false
L.save_metadata_json = false
L.download_comments = false
L.download_thumbnail = false

L.load_session_from_file("ex1m9966")
if not L.context.is_logged_in:
    L.interactive_login("ex1m9966")

profile = instaloader.Profile.from_username(L.context, "ex1m9966")

video_paths = []
for post in profile.get_saved_posts():
    if post.typename == 'Video':
        title = os.path.splitext(os.path.basename(post.url))[0]
        filename = f"{title}.mp4"
        L.download_post(post, target=video_folder, filename=filename)
        video_paths.append(os.path.join(video_folder, filename))
        if len(video_paths) == 5:
            break

L.close()

uploaded_videos = []
for video_path in video_paths:
    title = os.path.splitext(os.path.basename(video_path))[0]
    video_metadata = {
        'snippet': {
            'title': title,
            'categoryId': '24'
        },
        'status': {
            'privacyStatus': 'private',
        }
    }

    request = service.videos().insert(
        part='snippet,status',
        body=video_metadata,
        media_body=video_path
    )

    response = request.execute(num_retries=5)
    uploaded_videos.append(response)

for video_path in video_paths:
    os.remove(video_path)

print("The following videos were successfully uploaded to your YouTube channel:")
for video in uploaded_videos:
    print("- %s" % video['snippet']['title'])
