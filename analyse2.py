"""
# Author       : Paul Verhoeven
# Date         : 15-06-2022
This script was used for all analysis.
"""

import json
import pandas
import scipy.stats
from matplotlib.lines import Line2D
import objects
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from scipy.stats import pearsonr


def load_test_subjects(base_loc: str = ".\\results\\",
                       filename: str = "adaptive_ExperimentOneAdaptiveSubjectData.json"):
    """
    Loads the patient dictionary from .\\results\\ExperimentOneSubjectData.json.
    :param filename: As variable name implies, exact filename
    :param base_loc: Base diractory or path_to_file
    :return: Returns dictionary, example: {0: first name-last name-subject_id}
    """
    dictionary = {}
    try:
        with open(base_loc + filename, 'r') as file:
            dictionary = json.load(file)
            file.close()
    except json.decoder.JSONDecodeError:
        pass
    except FileNotFoundError:
        print(f"Error: check the existence of {base_loc + filename}")
        quit()

    list_of_subject_objects = {}
    for data in dictionary.items():
        subject_index = data[0]
        info = data[1]
        if len(info['answers']) == 16:
            list_of_subject_objects[subject_index] = objects.Subject(
                subject_id=info['subject_id'],
                order=info['order'],
                answers=info['answers'],
                actions=info['actions']
            )

        # If the number of answers are unqual to the amount of videos, active_subject is unfinished
    return list_of_subject_objects


def load_json(base_loc: str, filename: str):
    """
    Loads the number of phosphenes dictionary from .\\results\\phosphene_data.json
    :param filename: As variable name implies, exact filename
    :param base_loc: base diractory or path_to_file
    :return: Returns dictionary, example: {0: first name-last name-subject_id}
    """
    try:
        with open(base_loc + filename, 'r') as file:
            dictionary = json.load(file)
            file.close()
    except json.decoder.JSONDecodeError:
        print("Error: File is not in JSON format")
        quit()
    except FileNotFoundError:
        print(f"Error: check the existence of {base_loc + filename}")
        quit()
    return dictionary


def get_answers_df():
    """
    Convert json data to one big pandas dataframe
    :return: pandas dataframe
    """
    subject_id = []
    trials = []
    video_name = []
    mode = []
    correct_cars = []
    conf_cars = []
    correct_people = []
    conf_people = []
    vid_rating = []
    bar_plot_color_ppl = []
    bar_plot_color_cars = []

    correctness_numeric = {True: 1, False: 0}
    correctness_color = {True: '#0099d6', False: '#ff2f2f'}

    for subjects in [f_subjects, a_subjects]:
        for sub_id, subject in subjects.items():
            trial = 0
            subject_data = subject.get_object_as_dict()
            for vid_name, answer_data in subject_data.get('answers').items():
                if subjects == a_subjects:
                    mode_type = "Adaptive CED"
                else:
                    if subject_data.get('actions').get(vid_name).get('pre-start').get('DVS'):
                        mode_type = "DVS"
                    else:
                        mode_type = "Fixed CED"

                vid_name = vid_name.split("\\")[-1]
                trial += 1
                subject_id.append(sub_id)
                video_name.append(vid_name)
                trials.append(trial)
                correct_cars.append(
                    correctness_numeric.get(answer_data.get('cars') == ANSWERS.get(vid_name).get('cars')))
                bar_plot_color_cars.append(
                    correctness_color.get(answer_data.get('cars') == ANSWERS.get(vid_name).get('cars')))
                correct_people.append(
                    correctness_numeric.get(answer_data.get('people') == ANSWERS.get(vid_name).get('people'))
                )
                bar_plot_color_ppl.append(
                    correctness_color.get(answer_data.get('people') == ANSWERS.get(vid_name).get('people')))
                conf_cars.append(answer_data.get('cars_conf'))
                conf_people.append(answer_data.get('people_conf'))
                vid_rating.append(answer_data.get('rating'))
                mode.append(mode_type)

    dataframe = pd.DataFrame(
        data=dict(subject=subject_id, mode=mode, video=video_name, trial=trials, cars=correct_cars,
                  confidence_cars=conf_cars, people=correct_people, confidence_people=conf_people,
                  video_rating=vid_rating, car_col=bar_plot_color_cars, people_col=bar_plot_color_ppl)
    )

    return dataframe


