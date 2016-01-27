__author__ = "huziy"
__date__ = "$5 juil. 2011 14:05:27$"

import os
import subprocess
import shutil

phy_folder = '../../PHY'
dyn_folder = '../../DYN'

subroutine_word = 'subroutine'
function_word = "function"
end = 'end'
end_subroutine = end + subroutine_word
end_function = end + function_word

interface = 'interface'
end_interface = end + interface

FORTRAN_CALL = 'call '

from node import Node
import re

# to get node object by name
name_to_node = {}


# get node object by name, create new if does not yet exists
def get_node_by_name(name=''):
    if name in name_to_node:
        return name_to_node[name]
    else:
        node = Node(name=name)
        name_to_node[name] = node
        return node


def is_fixed_form_splited(lines):
    if len(lines) == 0:  # if there is no following line
        return False

    follow_line = lines[0]
    if follow_line[0:5] == '     ' and follow_line[5] != ' ':
        return True

    return False


def next_line(lines, fixed_format=False):
    '''
    returns line in lower case without comments
    if the lines were splitted in the file, the peaces are
    connected.
    '''
    line = lines.pop(0)

    # treat comments in fixed format file
    if fixed_format:
        if line[0] != ' ' and line[0:8] != '#include':
            return ''

    line = line.lower()

    if line.strip().startswith('!'):  # skip comments
        return ''

    line = line.strip()

    # connect splitted lines
    if not fixed_format:
        line1 = line
        if "!" in line1:
            line1 = line1[:line1.index("!")]

        while line1.endswith('&'):
            line = lines.pop(0)
            if "!" in line:
                line = line[:line.index("!")]
            line1 = line[:-1] + line
        line = line1.strip()

    if fixed_format:
        # Do line connecting for the fixed format
        line1 = line
        if "!" in line:
            line1 = line1[:line.index("!")]

        while is_fixed_form_splited(lines):
            line = lines.pop(0).strip()
            if "!" in line:
                line = line[:line.index("!")]
            line1 += line.strip()[1:]
        line = line1.strip()
        pass

    line = re.sub(r"\"(.*)\"|'(.*)'", "", line).strip()

    return line


# parse file to Nodes
def parse_file(path, ignore_nodes=()):
    print(path)

    lines = []
    with open(path, errors="ignore") as f:
        for l in f:
            lines.append(l)

    path_lower = path.lower()
    fixed = path_lower.endswith('.ftn') or path_lower.endswith('.f')
    while len(lines) > 0:
        line = next_line(lines, fixed_format=fixed)
        the_word = None
        if line.startswith(subroutine_word) or line.startswith(function_word):
            the_word = subroutine_word if line.startswith(subroutine_word) else function_word

        if the_word is not None:

            sub_name = get_sub_name(line, the_word)
            parentNode = get_node_by_name(sub_name)

            line = next_line(lines, fixed_format=fixed)
            line_without_spaces = line.replace(' ', '')
            while end_subroutine not in line_without_spaces and end_function not in line_without_spaces:
                line = next_line(lines, fixed_format=fixed)
                line_without_spaces = line.replace(' ', '')

                # skip interface
                if line_without_spaces.startswith(interface):
                    while not line_without_spaces.startswith(end_interface):
                        line = next_line(lines, fixed_format=fixed)
                        line_without_spaces = line.replace(' ', '')
                    line = next_line(lines, fixed_format=fixed)
                    line_without_spaces = line.replace(' ', '')

                # end of the subroutine or function
                if line_without_spaces == end:
                    break

                # parse children nodes
                if FORTRAN_CALL in line:
                    fields = line.split()
                    if FORTRAN_CALL.strip() not in fields:
                        continue

                    called_name = get_sub_name(line)

                    if called_name in ['vsexp', 'vslog', 'vssqrt', 'vssin', 'vscos', 'vspownn', 'vspown1']:
                        continue

                    if called_name in ['vexp', 'vsqrt', 'vpown1', 'vlog', 'vspow1n', 'vsdiv']:
                        continue

                    if called_name in ['random_number', 'random_seed']:
                        continue

                    if called_name in ignore_nodes:
                        continue


                    if called_name.strip() == '':
                        line = next_line(lines, fixed_format=fixed)[1:]
                        called_name = get_sub_name(FORTRAN_CALL + ' ' + line)

                    child = get_node_by_name(called_name)
                    parentNode.add_child(child)


