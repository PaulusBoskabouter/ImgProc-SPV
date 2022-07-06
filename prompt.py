"""
# Author       : Paul Verhoeven
# Date         : 25-03-2022


In this script all GUI's used are written
"""
import tkinter as tk
import tkinter.messagebox
from tkinter import ttk
import objects


def callback(entry_string):
    """
    Check if Entered string consists of numbers only
    :param entry_string: String of all characters entered in tk.Entry
    :return: Boolean weather
    """
    if str.isdigit(entry_string) or entry_string == "":
        return True
    else:
        return False


class NewUserGUI(tk.Tk):
    def __init__(self, subject_data: objects.Subject):
        """
        GUI at the start of new experiment, active_subject provides data, namely: first/last name and subject_id.
        :param subject_data: object.Subjects to save entered data in.
        """

        super().__init__()

        # Styling
        entry_font = {'font': ('Calibri', 13)}
        label_font = {'font': ('Calibri', 18)}
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
        self.style = ttk.Style(self)
        self.style.theme_use('vista')
        self.style.configure('TButton', font=('Helvetica', 20))

        # Declare variables
        self.test_subject_id = tk.StringVar()
        self.subject_data_object = subject_data

        # Config main window
        # Center window to screen
        width = 300
        frm_width = self.winfo_rootx() - self.winfo_x()
        win_width = width + 2 * frm_width
        height = 200
        titlebar_height = self.winfo_rooty() - self.winfo_y()
        win_height = height + titlebar_height + frm_width
        x = self.winfo_screenwidth() // 2 - win_width // 2
        y = self.winfo_screenheight() // 2 - win_height // 2
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        self.config(bg='#aaaaaa')
        self.title("Start")
        self.iconbitmap("resource/img/donderIcon.ico")
        self.resizable(False, False)

        # When window is close, force quit all code!
        self.protocol('WM_DELETE_WINDOW', quit)

        # Checks is applied ttk.Entry only contains numbers.
        vcmd = (self.register(callback))

        # Init GUI widgets
        # Labels
        age_label = ttk.Label(self, text="Enter subject id:", **label_font, background='#aaaaaa')

        # Entries
        self.id_entry = ttk.Entry(self, textvariable=self.test_subject_id, **entry_font, validate='all',
                                  validatecommand=(vcmd, '%P'))

        # Button
        self.button = ttk.Button(self, text="Start", width=10, command=self.submit)

        # Widget grid layout
        age_label.pack(fill=tk.X, padx=5, pady=5)
        self.id_entry.pack(fill=tk.X, padx=5, pady=5)
        self.button.pack(fill=tk.X, padx=5, pady=5)
        tk.mainloop()

    def submit(self):
        """
        When the submit button is pressed all data is checked and saved to objects.Subject object.
        """
        try:
            # Entries cannot be empty
            assert len(self.test_subject_id.get()) != 0

            # Update objects.Subject object with entered entry string
            self.subject_data_object.set_age(self.test_subject_id.get())
            self.destroy()
        except AssertionError:
            tkinter.messagebox.showerror(title="Warning!", message="Please fill in all fields.")


class StartExperiment(tk.Tk):
    def __init__(self, message: str, button_str: str, window_str: str):
        """
        Simple GUI with countdown timer to destroying itself.
        Used to make it visually clear to subjects that the test starts.
        """
        super().__init__()
        # Styling
        padding = 5
        self.style = ttk.Style(self)
        self.style.theme_use('vista')
        self.style.configure('TButton', font=('Helvetica', 20))

        # Config main window
        # Center window to screen
        width = 400
        frm_width = self.winfo_rootx() - self.winfo_x()
        win_width = width + 2 * frm_width
        height = 160
        titlebar_height = self.winfo_rooty() - self.winfo_y()
        win_height = height + titlebar_height + frm_width
        x = self.winfo_screenwidth() // 2 - win_width // 2
        y = self.winfo_screenheight() // 2 - win_height // 2
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        self.config(bg='#aaaaaa')
        self.title(window_str)
        self.iconbitmap("resource/img/donderIcon.ico")
        self.resizable(False, False)

        # When window is close, force quit all code!
        self.protocol('WM_DELETE_WINDOW', quit)

        # Init GUI widgets
        # Label
        self.purpose_of_window = ttk.Label(self, text=message,
                                           background='#aaaaaa', font=('Calibri', 18))

        # Button
        self.start_button = ttk.Button(self, text=button_str, width=10, command=self.start)

        # Layout of widgets

        self.purpose_of_window.pack(anchor='center', padx=padding, pady=padding)
        self.start_button.pack(fill=tk.X, padx=padding, pady=padding)
        tk.mainloop()

    def start(self):
        """
        Visualised countdown timer to start of test.
        """
        self.destroy()


