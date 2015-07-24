# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="huziy"
__date__ ="$6 juil. 2011 23:08:00$"


from tkinter.constants import HORIZONTAL
from tkinter import Scrollbar
from tkinter import Frame
from tkinter import *
from tkinter.constants import VERTICAL
import tkinter.ttk

class App:

    def __init__(self, master):

        frame = Frame(master)
        frame.pack()

        self.button = Button(frame, text="QUIT", fg="red", command=frame.quit)
        self.button.pack(side=LEFT)

        self.hi_there = Button(frame, text="Hello", command=self.say_hi)
        self.hi_there.pack(side=LEFT)

    def say_hi(self):
        print("hi there, everyone!")



def main():
    root = Tk()


    frame = Frame(root)
    frame.pack()
    tree = tkinter.ttk.Treeview(frame)
    # Inserted at the root, program chooses id:
    tree.insert('', 'end', 'widgets', text='Widget Tour')

    # Same thing, but inserted as first child:
    tree.insert('', 0, 'gallery', text='Applications')
    tree.pack()
    print('Test')


#    app = App(root)
    root.mainloop()



def show_source_tree(head):
    root = Tk()
    frame = Frame(root)
    frame.pack(fill = 'both')
    tree = tkinter.ttk.Treeview(frame)
    
    #insert root subroutine
    # @type head Node
    parent_id = tree.insert('', 'end', '', text = head.name)
    for child in head.children:
        child.insert_to_tree(tree, parent_id)



    
    #add scrollbar
    v_scrollbar = Scrollbar(frame, orient = VERTICAL, command = tree.yview)
    h_scrollbar = Scrollbar(frame, orient = HORIZONTAL, command = tree.xview)
    tree.configure(yscrollcommand = v_scrollbar.set, xscrollcommand = h_scrollbar.set)
    
    v_scrollbar.pack(side = 'right', fill = 'y')
    h_scrollbar.pack(side = 'bottom', fill = 'x')


    tree.pack(fill = 'both')
    root.geometry("600x600")
    root.mainloop()




if __name__ == "__main__":
    main()
    print("Hello World")
