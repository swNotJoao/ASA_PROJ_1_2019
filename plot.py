# Instructions:
#
# sudo apt-get install python3-pip
# pip3 install numpy matplotlib
# sudo apt-get install python3-tk
# python3 plot.py --help
#
# Example:
# python3 plot.py ./a.out -fd=0.5 -r 100 2000 15 -m=5
#
# If no visual desktop is available use --hide or --output=result

import gen
import argparse
import numpy
import pickle
import os
import timeit
from math import sqrt, log10, floor
# Uncomment if GUI not available
# import matplotlib
# matplotlib.use('Agg')
from matplotlib import pyplot
from subprocess import Popen, PIPE, DEVNULL


class Plot:

    def __init__(self, program):

        # Style
        self.line_color = "red"
        self.dots_color = "blue"
        self.dot_size = 2
        self.line_width = 2

        # Config options
        self.program = program

        self.nodes_plus_links = None
        self.links = None
        self.density = None
        self.nodes = None
        self.save_file = None

        self.tests = 0
        self.multiple = 1
        self.test_n = 1

        self.last = [(0, 0), (0, 0)]

        self.hide = False
        self.output = None
        self.memory = False

        # All inputs should be here, poor RAM :(
        self.objs = {}

        self.save_as = False

    def load(self, saved_file):

        log("Loading input from %s" % saved_file)
        with open(saved_file, "rb") as file:
            self.objs = pickle.load(file)

    def save(self):

        if self.save_file is None:
            return

        log("Saving generated input %s" % self.save_file)
        with open(self.save_file, "wb") as file:
            pickle.dump(self.objs, file, protocol=2)

    def draw(self, xs, ys, plot):

        # noinspection PyTupleAssignmentBalance
        (m, b) = numpy.polyfit(xs, ys, 1)

        yp = numpy.polyval([m, b], xs)

        plot.scatter(xs, ys, s=self.dot_size, edgecolors=self.dots_color)
        plot.plot(xs, yp, color=self.line_color, linewidth=self.line_width)

        return m, b

    def run(self, obj):

        values, data = obj['values'], obj['data']

        xs = list(a / 1000 for a in values)  # in thousands
        ys = [[], []]

        size = len(values)
        for i in range(1, size + 1):

            time = 0
            space = 0

            for j in range(1, self.multiple + 1):

                msg=""
                if self.tests > 1:
                    msg = "previous: y=%fx+%f; " % self.last[0]
                    if self.memory:
                        msg += "last space: y=%fx+%f; " % self.last[1]

                msg += "Plot {:0{p}}/{:0{p}}; ".format(self.test_n, self.tests, p=1+floor(log10(self.tests))) \
                    + "Input {:0{p}}/{:0{p}}; ".format(i, size, p=1+floor(log10(size))) \
                    + "Repeat {:0{p}}/{:0{p}}".format(j, self.multiple, p=1+floor(log10(self.multiple)))

                log(msg, end='\r')

                start_time = timeit.default_timer()

                if not self.memory:
                    # Run only for time
                    p = Popen(self.program, stdout=DEVNULL, stdin=PIPE)
                    p.communicate(data[i - 1].encode("utf-8"))

                else:
                    # Get memory and time
                    # LINUX Only sorry
                    p = Popen(["/usr/bin/time", "-f", "%M", self.program], stdout=DEVNULL, stdin=PIPE, stderr=PIPE)
                    memory = int(p.communicate(data[i - 1].encode("utf-8"))[1])
                    space += memory / 1024  # mb

                time += (timeit.default_timer() - start_time) * 1000  # ms

            ys[0].append(time / self.multiple)
            ys[1].append(space / self.multiple)

        res = [(0, 0), (0, 0)]
        time_plot = pyplot
        space_plot = None

        if self.memory:
            fig, (time_plot, space_plot) = pyplot.subplots(nrows=1, ncols=2, figsize=(9, 3))
            fig.tight_layout(pad=2.5)
            res[1] = self.draw(xs, ys[1], space_plot)

        res[0] = self.draw(xs, ys[0], time_plot)

        if self.memory:
            space_plot.set_title("y=%fx+%f" % res[1])
            time_plot.set_title("y=%fx+%f" % res[0])
        else:
            time_plot.title("y=%fx+%f" % res[0])

        self.save_as = False
        if self.hide and self.output is None:
            return res

        if self.output is not None:
            if self.output:
                ext = "" if self.tests == 1 else str(self.test_n)
                pyplot.savefig(self.output[0] + ext)
            else:
                log()  # Print new line
                pyplot.savefig(input("Save as: "))
                self.save_as = True
        else:
            pyplot.show()

        # clear!
        pyplot.clf()

        return res

    def average(self, res):
        return res[0] / self.tests, res[1] / self.tests

    def generate_output(self):

        self.tests = len(self.objs)
        log("Generating outputs")

        all_plots = []
        lines = [[0, 0], [0, 0]]
        for i in range(1, self.tests + 1):
            self.test_n = i
            self.last = self.run(self.objs[i - 1])

            all_plots.append(self.last)
            lines[0][0] += self.last[0][0]
            lines[0][1] += self.last[0][1]

            lines[1][0] += self.last[1][0]
            lines[1][1] += self.last[1][1]

        if not self.save_as:
            log()

        if self.tests > 1:
            zeros = 1 + floor(log10(self.tests))
            x = 1
            for (time, space) in all_plots:
                msg = "Plot #{:0{p}}".format(x, p=zeros)
                msg += " -> time: y=%fx+%f; space: y=%fx+%f" % (time + space)
                log(msg)
                x += 1
            log("~ Average ~")

        log("time: y=%fx+%f" % self.average(lines[0]))
        if self.memory:
            log("memory: y=%fx+%f" % self.average(lines[1]))

    def generate_input(self):

        self.objs = []

        for x in range(1, self.tests + 1):

            log("Generating inputs %d/%d" % (x, self.tests), end='\r')
            obj = {}

            if self.density is not None:

                d = self.density

                obj["values"] = []
                obj["data"] = []

                for r in self.nodes_plus_links:

                    """
                                n = floor(
                                    (-2 + d + sqrt(4 - 4 * d + d * d + 8 * d * r)) / (2 * d)
                                )
            
                                m = r - n
                    """
                    n = (-2 + d + d * sqrt((d*d+8*d*r-4*d+4)/(d*d)))/(2*d)
                    n = floor(n)
                    m = r - n

                    obj["values"].append(r)
                    obj["data"].append(gen.get_input(n, m))

            elif type(self.links) == int:
                obj["values"] = self.nodes
                obj['data'] = [gen.get_input(n, self.links) for n in self.nodes]
            else:
                obj["values"] = self.links
                obj['data'] = [gen.get_input(self.nodes, l) for l in self.links]

            self.objs.append(obj)

        log()
        self.save()


