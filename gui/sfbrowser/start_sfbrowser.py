#!/usr/bin/env python

import argparse
import os
import vdomr as vd
from cairio import client as ca
from sfbrowsermainwindow import SFBrowserMainWindow
os.environ['SIMPLOT_SRC_DIR'] = '../../simplot'


class TheApp():
    def __init__(self):
        pass

    def createSession(self):
        print('creating main window')
        W = SFBrowserMainWindow()
        print('done creating main window')
        return W


def main():
    parser = argparse.ArgumentParser(description='Browse SpikeForest results')
    parser.add_argument(
        '--port', help='The port to listen on (for a web service). Otherwise, attempt to launch as stand-alone GUI.', required=False, default=None)

    args = parser.parse_args()

    # Configure readonly access to kbucket
    ca.autoConfig(collection='spikeforest', key='spikeforest2-readonly')

    APP = TheApp()

    if args.port is not None:
        vd.config_server()
        server = vd.VDOMRServer(APP)
        server.setPort(int(args.port))
        server.start()
    else:
        vd.config_pyqt5()
        W = APP.createSession()
        vd.pyqt5_start(root=W, title='SFBrowser')


if __name__ == "__main__":
    main()
