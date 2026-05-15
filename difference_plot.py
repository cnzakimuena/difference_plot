"""
This code generates a difference plot. The plot uses the chick weight dataset for demonstration, 
and includes example annotations for significance based on statistical testing. The appearance of 
the plot is customized and the final figure is saved.
"""
import os
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

from preprocessing import Preprocessor

# non-italic matplotlib greek characters
matplotlib.rcParams['mathtext.default'] = 'regular'


def get_star_number(p_value):
    """
    Determines the number of stars for a given p-value based on significance thresholds.
    """
    star_integer = None
    if 0.01 < p_value <= 0.05:
        star_integer = 1
    elif 0.001 < p_value <= 0.01:
        star_integer = 2
    elif p_value <= 0.001:
        star_integer = 3
    if star_integer is None:
        raise ValueError(r'Star integer is None.')
    return star_integer


def generate_plot(metrics_df,
                  metrics_variable_list,
                  x_range,
                  **plot_kwargs):
    """
    Generates a difference plot with error bars and optional p-value annotations 
    based on the provided dataframes and parameters.
    """

    if 'specified_color' not in plot_kwargs:
        plot_kwargs['specified_color'] = 'blue'

    # set font and font size
    plt.rcParams['font.family'] = ['Arial']
    plt.rcParams.update({'font.size': 16})

    # generate plot
    fig, ax = plt.subplots(figsize=(6, 6))

    # create list with specified lenght starting from 2 with interval 2, reverse the list
    y_locations_start = 2
    y_locations_interval = 2
    y_locations = \
        list(range(2, (len(metrics_df) * 2) + y_locations_interval, y_locations_start))[::-1]

    # set x and y limits
    plt.xlim([x_range[0], x_range[1]])
    plt.ylim([0, max(y_locations) + y_locations_interval])
    for i in range(len(metrics_df)):
        plt.hlines(y=y_locations[i],
                   xmin=metrics_df.iat[i, 1],
                   xmax=metrics_df.iat[i, 2],
                   color=plot_kwargs['specified_color'], linewidth=2.5)
        plt.scatter(x=metrics_df.iat[i, 0],
                    y=y_locations[i],
                    c=plot_kwargs['specified_color'], s=46)

    if 'p_values_df' in plot_kwargs:
        # add p-value star next to range limits
        current_p_values_list = \
            plot_kwargs['p_values_df'][plot_kwargs['p_values_variable']].tolist()
        current_q1_list = metrics_df[metrics_variable_list[1]].tolist()
        current_q3_list = metrics_df[metrics_variable_list[2]].tolist()
        p_location_reference = (x_range[1]-x_range[0]) * 0.08
        for h, current_p_value in enumerate(current_p_values_list):
            if current_p_value < 0.05:
                x_location = None
                # right if mean is positive
                if metrics_df.iat[h, 0] >= 0:
                    x_location = current_q3_list[h] + p_location_reference
                # left if mean is negative
                elif metrics_df.iat[h, 0] < 0:
                    x_location = current_q1_list[h] - p_location_reference
                elif x_location is None:
                    raise ValueError(r'x location is None.')
                star_number = get_star_number(current_p_value)
                star_string = r'$\mathbf{\ast}$' * star_number
                ax.annotate(star_string, xy=(x_location, y_locations[h]),
                            color='black',
                            fontsize="xx-small", weight='normal',
                            horizontalalignment='center',
                            verticalalignment='center')

    # add vertical dotted line at x = 0 location
    plt.plot([0, 0], [0, max(y_locations) + y_locations_interval],
             color='black', linewidth=2, linestyle="dashed", dashes=(1, 3))

    plt.xticks(np.linspace(x_range[0], x_range[1], num=5).tolist())
    if 'specified_y_tick_labels' in plot_kwargs:
        plt.yticks(y_locations, plot_kwargs['specified_y_tick_labels'])
    if 'specified_x_label' in plot_kwargs and 'specified_x_label_text_padding' in plot_kwargs:
        plt.xlabel(plot_kwargs['specified_x_label'],
                   labelpad=plot_kwargs['specified_x_label_text_padding'])
    if 'specified_y_label' in plot_kwargs and 'specified_y_label_text_padding' in plot_kwargs:
        plt.ylabel(plot_kwargs['specified_y_label'],
                   labelpad=plot_kwargs['specified_y_label_text_padding'])
    ax.tick_params(axis='both', colors='black')

    # set the color of the axis labels
    ax.xaxis.label.set_color('black')
    ax.yaxis.label.set_color('black')

    # change all spines
    for axis in ['bottom', 'left', 'top', 'right']:
        plt.gca().spines[axis].set_linewidth(2)
    plt.gca().tick_params(width=2)

    # adjust subplots spacing
    # if subplots are added, can include, for e.g., 'wspace=0.4, hspace=0.4'
    # to control padding between subplots
    plt.subplots_adjust(bottom=0.2, top=0.85, left=0.3, right=0.85)

    # add global title
    if 'super_title' in plot_kwargs:
        fig.suptitle(plot_kwargs['super_title'], fontsize="large", color="black")


