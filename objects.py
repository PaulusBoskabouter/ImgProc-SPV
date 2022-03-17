"""
# Author       : Paul Verhoeven
# Version      : 1.0
# Date         : 17-03-2022
In this script 3 different objects are written used by both main.py and prompt.py
"""


class Subject:
    def __init__(self, index, fname, lname, age, order, answers, actions):
        """
        In this object all results; test subject data, answers and events are stored and primarily used to communicate
        between scripts.
        """
        self.index = index
        self.fname = fname
        self.lname = lname
        self.age = age
        self.answers = answers
        self.actions = actions
        self.vidorder = order

    # Setters and getters, you get the gist, I'm not documenting all of them...
    def set_fname(self, first_name: str):
        self.fname = first_name

    def set_lname(self, last_name: str):
        self.lname = last_name

    def set_age(self, age: str):
        self.age = age

    def set_answers(self, video: str, cars: int, conf_cars: int, people: int, conf_people: int, video_rating: int,
                    comment: str):
        self.answers[video] = {'cars': cars, 'cars_conf': conf_cars, 'people': people, 'people_conf': conf_people,
                               'rating': video_rating, 'extra_comment': comment}

    def get_answers(self):
        return self.answers

    def get_vidorder(self):
        return self.vidorder

    def get_full_name(self):
        return f"{self.fname} {self.lname}"

    def get_data(self):
        return self.index, self.fname, self.lname, self.age, self.answers, self.actions

    def get_object_as_dict(self):
        return {'index': self.index, 'first_name': self.fname, 'last_name': self.lname, 'age': self.age,
                'answers': self.answers, 'actions': self.actions, 'order': self.vidorder}

    def update_actions(self, index: str, action_dict: dict):
        """
        This is used to add actions to the event dictionary
        :param index: Video name for example: stim16.mp4
        :param action_dict: Dictionary with
        """
        self.actions[index] = action_dict


class BooleanCheck:
    def __init__(self, value: bool):
        """
        Small object used to check if 'new user' or 'resume old user' has button has been pressed in prompt.StartGUI
        :param value: boolean
        """
        self.value = value

    # Getter and setter
    def set_value(self, value):
        self.value = value

    def get_value(self):
        return self.value


class ContinuationIndex:
    def __init__(self):
        """
        Small object used to check if 'new user' or 'resume old user' has button has been pressed in prompt.StartGUI
        """
        self.index = str

    # Getter and setter
    def set_index(self, index: str):
        self.index = index

    def get_index(self):
        return self.index
