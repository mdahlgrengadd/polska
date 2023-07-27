import os
import subprocess

# Mapping for transposition
TRANSPOSITION_DICT = {
    # For Major keys
    'C': 0,  'G': -7,  'D': -2,  'A': 3,  'E': -4, 
    'B': 1, 'F#': -6, 'Db': -1,  'Ab': 4,  'Eb': -3,
    'Bb': 2, 'F': -5, 
    # For Minor keys
    'Am': 0,  'Em': -7,  'Bm': -2,  'F#m': 3,  'C#m': -4,  
    'G#m': 1, 'D#m': -6, 'Bbm': -1, 'Fm': 4,  'Cm': -3,
    'Gm': 2, 'Dm': -5,
}

# Specify your directory here
abc_dir_downloaded = 'downloaded_songs'
abc_dir_converted = 'converted_songs'

for filename in os.listdir(abc_dir_downloaded):
    if filename.endswith('.abc'):
        filepath = os.path.join(abc_dir_downloaded, filename)
        # Transpose the file with abc2abc
        try:
            with open(filepath, 'r') as file:
                tune = file.read()
                # Detect the key
                key_line = [line for line in tune.split('\n') if line.startswith('K:')][0]
                original_key = key_line.split(':')[1].strip()
                # Look up the number of semitones to transpose
                try:
                    semitones = TRANSPOSITION_DICT[original_key]
                except KeyError:
                    print(f'Original key {original_key} not found in transposition dictionary')
                    continue
                # Transpose the tune
                transposed_tune = subprocess.run(['abc2abc', filepath, '-t', str(semitones), '-V', '1', '-e'], capture_output=True, text=True).stdout
                # Write the transposed tune to a new file
                new_filename = os.path.splitext(filename)[0] + '_transposed.abc'
                new_filepath = os.path.join(abc_dir_converted, new_filename)
                with open(new_filepath, 'w') as new_file:
                    new_file.write(transposed_tune)
        except Exception as e:
            print(f"Failed to transpose {filename}. Error: {e}")