def get_sub_name(line, word=subroutine_word):
    if FORTRAN_CALL in line:
        fields = line.split(FORTRAN_CALL)
    else:
        fields = line.split(word)

    s = fields[1]
    if '(' in s:
        s = s.split('(')[0].strip()
    else:
        s = s.strip()

    if s.strip() == '':
        print(line)

    if '!' in s:
        s = s[:s.index('!')]
    return s


def write_gv_file(entry_name, depth=None):
    if entry_name in name_to_node:
        head = name_to_node[entry_name]
        """
        :type head: Node
        """
    else:
        print('No subroutine called {}'.format(entry_name))
        return

    # Crop the details after the given depth
    if depth is not None:
        head.crop_deeper_than(depth=depth)

    print(len(head.children))

    gvlines = head.get_gv_strings()
    print(len(head.children))
    gvlines.insert(0, 'size=\"20,20\";\n')
    gvlines.insert(0, 'digraph Gem_graph{\n')
    gvlines.append('}')

    with open('gem.gv', 'w') as f:
        f.writelines(gvlines)

    dot_guess_path = "/usr/local/bin/dot"
    if os.path.exists(dot_guess_path):
        subprocess.call([dot_guess_path, "-Tpdf", "gem.gv"],
                        stdout=open("{}.pdf".format(entry_name), "wb"))
    else:
        subprocess.Popen(["dot", "-Tpdf", "gem.gv", ">", "{}.pdf".format(entry_name)])


def create_relations(folders=None, depth=None, ignore_nodes=()):
    for folder in folders:
        for path in os.listdir(folder):

            if path.startswith('.'):  # skip hidden files
                continue

            # skip files of the following types
            if path.endswith('.cdk'):
                continue
            if path.endswith('.cdk90'):
                continue
            if path.endswith('.h'):
                continue
            if path.endswith('.c'):
                continue
            if '#' in path:
                continue  # skip files with weird names
            if '.' not in path:
                continue  # skip files without extension
            if path.endswith('~'):
                continue  # skip autosave files

            # take into account only fortran sources
            ext = path.split('.')[-1].strip()
            if ext.lower() not in ['ftn', 'ftn90', 'f', 'f90', 'incf']:
                continue

            file_path = os.path.join(folder, path)

            if os.path.isdir(file_path):  # do not treat folders
                continue

            parse_file(file_path, ignore_nodes=ignore_nodes)


def main():
    #    folders = [phy_folder, dyn_folder] #gem
    #    folders = ['../../hs_and_flake_integrated']
    # folders = ['/home/san/Fortran/oda', ]

    # NEMO
    # folders = ["/gs/project/ugh-612-aa/huziy/Coupling_CRCM_NEMO/NEMO/dev_v3_4_STABLE_2012/NEMOGCM/CONFIG/COUPLED/WORK",]
    # folders = ["nemo_src"]

    # Hostetler offline
    # folders = ["/home/san/Fortran/hostetler_offline"]


    # NEMO 1
    folders = ["/Users/san/Downloads/WORK"]
    nemo_ignore_nodes = ["abort", "timing_start", "timing_stop", "prt_ctl", "ctl_stop"]
    create_relations(folders, ignore_nodes=nemo_ignore_nodes)
    write_gv_file('stp', depth=1)

    showTreeUsingTkinter = False  # set true only if you have tkinter installed
    if showTreeUsingTkinter:
        from gui.test_tkinter import show_source_tree

        show_source_tree(get_node_by_name('readdyn'))


if __name__ == "__main__":
    main()
