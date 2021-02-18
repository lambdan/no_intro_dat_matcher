import os, sys, hashlib, shutil, time, xmltodict
from tqdm import tqdm
from argparse import ArgumentParser


large_size = 100*1000*1000 # 100 MB

# handle arguments
parser = ArgumentParser(description='Matches files (typically ROMs) with hashes from No-Intro and Redump .dat files to properly rename the files (roms)')
parser.add_argument("--input", action='store', dest='inputfolder', help='folder containing all roms', required=True)
parser.add_argument("--dat", action='store', dest='datfile', help='path to .dat file', required=True)
parser.add_argument("--output", action='store', dest='outputfolder', help='output folder for renamed roms. defaults to current working dir with the dat file as a subfolder if not specified')
parser.add_argument("--mode", action='store', dest='workmode', help='copy (cp), move (mv), or hardlink (lnk) roms. defaults to hardlink if not specified')
parser.add_argument('--verbose', action="store_true", dest='verbose', default=False)
parser.add_argument('-y', action="store_true", dest='no_confirm', default=False, help="Skips continue y/n prompt if used")
parser.add_argument('--skip-existing', action="store_true", dest='skip_existing', default=False, help="Files that are already in output folder will be considered matched. Useful when working with large files. Please note this does not hash the files so it's possible to have an incorrect match.")
parsed = parser.parse_args()

inputdir = parsed.inputfolder
datfile = parsed.datfile
verbose = parsed.verbose

if verbose:
	verbose = True
	print("Verbose mode activated")

if str(parsed.workmode).lower() == 'mv' or str(parsed.workmode).lower() == 'move':
	workmode = 'mv'
elif str(parsed.workmode).lower() == 'cp' or str(parsed.workmode).lower() == 'copy':
	workmode = 'cp'
else:
    workmode = 'lnk'

if verbose: print("Workmode set to", workmode)

if not parsed.outputfolder:
	outfolder = os.path.abspath('./' + os.path.splitext(datfile)[0]) # dat file without extension
else:
	outfolder = parsed.outputfolder


if not os.path.exists(outfolder):
	os.makedirs(outfolder)

if not os.path.isfile(datfile):
	print ("error! .dat file does not exist:", datfile)
	sys.exit(1)

if not os.path.exists(inputdir):
	print("error! input folder", inputdir, "does not exist")
	sys.exit(1)

if os.path.abspath(inputdir) == os.path.abspath(outfolder):
	print("error! input", inputdir, "and output", outputfolder, "is the same. that's probably not a good idea.")
	sys.exit(1)


def md5sum(filename, offset):
	size = os.path.getsize(filename)
	if verbose: print("md5sum", filename, str(offset) + " offset")
	if size > large_size: # only show hash progress bar if the file is large
		pbar_file = tqdm(total=os.path.getsize(filename))
		pbar_file.set_description("Hashing " + os.path.basename(filename))

	h = hashlib.md5()
	with open(filename, 'rb') as file:
		if offset > 0:
			file.read(offset) # read files with an offset, for iNES roms etc
		chunk = 0
		while chunk != b'':
			chunk = file.read(1024)
			h.update(chunk)
			if size > large_size:
				pbar_file.update(1024)

	if size > large_size:
		pbar_file.close()
	return h.hexdigest()


# read dat
with open(datfile) as df:
	doc = xmltodict.parse(df.read())
games= doc['datafile']['game']


files_handled = 0
unmatched = 0
dupes = 0
matches = 0
hashes = []

# count inputfolder
in_count = 0
for root, dirs, files in os.walk(inputdir):
    in_count += len(files)

# count outfolder
out_count = 0
for root, dirs, files in os.walk(outfolder):
    out_count += len(files)

# Confirm settings with user
print()
print ("DAT file:", datfile, "(" + str(len(games)) + " entries)")
print ("Input folder:", inputdir, "(" + str(in_count) + " files)")
print ("Output folder:", outfolder, "(" + str(out_count) + " files)")
if workmode == 'mv':
	print("Mode: move (files will be MOVED out of the input folder to the output folder)")
