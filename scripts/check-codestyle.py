#!/usr/bin/env python

import argparse
import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_DIR = os.path.join(BASE_DIR, "src")


class CheckError(Exception):
    pass


class CodestyleChecker:
    def __init__(self, module=None, no_color=False):
        """ Initialize the code checker.

        module: If given, only this module is checked.
        no_color: Do not show any colors.
        """
        self._modules = self._find_modules()
        if module:
            # only one module -> check if it exists
            if module in self._modules:
                self._modules = [module]
            else:
                raise CheckError("Module not found: {}".format(module))

        self._no_color = no_color

    def check(self):
        """ Run all checks.

        Returns the total number of findings."""
        total = 0

        for module in self._modules:
            # print currently checked module as status message
            print(self._color(self._fill("Checking module: {} ".format(module), 37), "green"), end="")
            sys.stdout.flush()

            # run the checks
            flake8_findings = self._run_flake8(module)
            pylint_findings = self._run_pylint(module)
            failed = flake8_findings or pylint_findings
            total += len(flake8_findings) + len(pylint_findings)

            # show [failed] or [ok]
            if failed:
                print(self._color("[failed]", "red"))
            else:
                print(self._color("[ok]", "green"))

            # show errors
            if flake8_findings:
                print(self._color("PEP8", "blue"))
                for f in flake8_findings:
                    print(f)
            if pylint_findings:
                print(self._color("pylint", "blue"))
                for f in pylint_findings:
                    print(f)

            # show summary
            if failed:
                print(self._color("PEP8: {}, pylint: {}".format(len(flake8_findings), len(pylint_findings)), "red"))

        return total

    def _find_modules(self):
        """ Find all modules: the directories inside `src` folder. """
        modules = []
        for f in sorted(os.listdir(SOURCE_DIR)):
            if os.path.isdir(os.path.join(SOURCE_DIR, f)):
                modules.append(f)
        return modules

    def _run_check(self, name, cmd):
        """ Run the command for a check and handle output.

        Flake8 currently does not have a stable non-legacy API and pylint internally also uses Popen.
        So forget about using python libs, we just use subprocess here.

        name: name of the check (for error messages)
        cmd: list with command and parameters

        Returns: list of strings
        """
        try:
            tmp = subprocess.run(cmd, cwd=SOURCE_DIR, capture_output=True, text=True)
        except FileNotFoundError:
            raise CheckError("{} not found".format(name))

        # check for errors
        if tmp.returncode != 0:
            raise CheckError("{} error: {}".format(name, tmp.stderr))

        findings = []
        for line in tmp.stdout.splitlines():
            if line:  # get rid of empty lines
                findings.append(line)

        return findings

    def _run_flake8(self, module):
        """ Run flake8 for this module.

        Returns list of findings."""
        cmd = ["flake8",
               "--config", "../.flake8",
               "--exit-zero",
               module]

        return self._run_check("flake8", cmd)

    def _run_pylint(self, module):
        """ Run pylint for this module.

        Returns list of findings."""
        cmd = ["pylint",
               "--rcfile=../.pylintrc",
               "--errors-only",
               "--reports=n",
               "--exit-zero",
               module]

        findings = self._run_check("pyltint", cmd)

        # filter lines with "*************" (pylint shows that between findingds)
        findings = list(filter(lambda s: "*************" not in s, findings))

        return findings

    def _color(self, text, color):
        """ Return the text in the given color for printing on the terminal.
        If no_color was False, just return the text."""
        if self._no_color:
            return text

        colors = {
            "red": "\x1b[31m",
            "green": "\x1b[32m",
            "blue": "\x1b[34m",
        }
        return "{}{}\x1b[0m".format(colors.get(color, ""), text)

    def _fill(self, text, width):
        """ Fill the text with whitespaced until it has `width` characters. """
        missing = width - len(text)
        if missing > 0:
            return "{}{}".format(text, " "*missing)
        return text


def main():
    # parse arguments
    parser = argparse.ArgumentParser(description='Check Helfertool code style (PEP8 and pylint)')
    parser.add_argument("--module", help="Check this module only")
    parser.add_argument('--no-color', action='store_true', help='Do not output colors')
    args = parser.parse_args()

    # run the checks
    try:
        checker = CodestyleChecker(args.module, args.no_color)
        num_findings = checker.check()

        if num_findings > 0:
            sys.exit(1)
    except CheckError as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
