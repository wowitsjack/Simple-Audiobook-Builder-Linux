import os
import json
import glob
import shutil
import eyed3
import emoji
from tqdm import tqdm
from pydub import AudioSegment
from humanfriendly import format_size

def main():
    print(emoji.emojize(':books: Welcome to the Audiobook Processor! :books:\n'))
    base_dir = input(emoji.emojize(':file_folder: Enter the path to the base directory containing the audiobook folders: '))

    if not os.path.exists(base_dir):
        print(emoji.emojize(':x: The specified directory does not exist.'))
        return

    json_file = 'processed_books.json'
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            processed_books = json.load(f)
    else:
        processed_books = []

    for folder in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder)
        if folder in processed_books:
            print(emoji.emojize(f':arrow_forward: Skipping {folder} (already processed).'))
            continue

        if os.path.isdir(folder_path):
            process_audiobook(folder_path)
            processed_books.append(folder)

            with open(json_file, 'w') as f:
                json.dump(processed_books, f)

    print(emoji.emojize(':white_check_mark: All audiobooks processed.'))

def process_audiobook(folder_path):
    print(emoji.emojize(f':file_folder: Processing {os.path.basename(folder_path)}...'))

    # Find and sort MP3 files
    mp3_files = sorted(glob.glob(os.path.join(folder_path, '*.mp3')))

    if not mp3_files:
        print(emoji.emojize(':x: No MP3 files found in the folder.'))
        return

    print(emoji.emojize(':scroll: Sorted MP3 files:'))
    for mp3_file in mp3_files:
        print(f'\t{os.path.basename(mp3_file)}')

    # Combine MP3 files
    combined = AudioSegment.empty()
    print(emoji.emojize(':arrows_counterclockwise: Combining MP3 files...'))
    for mp3_file in tqdm(mp3_files, unit='file'):
        audio = AudioSegment.from_mp3(mp3_file)
        combined += audio

    # Save combined file
    output_file = os.path.join(folder_path, 'combined.mp3')
    print(emoji.emojize(':floppy_disk: Saving combined MP3...'))
    combined.export(output_file, format='mp3')

    # Set ID3 details
    audiofile = eyed3.load(output_file)
    info_file = os.path.join(folder_path, 'info.txt')
    if os.path.exists(info_file):
        with open(info_file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith('Series Name'):
                    audiofile.tag.album = line.split('......')[1].strip()
                elif line.startswith('Total Runtime'):
                    audiofile.tag.title = line.split('......')[1].strip()
                elif line.startswith('Read by'):
                    audiofile.tag.artist = line.split('......')[1].strip()
            print(emoji.emojize(':wrench: Updating ID3 tags...'))
            audiofile.tag.save()

    output_size = format_size(os.path.getsize(output_file))
    print(emoji.emojize(f':white_check_mark: {os.path.basename(folder_path)} processed successfully. Combined MP3: {output_file} (Size: {output_size})'))

if __name__ == '__main__':
        main()
