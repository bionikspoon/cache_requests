#!/usr/bin/env python3
# coding=utf-8
from datetime import datetime
from functools import partial, reduce
from os.path import dirname, realpath, join, relpath


# CONFIG UTILS
# ----------------------------------------------------------------------------
def path(*args):
    return realpath(join(*args))


# CONFIG
# ----------------------------------------------------------------------------
# PATH FUNCTIONS
DOCS = partial(path, dirname(__file__))
SOURCE = partial(DOCS, 'source')
PROJECT = partial(DOCS, '..')

# CONSTANTS
README = 'README.rst'
OUT_FILE = PROJECT(README)
TODAY = datetime.now().strftime('%A, %B %d, %Y')  # %A, %B %d, %Y -> Friday, December 11, 2015
FILE_HEADER = '.. Source defined in %s\n\n'

# SOURCE DEFINITIONS
# ----------------------------------------------------------------------------
comment_line = """
.. This document was procedurally generated by %s on %s
""".strip() % (__file__, TODAY)

roles_override = """
.. role:: mod(literal)
.. role:: data(literal)
.. role:: envvar(literal)
"""


def include_documents(_=None):
    yield read_text(comment_line)
    yield read_text(roles_override)
    yield read_source('readme_title.rst')
    yield read_source('readme_features.rst')
    yield read_source('installation.rst')
    yield read_source('usage.rst')
    yield read_source('readme_credits.rst')


# PRE CONFIGURED PARTIALS
# ----------------------------------------------------------------------------
def read_source(file_name):
    yield from read_file(SOURCE(file_name))


def write_out(lines):
    yield from write_file(OUT_FILE, lines)


# PROCESS PIPELINE
# ----------------------------------------------------------------------------
def read_file(file_name):
    yield FILE_HEADER % relpath(file_name, PROJECT())
    with open(file_name) as f:
        yield from f


def read_text(text):
    yield FILE_HEADER % relpath(__file__, PROJECT())
    yield from text.splitlines(True)


def concatenate(sources):
    for source in sources:
        yield from source
        yield '\n\n'


def sanitize(lines):
    rules = rule__code_blocks, rule__other_rules
    yield from pipeline(rules, lines)


def write_file(file_name, lines):
    with open(file_name, 'w') as f:
        for line in lines:
            yield f.write(line)


def notify(lines):
    # Print messages for start and finish; draw a simple progress bar

    print('Writing', README, end='')
    for i, line in enumerate(lines):
        if i % 5 is 0:
            print('.', end='')

        yield line

    print('Done!')


# SANITIZE RULES
# ----------------------------------------------------------------------------
def rule__code_blocks(lines):
    # Replace highlight directive with code blocks

    code_block_language = 'python'

    for line in lines:
        # named conditions
        is_new_file = line.startswith(FILE_HEADER[:-5])
        is_code_block_shorthand = line.endswith('::\n') and not line.strip().startswith('..')

        # set highlight language and remove directive
        if line.startswith('.. highlight:: '):
            _, code_block_language = line.rsplit(maxsplit=1)  # parse and set language
            continue  # remove highlight directive

        # reset highlight language to default
        if is_new_file:
            code_block_language = 'python'

        # write code block directive
        if is_code_block_shorthand:
            yield line.replace('::\n', '\n')  # remove the shorthand
            yield '\n.. code-block:: %s\n' % code_block_language  # space out new directive
            continue

        yield line


def rule__other_rules(lines):
    # add small rules here, or create a named rule.

    for line in lines:

        # remove orphan directive.
        if line.startswith(':orphan:'):
            continue

        yield line


# SCRIPT UTILS
# ----------------------------------------------------------------------------
def pipeline(steps, initial=None):
    """
    Chain results from a list of functions. Inverted reduce.

    :param (function) steps: List of function callbacks
    :param initial: Starting value for pipeline.
    """

    def apply(result, step):
        yield from step(result)

    yield from reduce(apply, steps, initial)


# RUN SCRIPT
# ----------------------------------------------------------------------------
if __name__ == '__main__':
    process = include_documents, concatenate, sanitize, write_out, notify
    list(pipeline(process))