def learning_curve(mode: str):
    """
    Preform r-pearson test
    :param mode: mode name, further defined under main
    """
    y_axis = {'cars_y': [],
              'people_y': []}

    for trial in range(1, 17):
        target_rows = subject_answers_df.loc[
            (subject_answers_df['mode'] == mode) & (subject_answers_df['trial'] == trial)]

        temp_cars = []
        temp_people = []
        for row_index, row in target_rows.iterrows():
            if row['confidence_cars'] > CUTOFF:
                temp_cars.append(row['cars'])
            if row['confidence_people'] > CUTOFF:
                temp_people.append(row['people'])

        y_axis['cars_y'].append(np.average(temp_cars) * 100)
        y_axis['people_y'].append(np.average(temp_people) * 100)

    x_axis = [x + 1 for x in range(16)]

    plt.figure(figsize=(14, 8))
    plt.ylim(0, 100)
    plt.plot(x_axis, y_axis['cars_y'], label='Cars', color="BLACK", alpha=1)
    plt.plot(x_axis, y_axis['people_y'], label='People', color="BLUE", alpha=1)
    plt.xticks(np.arange(1, max(x_axis) + 1, 1), fontsize=24)
    plt.yticks(fontsize=24)
    plt.xlabel('Trial number', fontweight='bold', fontsize=24)
    plt.ylabel('Average accuracy (in %)', fontweight='bold', fontsize=24)
    plt.legend(loc="upper right", fontsize=18)
    x_axis = [x for x in range(16)]
    car_corr, pval_c = pearsonr(x_axis, y_axis['cars_y'])
    people_corr, pval_p = pearsonr(x_axis, y_axis['people_y'])
    plt.title(f'With confidence cut-off of: {CUTOFF}', fontsize=16)
    plt.suptitle(f'Average accuracy over time in {mode}', fontsize=20, y=0.95)

    print(f"Learning curve correlation cars for {mode}: {car_corr}\n"
          f"With p-value of: {pval_c}\n"
          f"Learning curve correlation people for {mode}: {people_corr}\n"
          f"With p-value of: {pval_p}\n")
    plt.show()



def test_normality():
    """
    Test for normality for each study condition, each object (cars & people)
    """
    for mode in MODES:
        avg_cars = car_accuracy.loc[(car_accuracy['mode'] == mode)]['accuracy'].to_list()
        avg_people = people_accuracy.loc[(people_accuracy['mode'] == mode)]['accuracy'].to_list()
        print(mode)
        print('Accuracy:')
        print(f'\tCars:\t{scipy.stats.shapiro(avg_cars)}')
        print(f'\tPeople:\t{scipy.stats.shapiro(avg_people)}')

        avg_cars = car_confidence.loc[(car_confidence['mode'] == mode)]['confidence'].to_list()
        avg_people = people_confidence.loc[(people_confidence['mode'] == mode)]['confidence'].to_list()
        print('Confidence:')
        print(f'\tCars:\t{scipy.stats.shapiro(avg_cars)}')
        print(f'\tPeople:\t{scipy.stats.shapiro(avg_people)}')
        print()


def get_average_sub_accuracy():
    """
    Convert individual's answers to correct
    :return: 4 pandas dataframes
    """
    c_accuracy = []
    car_mode = []
    car_conf = []

    p_accuracy = []
    people_mode = []
    people_conf = []

    for mode in MODES:
        if mode == 'Fixed CED' or mode == 'DVS':
            loop_range = range(10, 30)
        else:
            loop_range = range(10)
        for subject in loop_range:
            target_rows = subject_answers_df.loc[
                (subject_answers_df['mode'] == mode) & (subject_answers_df['subject'] == f'{subject}')]
            if len(target_rows) != 0:
                c_accuracy.append(np.average(target_rows['cars'].tolist()))
                p_accuracy.append(np.average(target_rows['people'].tolist()))

                car_conf.append(np.average(target_rows['confidence_cars'].tolist()))
                people_conf.append(np.average(target_rows['confidence_people'].tolist()))

                car_mode.append(mode)
                people_mode.append(mode)

    df_cars_acc = pandas.DataFrame(dict(mode=car_mode, accuracy=c_accuracy))
    df_car_conf = pandas.DataFrame(dict(mode=people_mode, confidence=car_conf))

    df_people_acc = pandas.DataFrame(dict(mode=people_mode, accuracy=p_accuracy))
    df_people_conf = pandas.DataFrame(dict(mode=people_mode, confidence=people_conf))

    return df_cars_acc, df_car_conf, df_people_acc, df_people_conf


