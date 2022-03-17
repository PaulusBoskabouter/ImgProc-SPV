"""
# Author       : Paul Verhoeven
# Version      : 1.0
# Date         : 17-03-2022


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


class StartGUI(tk.Tk):
    def __init__(self, boolean_check: objects.BooleanCheck, resume_is_enabled: bool):
        """
        GUI at the start of the experiment, gives selection between start of new test with new subject.
        Or if possible continue an unfinished one.
        :param boolean_check: Object to write this data to
        """
        super().__init__()

        # Styling:
        header_font = {'font': ('Calibri', 32)}
        standard_font = {'font': ('Calibri', 18)}
        self.style = ttk.Style(self)
        self.style.theme_use('vista')
        self.style.configure('TButton', font=('Helvetica', 20))

        # Declare variables
        self.boolean_check = boolean_check

        # Config main window
        self.config(bg='#aaaaaa')
        self.title("Start")
        self.iconbitmap("resource/img/donderIcon.ico")
        self.geometry("600x250")
        self.resizable(False, False)

        # When window is close, force quit all code!
        self.protocol('WM_DELETE_WINDOW', quit)

        # If there's no unfinished experiment, the 'self.start_new' button should be disabled.
        if resume_is_enabled:
            continue_state = 'normal'
        else:
            continue_state = 'disabled'

        ####################
        # Init GUI widgets #
        ####################
        # Labels
        welcome_label = ttk.Label(self, text="Welcome!", **header_font, background='#aaaaaa')
        welcome_2_label = ttk.Label(self, text="Thanks you for participating in this test!",
                                    **standard_font, background='#aaaaaa', width=50)

        continue_label = ttk.Label(self, text="Do you want to start a new test? Or resume one?", **standard_font,
                                   background='#aaaaaa')

        # Buttons
        self.continue_button = ttk.Button(self, text="Continue", width=15, command=self.set_bool_resume,
                                          state=continue_state)
        self.start_new = ttk.Button(self, text="Start new test", width=15, command=self.set_bool_start_new)

        # Layout of widgets
        welcome_label.place(x=200, y=5)
        welcome_2_label.place(x=110, y=80)
        continue_label.place(x=60, y=110)
        self.continue_button.place(x=10, y=200)
        self.start_new.place(x=350, y=200)
        tk.mainloop()

    def set_bool_start_new(self):
        """
        Sets object.BooleanCheck to True which tells the code a new test will be run.
        """
        self.boolean_check.set_value(True)
        self.destroy()

    def set_bool_resume(self):
        """
        Sets object.BooleanCheck to False which tells the code to continue an unfinished test.
        """
        self.boolean_check.set_value(False)
        self.destroy()


class ResumeGUI(tk.Tk):
    def __init__(self, incomplete_subjects: dict, pass_on_index: objects.ContinuationIndex):
        """
        GUI at the start of the experiment, subject provides data, namealy: first/last name and age.
        :param incomplete_subjects: Object to write this data to
        """
        super().__init__()
        # Looks:
        self.style = ttk.Style(self)
        self.style.theme_use('vista')
        self.style.configure('TButton', font=('Helvetica', 20))
        self.style.configure('my.TCombobox', arrowsize=30)
        self.style.configure('my.TCombobox.Vertical.TScrollbar', arrowsize=28)

        # Declare variables
        self.subject_data_object = incomplete_subjects
        self.pass_on_index = pass_on_index
        self.names_variable = tk.StringVar(self)

        # Config main window
        self.config(bg='#aaaaaa')
        self.title("Resume old test")
        self.iconbitmap("resource/img/donderIcon.ico")
        self.geometry("300x200")
        self.resizable(False, False)

        # When window is close, force quit all code!
        self.protocol('WM_DELETE_WINDOW', quit)

        # Not the cleanest bit of code, but it works :-).
        # Parameter incomplete_subjects looks like this: {"0": <objects.Subject>} etc.
        # This temp dictionary takes the username from the object and links it to the correlating index as follows:
        # {"Firstname Lastname": index}
        # This way the Combobox values consists of subject names, and the selection can be linked to the actual object.
        self.temp_reverse_dict = {}
        for index, item in incomplete_subjects.items():
            self.temp_reverse_dict[item.get_full_name()] = index
        subject_names = list(self.temp_reverse_dict.keys())
        self.names_variable.set(subject_names[0])  # default value

        ####################
        # Init GUI widgets #
        ####################
        # Label
        explain_purpose_of_window = ttk.Label(self, text="Select user to resume:", background='#aaaaaa',
                                              font=('Calibri', 18))
        # Combobox
        self.w = ttk.Combobox(self, textvariable=self.names_variable, state='readonly', values=subject_names)
        # Button
        self.select_button = ttk.Button(self, text="Select", width=10, command=self.continue_user)

        # Layout of widgets
        explain_purpose_of_window.pack(fill=tk.X, padx=5, pady=5)
        self.w.pack(fill=tk.X, padx=5, pady=5)
        self.select_button.pack(fill=tk.X, padx=5, pady=5)
        self.tk.eval('set popdown [ttk::combobox::PopdownWindow %s]' % self.w)
        tk.mainloop()

    def continue_user(self):
        """
        Passes on the selected index in the objects.ContinuationIndex so the code knows which user to resume.
        """
        self.pass_on_index.set_index(self.temp_reverse_dict.get(self.names_variable.get()))
        self.destroy()


class NewUserGUI(tk.Tk):
    def __init__(self, subject_data: objects.Subject):
        """
        GUI at the start of new experiment, subject provides data, namely: first/last name and age.
        :param subject_data: object.Subjects to save entered data in.
        """

        super().__init__()

        # Styling
        paddings = {'padx': 25, 'pady': 5}
        entry_font = {'font': ('Calibri', 13)}
        label_font = {'font': ('Calibri', 18)}
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
        self.style = ttk.Style(self)
        self.style.theme_use('vista')
        self.style.configure('TButton', font=('Helvetica', 20))

        # Declare variables
        self.fname_value = tk.StringVar()
        self.lname_value = tk.StringVar()
        self.age_value = tk.StringVar()
        self.subject_data_object = subject_data

        # Config main window
        self.config(bg='#aaaaaa')
        self.title("Start")
        self.iconbitmap("resource/img/donderIcon.ico")
        self.geometry("300x500")
        self.resizable(False, False)

        # When window is close, force quit all code!
        self.protocol('WM_DELETE_WINDOW', quit)

        # Checks is applied ttk.Entry only contains numbers.
        vcmd = (self.register(callback))

        ####################
        # Init GUI widgets #
        ####################
        # Labels
        fname_label = ttk.Label(self, text="First name:", **label_font, background='#aaaaaa')
        lname_label = ttk.Label(self, text="Last name:", **label_font, background='#aaaaaa')
        age_label = ttk.Label(self, text="Age:", **label_font, background='#aaaaaa')

        # Entries
        self.fname_entry = ttk.Entry(self, textvariable=self.fname_value, **entry_font)
        self.lname_entry = ttk.Entry(self, textvariable=self.lname_value, **entry_font)
        self.age_entry = ttk.Entry(self, textvariable=self.age_value, **entry_font, validate='all',
                                   validatecommand=(vcmd, '%P'))

        # Button
        self.button = ttk.Button(self, text="Start", width=10, command=self.submit)

        # Widget grid layout
        fname_label.grid(column=0, row=0, sticky=tk.W, **paddings)
        lname_label.grid(column=0, row=2, sticky=tk.W, **paddings)
        age_label.grid(column=0, row=4, sticky=tk.W, **paddings)
        self.fname_entry.grid(column=0, row=1, sticky=tk.W, **paddings)
        self.lname_entry.grid(column=0, row=3, sticky=tk.W, **paddings)
        self.age_entry.grid(column=0, row=5, sticky=tk.W, **paddings)
        self.button.grid(column=0, row=6, sticky=tk.W, pady=40, padx=45)
        tk.mainloop()

    def submit(self):
        """
        When the submit button is pressed all data is checked and saved to objects.Subject object.
        """
        try:
            # Entries cannot be empty
            assert len(self.fname_value.get()) != 0
            assert len(self.lname_value.get()) != 0
            assert len(self.age_value.get()) != 0

            # Update objects.Subject object with entered entry string
            self.subject_data_object.set_fname(self.fname_value.get())
            self.subject_data_object.set_lname(self.lname_value.get())
            self.subject_data_object.set_age(self.age_value.get())
            self.destroy()
        except AssertionError:
            tkinter.messagebox.showerror(title="Warning!", message="Please fill in all fields.")


class E1(tk.Tk):
    def __init__(self, vid_id: str, vid_nr: int, subject_data: objects.Subject):
        """
        This GUI is for the 1st experiment (e1 for short :D). Answers to the questions are submitted to a Data object.
        :param vid_id: Exact video name, primarily used for parsing it to the data object.
        :param vid_nr: Relative video nummer (1-16) only used for the GUI's title bar.
        :param subject_data: objects.Subject object to save answers to
        """
        super().__init__()

        # Styling:
        paddings = {'padx': 25, 'pady': 5}
        entry_font = {'font': ('Calibri', 13)}
        label_font = {'font': ('Calibri', 18)}
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
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
        self.cars = tk.StringVar()
        self.people = tk.StringVar()
        self.subject_data = subject_data

        # Config main window
        self.config(bg='#727272')
        self.title(f"Questions video {vid_nr}")
        self.iconbitmap("resource/img/donderIcon.ico")
        self.geometry("850x600")
        self.resizable(False, False)

        # When window is close, force quit all code!
        self.protocol('WM_DELETE_WINDOW', quit)

        # Entry only takes in integers
        vcmd = (self.register(callback))

        ####################
        # Init GUI widgets #
        ####################

        # Labels
        cars_label = ttk.Label(self, text="How many cars are there?", **label_font, background='#727272')
        people_label = ttk.Label(self, text="How many people are there?", **label_font, background='#727272')
        feedback_label = ttk.Label(self, text="Do you have any extra comment\non video interpretability? (Optional)",
                                   **label_font, background='#727272')
        conf_cars_label = ttk.Label(self, text="On a 1-5 scale, how confident are you?\n(1=not sure, 5=very sure)",
                                    **label_font, background='#727272')
        conf_people_label = ttk.Label(self, text="On a 1-5 scale, how confident are you?",
                                      **label_font, background='#727272')
        feedback_scale_label = ttk.Label(self.feedback_scale_frame,
                                         text="On a 1-5 scale, how would you rate the \nvideo's interpretability",
                                         **label_font, background='#727272')

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

        # Feedback textfield
        self.text_scroll_combo = tk.Frame(background='#727272')
        self.feedback = tk.Text(self.text_scroll_combo, height=10, width=35, wrap='word')
        scrollb = ttk.Scrollbar(self.text_scroll_combo, command=self.feedback.yview)
        self.feedback['yscrollcommand'] = scrollb.set

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
        self.cars_box.grid(column=0, row=1, sticky=tk.W, **paddings)
        self.people_box.grid(column=0, row=3, sticky=tk.W, **paddings)
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
            # Entries cannot be empty
            cars = int(self.cars.get())
            people = int(self.people.get())

            self.subject_data.set_answers(video=self.vid_id, cars=cars, conf_cars=self.conf_cars.get(),
                                          people=people, conf_people=self.conf_people.get(),
                                          video_rating=self.feedback_rating.get(),
                                          comment=self.feedback.get("1.0", "end-1c"))
            self.destroy()
        except ValueError:
            tkinter.messagebox.showerror(title="Warning!", message="Please fill in all fields.")
