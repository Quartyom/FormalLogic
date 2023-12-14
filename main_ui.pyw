import tkinter as tk
import core

# Define a function to be called when the button is clicked
def calculate():
    # Get the text from the input area
    input_text = input_area.get("1.0", "end-1c")
    # Delete the existing text in the output area
    output_area.delete("1.0", "end")
    # Print the text in the output area

    output = core.solve_input(input_text)

    output_area.insert("end", output)


# Create the main window
window = tk.Tk()
window.iconbitmap("icon.ico")

# Set the window title
window.title("FAT transform")

# Create a label and input area
input_label = tk.Label(window, text="Input:")
output_label = tk.Label(window, text="Output:")
input_area = tk.Text(window, height=2, width=70)

# Create a button
calculate_button = tk.Button(window, text="Calculate", command=calculate)

# Create an output area
output_area = tk.Text(window, height=28, width=70)

# Grid the widgets in the window
input_label.grid(row=0, column=0, sticky="w")
input_area.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
calculate_button.grid(row=1, column=1, padx=10, pady=10, sticky="e")
output_label.grid(row=2, column=0, sticky="w")
output_area.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")


# Configure the grid columns and rows to resize with the window
window.columnconfigure(0, weight=1)
window.rowconfigure(1, weight=1)
window.rowconfigure(2, weight=1)
window.rowconfigure(3, weight=1)

# Start the event loop
window.mainloop()
