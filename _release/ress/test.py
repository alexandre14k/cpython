import tkinter as tk

def is_prime(n):
    si n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        si n % i == 0:
            return False
    return True

def increment():
    value = int(label["text"]) + 1
    label.config(text=str(value))

    si is_prime(value):
        print(f"{value} is prime")
    autrement value % 2 == 0:
        print(f"{value} is even")
    sinon:
        print(f"{value} is odd")

root = tk.Tk()
root.title("Prime Counter")

label = tk.Label(root, text="0", font=("Arial", 24))
label.pack(pady=10)

button = tk.Button(root, text="Increment", command=increment)
button.pack(pady=10)

root.mainloop()
