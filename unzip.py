#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import codecs
import zipfile
import textwrap

def print_usage(myname):
    USAGE = textwrap.dedent("""
        Usage: {0} operation [...]
        operation:
            {0} -h                                   # show help
            {0} -l [option] foo.zip [bar.zip ...]    # show file list of zipfiles
            {0} -z [option] foo.zip [bar.zip ...]    # show comment only
            {0} -t [option] foo.zip [bar.zip ...]    # test if zipfiles are valid
            {0} [option] foo.zip [bar.zip ...]       # extract zipfile
        option:
            -O encoding    # give specific encoding, such as gbk, shift-jis and so on
        """).format(myname)
    print(USAGE)
    return None

def main(*argv):
    myname = os.path.basename(argv[0])
    args = argv[1:]
    i = 0
    l = len(args)
    encoding = "utf-8"
    files = []
    O_FLAG = 0
    MODE = 0

    if l == 0:
        print_usage(myname)
        sys.exit(255)

    while i < l:
        arg = args[i]
        if arg.startswith("-"):
            option = arg[1:]
            if option == "O":
                if O_FLAG == 0:
                    i += 1
                    try:
                        encoding = args[i]
                    except IndexError:
                        print("Error: no targets specified! (use -h for help)")
                        sys.exit(2)
                    else:
                        try:
                            codecs.lookup(encoding)
                        except LookupError:
                            print("Error: unkown encoding: %s" % encoding)
                            sys.exit(3)
                        else:
                            O_FLAG = 1
                else:
                    print("Error: do not set '%s' more than once!" % arg)
                    sys.exit(1)
            else:
                if MODE == 0:
                    if option == "t":
                        MODE = 1
                    elif option == "l":
                        MODE = 2
                    elif option == "z":
                        MODE = 3
                    elif option == "h":
                        MODE = 4
                    else:
                        print("Error: invalid option -- '%s'" % option)
                else:
                    print("Error: only one operation may be used at a time!")
        else:
            files.append(arg)
        i += 1

    if MODE == 0:
        for filename in files:
            try:
                if not zipfile.is_zipfile(filename):
                    print("Error: %s is not a valid ZIP file!" % filename)
                f = zipfile.ZipFile(filename, "r")
            except IOError:
                print("Error: No such file or directory: '%s'" % filename)
                sys.exit(404)
            else:
                print("\nProcessing archive: %s \n" % filename)
                ALL_FLAG = 0
                for name in f.namelist():
                    utf8name = name.decode(encoding).encode("utf-8")
                    pathname = os.path.dirname(utf8name)
                    if utf8name.endswith("/"):
                        if not os.path.exists(pathname):
                            print("Creating %s" % utf8name)
                            os.makedirs(pathname)
                    else:
                        if os.path.exists(utf8name):
                            print("Extracting %s" % utf8name)
                            while True:
                                if ALL_FLAG == 0:
                                    print(pathname)
                                    input_str = raw_input("replace %s? [y]es, [n]o, [A]ll, [N]one, [r]ename: " % utf8name)
                                    if input_str == "y" or input_str == "A":
                                        with open(utf8name, "wb") as fo:
                                            fo.write(f.read(name))
                                        if input_str == "A":
                                            ALL_FLAG = 1
                                        break
                                    elif input_str == "n" or input_str == "N":
                                        if input_str == "N":
                                            ALL_FLAG = 2
                                        break
                                    elif input_str == "r":
                                        new_name = raw_input("new name: ")
                                        new_pathname = pathname + "/" + new_name
                                        print("\trenaming: %s -> %s" % (utf8name, new_pathname))
                                        with open(new_pathname, "wb") as fo:
                                            fo.write(f.read(name))
                                        break
                                    else:
                                        continue
                                elif ALL_FLAG == 1:
                                    with open(utf8name, "wb") as fo:
                                        fo.write(f.read(name))
                                    break
                                elif ALL_FLAG == 2:
                                    print("skip...")
                                    break
                        else:
                            with open(utf8name, "wb") as fo:
                                fo.write(f.read(name))
                f.close()
        print("\nEverything is Ok")

    elif MODE == 1:
        for filename in files:
            try:
                if not zipfile.is_zipfile(filename):
                    print("Error: %s is not a valid ZIP file!" % filename)
                f = zipfile.ZipFile(filename, "r")
            except IOError:
                print("Error: No such file or directory: '%s'" % filename)
                sys.exit(404)
            else:
                print("\nTesting archive: %s\n" % filename)
                try:
                    f.testzip()
                except RuntimeError:
                    print("Error: %s is a closed ZipFile!" % filename)
                    sys.exit(4)
                else:
                    print("No errors detected in compressed data of %s\n" % filename)

    elif MODE == 2 or MODE == 3:
        for filename in files:
            try:
                if not zipfile.is_zipfile(filename):
                    print("Error: %s is not a valid ZIP file!" % filename)
                f = zipfile.ZipFile(filename, "r")
            except IOError:
                print("Error: No such file or directory: '%s'" % filename)
                sys.exit(404)
            else:
                print("\nListing archive: %s\n" % filename)
                if f.comment == "":
                    print("No comment")
                else:
                    print("Comment: %s" % f.comment)
                if MODE == 2:
                    print("\nDate\tTime\t\tSize\tCompressed\tName")
                    print("------------------\t------\t----------\t------------------------")
                    for zipinfo in f.infolist():
                        utf8name = zipinfo.filename.decode(encoding).encode("utf-8")
                        date_time = zipinfo.date_time
                        size = zipinfo.file_size
                        compressed = zipinfo.compress_size
                        print("%d-%d-%d %02d:%02d:%02d\t%s\t%s\t\t%s" % (date_time[0], date_time[1], date_time[2], date_time[3], date_time[4], date_time[5], size, compressed, utf8name))
                f.close()

    elif MODE == 4:
        print_usage(myname)

    return 0

if __name__ == "__main__":
    import sys
    main(*sys.argv)