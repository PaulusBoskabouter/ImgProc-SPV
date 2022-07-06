"""
# Author       : Paul Verhoeven
# Date         : 25-03-2022
In this script 3 different objects are written used by both main_pipeline.py and prompt.py
"""


class Subject:
    def __init__(self, subject_id, order, answers, actions):
        """
        In this object all results; test active_subject data, answers and events are stored and primarily used to
        communicate between scripts.
        """
        self.subject_id = subject_id
        self.answers = answers
        self.actions = actions
        self.vidorder = order

    # Setters and getters, you get the gist, I'm not documenting all of them...

    def set_age(self, age: str):
        self.subject_id = age

    def set_answers(self, video: str, cars: bool, conf_cars: int, people: bool, conf_people: int, video_rating: int,
                    comment: str):
        self.answers[video] = {'cars': cars, 'cars_conf': conf_cars, 'people': people, 'people_conf': conf_people,
                               'rating': video_rating, 'extra_comment': comment}

    def set_actions(self, actions: dict):
        self.actions = actions

    def set_order(self, order: list):
        self.vidorder = order

    def get_answers(self):
        return self.answers

    def get_subject_id(self):
        return self.subject_id

    def get_vidorder(self):
        return self.vidorder

    def get_data(self):
        return self.subject_id, self.answers, self.actions

    def get_object_as_dict(self):
        return {'subject_id': self.subject_id,
                'answers': self.answers, 'actions': self.actions, 'order': self.vidorder}

    def update_actions(self, index: str, action_dict: dict):
        """
        This is used to add actions to the event dictionary
        :param index: Video name for example: stim16.mp4
        :param action_dict: Dictionary with
        """
        self.actions[index] = action_dict



