__author__="huziy"
__date__ ="$5 juil. 2011 14:05:27$"



import os

phy_folder = '../../PHY'
dyn_folder = '../../DYN'

subroutine = 'subroutine'
end = 'end'
end_subroutine = end + subroutine

call = 'call '



class Node():
    def __init__(self, name = ''):
        self.name = name
        self.children = []

    def get_gv_strings(self):
        lines = []
        for c in self.children:
            for line in c.get_gv_strings():
                if line not in lines:
                    lines.append(line)
            line = '%s -> %s; \n' % (self.name, c.name)
            if line not in lines:
                lines.append(line)
        return lines


#to get node object by name
name_to_node = {}

#get node object by name, create new if does not yet exists
def get_node_by_name(name = ''):
    if name in name_to_node:
        return name_to_node[name]
    else:
        node = Node(name = name)
        name_to_node[name] = node
        return node


def is_fixed_form_splited(lines):
    if len(lines) == 0: #if there is no following line
        return False

    follow_line = lines[0]
    if follow_line[0:5] == '     ' and follow_line[5] != ' ':
        return True

    return False


def next_line(lines, fixed_format = False):
    line = lines.pop(0)

    #treat comments in fixed format file
    if fixed_format:
        if line[0] != ' ' and line[0:8] != '#include':
            return ''

    line = line.lower()

    if line.strip().startswith('!'): #skip comments
        return ''
    
    line = line.strip()

    #connect splitted lines
    if not fixed_format:
        line1 = line
        while line1.endswith('&'):
            line = lines.pop(0)
            line1 = line[:-1] + line
        line = line1.strip()


    if fixed_format:
        #TODO: do line connecting for the fixed format
        line1 = line
        while is_fixed_form_splited(lines):
            line = lines.pop(0).strip()
            line1 += line.strip()[1:]
        line = line1.strip()
        pass


    return line


#parse file to Nodes
def parse_file(path):
    #print(path)
    f = open(path)
    lines = f.readlines()
  

    path_lower = path.lower()
    fixed = path_lower.endswith('.ftn') or path_lower.endswith('.f')
    while len(lines) > 0:
        line = next_line(lines, fixed_format = fixed)


        if line.startswith(subroutine):
            sub_name = get_sub_name(line)
            parentNode = get_node_by_name(sub_name)


            line = next_line(lines, fixed_format = fixed)
            line_without_spaces = line.replace(' ', '')
            while end_subroutine not in line_without_spaces:
                line = next_line(lines, fixed_format = fixed)
                line_without_spaces = line.replace(' ', '')


                #end of the subroutine or function
                if line_without_spaces == end:
                    break

                #parse children nodes
                if call in line:
                    called_name = get_sub_name(line)

                    if called_name in ['vsexp', 'vslog', 'vssqrt', 'vssin', 'vscos', 'vspownn', 'vspown1']:
                        continue

                    if called_name in ['vexp', 'vsqrt', 'vpown1', 'vlog', 'vspow1n', 'vsdiv']:
                        continue

                    if called_name in ['random_number', 'random_seed']:
                        continue


                    if called_name.strip() == '':
                        line = next_line(lines, fixed_format = fixed)[1:]
                        called_name = get_sub_name(call + ' ' + line)

                    child = get_node_by_name(called_name)
                    if not child in parentNode.children:
                        parentNode.children.append(child)
    f.close()




def get_sub_name(line):

    if call in line:
        fields = line.split(call)
    else:
        fields = line.split(subroutine)


    s = fields[1]
    if '(' in s:
        s = s.split('(')[0].strip()
    else:
        s = s.strip()


    if s.strip() == '': print(line)
    if '!' in s:
        s = s[0:s.index('!')]
    return s



def write_gv_file(entry_name):

    if name_to_node.has_key(entry_name):
        head = name_to_node[entry_name]
    else:
        print('No subroutine called %s' % entry_name)
        return

 
    gvlines = head.get_gv_strings()
    print len(head.children)
    gvlines.insert(0, 'size=\"100,100\";\n')
    gvlines.insert(0,'digraph Gem_graph{\n')
    gvlines.append('}')

    f = open('gem.gv', 'w')
    f.writelines(gvlines)
    f.close()

    os.system('/usr/local/bin/dot -Tpdf gem.gv > %s.pdf' % entry_name)
#    os.system('/usr/local/bin/circo -Tpng gem.gv > %s.png' % entry_name)


def create_relations(folders = []):
    for folder in folders:
        for path in os.listdir(folder):

            if path.startswith('.'): #skip hidden files
                continue

            #skip files of the following types
            if path.endswith('.cdk'): continue
            if path.endswith('.cdk90'): continue
            if path.endswith('.h'): continue
            if path.endswith('.c'): continue
            if '#' in path: continue     #skip files with weird names
            if '.' not in path: continue #skip files without extension
            if path.endswith('~'): continue #skip autosave files

            #take into account only fortran sources
            ext = path.split('.')[-1].strip()
            if ext not in ['ftn', 'ftn90', 'f', 'f90', 'incf']: continue


            file_path = os.path.join(folder, path)

            if os.path.isdir(file_path): #do not treat folders
                continue

            parse_file(file_path)




def main():
    folders = [phy_folder, dyn_folder] #gem
#    folders = ['../../hs_and_flake_integrated']
    create_relations(folders)
    write_gv_file('dynstep')




if __name__ == "__main__":
    main()
