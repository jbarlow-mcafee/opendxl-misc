#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function
import argparse
import os
import re
import shutil
import subprocess

ORIGINAL_REF = None


def shutdown(exit_code=0):
    if ORIGINAL_REF:
        subprocess.call(["git", "checkout", "--quiet", ORIGINAL_REF])
    exit(exit_code)


def run_command(args, exit_message=None):
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    output, _ = proc.communicate()
    output = output.decode()
    exit_code = proc.returncode
    if exit_message and exit_code != 0:
        print("{}{}, aborting...".format(output, exit_message))
        shutdown(exit_code)
    return proc.returncode, output.strip()


def run_git_command(args, exit_message=None):
    return run_command(["git"] + args, exit_message)


_, ORIGINAL_COMMIT_SHA = run_git_command(["rev-parse", "HEAD"],
                                         "Can't get current git commit")
ORIGINAL_REF_RETURN_CODE, ORIGINAL_REF = run_git_command(["symbolic-ref",
                                                          "-q", "HEAD"])
if ORIGINAL_REF_RETURN_CODE == 0:
    ORIGINAL_REF = re.sub("^refs/heads/", "", ORIGINAL_REF)
else:
    ORIGINAL_REF = ORIGINAL_COMMIT_SHA


def staged_changes_in_repo(exit_message=None):
    exit_code, _ = run_git_command(["diff-index", "--exit-code", "--cached",
                                    "HEAD", "--"], exit_message)
    return exit_code


def main():
    parser = argparse.ArgumentParser(description="publish ghpages")
    parser.add_argument("remote", nargs="?", default="origin",
                        help="github remote name, default is 'origin'")
    args = parser.parse_args()

    remote = args.remote

    run_git_command(["status"], "Unable to determine git repo status")

    if not os.path.exists("setup.py"):
        print("Unable to locate setup.py file. This may not be a Python project.")
        shutdown(1)

    print("Validating that no git repo changes are outstanding...")
    staged_changes_in_repo("Staged changes in git repo")
    run_git_command(["diff-files", "--exit-code"],
                    "Unstaged changes in git repo")

    print("Running dist task...")
    run_command(["python", "dist.py"], "Dist task failed")

    print("Checking out gh-pages branch...")
    exit_code, _ = run_git_command(["rev-parse", "--quiet", "--verify",
                                    "gh-pages"])
    if exit_code == 0:
        run_git_command(["checkout", "gh-pages"],
                        "Unable to checkout gh-pages branch")
        run_git_command(["pull", remote, "gh-pages"])
    else:
        print("Local gh-pages branch does not exist so try to fetch it...")
        exit_code, _ = run_git_command(["fetch", remote, "gh-pages"])
        if exit_code == 0:
            run_git_command(["checkout", "-b", "gh-pages",
                             "remotes/{}/gh-pages".format(remote)])
        else:
            print("gh-pages does not exist in remote, so creating...")
            run_git_command(["checkout", "--orphan", "gh-pages"],
                            "Unable to create new gh-pages branch")
            run_git_command(["reset"], "Unable to reset local gh-pages branch")

    print("Copying latest generated docs to pydoc directory...")
    if os.path.exists("pydoc"):
        shutil.rmtree("pydoc")
    shutil.copytree("dist/doc", "pydoc")

    print("Ensuring .nojekyll file exists...")
    open(".nojekyll", "a").close()

    print("Adding changed files to git index...")
    run_git_command(["add", "pydoc/*"], "Unable to add pydoc/* files to index")
    run_git_command(["add", ".nojekyll"],
                    "Unable to add .nojekyll file to index")
    if staged_changes_in_repo() == 0:
        print("gh-pages branch already up to date, skipping commit...")
    else:
        print("Committing changes to gh-pages branch...")
        short_commit_sha = ORIGINAL_COMMIT_SHA[:7]
        run_git_command(["commit", "-m",
                         "Updating docs for {}".format(short_commit_sha)],
                        "Unable to commit changes")

    print("Pushing gh-pages changes to {}...".format(remote))
    run_git_command(["push", remote, "gh-pages"], "Unable to push changes")

    # Clean files so can switch back to the original ref. Preserve dist
    # directory so it's available for inspection, if desired.
    print("Cleaning up files before exit...")
    run_git_command(["clean", "-dfq", "-e", "dist"])

    print("Publish was successful, exiting...")
    shutdown()


main()