def individual_scoring(subject_id: str):
    """
    Create plot combining all individual's performance metrics. Graph is self-explanatory
    :param subject_id: id of subject, must range within 0-29
    """
    target_rows = subject_answers_df.loc[(subject_answers_df['subject'] == subject_id)]

    # set width of bar
    bar_width = 0.25
    plt.rcParams["figure.figsize"] = [7.50, 3.50]
    plt.rcParams["figure.autolayout"] = True

    font = {'weight': 'bold',
            'size': 9}

    plt.rc('font', **font)
    fig, ax = plt.subplots(figsize=(16, 8))
    numeric_x_axis = np.arange(len(target_rows['video']))

    def autolabel(rects, label):
        for idx, rect in enumerate(rects):
            ax.text(x=rect.get_x() + 0.05, y=0.2, s=label, fontdict={'weight': 'bold', 'size': 9},
                    multialignment='center'
                    )

    car_bar = ax.bar(numeric_x_axis + 0.15, target_rows['confidence_cars'], color=target_rows['car_col'],
                     width=bar_width,
                     tick_label='cars')
    people_bar = ax.bar(numeric_x_axis - 0.15, target_rows['confidence_people'],
                        color=target_rows['people_col'],
                        width=bar_width,
                        tick_label='people')
    autolabel(car_bar, 'C')
    autolabel(people_bar, 'P')
    ax.plot(numeric_x_axis, target_rows['video_rating'], color='black', label='video rating')
    ax.scatter(numeric_x_axis, target_rows['video_rating'], s=100, color='black')

    # Make the plot
    plt.xlabel('Video name', fontweight='bold', fontsize=15)
    plt.ylabel('Confidence rating', fontweight='bold', fontsize=15)
    plt.xticks(numeric_x_axis, target_rows['video'])  # Replace numerics with video names.
    plt.title(f"Confidence and accuracy in detecting cars & people for subject {subject_id}")

    #  Legend stuff
    blue_patch = mpatches.Patch(color='#0099d6', label='Correct')
    red_patch = mpatches.Patch(color='#ff2f2f', label='Incorrect')
    line = Line2D([0], [0], color='black', label="Video score")
    p = mpatches.Circle((0, 0), radius=0, facecolor='None', label='P = People')
    c = mpatches.Circle((0, 0), radius=0, facecolor='None', label='C = Cars')
    plt.legend(handles=[blue_patch, red_patch, line, p, c], loc='upper right')
    plt.savefig(f".\\results\\plots\\individual\\{subject_id}_bar.png")
    plt.show()


