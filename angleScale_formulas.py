# execfile(r"C:\src\NVIDIA\usd-ci\angleScale_formulas.py")
import inspect
import math
import os

import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d
import spb
import sympy

# from sympy import *
from spb import plot, plot3d

INTERACTIVE_VIEW = False


THIS_FILE = os.path.abspath(inspect.getsourcefile(lambda: None) or __file__)
THIS_DIR = os.path.dirname(THIS_FILE)

IMAGE_SAVE_FOLDER = THIS_DIR
os.makedirs(IMAGE_SAVE_FOLDER, exist_ok=True)


def Clamp(x, min, max):
    return sympy.Min(sympy.Max(x, min), max)


def save_graph(graph, filename, dpi=300):
    ext = os.path.splitext(filename)[-1].lstrip(".")
    if not ext or ext.isdigit():
        filename = filename + ".jpg"
    print(f"Saving: {filename}")
    filepath = os.path.join(IMAGE_SAVE_FOLDER, filename)
    # this also ensures the graph is evaluated... I tried using
    # "graph.process_series()", but that seemed to make a second copy of the
    # graph, that didn't respect the zlim
    axes = graph.ax

    set_axis_limits(axes)
    graph.fig.savefig(filepath, dpi=dpi)


theta, angleScale = sympy.symbols("theta angleScale")


# angle_units = "radians"
angle_units = "degrees"

if angle_units == "radians":
    theta_max = sympy.pi
elif angle_units == "degrees":
    theta_max = 180

# in latex format
theta_input_label = r"$\theta_{light}$"
theta_output_label = r"$\theta_{ies}$"
theta_input_label = f"{theta_input_label} ({angle_units})"
theta_output_label = f"{theta_output_label} ({angle_units})"

theta_lim = (theta, 0, theta_max)
angleScale_lim = (angleScale, -1, 1)


def set_axis_limits(axes):
    if not "theta" in axes.get_xlabel():
        raise ValueError("expected x-axis to be theta")
    axes.set_xlabel(theta_input_label)
    axes.set_xlim(*theta_lim[1:])
    if hasattr(axes, "set_zlim"):
        axes.set_ylim(*angleScale_lim[1:])
        axes.set_zlim(*theta_lim[1:])
        axes.set_zlabel(theta_output_label)
    else:
        axes.set_ylim(*theta_lim[1:])
        axes.set_ylabel(theta_output_label)


def save_graph_slices(function, title, filename):
    for i in range(-100, 101, 25):
        angleScale_val = i / 100
        angleScale_str = f"{angleScale_val:+.02f}"
        title_i = f"{title} (angleScale = {angleScale_str})"
        filename_i = f"{filename}_{angleScale_str}"
        slice_func = function.subs(angleScale, angleScale_val)
        graph = spb.plot(slice_func, theta_lim, show=False, title=title_i)
        if any(isinstance(x, sympy.core.numbers.ComplexInfinity) for x in slice_func.atoms()):
            del graph.series[0]
            axes = graph.ax
            set_axis_limits(axes)
            x_center = sum(axes.get_xlim()) / 2
            y_center = sum(axes.get_ylim()) / 2
            axes.text(
                x_center,
                y_center,
                "Undefined\nAsymptote",
                verticalalignment="center",
                horizontalalignment="center",
                fontsize=50,
            )
        else:
            graph.ax.get_lines()[0].set_linewidth(5)
        save_graph(graph, filename_i)
        plt.close(graph.fig)


def plot3d_and_save(function, title, slices=False):
    graph = spb.plot3d(function, theta_lim, angleScale_lim, show=False, title=title)
    filename = f"ies_angleScale_{title}"
    filename = filename.replace(" - ", "-")
    filename = filename.replace("/", "over")
    for to_erase in "()":
        filename = filename.replace(to_erase, "")
    filename = filename.replace(" ", "_")

    save_graph(graph, filename)
    if slices:
        save_graph_slices(function, title, filename)
    return graph


karma_pos = theta / (1 - angleScale)
karma_neg = theta * (1 + angleScale)

karma = sympy.Piecewise((0, angleScale < -1), (karma_neg, angleScale < 0), (karma_pos, angleScale < 1), (0, True))
karma_clamp = Clamp(karma, 0, theta_max)

karma_pos_clamp = Clamp(sympy.Piecewise((0, angleScale < -1), (karma_pos, angleScale < 1), (0, True)), 0, theta_max)


# karma_pos_graph = plot3d_and_save(karma_pos, "Karma (positive)")
# karma_neg_graph = plot3d_and_save(karma_neg, "Karma (negative)")

karma_graph = plot3d_and_save(karma, "Karma (unclamped)")

karma_clamp_graph = plot3d_and_save(karma_clamp, "Karma (clamped)", slices=True)
# save_graph_slices(karma_clamp, "ies_angleScale_karma_clamped")

karma_pos_clamp_graph = plot3d_and_save(karma_pos_clamp, "Karma - theta / (1-angleScale) only (clamped)")

profile_scale = 1 + angleScale
rman = ((theta - theta_max) / profile_scale) + theta_max
rman_clamp = Clamp(sympy.Piecewise((rman, angleScale > -1), (0, True)), 0, theta_max)

rman_graph = plot3d_and_save(rman, "Renderman (unclamped)")

rman_clamp_graph = plot3d_and_save(rman_clamp, "Renderman (clamped)", slices=True)

if INTERACTIVE_VIEW:
    plt.show()
else:
    plt.close("all")
