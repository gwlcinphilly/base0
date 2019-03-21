"""
This library will handle command line parameters and related GUI options
"""
__all__ = []
import argparse
import os
import json
import sys
from argparse import ArgumentDefaultsHelpFormatter,RawDescriptionHelpFormatter, ArgumentParser

class CustomFormatter(ArgumentDefaultsHelpFormatter, RawDescriptionHelpFormatter):
    """required for the future argument process"""
    pass

def args_parseconfigfile(parser, filecontent):
    """passing argument files"""
    input_tree = ET.fromstring(filecontent)
    inputs = input_tree.findall("inputs//input")
    inputlist = []
    for input_ in inputs:
        inputlist.append("--%s" % input_.get('name'))
        inputlist.append(input_.text)
        args_ = parser.parse_args(inputlist)
    return args_

def args_parse(arg_def):
    """Passing arguments from command line """
    # create parameter process objects
    parser = ArgumentParser(description=arg_def['description'],
                            prog=arg_def['prog'],
                            epilog=arg_def['epilog'],
                            formatter_class=CustomFormatter)

    for arg_ in arg_def['args']:
        if "choices" in arg_.keys():
            parser.add_argument("-%s" % arg_['short'],
                                "--%s" % arg_['para'],
                                help="%s" % arg_['help'],
                                choices=arg_['choices'],
                                default=arg_['choices'][0])
        elif 'default' in arg_.keys():
            parser.add_argument("-%s" % arg_['short'],
                                "--%s" % arg_['para'],
                                default="%s" % arg_['default'],
                                help="%s" % arg_['help'])
        elif 'type' in arg_.keys():
            if arg_['type'] == "file":
                parser.add_argument("-%s" % arg_['short'],
                                    "--%s" % arg_['para'],
                                    help="%s" % arg_['help'],
                                    type=file) # pylint: disable=E0602
        else:
            if "require" in arg_.keys():
                parser.add_argument("-%s" % arg_['short'],
                                    "--%s" % arg_['para'],
                                    help="%s" % arg_['help'])
            else: 
                parser.add_argument("-%s" % arg_['short'],
                                    "--%s" % arg_['para'],
                                    help="%s" % arg_['help'],
                                    action='store_true')

    # if there is not parameter passed
    if len(sys.argv) == 1:
        if arg_def["gui_define"] is None:
            parser.print_help()
            parser.exit()           
        else:
            if os.path.exists(arg_def['gui_define']['defaultconfig']):
                with open(arg_def['gui_define']['defaultconfig'], 'r') as \
                filehandleobj: filecontent = filehandleobj.read()
                args_ = args_parseconfigfile(parser, filecontent)
                return args_
    # if there are parameter passed from command line
    else:
        args_ = parser.parse_args(sys.argv[1:])
        try:
            filecontent = args_.configfile.read()
        except: # pylint: disable=W9702
            return args_
        args_ = args_parseconfigfile(parser, filecontent)
        return args_

def args_files(filename, args=None, desc=None, datapath=None):
    """ Processed defined xml for the command line arguments"""
    filebasic = os.path.basename(filename).split('.py')[0]
    # set default args files and descript file path
    # read command line argument files
    if datapath is None:
        argsfilename = None
        descfilename = None
    else:
        argsfilename = os.path.join(datapath, f"{filebasic}.args")
        descfilename = os.path.join(datapath, f"{filebasic}.desc")
    
    if argsfilename is not None:
        if args is None:
            with open(argsfilename, 'r') as filehandleobj: 
                args_def = json.loads(filehandleobj.read())
    else:
        args_def = {'epilog' : "brief intruduction of app",
                    "description" : "Application description, inlcude history, known isuses and todo",
                    "prog": "",
                    "args": [],
                    "gui_define": {}}
    if args is not None:
        args_def = args
    # read command line description file name

    if descfilename is not None:
        if desc is None:
            with open(descfilename, 'r') as filehandleobj:
                desc_epilog = filehandleobj.read()
    else:
        desc_epilog = desc
    args_def['epilog'] = desc_epilog
    # add gui related defination if it is defined. 
    if "gui_define" in args_def.keys():
        args_def['gui_define']['classname'] = args_def['prog']
        args_def['gui_define']['guifile'] = "conf/"+filebasic+'.ui'
        args_def['gui_define']['defaultconfig'] = "conf/"+filebasic+'.xml'
    else: 
        args_def['gui_define'] = None
    args_def['arguments'] = argsfilename
    if "description" not in args_def:
        args_def['description'] = descfilename

    return args_def

