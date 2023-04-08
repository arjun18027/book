import os
import cv2
import numpy as np
import os
import random
import auto_subtitle
from moviepy.editor import AudioFileClip, VideoFileClip, CompositeVideoClip, concatenate_videoclips
import subprocess
import shutil
from pydub import AudioSegment

# set folder paths
audio_folder = 'audio'
video_folder = 'book'
output_folder = 'output'
subtitled_folder = 'subtitled'

audio_files = [f for f in os.listdir(audio_folder) if f.endswith('.mp3')]
video_files = [f for f in os.listdir(video_folder) if f.endswith('.mp4')]

for audio_file in audio_files:
    audio_path = os.path.join(audio_folder, audio_file)
    audio_duration = AudioFileClip(audio_path).duration

    # hitung jumlah video yang dibutuhkan berdasarkan durasi audio
    num_videos_needed = int(audio_duration / 10) + 1

    # jika jumlah video yang dibutuhkan lebih banyak daripada jumlah video yang tersedia
    # maka lakukan repetisi secara acak
    if num_videos_needed > len(video_files):
        selected_videos = random.choices(video_files, k=num_videos_needed)
    else:
        selected_videos = random.sample(video_files, num_videos_needed)

    # buat list VideoFileClip dari video yang dipilih
    video_clips = [VideoFileClip(os.path.join(video_folder, v)) for v in selected_videos]

    # gabungkan video menjadi satu file
    final_clip = concatenate_videoclips(video_clips, method="chain")

    # tambahkan audio dari file audio asli
    audio_clip = AudioFileClip(audio_path)
    final_clip = final_clip.set_audio(audio_clip)

    # potong bagian video yang melebihi durasi audio
    if final_clip.duration > audio_duration:
        final_clip = final_clip.subclip(0, audio_duration)

    # simpan hasil video ke dalam folder output dengan nama file yang sama dengan file audio
    output_path = os.path.join(output_folder, f"{os.path.splitext(audio_file)[0]}.mp4")
    final_clip.write_videofile(output_path, codec='h264_amf')

    # buat subtitle dan simpan ke dalam folder subtitled dengan nama file yang sama dengan file audio
    subtitle_path = os.path.join(subtitled_folder, f"{os.path.splitext(audio_file)[0]}.srt")
    os.system(f"auto_subtitle {os.path.join(output_folder, os.path.splitext(audio_file)[0] + '.mp4')} -o {subtitled_folder} --model large")

     # tambahkan subtitle ke video
    subtitle_path = f"{subtitled_folder}/{os.path.splitext(audio_file)[0]}.srt"
    subtitle_file = os.path.join(subtitled_folder, f"{os.path.splitext(audio_file)[0]}.srt")
    input_video_file = os.path.join(output_folder, f"{os.path.splitext(audio_file)[0]}.mp4")
    output_video_file = os.path.join(output_folder, f"{os.path.splitext(audio_file)[0]}_subtitled.mp4")

# Membuka backsound dan mendapatkan durasinya
backsound = AudioSegment.from_file("output/audio.mp3", format="mp3")
backsound_duration = backsound.duration_seconds

# loop untuk setiap file di folder subtitled
for filename in os.listdir(subtitled_folder):
    # cek apakah file adalah file video
    if filename.endswith(VIDEO_EXTENSIONS):
        # buka file video
        video_path = os.path.join(subtitled_folder, filename)
        video_clip = VideoFileClip(video_path)

        # Mendapatkan durasi video
        video_duration = video_clip.duration

        # Memotong backsound jika durasinya lebih panjang dari video
        if backsound_duration > video_duration:
            backsound = backsound[:video_duration*1000]

        # Mengulangi backsound sampai durasinya sama dengan video
        while backsound_duration < video_duration:
            backsound += backsound
            backsound_duration = backsound.duration_seconds

        # Mengedit level suara backsound
        backsound = backsound - 20

        # Menambahkan backsound ke video
        video_with_backsound = video_clip.set_audio(backsound)

        # Simpan video dengan backsound
        result_path = os.path.join(subtitled_folder, filename)
        video_with_backsound.write_videofile(result_path, codec="h264_amf")

        # hapus file lama
        os.remove(video_path)
