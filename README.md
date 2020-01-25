# No-Intro DAT Matcher

(also Redump DAT Matcher)

Pretty filenames for ROM-files based on No-Intro/Redump filenames.

Script will hash files and match them with corresponding hash in the dat file, and use the filename from there, and copy the file with the new filename to the output folder.

Missing ROMS and Unmatched files will be printed out to a text file. This is useful for checking what ROM's you are missing.

# Usage

- Make sure you have Python 3 with `xmltodict` and `tqdm` installed: `pip3 install xmltodict tqdm`
- Get dat files from [DAT-o-MATIC](https://datomatic.no-intro.org/index.php?page=download) or [Redump](http://redump.org/downloads/)
- Run the script: `python3 no-intro-dat-matcher.py --dat datfile.dat --input /folder/with/roms/`
 
See the help page for more details: `python3 no-intro-dat-matcher.py -h`

# Examples

Use the .DAT file `n64.dat` with N64 ROMS that are in `./n64_roms/` and *copy* them properly renamed to `./n64_roms_proper_names/`:

    python3 no-intro-dat-matcher.py --dat n64.dat --input ./n64_roms/ --output ./n64_roms_proper_names/

Use the .DAT file `gc.dat` with GC ISOS that are in `./gc_in/` and **move** them properly renamed to `./gc_out/` and skip files that are already in `./gc_out/`:

    python3 no-intro-dat-matcher.py --dat gc.dat --input ./gc_in/ --output ./gc_out/ --mode move --skip-existing

# Notes

- Working with mulitple drives/volumes should work, and I have tested it, but if possible I recommend keeping the script, input and output folders on the same volume in the same folder
- If dealing with large disc based games I recommend using `--skip-existing` if you need to do multiple runs (like if you're adding games) because hashing many large files takes a very long time.
- For smaller cartridge based games I recommend not using `--skip-existing` as they don't take very long to hash and this ensures the files are correct
- Simiarily, if you are low on disk space and dealing with large games I recommend using `--mode move` to move the files instead of copying them. 
- NES games must end in .nes if they have a iNES header (most of them do), otherwise the hashes will not be matched. This script checks if the file ends with ".nes" and if so ignores the header by offsetting 16 bytes.
- For N64 games you might need both the Byte Swapped and Big Endian DATs, see: http://n64dev.org/romformats.html. You can use tool64 to convert the ROMs into one format.
- Gives errors in Windows sometimes if run through cmd/powershell. Seems to work better by using the Python version in cygwin and using cygwin terminal.
