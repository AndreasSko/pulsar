#!/usr/bin/env python
# Little script to make HISTORY.rst more easy to format properly, lots TODO
# pull message down and embed, use arg parse, handle multiple, etc...
import os
import sys


PROJECT_DIRECTORY = os.path.join(os.path.dirname(__file__))
PROJECT_URL="https://github.com/galaxyproject/pulsar"

def main(argv):
    history_path = os.path.join(PROJECT_DIRECTORY, "HISTORY.rst")
    history = open(history_path, "r").read()

    def extend(from_str, line):
        from_str += "\n"
        return history.replace(from_str, from_str + line + "\n" )

    ident = argv[1]
    if ident.startswith("pr"):
        pull_request = ident[len("pr"):]
        text = ".. _Pull Request {0}: {1}/pull/{0}".format(pull_request, PROJECT_URL)
        history = extend(".. github_links", text)
        history = extend(".. to_doc", "`Pull Request {0}`_".format(pull_request))
    elif ident.startswith("issue"):
        issue = ident[len("issue"):]
        text = ".. _Issue {0}: {1}/issues/{0}".format(issue, PROJECT_URL)
        history = extend(".. github_links", text)
        history = extend(".. to_doc", "`Issue {0}`_".format(issue))
    else:
        short_rev = ident[:7]
        text = ".. _{0}: {1}/commit/{0}".format(short_rev, PROJECT_URL)
        history = extend(".. github_links", text)
        history = extend(".. to_doc", "{0}_".format(short_rev))
    open(history_path, "w").write(history)

if __name__ == "__main__":
    main(sys.argv)
