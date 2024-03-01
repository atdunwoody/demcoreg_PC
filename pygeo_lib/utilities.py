import os



def log(msg, log_file, header =False, print_msg = True):
    """Write a message to a log file."""
    if header:
        with open(log_file, 'w') as f:
            f.write('----------------------------------------------\n')
            f.write(msg + '\n')
        if print_msg:
            print(msg)
    else:            
        with open(log_file, 'a') as f:
            f.write(msg + '\n')
        if print_msg:
            print(msg)

def files_from_folder(folder, ext = None, tag = None):
    """Return a list of files from a folder.
    folder: folder path
    ext: file extension
    """
    if ext is None and tag is None:
        return [os.path.join(folder, f) for f in os.listdir(folder)]
    elif ext is not None and tag is None:
        return [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(ext)]
    elif ext is None and tag is not None:
        return [os.path.join(folder, f) for f in os.listdir(folder) if tag in f]
    else:
        return [os.path.join(folder, f) for f in os.listdir(folder) if tag in f and f.endswith(ext)]

