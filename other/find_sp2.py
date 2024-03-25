import os, fnmatch

def masking_sp():
    listOfFiles = os.listdir('/opt/utm/transport/lib')
    pattern = "sp-1.*"
    full_list = []
    for entry in listOfFiles:
        if fnmatch.fnmatch(entry, pattern):
                full_list.append(entry)
    full_list.sort(reverse=True)
    return (full_list[0])[:-4]

def masking_backbone():
    listOfFiles = os.listdir('/opt/utm/transport/lib')
    pattern = "terminal-backbone-*.jar"
    full_list = []
    for entry in listOfFiles:
        if fnmatch.fnmatch(entry, pattern):
                full_list.append(entry)
    full_list.sort(reverse=True)
    return (full_list[0])[:-4]