def fixed_adaptive_comparison():
    """
    Plots graphs for comparison of people-cars accuracy-confidence between fixed CED and adaptive CED.
    And preform corresponding statistical tests.
    """
    avg_cars_adaptive = car_accuracy.loc[(car_accuracy['mode'] == 'Adaptive CED')]['accuracy'].to_list()
    avg_cars_fixed = car_accuracy.loc[(car_accuracy['mode'] == 'Fixed CED')]['accuracy'].to_list()

    target_rows = car_accuracy.loc[car_accuracy['mode'].isin(['Adaptive CED', 'Fixed CED'])]
    plt.ylim(0, 102)
    sns.boxplot(x=target_rows['mode'], y=target_rows['accuracy'] * 100, data=target_rows, whis=np.inf,
                palette=box_colors)

    sns.swarmplot(x=target_rows['mode'], y=target_rows['accuracy'] * 100, data=target_rows, color="white",
                  edgecolor="black", linewidth=.5)
    plt.title(f'Fixed CED and Adaptive CED', fontsize=12)
    plt.suptitle(f'Percentage correct for identifying cars', fontsize=16, y=0.98)
    plt.show()
    car_null_hypothesis = scipy.stats.ttest_ind(avg_cars_adaptive, avg_cars_fixed)

    avg_people_adaptive = people_accuracy.loc[(people_accuracy['mode'] == 'Adaptive CED')]['accuracy'].to_list()
    avg_people_fixed = people_accuracy.loc[(people_accuracy['mode'] == 'Fixed CED')]['accuracy'].to_list()

    target_rows = people_accuracy.loc[people_accuracy['mode'].isin(['Adaptive CED', 'Fixed CED'])]
    plt.ylim(0, 102)
    sns.boxplot(x=target_rows['mode'], y=target_rows['accuracy'] * 100, data=target_rows, whis=np.inf,
                palette=box_colors)

    sns.swarmplot(x=target_rows['mode'], y=target_rows['accuracy'] * 100, data=target_rows, color="white",
                  edgecolor="black", linewidth=.5)
    plt.title(f'Fixed CED and Adaptive CED', fontsize=12)
    plt.suptitle(f'Percentage correct for identifying people', fontsize=16, y=0.98)
    plt.show()

    people_null_hypothesis = scipy.stats.ttest_ind(avg_people_adaptive, avg_people_fixed)
    print('ACCURACY')
    print("AUTOS")
    print(f'Gemiddelde voor accuracy in a-CED: {np.average(avg_cars_adaptive)}')
    print(f'Std voor accuracy in a-CED: {np.std(avg_cars_adaptive)}')

    print(f'Gemiddelde voor accuracy in f-CED: {np.average(avg_cars_fixed)}')
    print(f'Std voor accuracy in f-CED: {np.std(avg_cars_fixed)}')

    print(car_null_hypothesis)
    print('\nMENSEN')
    print(f'Gemiddelde voor accuracy in a-CED: {np.average(avg_people_adaptive)}')
    print(f'Std voor accuracy in a-CED: {np.std(avg_people_adaptive)}')

    print(f'Gemiddelde voor accuracy in f-CED: {np.average(avg_people_fixed)}')
    print(f'Std voor accuracy in f-CED: {np.std(avg_people_fixed)}')
    print(people_null_hypothesis)
    print()

    avg_cars_adaptive = car_confidence.loc[(car_accuracy['mode'] == 'Adaptive CED')]['confidence'].to_list()
    avg_cars_fixed = car_confidence.loc[(car_accuracy['mode'] == 'Fixed CED')]['confidence'].to_list()

    target_rows = car_confidence.loc[car_confidence['mode'].isin(['Adaptive CED', 'Fixed CED'])]
    plt.ylim(1, 5)
    sns.boxplot(x=target_rows['mode'], y=target_rows['confidence'], data=target_rows, whis=np.inf, palette=box_colors)

    sns.swarmplot(x=target_rows['mode'], y=target_rows['confidence'], data=target_rows, color="white",
                  edgecolor="black", linewidth=.5)
    plt.title(f'Fixed CED and Adaptive CED', fontsize=12)
    plt.suptitle(f'Confidence in identifying cars', fontsize=16, y=0.98)
    plt.show()

    car_null_hypothesis = scipy.stats.ttest_ind(avg_cars_adaptive, avg_cars_fixed)

    avg_people_adaptive = people_confidence.loc[(people_confidence['mode'] == 'Adaptive CED')]['confidence'].to_list()
    avg_people_fixed = people_confidence.loc[(people_confidence['mode'] == 'Fixed CED')]['confidence'].to_list()

    target_rows = people_confidence.loc[people_confidence['mode'].isin(['Adaptive CED', 'Fixed CED'])]
    plt.ylim(1, 5)
    sns.boxplot(x=target_rows['mode'], y=target_rows['confidence'], data=target_rows, whis=np.inf, palette=box_colors)

    sns.swarmplot(x=target_rows['mode'], y=target_rows['confidence'], data=target_rows, color="white",
                  edgecolor="black", linewidth=.5)
    plt.title(f'Fixed CED and Adaptive CED', fontsize=12)
    plt.suptitle(f'Confidence in identifying people', fontsize=16, y=0.98)
    plt.show()

    people_null_hypothesis = scipy.stats.ttest_ind(avg_people_adaptive, avg_people_fixed)
    print("CONFIDENCE")
    print("AUTOS")
    print(f'Gemiddelde voor accuracy in a-CED: {np.average(avg_cars_adaptive)}')
    print(f'Std voor accuracy in a-CED: {np.std(avg_cars_adaptive)}')

    print(f'Gemiddelde voor accuracy in f-CED: {np.average(avg_cars_fixed)}')
    print(f'Std voor accuracy in f-CED: {np.std(avg_cars_fixed)}')

    print(car_null_hypothesis)
    print('\nMENSEN')
    print(f'Gemiddelde voor accuracy in a-CED: {np.average(avg_people_adaptive)}')
    print(f'Std voor accuracy in a-CED: {np.std(avg_people_adaptive)}')

    print(f'Gemiddelde voor accuracy in f-CED: {np.average(avg_people_fixed)}')
    print(f'Std voor accuracy in f-CED: {np.std(avg_people_fixed)}')
    print(people_null_hypothesis)


