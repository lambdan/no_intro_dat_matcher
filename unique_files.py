import os, sys, hashlib, shutil
from tqdm import tqdm
from argparse import ArgumentParser


# handle arguments
parser = ArgumentParser(description='Hashes files and copies unique files to a folder. Useful for removing duplicate roms.')
parser.add_argument("-i", action='store', dest='inputfolder', help='folder containing all files', required=True)
parser.add_argument("-o", action='store', dest='outputfolder', help='output folder for unique files', required=True)
parser.add_argument("-m", action='store', dest='workmode', help='copy (cp) or move (mv) roms. defaults to copy if not specified')
parser.add_argument('-v', action="store_true", dest='verbose', default=False)
parsed = parser.parse_args()

inputdir = parsed.inputfolder
verbose = parsed.verbose
outfolder = parsed.outputfolder

if verbose:
	verbose = True
	print("Verbose mode activated")

if str(parsed.workmode).lower() == 'mv' or str(parsed.workmode).lower() == 'move':
	workmode = 'mv'
else:
	workmode = 'cp'

if verbose: print("Workmode set to", workmode)


if not os.path.exists(outfolder):
	os.makedirs(outfolder)

if not os.path.exists(inputdir):
	print("error! input folder", inputdir, "does not exist")
	sys.exit(1)

if os.path.abspath(inputdir) == os.path.abspath(outfolder):
	print("error! input", inputdir, "and output", outputfolder, "is the same. that's probably not a good idea.")
	sys.exit(1)


def md5sum(filename, offset):
	size = os.path.getsize(filename)
	if verbose: print("md5sum", filename, str(offset) + " offset")

	h = hashlib.md5()
	with open(filename, 'rb') as file:
		if offset > 0:
			file.read(offset) # read files with an offset, for iNES roms etc
		chunk = 0
		while chunk != b'':
			chunk = file.read(1024)
			h.update(chunk)

	return h.hexdigest()



files_handled = 0
dupes = 0
hashes = []

# count inputfolder
in_count = 0
for root, dirs, files in os.walk(inputdir):
    in_count += len(files)


pbar = tqdm(total=in_count) # start progress bar
pbar.set_description("Processing")

# iterate over input folder
for path, subdir, file in os.walk(inputdir):
	for name in file:
		files_handled += 1
		src = os.path.normpath(os.path.join(path,name))

		offset = 0
		h = md5sum(src, offset).lower() # hashing should be the slow step, so updating the progress bar after it shouldn't be terrible?

		if h in hashes: # dupe
			dupes += 1
			pbar.update(1)
			continue
		else:
			hashes.append(h)

		destination = os.path.join(outfolder, h) # h (hash) as filename, no extension

		if not os.path.isfile(destination):
			if workmode == 'mv':
				if verbose: print ("moving:", name, "-->", destination)
				shutil.move(src, destination)
			elif workmode == 'cp':
				if verbose: print ("copying:", name, "-->", destination)
				shutil.copy(src, destination)
		else:
			if verbose: print ("skipping copy: already exists:", destination)


		pbar.update(1)


pbar.close()
print()

################################

print()
print ("Files handled:", files_handled)
print ("Unique hashes:", len(hashes))
print ("Duplicate files in input folder:", dupes)