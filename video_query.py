from google.genai import types
from google import genai
import time

# load api key from .env file
import dotenv
import os
dotenv.load_dotenv()
api_key = os.getenv("API_KEY")


client = genai.Client(api_key=api_key)
MODEL_ID = "gemini-2.0-flash-exp"

prompt = "Generate a summary of the video and list all the formulas that were used and the reasoning behind it in a separate section. Just output the answer to my request and nothing else."

allFiles = os.listdir("./assets/videos")
# sort the all files to address the naming based on the last two digits of the file name
allFiles.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))

# exclude the first 9 files
allFiles = allFiles[9:]
# remember the 10th file is corrupted;
for ff in allFiles:
    if ff.endswith('.mp4'):
        print("Starting to upload video file: " + ff)
        video_file_name = f"./assets/videos/{ff}"
        video_file = client.files.upload(path=video_file_name)
        print(f"Completed upload : {video_file.uri}")

        # check the state of the video whether it's processed or not
        print("Checking the state of the video file...")
        while video_file.state == "PROCESSING":
            print("\tstill uploading file...")
            time.sleep(10)
            video_file = client.files.get(name=video_file.name)

        if video_file.state == "FAILED":
            raise ValueError(video_file.state)

        print(f'Video processing complete: ' + video_file.uri)

        response = client.models.generate_content(
            model=MODEL_ID,
            contents = [
                types.Content(
                    role='user',
                    parts=[
                        types.Part.from_uri(
                            file_uri=video_file.uri,
                            mime_type=video_file.mime_type),
                    ]),
                    prompt,
            ]
        )

        # Add the response to a single text file.
        with open(f"./assets/summaries.txt", "a") as text_file:
            text_file.write(response.text)
            text_file.write("\n\n\n")