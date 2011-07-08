# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="huziy"
__date__ ="$6 juil. 2011 23:08:00$"


from Tkinter import *
import ttk

class App:

    def __init__(self, master):

        frame = Frame(master)
        frame.pack()

        self.button = Button(frame, text="QUIT", fg="red", command=frame.quit)
        self.button.pack(side=LEFT)

        self.hi_there = Button(frame, text="Hello", command=self.say_hi)
        self.hi_there.pack(side=LEFT)

    def say_hi(self):
        print "hi there, everyone!"



def main():
    root = Tk()


    frame = Frame(root)
    frame.pack()
    tree = ttk.Treeview(frame)
    # Inserted at the root, program chooses id:
    tree.insert('', 'end', 'widgets', text='Widget Tour')

    # Same thing, but inserted as first child:
    tree.insert('', 0, 'gallery', text='Applications')
    tree.pack()
    print('Test')


#    app = App(root)
    root.mainloop()




if __name__ == "__main__":
    main()
    print "Hello World"