elif workmode == 'cp':
	print("Mode: copy (files will be COPIED from the input folder to the output folder)")
elif workmode == 'lnk' :
    print("Mode: hardlink (files will be HARDLINKED from the input folder to the output folder)")
print ("Skip existing:", parsed.skip_existing)
print()

if parsed.no_confirm == False:
	yn = input("Continue? y/N ").lower()
	if yn != "y":
		print ("Exiting...")
		sys.exit(1)

	print()

# Check for files already in output folder if --skip-existing
exist_skipped = 0
if parsed.skip_existing:
	print("Skip existing enabled! Checking for already existing files...")
	for g in games:
		destination = os.path.join(outfolder, g['rom']['@name'])

		if os.path.isfile(destination) and parsed.skip_existing:
			if verbose: print(g['rom']['@name'], "already in output folder!")
			matches += 1
			hashes.append(g['rom']['@md5'].lower())
			exist_skipped += 1
			files_handled += 1
	print("Skipped based on existing:", exist_skipped)
	print()

pbar = tqdm(total=in_count) # start progress bar
pbar.set_description("Processing input folder")

unmatched_output = ""

# iterate over input folder
for path, subdir, file in os.walk(inputdir):
	for name in file:
		files_handled += 1
		src = os.path.normpath(os.path.join(path,name))

		if os.path.isfile(os.path.join(outfolder, name)) and parsed.skip_existing:
			if verbose: print(" ", name, "is already in output folder, skipping...")
			pbar.update(1)
			continue

		if name.lower().endswith(".nes"):
			offset = 16 # iNES header offset
		else:
			offset = 0

		h = md5sum(src, offset).lower() # hashing should be the slow step, so updating the progress bar after it shouldn't be terrible?

		if h in hashes: # dupe
			dupes += 1
			pbar.update(1)
			continue
		else:
			hashes.append(h)

		matched = False
		for g in games:
			destination = os.path.join(outfolder, g['rom']['@name'])
			if h == g['rom']['@md5'].lower():
				matches += 1
				matched = True
				if verbose: print ("matched:", name, "-->", g['rom']['@name'])
				if not os.path.isfile(destination):
					if workmode == 'mv':
						if verbose: print ("moving:", name, "-->", destination)
						shutil.move(src, destination)
					elif workmode == 'cp':
						if verbose: print ("copying:", name, "-->", destination)
						shutil.copy(src, destination)
					elif workmode == 'lnk':
						if verbose: print ("hardlinking:", name, "-->", destination)
						os.link(src, destination)
				else:
					if verbose: print ("skipping copy: already exists:", destination)

				break

		if matched == False:
			if verbose: print ("no match:", name)
			unmatched += 1
			unmatched_output += name + "\n"

		pbar.update(1)


pbar.close()
print()

# missing roms
print ("Checking for missing roms...")
missing_output = "ROM\tMD5\tSHA1\n"
missing = 0
for g in games:
	h = g['rom']['@md5'].lower()
	if h not in hashes:
		missing += 1
		if verbose: print ("missing:", g['rom']['@name'])
		missing_output += g['rom']['@name'] + "\t" + g['rom']['@md5'] + "\t" + g['rom']['@sha1'] + "\n"

missing_filename = "Missing - " + os.path.basename(os.path.splitext(datfile)[0]) + ".txt"
print ("Writing", missing_filename)
with open(missing_filename, "w") as f:
	f.write(missing_output)

unmatched_filename = "Unmatched - " + os.path.basename(os.path.splitext(datfile)[0]) + ".txt"
print ("Writing", unmatched_filename)
with open(unmatched_filename, "w") as f:
	f.write(unmatched_output)

################################

print()
print ("Files handled:", files_handled)
print ("Unique hashes:", len(hashes))
print ("Duplicate files in input folder:", dupes)
if parsed.skip_existing: print ("Skipped existing:", exist_skipped)
print ("Matched roms:", matches)
print ("Missing roms:", missing, "(see " + missing_filename + ")")
print ("Unmatched files:", unmatched, "(see " + unmatched_filename + ")")