def fixed_dvs_comparison():
    """
    Plots graphs for comparison of people-cars accuracy-confidence between fixed CED and DVS.
    And preform corresponding statistical tests.
    """
    avg_cars_dvs = car_accuracy.loc[(car_accuracy['mode'] == 'DVS')]['accuracy'].to_list()
    avg_cars_fixed = car_accuracy.loc[(car_accuracy['mode'] == 'Fixed CED')]['accuracy'].to_list()

    target_rows = car_accuracy.loc[car_accuracy['mode'].isin(['DVS', 'Fixed CED'])]
    plt.ylim(0, 102)
    sns.boxplot(x=target_rows['mode'], y=target_rows['accuracy'] * 100, data=target_rows, whis=np.inf,
                palette=box_colors)

    sns.swarmplot(x=target_rows['mode'], y=target_rows['accuracy'] * 100, data=target_rows, color="white",
                  edgecolor="black", linewidth=.5)
    plt.title(f'Fixed CED and DVS', fontsize=12)
    plt.suptitle(f'Percentage correct for identifying cars', fontsize=16, y=0.98)
    plt.show()

    car_null_hypothesis = scipy.stats.ttest_rel(avg_cars_dvs, avg_cars_fixed, alternative='two-sided')

    avg_people_dvs = people_accuracy.loc[(people_accuracy['mode'] == 'DVS')]['accuracy'].to_list()
    avg_people_fixed = people_accuracy.loc[(people_accuracy['mode'] == 'Fixed CED')]['accuracy'].to_list()

    people_null_hypothesis = scipy.stats.wilcoxon(x=avg_people_dvs, y=avg_people_fixed)

    target_rows = people_accuracy.loc[people_accuracy['mode'].isin(['DVS', 'Fixed CED'])]
    plt.ylim(0, 102)
    sns.boxplot(x=target_rows['mode'], y=target_rows['accuracy'] * 100, data=target_rows, whis=np.inf,
                palette=box_colors)

    sns.swarmplot(x=target_rows['mode'], y=target_rows['accuracy'] * 100, data=target_rows, color="white",
                  edgecolor="black", linewidth=.5)
    plt.title(f'Fixed CED and DVS', fontsize=12)
    plt.suptitle(f'Percentage correct for identifying People', fontsize=16, y=0.98)
    plt.show()
    print('ACCURACY')
    print("AUTOS")
    print(f'Gemiddelde voor accuracy in DVS: {np.average(avg_cars_dvs)}')
    print(f'Std voor accuracy in DVS: {np.std(avg_cars_dvs)}')

    print(f'Gemiddelde voor accuracy in f-CED: {np.average(avg_cars_fixed)}')
    print(f'Std voor accuracy in f-CED: {np.std(avg_cars_fixed)}')

    print(car_null_hypothesis)
    print('\nMENSEN')
    print(f'Gemiddelde voor accuracy in dvs: {np.average(avg_people_dvs)}')
    print(f'Std voor accuracy in dvs: {np.std(avg_people_dvs)}')

    print(f'Gemiddelde voor accuracy in f-CED: {np.average(avg_people_fixed)}')
    print(f'Std voor accuracy in f-CED: {np.std(avg_people_fixed)}')
    print(people_null_hypothesis)
    print()

    avg_cars_dvs = car_confidence.loc[(car_confidence['mode'] == 'DVS')]['confidence'].to_list()
    avg_cars_fixed = car_confidence.loc[(car_confidence['mode'] == 'Fixed CED')]['confidence'].to_list()

    target_rows = car_confidence.loc[car_confidence['mode'].isin(['DVS', 'Fixed CED'])]
    plt.ylim(1, 5)
    sns.boxplot(x=target_rows['mode'], y=target_rows['confidence'], data=target_rows, whis=np.inf,
                palette=box_colors)

    sns.swarmplot(x=target_rows['mode'], y=target_rows['confidence'], data=target_rows, color="white",
                  edgecolor="black", linewidth=.5)
    plt.title(f'Fixed CED and DVS', fontsize=12)
    plt.suptitle(f'Confidence in identifying cars', fontsize=16, y=0.98)
    plt.show()

    car_null_hypothesis = scipy.stats.ttest_rel(avg_cars_dvs, avg_cars_fixed, alternative='two-sided')

    avg_people_dvs = people_confidence.loc[(people_confidence['mode'] == 'DVS')]['confidence'].to_list()
    avg_people_fixed = people_confidence.loc[(people_confidence['mode'] == 'Fixed CED')]['confidence'].to_list()

    people_null_hypothesis = scipy.stats.wilcoxon(x=avg_people_dvs, y=avg_people_fixed)

    target_rows = people_confidence.loc[people_confidence['mode'].isin(['DVS', 'Fixed CED'])]
    plt.ylim(1, 5)
    sns.boxplot(x=target_rows['mode'], y=target_rows['confidence'], data=target_rows, whis=np.inf,
                palette=box_colors)

    sns.swarmplot(x=target_rows['mode'], y=target_rows['confidence'], data=target_rows, color="white",
                  edgecolor="black", linewidth=.5)
    plt.title(f'Fixed CED and DVS', fontsize=12)
    plt.suptitle(f'Confidence in identifying people', fontsize=16, y=0.98)
    plt.show()

    print("CONFIDENCE")
    print("AUTOS")
    print(f'Gemiddelde voor accuracy in dvs: {np.average(avg_cars_dvs)}')
    print(f'Std voor accuracy in dvs: {np.std(avg_cars_dvs)}')

    print(f'Gemiddelde voor accuracy in f-CED: {np.average(avg_cars_fixed)}')
    print(f'Std voor accuracy in f-CED: {np.std(avg_cars_fixed)}')

    print(car_null_hypothesis)
    print('\nMENSEN')
    print(f'Gemiddelde voor accuracy in dvs: {np.average(avg_people_dvs)}')
    print(f'Std voor accuracy in dvs: {np.std(avg_people_dvs)}')

    print(f'Gemiddelde voor accuracy in f-CED: {np.average(avg_people_fixed)}')
    print(f'Std voor accuracy in f-CED: {np.std(avg_people_fixed)}')
    print(people_null_hypothesis)


