"""Translate a subset of LaTeX into MoinMoin wiki syntax.

This program was originally written by Maxime Biais <maxime@biais.org>
and then modified by Allen Downey <downey@allendowney.com>.  The
original is available at http://wiki.loria.fr/wiki/Latex2wiki

The primary limitation of this program is that it only recognizes
Latex patterns if they appear on a single line, so {\tt this pattern}
would get translated, but {\tt this
pattern} would not.

Other limitations include:

1) It doesn't distinguish between itemize, enumerate and
description; everything becomes itemize.

2) It only recognizes the subset of Latex I use.

3) It's not particularly efficient, but for the files I have
   translated, it doesn't matter.

"""

#    Copyright (C) 2003, Maxime Biais <maxime@biais.org>
#    Modified version Copyright 2005 Allen B. Downey
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import sys, re

# rewrites is a list of rewrite rules.
# The first entry in each line is a regular expression.
# The second line is the format string
# used to rewrite the line if the regexp matches.

rewrites = [
    # comments
    (r"%.*", ""),
    # simple Latex commands we ignore
    (r"\\[^ {]*$", ""),
    # other Latex commands we ignore
    (r"\\label{.*}", ""),
    (r"\\documentclass{.*}", ""),
    (r"\\usepackage{.*}", ""),
    (r"\\newcommand{.*}", ""),
    (r"\\setlength{.*}", ""),
    # some characters that have to be quoted in Latex
    # that don't have to be quoted in wiki
    (r"(.*)\\#(.*)", "%s#%s"),
    (r"(.*)\\\$(.*)", "%s$%s"),
    (r"(.*)\\&(.*)", "%s&%s"),
    # text formats
    (r"(.*)\\emph{([^}]*)}(.*)", "%s'''%s'''%s"),
    (r"(.*){\\sf ([^}]*)}(.*)", "%s`%s`%s"),
    (r"(.*){\\bf ([^}]*)}(.*)", "%s'''%s'''%s"),
    (r"(.*){\\em ([^}]*)}(.*)", "%s''%s''%s"),
    # urls (a url at the beginning of a line gets a special rule
    (r"^\\url{([^}]*)}(.*)", "%s %s"),
    (r"(.*)\\url{([^}]*)}(.*)", "%s %s %s"),
    (r"(.*){\\tt ([^}]*)}(.*)", "%s{{{%s}}}%s"),
    # arrow is a special command that appears in some of my files
    (r"(.*)\\arrow (.*)", "%s-->%s"),
    # footnotes get translated into parenthetical comments
    # (which some people think is a preferable style anyway)
    (r"(.*)\\footnote{(.*)}(.*)", "%s (footnote: %s) %s"),
    # all items become bulleted items (no unemerations)
    (r"\\item (.*)", " * %s"),
    # verbatim becomes code display
    (r"\\begin{verbatim}", "{{{"),
    (r"\\end{verbatim}", "}}}"),
    # all other latex environments are ignored
    (r"\\begin{.*}", ""),
    (r"\\end{.*}", ""),
    # turn Latex quotation marks into plain old quotation marks
    (r"(.*)``(.*)''(.*)", "%s\"%s\"%s"),
    # headings and title page entries
    (r"\\paragraph{(.*)}", "==== %s ===="),
    (r"\\subsubsection{(.*)}", "==== %s ===="),
    (r"\\subsection{(.*)}", "=== %s ==="),
    (r"\\section{(.*)}", "== %s =="),
    (r"\\chapter{(.*)}", "= Chapter %s ="),
    (r"\\title{(.*)}", "= %s ="),
    (r"\\author{(.*)}", "%s"),
    (r"\\date{(.*)}", "%s"),
    (r"\\caption{(.*)}", "(caption: %s)"),
    ]


def apply_rewrites(line, rewrites):
    """apply each rewrite rule repeatedly and return the result"""
    for reg, format in rewrites:
        # keep applying each rule until it doesn't match.
        # compiling the reg would probably improve performance.
        while True:
            m = re.search(reg, line)
            if not m: break
            line = format % m.groups()
    return line


def main(script, infile, outfile=None):
    in_stream = open(infile)
    if outfile:
        out_stream = open(outfile, 'w')
    else:
        out_stream = sys.stdout

    for line in in_stream:
        line = line.rstrip()
        line = apply_rewrites(line, rewrites)
        print >> out_stream, line

if __name__ == '__main__':
    main(*sys.argv)
