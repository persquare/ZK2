#!/usr/bin/env python3

import os
import subprocess
import argparse

TARGET =  os.path.expanduser("~/Library/LaunchAgents/com.github.persquare.zk2.plist")

def app():
    parser = argparse.ArgumentParser(description="Start/stop/restart the ZK webserver.")

    parser.add_argument('action', choices=['start', 'stop', 'restart'])

    args = parser.parse_args()

    if args.action in ['stop', 'restart']:
        subprocess.check_call(["/bin/launchctl", "unload", TARGET])

    if args.action in ['start', 'restart']:
        subprocess.check_call(["/bin/launchctl", "load", TARGET])


if __name__ == '__main__':
    app()