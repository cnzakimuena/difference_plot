"""
This code generates a difference plot. The plot uses the chick weight dataset for demonstration, 
and includes example annotations for significance based on statistical testing. The appearance of 
the plot is customized and the final figure is saved.
"""
import os
import numpy as np
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
                  group_variable,
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
    fig, ax = plt.subplots(figsize=(7, 7))

    # create list with specified lenght starting from 2 with interval 2, reverse the list
    group_values = sorted(list(metrics_df[group_variable].tolist()))
    y_locations_start = 2
    y_locations_interval = 2
    y_locations = \
        list(range(2, (len(group_values) * 2) + y_locations_interval, y_locations_start))[::-1]

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
            if current_p_value is not None and current_p_value < 0.05:
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
    plt.subplots_adjust(bottom=0.25, top=0.85, left=0.3, right=0.8)

    # add global title
    if 'super_title' in plot_kwargs:
        fig.suptitle(plot_kwargs['super_title'], fontsize="large", color="black")


if __name__ == '__main__':

    # --- read data ---
    EXAMPLE_DATA_PATH = r'.\chickweight.csv'
    example_data = Preprocessor(EXAMPLE_DATA_PATH)
    example_data.get_preprocessed_data(save_csv_files=False)
    # apply filters
    example_data.apply_multiple_filters([0], list(range(4, 8)))
    # specify data-related plotting parameters (optional)
    example_y_tick_labels = example_data.get_y_tick_labels()

    # --- plot data ---
    generate_plot(example_data.prep_results["metrics"],
                  example_data.prep_variables["group"],
                  example_data.prep_results["metrics variables"],
                  [-50, 150],
                  p_values_df=example_data.prep_results["p-values"],
                  p_values_variable=example_data.prep_results["p-values variable"],
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