def log(*args, **kwargs):
    print(*args, **kwargs, flush=True)


def parse_args():

    parser = argparse.ArgumentParser()
    parser.add_argument("program", help="Executable file")

    parser.add_argument("-p", "--memory", help="Draw second plot for memory usage", action="store_true")

    parser.add_argument("-m", "--multiple", help="Perform multiple tests for each input", type=int, default=1)
    parser.add_argument("-t", "--tests", help="Perform test a certain quantity of times", type=int, default=1)
    parser.add_argument("-hi", "--hide", help="Ignore plot", action="store_true")

    primary = parser.add_mutually_exclusive_group(required=True)
    primary.add_argument("-l", "--load", help="Load saved input")
    primary.add_argument("-r", "--range", nargs=3, metavar=("Start", "End", "Step"),
                         help="Range of values for plotting variable", type=int)

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("-fl", "--fix-links", help="Plot nodes with fixed links", type=int)
    group.add_argument("-fn", "--fix-nodes", help="Plot links with fixed nodes", type=int)
    group.add_argument("-fd", "--fix-density", help="Plot nodes + links with fixed density", type=float)

    parser.add_argument("-s", "--save", help="Save generated input")
    parser.add_argument("-o", "--output", help="Output each plot to file", nargs='*', default=None)

    return parser.parse_args()


def main():

    args = parse_args()

    begin = timeit.default_timer()

    values = None
    if args.range is not None:
        start, end, step = tuple(args.range)
        values = range(start, end, step)

    plot = Plot(args.program)
    plot.save_file = args.save
    plot.memory = args.memory
    plot.hide = args.hide
    plot.multiple = args.multiple
    plot.output = args.output
    plot.tests = args.tests

    if plot.memory and os.name != "posix":
        log("Memory plots only available on POSIX systems")
        plot.memory = False

    if args.load is None:

        if args.fix_density is not None:
            plot.nodes_plus_links = values
            plot.density = args.fix_density
        elif args.fix_links is not None:
            plot.nodes = values
            plot.links = args.fix_links
        elif args.fix_nodes is not None:
            plot.links = values
            plot.nodes = args.fix_nodes

    log("Links + Nodes", plot.nodes_plus_links)
    log("Links        ", plot.links)
    log("Nodes        ", plot.nodes)
    log("Density      ", plot.density)
    log("Tests        ", plot.tests)
    log("Multiple     ", plot.multiple)
    log("Output file  ", plot.output)
    log("Save file    ", plot.save_file)

    log("Starting linear fitting")
    if args.load:
        plot.load(args.load)
    else:
        plot.generate_input()

    plot.generate_output()
    log("Exiting; t=%ss" % (timeit.default_timer() - begin))


if __name__ == "__main__":
    main()