if __name__ == '__main__':
    ANSWERS = {"stim1.mp4": {'cars': True, 'people': False},
               "stim2.mp4": {'cars': False, 'people': False},
               "stim3.mp4": {'cars': False, 'people': False},
               "stim4.mp4": {'cars': False, 'people': True},
               "stim5.mp4": {'cars': True, 'people': True},
               "stim6.mp4": {'cars': False, 'people': True},
               "stim7.mp4": {'cars': False, 'people': True},
               "stim8.mp4": {'cars': True, 'people': True},
               "stim9.mp4": {'cars': True, 'people': False},
               "stim10.mp4": {'cars': True, 'people': False},
               "stim11.mp4": {'cars': True, 'people': True},
               "stim12.mp4": {'cars': True, 'people': True},
               "stim13.mp4": {'cars': True, 'people': True},
               "stim14.mp4": {'cars': True, 'people': True},
               "stim15.mp4": {'cars': True, 'people': True},
               "stim16.mp4": {'cars': True, 'people': True}
               }

    # Multiple subject analysis parameters
    CUTOFF = 0  # Confidence ratings equal to / smaller than this number will not be taken into consideration.
    sns.set(style="darkgrid")
    box_colors = {"Fixed CED": "b", "Adaptive CED": "darkorange", "DVS": "darkgreen"}

    # Load all subject data.
    a_subjects = load_test_subjects(base_loc=".\\results\\subjectdata\\adaptive\\", filename="combined_adaptive.json")
    f_subjects = load_test_subjects(base_loc=".\\results\\subjectdata\\fixed\\", filename="combined_fixed.json")
    # Convert JSON data to pandas dataframe
    subject_answers_df = get_answers_df()

    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(subject_answers_df)

    MODES = ['Fixed CED', 'DVS', 'Adaptive CED']
    # Get pandas dataframe of study-population individual preformance.
    car_accuracy, car_confidence, people_accuracy, people_confidence = get_average_sub_accuracy()
    # For each mode calculate learning curve with R-pearson test
    for mode in MODES:
        learning_curve(mode)

    for individual in range(30):
        individual_scoring(str(individual))

    test_normality()
    fixed_dvs_comparison()
    fixed_adaptive_comparison()
