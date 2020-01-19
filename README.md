# No-Intro DAT Matcher

Pretty filenames for ROM's based on No-Intro filenames.

Script will hash ROM files and match them with corresponding hash in the No-Intro dat file, and use the filename from there, and copy the ROM with the new filename to the destination folder. 

Missing and Unmatched ROM's/files will be printed out to a text file. This is useful for checking what ROM's you are missing.

This script will *never* move or delete any of your ROM's, it only copies them (make sure you have disk space!). 
Only files this script will overwrite is its own Missing and Unmatched text files.

# Pre-reqs

Python 3 with xmltodict and tqdm:

    pip3 install xmltodict tqdm
    
# Usage

- Get dat files from [DAT-o-MATIC](https://datomatic.no-intro.org/)
- Put roms in a folder
- Run the script: `python3 no-intro-dat-matcher.py platform.dat /folder/with/roms/`
    
# Example
    
    python3 no-intro-dat-matcher.py n64.dat ./n64_roms/
    
# Notes

-  NES games should end in .nes if they have a iNES header (most of them do). This script checks if the file ends with ".nes" and if so ignores the header by offsetting 16 bytes.
- For N64 games you might need both the Byte Swapped and Big Endian DATs, see: http://n64dev.org/romformats.html. You can use tool64 to convert the ROMs into one format.
- Gives errors in Windows sometimes if run through cmd/powershell. Seems to work better by using the Python version in cygwin and using cygwin terminal.
