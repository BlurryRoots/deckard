import os
import collections
import hashlib

searchpath = os.getcwd()

filters = ["Node2.1"]

CALCULATE_HASHES = True

HASH_CUNCK_SIZE = 65536
def hash_in_chuncks(filepath):
	sha1_hash = hashlib.sha1()
	with open(filepath, "rb") as filehandle:
		while True:
			chunk = filehandle.read(HASH_CUNCK_SIZE)
			if not chunk:
				break
			sha1_hash.update(chunk)
	return sha1_hash.hexdigest()

class SearchResult():
	def __init__(self, path, filenames, contained_folders):
		self.path = path
		self.filenames = filenames
		self.contained_folders = contained_folders
		self.filesizes = {}
		self.hashes = {}
		for filename in self.filenames:
			filepath = os.path.join(self.path, filename)
			self.filesizes[filename] = os.stat(filepath).st_size
			if CALCULATE_HASHES:
				self.hashes[filename] = hash_in_chuncks(filepath)
	def __str__(self):
		result = "%s / %s : %s" % (self.path, self.filesizes, self.contained_folders)
		return result
	def contains_file(self, filename):
		has_file = filename in self.filenames
		return has_file

results_by_path = {}
search_results = []
for (path, directories, filenames) in os.walk(searchpath):
	s = SearchResult(path, filenames, directories)
	search_results.append(s)
	results_by_path[path] = s

file_to_path_lookup = {}
duplicates = {}
for result in search_results:
	for filename in result.filenames:
		if filename in file_to_path_lookup:
			ignore_entry = False
			for entry in filters:
				if (entry in file_to_path_lookup[filename]) or (entry in result.path):
					ignore_entry = True
					break
			if not ignore_entry:
				if not filename in duplicates:
					path = file_to_path_lookup[filename]
					referenced_result = results_by_path[file_to_path_lookup[filename]]
					size = referenced_result.filesizes[filename]
					dup_info = {}
					dup_info["path"] = path
					dup_info["size"] = size
					if CALCULATE_HASHES:
						sha1_hash = referenced_result.hashes[filename]
						dup_info["hash"] = sha1_hash
					duplicates[filename] = [dup_info]
				dup_info = {}
				dup_info["path"] = result.path
				dup_info["size"] = result.filesizes[filename]
				if CALCULATE_HASHES:
					dup_info["hash"] = result.hashes[filename]
				duplicates[filename].append(dup_info)
		else:
			file_to_path_lookup[filename] = result.path

number_of_duplicates = len(duplicates)
message_ending = "s!"
if number_of_duplicates == 0:
	message_ending = "s."
elif number_of_duplicates == 1:
	message_ending = "!"

print("Found %s replicant%s\n" % (str(number_of_duplicates), message_ending))

for dup in duplicates:
	print("%s" % (dup))
	for path in duplicates[dup]:
		print(path)
	print("\n")