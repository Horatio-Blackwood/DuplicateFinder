import hashlib, os, pprint, sys, time

def get_time_string(start, end):
    """ Given two times (a start and an end time in seconds) this function
        returns a formatted string showing the difference in hours minutes and
        seconds like so:  HH:MM:SS
    """
    diff = int(end) - int(start)
    seconds = 0
    minutes = 0
    hours = 0
    if diff > 60:
        seconds = diff % 60
        minutes = diff // 60

        if minutes > 60:
            minutes = minutes % 60
            hours = minutes // 60

    else:
        seconds = diff

    return str(hours) + ":" + str(minutes) + ":" + str(seconds)

def print_item(item):
    """ Prints out the tuple (key, val) pair from the results dict in an easy to read fashion.
    """
    print(item[0])
    for file in item[1]:
        print(" - ", file)

def iterate(dictionary):
    """ Recursively pops an item from the supplied dict and prints out its data then
        prompts the user to confirm if we should pop another item from the dict.
    """
    print_item(dictionary.popitem())
    
    again = input("Another?  ")
    # if the user wants to pop another item and the dictionary is not empty, recurse.
    if 'y' in again.lower() and dictionary:
        iterate(dictionary)


def main(directory, bytes_to_read, files_per_status):
    """ Given a directory, this function recursively walks the files of that dir
        and creates a checksum of the first 512 bytes of the file.  The checksum
        is used as a key into a dictionary.  Any files with matching checksums
        are added to the list used as the dictionary's value.

        When all files have been scanned, any key/value pairs with only one file
        are removed from the dict and any with duplicates are pretty printed to
        the screen.
    """
    print("Data Dir:", directory)
    print("Bytes to Read", bytes_to_read)
    print("Report status every", files_per_status, "files.\n")
    
    results = {} # md5 signature -> list of file names
    files_read = 0
    start_time = time.time()

    # Roll over all of the files, hash them and dump them into a dict
    for path, dirs, files in os.walk(directory):
        for filename in files:
            fullname = os.path.join(path, filename)

            with open(fullname, 'rb') as f:
                d = f.read(bytes_to_read)
                h = hashlib.md5(d).hexdigest()
                filelist = results.setdefault(h, [])
                filelist.append(fullname)
                files_read += 1

                if (files_read % files_per_status == 0):
                    print("Files read:  ", files_read)
                    print("Time elapsed:", get_time_string(start_time, time.time()), "\n")


    # Remove the Files that DON'T have duplicates.
    print("\nRemoving non-duplicates from results.")
    to_remove = []
    for key, value in results.items():
        if len(value) < 2:
            to_remove.append(key)
            
    for key in to_remove:
        del results[key]
    print("Done removing non-duplicates.")


    print("\nProcessing complete.")
    print("Checked ", files_read, "files in ", get_time_string(start_time, time.time()), ",")
    print("Found ", len(results), "files which likely have duplicates.")

    response = input("\nPrint Results?  ")
    if 'y' in response.lower():
        while(results):
            print_item(results.popitem())
    elif response == 'iter':
        iterate(results)



if __name__ == "__main__":
    directory = "."
    
    # Run script on current directory,
    # read in 2048 bytes fo each byte and do the hash on that.
    # print process time/stats every 1000 files.
    main(directory, 2048, 1000)
