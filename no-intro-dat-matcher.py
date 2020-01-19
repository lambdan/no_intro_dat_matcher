import os, sys, hashlib, shutil, time, xmltodict
from tqdm import tqdm

large_size = 100*1000*1000 # 100 MB

if len(sys.argv) < 3:
    sys.exit('Usage: %s datfile.dat /folder/with/roms/' % sys.argv[0])

inputdir = os.path.abspath(sys.argv[2])
datfile = os.path.abspath(sys.argv[1])

def md5sum(filename, offset):
	size = os.path.getsize(filename)
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

if not os.path.exists(inputdir):
	print ("error: roms dir: " + inputdir + ": does not exist")
	sys.exit(1)

if not os.path.isfile(datfile):
	print ("error: dat: " + datfile + ": does not exist")
	sys.exit(1)

workdir = os.path.splitext(datfile)[0] # dat file without extension
if not os.path.exists(workdir):
	os.makedirs(workdir)

# read dat
with open(datfile) as df:
	doc = xmltodict.parse(df.read())
games= doc['datafile']['game']


files_handled = 0
unmatched = 0
dupes = 0
matches = 0
hashes = []

# setup
total = 0
for root, dirs, files in os.walk(inputdir):
    total += len(files)
files_to_process = total

print (".dat file:", datfile)
print ("Games in .dat:", len(games))
print ("Roms folder:", inputdir)
print ("Files in rom folder:", files_to_process)
pbar = tqdm(total=files_to_process) # start progress bar
pbar.set_description("Total progress")

unmatched_output = ""

# iterate roms
for path, subdir, file in os.walk(inputdir):
	for name in file:
		files_handled += 1
		src = os.path.normpath(os.path.join(path,name))

		if name.lower().endswith(".nes"):
			offset = 16 # iNES header offset
		else:
			offset = 0

		h = md5sum(src, offset).lower()

		if h in hashes: # dupe
			dupes += 1
			pbar.update(1)
			continue
		else:
			hashes.append(h)

		matched = False
		for g in games:
			if h == g['rom']['@md5'].lower():
				matches += 1
				matched = True
				#print ("matched:", name, "-->", g['rom']['@name'])
				destination = os.path.join(workdir, g['rom']['@name'])
				if not os.path.isfile(destination):
					#print ("copying:", name, "-->", destination)
					shutil.copy(src, destination)
				#else:
					#print ("skipping copy: already exists:", destination)
				break

		if matched == False:
			#print ("no match:", name)
			unmatched += 1
			unmatched_output += name + "\n"

pbar.close()

# missing roms
print ("Checking for missing roms...")
missing_output = "ROM\tMD5\tSHA1\n"
missing = 0
for g in games:
	h = g['rom']['@md5'].lower()
	if h not in hashes:
		missing += 1
		#print ("missing:", g['rom']['@name'])
		missing_output += g['rom']['@name'] + "\t" + g['rom']['@md5'] + "\t" + g['rom']['@sha1'] + "\n"

print ("Writing Missing.txt")
with open("Missing - " + os.path.basename(os.path.splitext(datfile)[0]) + ".txt", "w") as f:
	f.write(missing_output)

print ("Writing Unmatched.txt")
with open("Unmatched - " + os.path.basename(os.path.splitext(datfile)[0]) + ".txt", "w") as f:
	f.write(unmatched_output)

################################

print()
print ("Files handled:", files_handled)
print ("Unique files:", len(hashes))
print ("Duplicate files:", dupes)
print ("Matched roms:", matches)
print ("Missing roms:", missing, "(see Missing.txt)")
print ("Unmatched files:", unmatched, "(see Unmatched.txt)")