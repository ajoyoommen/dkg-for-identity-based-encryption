from Tkinter import *
root=Tk()
root.title("my window")
root.geometry("500x500")
app=Frame(root)
app.grid()
label=Label(app,text="Which type of authentication do you want???")
label.grid()
check1=Checkbutton(app,text="LDAP authentication")
check1.grid()
check2=Checkbutton(app,text="Gmail authentication")
check2.grid()
button=Button(app,text="ok")
button.grid()
root.mainloop() 

