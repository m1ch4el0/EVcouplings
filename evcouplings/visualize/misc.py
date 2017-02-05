"""
Miscellaneous visualization functions

Authors:
  Thomas A. Hopf
"""

import matplotlib.pyplot as plt


def plot_context(font="Helvetica", size=12,
                 axis_label_size=12, axis_title_size=14,
                 axis_line_width=1, tick_label_size=12,
                 tick_direction="out", dpi=300,
                 additional_param_dict=None):
    """
    Syntactic sugar for matplotlib rc_context defaulting
    to values useable for nice figures

    Parameters
    ----------
    font : str, optional (default: "Helvetica")
        Default font (make sure this font is added to
        fonts available to matplotlib)
    size : float, optional (default: 12)
        Default font size
    axis_label_size : float, optional (default: 12)
        Default size of axis labels
    axis_title_size : float, optional (default: 14)
        Default size of axis titles
     axis_line_width : float, optional (default: 1)
        Default line width
    tick_label_size : float, optional (default: 12)
        Default tick label size
    tick_direction : {"in", "out"}, optional (default: "out")
        Direction of axis ticks
    dpi : int, optional (default: 300)
        Resolution of plot in dpi
    additional_param_dict : dict, optional (default: None)
        Additional parameters passed to matplotlib.rc_context

    Returns
    -------
    matplotlib.rc_context
        Context for matplotlib plotting
    """
    from matplotlib import rc_context
    param_dict = {
        "font.family": font,
        "font.size": size,
        "axes.labelsize": axis_label_size,
        "axes.titlesize": axis_title_size,
        "axes.linewidth": axis_line_width,
        "xtick.labelsize": tick_label_size,
        "ytick.labelsize": tick_label_size,
        "xtick.direction": tick_direction,
        "ytick.direction": tick_direction,
        "figure.dpi": dpi,
        "savefig.dpi": dpi,
        "savefig.bbox": "tight",
        "pdf.fonttype": 42,
    }

    # add additional parameters
    if additional_param_dict is not None:
        param_dict = dict(param_dict.items() + additional_param_dict.items())

    return rc_context(param_dict)


def remove_chart_junk(ax=None, remove=("top", "right"),
                      x_ticks_loc="bottom", y_ticks_loc="left",
                      hide_x_labels=False, hide_y_labels=False):
        """
        Remove unnecessary plot axis, ticks etc.

        Parameters
        ----------
        ax : matplotlib Axes object
            Remove chart junk from this axis
        remove : list, optional (default: ["top", "right"])
            Remove the selected axis. Options:
            ["top", "bottom", "right", "left"]:
        x_ticks_loc : str, optional (default: "bottom")
            Location of x-axis ticks. Set "none" to hide
            ticks completely.
        y_ticks_loc : str, optional (default: "left")
            Location of y-axis ticks. Set "none" to hide
            ticks completely.
        hide_x_label : bool, optional (default: False)
            Hide x-tick labels on x-axis
        hide_y_label : bool, optional (default: False)
            Hide y-tick labels on y-axis
        """
        if ax is None:
            ax = plt.gca()

        for line in remove:
            ax.spines[line].set_visible(False)

        ax.xaxis.set_ticks_position(x_ticks_loc)
        ax.yaxis.set_ticks_position(y_ticks_loc)

        if hide_x_labels:
            plt.setp(plt.gca().get_xticklabels(), visible=False)
        if hide_y_labels:
            plt.setp(plt.gca().get_yticklabels(), visible=False)
