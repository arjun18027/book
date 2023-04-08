import os
import multiprocessing as mp
from pydub import AudioSegment, silence

# Get the current working directory
cwd = os.getcwd()

# Define a function to process audio files
def process_audio_file(audio_file):
    # Load audio file and increase volume by 6 dB
    audio = AudioSegment.from_file(audio_file, format="mp3") + 6

    # Find and split the audio into non-silent chunks
    chunks = silence.split_on_silence(audio, min_silence_len=500, silence_thresh=-50)

    # Add 0.3 seconds of silence to each chunk of silence except the first and last chunks
    for i in range(1, len(chunks) - 1, 2):
        silence_chunk = AudioSegment.silent(duration=300)
        chunks[i] = silence_chunk + chunks[i] + silence_chunk

    # Concatenate all chunks back into a single audio file
    output_audio = chunks[0]
    for chunk in chunks[1:]:
        output_audio += chunk

    # Export the output audio file with the same filename
    output_filename = os.path.join(cwd, "new_" + os.path.basename(audio_file))
    output_audio.export(output_filename, format="mp3")

    # Replace the original audio file with the processed audio file
    os.remove(audio_file)
    os.rename(output_filename, audio_file)

# Define a function to process audio files using multiprocessing
def process_audio_files_parallel(audio_files):
    with mp.Pool(processes=mp.cpu_count()) as pool:
        pool.map(process_audio_file, audio_files)

if __name__ == '__main__':
    mp.freeze_support()

    # Loop through each audio file in the current working directory and process it using multiprocessing
    audio_files = [os.path.join(cwd, filename) for filename in os.listdir(cwd) if filename.endswith(".mp3")]
    process_audio_files_parallel(audio_files)