class ExperimentForm(tk.Tk):
    def __init__(self, vid_id: str, title_bar: int, subject_data: objects.Subject):
        """
        This GUI is for the experiment. Answers to the questions are submitted to a Data object.
        :param vid_id: Exact video name, primarily used for parsing it to the data object.
        :param title_bar: Relative video nummer (1-16) only used for the GUI's title bar.
        :param subject_data: objects.Subject object to save answers to
        """
        super().__init__()

        # Styling:
        paddings = {'padx': 25, 'pady': 5}
        entry_font = {'font': ('Calibri', 13)}
        label_font = {'font': ('Calibri', 18)}
        radiobutton_font = {'font': ('Calibri', 20)}
        self.style = ttk.Style(self)
        self.style.theme_use('vista')
        self.style.configure('TButton', font=('Helvetica', 20))
        color_value = {
            "1": '#c90000',
            "2": '#ff8a00',
            "3": '#ffde00',
            "4": '#acde00',
            "5": '#00e255'
        }
        self.feedback_scale_frame = tk.Frame(background='#727272')

        # Declare variables
        self.vid_id = vid_id
        self.cars_conf_value = tk.IntVar()
        self.people_conf_value = tk.IntVar()
        self.feedback_rating = tk.IntVar()
        self.cars = tk.BooleanVar()
        self.people = tk.BooleanVar()
        self.subject_data = subject_data

        # Config main window
        # Center window to screen
        width = 925
        frm_width = self.winfo_rootx() - self.winfo_x()
        win_width = width + 2 * frm_width
        height = 600
        titlebar_height = self.winfo_rooty() - self.winfo_y()
        win_height = height + titlebar_height + frm_width
        x = self.winfo_screenwidth() // 2 - win_width // 2
        y = self.winfo_screenheight() // 2 - win_height // 2
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))

        self.config(bg='#727272')
        self.title(f"Questions video {title_bar}")
        self.iconbitmap("resource/img/donderIcon.ico")
        self.resizable(False, False)
        self.attributes("-topmost", True)

        # When window is close, force quit all code!
        self.protocol('WM_DELETE_WINDOW', quit)

        # Entry only takes in integers
        vcmd = (self.register(callback))

        # Init GUI widgets
        # Labels
        cars_label = ttk.Label(self, text="There is one or more car(s) in the video", **label_font,
                               background='#727272')
        people_label = ttk.Label(self, text="There is one or more human(s) in the video", **label_font,
                                 background='#727272')
        feedback_label = ttk.Label(self, text="Do you have any extra comment\non video interpretability? (Optional)",
                                   **label_font, background='#727272')
        conf_cars_label = ttk.Label(self, text="On a 1-5 scale, how confident are you?\n(1=not sure, 5=very sure)",
                                    **label_font, background='#727272')
        conf_people_label = ttk.Label(self, text="On a 1-5 scale, how confident are you?",
                                      **label_font, background='#727272')
        feedback_scale_label = ttk.Label(self.feedback_scale_frame,
                                         text="On a 1-5 scale, how would you rate the \nvideo's interpretability",
                                         **label_font, background='#727272')
        self.next_vid_countdown = ttk.Label(self, text="Test Starts in:", font=('Calibri', 32), background='#727272',
                                            foreground='#c90000')

        # Textbox
        self.cars_box = ttk.Entry(self, textvariable=self.cars, **entry_font, validate='all',
                                  validatecommand=(vcmd, '%P'))
        self.people_box = ttk.Entry(self, textvariable=self.people, **entry_font, validate='all',
                                    validatecommand=(vcmd, '%P'))

        # Scales
        self.conf_cars = tk.Scale(self, length="250px", variable=self.cars_conf_value, from_=1, to=5,
                                  orient=tk.HORIZONTAL,
                                  **entry_font,
                                  command=lambda val: self.conf_cars.configure(
                                      fg=color_value.get(val)),
                                  bg='#727272', fg="#c90000")

        self.conf_people = tk.Scale(self, length="250px", variable=self.people_conf_value, from_=1, to=5,
                                    orient=tk.HORIZONTAL,
                                    **entry_font,
                                    command=lambda val: self.conf_people.configure(
                                        fg=color_value.get(val)),
                                    bg='#727272', fg="#c90000")

        self.feedback_scale = tk.Scale(self.feedback_scale_frame, length="250px", variable=self.feedback_rating,
                                       from_=1, to=5,
                                       orient=tk.HORIZONTAL,
                                       **entry_font,
                                       command=lambda val: self.feedback_scale.configure(
                                           fg=color_value.get(val)),
                                       bg='#727272', fg="#c90000")

        # Frames
        self.text_scroll_combo = tk.Frame(background='#727272')
        self.cars_frame = tk.Frame(background='#727272')
        self.people_frame = tk.Frame(background='#727272')

        # Feedback textfield

        self.feedback = tk.Text(self.text_scroll_combo, height=10, width=35, wrap='word')
        scrollb = ttk.Scrollbar(self.text_scroll_combo, command=self.feedback.yview)
        self.feedback['yscrollcommand'] = scrollb.set

        # Radiobuttons
        self.cars_true_button = tk.Radiobutton(self.cars_frame, text="True", indicatoron=False, width=5, value=True,
                                               variable=self.cars, selectcolor='green', **radiobutton_font)
        self.cars_false_button = tk.Radiobutton(self.cars_frame, text="False", indicatoron=False, width=5, value=False,
                                                variable=self.cars, selectcolor='green', **radiobutton_font)

        self.people_true_button = tk.Radiobutton(self.people_frame, text="True", indicatoron=False, width=5, value=True,
                                                 variable=self.people, selectcolor='green', **radiobutton_font)
        self.people_false_button = tk.Radiobutton(self.people_frame, text="False", indicatoron=False, width=5,
                                                  variable=self.people, value=False, selectcolor='green',
                                                  **radiobutton_font)
        # Button
        self.button = ttk.Button(self, text="Submit", width=10, command=self.submit)

        # Grid layout
        cars_label.grid(column=0, row=0, sticky=tk.W, **paddings)
        people_label.grid(column=0, row=2, sticky=tk.W, **paddings)
        conf_cars_label.grid(column=1, row=0, sticky=tk.W, **paddings)
        conf_people_label.grid(column=1, row=2, sticky=tk.W, **paddings)
        feedback_label.grid(column=0, row=4, sticky=tk.W, **paddings)
        feedback_scale_label.grid(column=0, row=0, sticky=tk.W, **paddings)
        scrollb.grid(row=0, column=1, sticky="nsew")
        self.cars_frame.grid(column=0, row=1, sticky=tk.W, **paddings)
        self.cars_true_button.grid(column=0, row=1, sticky=tk.W, **paddings)
        self.cars_false_button.grid(column=1, row=1, sticky=tk.W, **paddings)
        self.people_frame.grid(column=0, row=3, sticky=tk.W, **paddings)
        self.people_true_button.grid(column=0, row=0, sticky=tk.W, **paddings)
        self.people_false_button.grid(column=1, row=0, sticky=tk.W, **paddings)
        self.conf_cars.grid(column=1, row=1, sticky=tk.W, **paddings)
        self.conf_people.grid(column=1, row=3, sticky=tk.W, **paddings)
        self.text_scroll_combo.grid(column=0, row=5, sticky=tk.W, **paddings)
        self.feedback.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.feedback_scale_frame.grid(row=5, column=1, sticky="nsew", padx=0, pady=0)
        self.feedback_scale.grid(column=0, row=1, sticky=tk.W, **paddings)
        self.button.grid(column=1, row=6, sticky=tk.W, pady=40, padx=45)
        tk.mainloop()

    def submit(self):
        """
        Submit entered data into Subject object
        """
        try:
            self.subject_data.set_answers(video=self.vid_id, cars=self.cars.get(), conf_cars=self.conf_cars.get(),
                                          people=self.people.get(), conf_people=self.conf_people.get(),
                                          video_rating=self.feedback_rating.get(),
                                          comment=self.feedback.get("1.0", "end-1c"))

            self.destroy()
        except ValueError:
            tkinter.messagebox.showerror(title="Warning!", message="Please fill in all fields.")
