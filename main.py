from pytube import YouTube
from pytube import Playlist
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from slugify import slugify
import anthropic_bedrock
from anthropic_bedrock import AnthropicBedrock
import sys
import json

claude = AnthropicBedrock(
    aws_region="us-west-2"
)

def get_subtitle(video_id):
    formatter = TextFormatter()
    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
    text_formatted = formatter.format_transcript(transcript)
    text_formatted = ' '.join(text_formatted.split())

    return text_formatted

def generate_abstract(subtitle, question):

    modelId = "anthropic.claude-v2:1"

    prompt = anthropic_bedrock.HUMAN_PROMPT + question + "\nTransctipt: \n" + subtitle + anthropic_bedrock.AI_PROMPT

    completion = claude.completions.create(
        model = modelId,
        max_tokens_to_sample=2048,
        temperature=0.5,
        top_p=0.999,
        top_k=250,
        prompt=prompt,
    )

    return completion.completion

def process_video(video_link):
    video = YouTube(video_link)
    video.streams.first()
    id = video.video_id
    title = video.title

    subtitle = get_subtitle(id)
    f = open(slugify(title)+'-sub.txt', 'w')
    f.write(subtitle)
    f.close()

    question = "Please answer the following questions based on a transcript from a Youtube video: \n 1. What is the video about? Is the video a customer case showcase or a feature deep dive? \n 2. What is the customer's challenge? \n 3. What feature or solutions does the video introduce? \n 4. What is the benefit of the feature or solutions?"

    abstract = generate_abstract(subtitle, question)
    f = open(slugify(title)+'abstract.txt', 'w')
    f.write("Title: " + title + "\n\n")
    f.write("Link: " + video_link + "\n\n")
    f.write("Description: " + video.description + "\n\n")
    f.write("Abstract generated by AI: \n\n")
    f.write(abstract)
    f.close()

def main():
    # video_link = "https://www.youtube.com/watch?v=up5t8Akof18"
    p = Playlist('https://www.youtube.com/playlist?list=PL2yQDdvlhXf-5R7VtNr9P4nosA7DiDtM1') # Re: Invent 2023 breakout sessions
    for url in p.video_urls[:1]:
        print ("Processing: " + url + "\n")
        process_video(url)

if __name__ == '__main__':
    sys.exit(main())