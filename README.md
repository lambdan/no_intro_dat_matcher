# no_intro_dat_matcher
Pretty names for ROMs based on no_intro filenames

Script will hash ROM files and match them with corresponding hash in the no_intro .dat file, and use the filename from there. 

# Pre-reqs

Python 3 with xmltodict and tqdm:

    pip3 install xmltodict tqdm
    
# Usage

- Get `.dat` files from [DAT-o-MATIC](https://datomatic.no-intro.org/)
- Put roms in a folder
- Run the script: `python3 no-intro-dat-matcher.py platform.dat /folder/with/roms/`
    
# Example
    
    python3 no-intro-dat-matcher.py n64.dat ./n64_roms/
    
# Notes

-  NES games should end in .nes if they have a iNES header (most of them do). This script checks if the file ends with ".nes" and if so ignores the header by offsetting 16 bytes.
- For N64 games you might need both the Byte Swapped and Big Endian DATs, see: http://n64dev.org/romformats.html. You can use tool64 to convert the ROMs into one format.
- Gives errors in Windows sometimes if run through cmd/powershell. Seems to work better by using the Python version in cygwin and using cygwin terminal.