if __name__ == '__main__':

    # --- read data ---
    # if preprocessed data does not exist, generate preprocessed data
    if not os.path.exists(r'.\metrics.csv') and not os.path.exists(r'.\p_values.csv'):
        EXAMPLE_DATA_PATH = r'.\chickweight.csv'
        example_preprocessor = Preprocessor(EXAMPLE_DATA_PATH)
        # specify preprocessing variables
        example_subject_variable = example_preprocessor.data_df.columns[2]
        example_dependent_variable = example_preprocessor.data_df.columns[0]
        example_condition_variable = example_preprocessor.data_df.columns[3]
        example_group_variable = example_preprocessor.data_df.columns[1]
        # gather preprocessed data
        example_preprocessor.get_preprocessed_data(example_subject_variable,
                                                example_dependent_variable,
                                                example_condition_variable,
                                                example_group_variable,
                                                save_csv_files=True)
    # read preprocessed data
    EXAMPLE_METRICS_PATH = r'.\metrics.csv'
    EXAMPLE_P_VALUES_PATH = r'.\p_values.csv'
    example_metrics_df = pd.read_csv(EXAMPLE_METRICS_PATH)
    example_p_values_df = pd.read_csv(EXAMPLE_P_VALUES_PATH)

    # --- specify plotting variables ---
    example_condition_variable = example_metrics_df.columns[3]
    example_group_variable = example_metrics_df.columns[4]
    # store average, Q1 and Q3 metrics variables, respectively
    example_metrics_variable_list = [example_metrics_df.columns[0],
                                     example_metrics_df.columns[1],
                                     example_metrics_df.columns[2]]

    # apply filters
    condition_filter_value = [0]
    group_filter_range_values = [4, 8]
    example_metrics_df = Preprocessor.apply_filter(example_metrics_df,
                                                   example_condition_variable,
                                                   condition_filter_value)
    example_p_values_df = Preprocessor.apply_filter(example_p_values_df,
                                                    example_condition_variable,
                                                    condition_filter_value)
    example_metrics_df = Preprocessor.apply_filter(example_metrics_df,
                                                   example_group_variable,
                                                   list(range(group_filter_range_values[0],
                                                              group_filter_range_values[1])))
    example_p_values_df = Preprocessor.apply_filter(example_p_values_df,
                                                    example_group_variable,
                                                   list(range(group_filter_range_values[0]-1,
                                                              group_filter_range_values[1]-1)))

    # specify data-related plotting parameters (optional)
    example_group_unique_values = \
        sorted(list(set(example_metrics_df[example_group_variable].tolist())))
    example_y_tick_labels = [str(s) + " days" for s in example_group_unique_values]

    # --- plot data ---
    generate_plot(example_metrics_df,
                  example_metrics_variable_list,
                  [-50, 150],
                  p_values_df=example_p_values_df,
                  p_values_variable=example_p_values_df.columns[0],
                  specified_x_label='Weight change [g]',
                  specified_y_label='Age',
                  specified_x_label_text_padding=20,
                  specified_y_label_text_padding=20,
                  specified_y_tick_labels=example_y_tick_labels,
                  specified_color='cornflowerblue')

    # save figure
    FILE_DESTINATION = r'.\figure'
    plt.savefig(os.path.join(FILE_DESTINATION + '.pdf').replace("\\", "/"), format="pdf")
    plt.savefig(os.path.join(FILE_DESTINATION + '.png').replace("\\", "/"), dpi=300)
    plt.close()
