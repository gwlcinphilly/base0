"""
This module is use to generate simple GUI
"""
__all__ = []

import os
import json
from PyQt5.Qt import QMainWindow, QTableWidgetItem
from PyQt5.QtWidgets import QMessageBox
from PyQt5 import QtCore, QtWidgets

from base0.baselibs import get_log

def qtobj_check(func):
    """ decorate to check QT entry, if it is name,retrn obj"""
    def wrapper(*args, **kwargs):
        """ check if the input is a qa object"""
        gui = args[0].gui
        if isinstance(args[1], str):
            ins_ = getattr(gui, args[1])
            args_ = []
            args_[0] = args[0]
            args_[1] = ins_
            args_ += args[2:]
            return func(*args_, **kwargs)
        else:
            return func(*args, **kwargs)
    return wrapper
    
def guiinfo(message, timeout=2):
    """ popup GUI information window"""
    msg = QMessageBox()
    msg.setWindowTitle("Information")
    msg.setIcon(QMessageBox.Information)
    msg.setText(message)
    if timeout is not None:
        QtCore.QTimer().singleShot(timeout*1000, msg.close)
    msg.exec_()

class GuiQtBasic(QMainWindow):
    """ This module will use the basic map and static features migrate from v2"""

    def __init__(self, **kwargs):
        """initial GUI objects"""
        super().__init__()
        self.qt_working_obj = None
        self.qt_objs_mapper()
        if "configurefile" in kwargs:
            self.configurefile = kwargs['configurefile']
        else:
            self.configurefile = None
        if "appbasefolder" in kwargs:
            self.appbasefolder = kwargs['appbasefolder']
        else:
            self.appbasefolder = None
        if "scriptfolder" in kwargs:
            self.scriptfolder = kwargs['scriptfolder']
        else:
            self.scriptfolder = None
        
        if self.scriptfolder is not None:
            self.log = get_log(path=os.path.join(self.scriptfolder, "log"))
        else:
            self.log = get_log()

    def qt_objs_mapper(self):
        """ Define the basic Qt Objects basic operation
            In general, it should have:
            get    : if there is a list or all options, return list
            read    : get current value, return string
            write    : set current value
            set    : set list value
        """
        self.typelist = ["LiEdit", "TextEdit", "ComboBox", "Label",
                         "PushButton", "CheckBox", "SpinBox", "Widget",
                         "GroupBox", "ProgressBar", "MenuBar", "StatusBar",
                         "TableWidget"]

        self.qt_mapper = {
            "LineEdit"  :   {'read' : 'text',
                             'write': 'setText',
                             'set' : 'setText'},
            'TextEdit'  :  {'read' : 'toPlainText',
                            'write' : 'setPlainText',
                            'set' : "setPlainText"},
            'ComboBox'   :   {'read' : "currentText",
                              "write" : "self.qt_combobox_write",
                              "get"  : "",
                              "set"  : "self.qt_combobox_set"},
            'CheckBox'  : {"read" :  "self.qt_checkbox_read",
                           "write" : "self.qt_checkbox_write",
                           "set" : "self.qt_checkbox_write"},
            'SpinBox'   : {"read" : 'text',
                           }, 
            "TableWidget" : {"set" : "self.qt_tablewidget_set"}, 
            "Label" :   {'set' : 'setText'
                        }
            }

    def guiobj_read(self,objname):
        return self.guiobjs_read([objname])[objname]

    def guiobjs_read(self, objectslist,
                     raw=False, name_mapper=None):
        """ read gui object """
        gui_values = self._get_values(objectslist, raw=raw,
                                      name_mapper=name_mapper)
        return gui_values

    def guiobjs_write(self, objectslist, valuedict,
                      raw=False, name_mapper=None):
        """ write to gui object"""
        self._write_values(objectslist, valuedict, raw=raw,
                         name_mapper=name_mapper)

    def guiobj_set(self, obj, value):
        self.guiobjs_set([obj], {obj: value})
    
    def guiobjs_set(self, objectslist, valuedict,
                    raw=False, name_mapper=None):
        """ set objects initail value"""
        self._set_values(objectslist, valuedict, raw=raw,
                         name_mapper=name_mapper)
        
    def _get_values(self, objectslist, raw=False, name_mapper=None):
        """ get gui object value"""
        objectlistvalue = {}

        if not isinstance(objectslist, list):
            objectslist = [objectslist]

        for obj_ in objectslist:
            obj_ins = getattr(self.gui, obj_)
            obj_type = obj_ins.__doc__.split("(")[0].split("Q")[1]
            obj_read = self.qt_mapper[obj_type]['read']
            if obj_read.startswith("self."):
                self.qt_working_obj = obj_ins
                read_method = obj_read.split("self.")[1]
                obj_value = getattr(self, read_method)(obj_ins)
                self.qt_working_obj = None
            else:
                obj_value = getattr(obj_ins, obj_read)()

            if raw:
                objectlistvalue[obj_] = obj_value
            else:
                if isinstance(obj_value, str):
                    objectlistvalue[obj_] = obj_value.strip()
                    if obj_value.strip() in [None, ""]:
                        objectlistvalue[obj_] = None
                else:
                    # checkbox will return Ture or False value
                    objectlistvalue[obj_] = obj_value

        if name_mapper is not None:
            mapvalue = {}
            for name in objectlistvalue:
                if name in name_mapper:
                    mapvalue[name_mapper[name]] = objectlistvalue[name]
                else:
                    mapvalue[name] = objectlistvalue[name]
            objectlistvalue = mapvalue
        return objectlistvalue

    def _set_values(self, objectslist, objectlistvalue, raw=False, name_mapper=None):
        """ set a value"""
        if not isinstance(objectslist, list):
            objlist = [objectslist]
        else:
            objlist = objectslist
        for obj_ in objlist:
            if isinstance(obj_, str):
                if name_mapper is None:
                    obj_ins = getattr(self.gui, obj_)
                else:
                    obj_ins = getattr(self.gui, name_mapper[obj_])
                self._qt_obj_set(obj_ins, objectlistvalue[obj_])
            else:
                self.log.debug("process combobox values")
                child_cb_name = obj_[1]
                parent_cb_name = obj_[0]
                if name_mapper is None:
                    obj_p = getattr(self.gui, parent_cb_name)
                    obj_c = getattr(self.gui, child_cb_name)
                else:
                    obj_p = getattr(self.gui, name_mapper[parent_cb_name])
                    obj_c = getattr(self.gui, name_mapper[child_cb_name])
                key0 = list(objectlistvalue[child_cb_name].keys())[0]
                self._qt_obj_set(obj_c, objectlistvalue[child_cb_name][key0])
                print(f"will check what is {obj_p} for, empty")
                print(f"need to check how to set {raw} data in the gui, empty")

    def _write_values(self, objectslist, objectslistvalue, raw=False, name_mapper=None):
        """write a value to gui objects"""
        for obj_ in objectslist:
            if isinstance(obj_, str):
                obj_ins = getattr(self.gui, obj_)
            else:
                obj_ins = getattr(self.gui, name_mapper[obj_])
            self._qt_obj_write(obj_ins, objectslistvalue[obj_])
        
    def _qt_obj_set(self, obj_, value):
        """ QA object set value"""
        obj_type = obj_.__doc__.split("(")[0].split("Q")[1]
        self.log.debug("Current Qt object %s type is %s", obj_, obj_type)
        obj_set = self.qt_mapper[obj_type]['set']
        # process objects
        if obj_set.startswith("self."):
            self.log.debug("%s is %s, will set value %s", obj_, obj_type, value)
            set_method = obj_set.split("self.")[1]
            getattr(self, set_method)(obj_, value)
        else:
            if isinstance(value, str):
                value = value
            else:
                value = ",".join(value)
            getattr(obj_, obj_set)(value)

    def _qt_obj_write(self, obj_, value):
        """ write obj value """
        obj_type = obj_.__doc__.split("(")[0].split("Q")[1]
        self.log.debug("Current Qt object %s type is %s", obj_, obj_type)
        if "write" not in self.qt_mapper[obj_type]:
            obj_write = self.qt_mapper[obj_type]['set']
        else:
            obj_write = self.qt_mapper[obj_type]['write']
        if obj_write.startswith("self."):
            self.log.debug("%s is %s, will set value %s", obj_, obj_type, value)
            set_method = obj_write.split("self.")[1]
            getattr(self, set_method)(obj_, value)
        else:
            if isinstance(value, str):
                value = value
            else:
                value = ",".join(value)
            getattr(obj_, obj_write)(value)

    def qt_combobox_pair(self):
        """ set combobox pair connection"""
        print('this is qt combobox pair process, empty now')
        pass

    def qt_comotox_link_initial(self, ins_, ins_c, value):
        """ comobox link change initial setting"""
        ins_.currentIndexChanged.connect(lambda: self.qt_comobox_link_change(ins_, ins_c, value))

    def qt_comobox_link_change(self, ins_, ins_c, value):
        """ comobox link change for all existing links"""
        parent_value = ins_.currentText()
        if parent_value in value:
            childvalue = value[parent_value]
        else:
            childvalue = []
        self.qt_combobox_set(ins_c, childvalue)

    @qtobj_check
    def qt_checkbox_read(self, obj_):
        """ read checkbox value"""
        return obj_.isChecked()

    @qtobj_check
    def qt_combobox_write(self, obj_, value):
        """ combobox write value"""
        v_index = obj_.findText(value, QtCore.Qt.MatchFixedString)
        if v_index >= 0:
            obj_.setCurrentIndex(v_index)

    @qtobj_check
    def qt_combobox_set(self, obj_, value):
        """ combobox instiial value set"""
        obj_.clear()
        for content in value:
            obj_.addItem(content)

    def qt_tablewidget_set(self, obj_, value):
        obj_.setColumnCount(value['column'])
        obj_.setRowCount(value['row'])
        obj_.setHorizontalHeaderLabels(value['header'])
        obj_.horizontalHeader().setStretchLastSection(True)
        obj_.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        
        obj_.resizeColumnsToContents()

        for line,value_ in enumerate(value['lines']):
            if isinstance(value_, str):
                value_ = [value_]
                
            if len(value_) != value['column']:
                for _ in range(len(value_),value['column']):
                    value_.append("no avlue")
    
            for count_ in range(value['column']):
                obj_.setItem(line ,count_, QTableWidgetItem(value_[count_]))

    def gui_debug(self, message):
        """ popup GUI debug windows"""
        QMessageBox.about(self, "GUI_Debug", message)


class GuiSimple(GuiQtBasic):
    """ This moduel is use to creater simple GUI application"""

    def __init__(self, Ui_mainWindow, appname, **kwargs):
        """initail GUI objects, load configure form default configure file
            configurefile
            appbasefolder
            are optional input
        """
        super().__init__(**kwargs)
        self.gui = Ui_mainWindow()
        self.winname = Ui_mainWindow.__name__[3:]
        self.gui.setupUi(self)
        self.appname = appname
        self.configure = {}
        self.tabs = []

        self._gui_initial(self.configurefile, self.appbasefolder)

    def _gui_initial(self, configurefile, appbasefolder):
        """ intial GUI """
        self._gui_configure(configurefile, appbasefolder)
        self._gui_objs_initial()

    def _gui_configure(self, configurefile, appbasefolder=None):
        """ read from configure files """
        self._gui_configurefile_load(configurefile, appbasefolder)
        # handle comobox initial
        # default combox entry come from list defined in configure file
        # if there is a relation (link) between two comobox items,
        # it will read qt_comobox_link to find the parent and child,
        # key is child, value is parent
        if "windows" in self.configure:
            self.log.debug(f"there is multiple windows, run configure")
            self._gui_configure_window(self.configure[self.winname])
        else:                
            self._gui_configure_window(self.configure)

    def _gui_configurefile_load(self, configurefile, appbasefolder):
        """ load configure from configure file """
        # save default configure for future usage
        self.log.debug("Configure file for app %s is %s", self.appname, configurefile)
        if self.appbasefolder is None:
            appbasefolder = f"./{self.appname}/"
            if self.configurefile is None:
                configurefile = os.path.join(appbasefolder, "config.json")
            else:
                configurefile = self.configurefile
        else:
            if self.configurefile is None:
                configurefile = os.path.join(appbasefolder, "config.json")
        if os.path.isfile(configurefile):
            with open(configurefile) as fhandle:
                config = json.load(fhandle)['gui']
        else:
            config = {}
        self._gui_mapper(config)
        self.configure = config
        self.log.debug("Configure content is %s", self.configure)

    def _gui_mapper(self, config):
        """create tab options and map special QT objects"""
        if config != {}:
            self.log.debug("start to initial configure file value")
            if "windows" in config:
                self.log.debug(f"There are multiple windows,{config['windows']}")
                for _ in config['windows']:
                    self.log.debug(f"initial map windows {_}")
                    self._gui_mapper_window(config[_])
            else: 
                self.log.debug("There is only one main windows")
                self._gui_mapper_window(config)
        else:
            print("will repalce with error handle, empty")

    def _gui_mapper_window(self, config):
        """ configure single windows"""
        if "tabs"  not in config:
            self.log.debug("This window doesn't have tab")
        else:
            self.log.debug(f"There are mutliple tabs {config['tabs']}")
            self.tabs = config['tabs']
            for tab in self.tabs:
                if tab in config.keys():
                    config_entries = config[tab]['entries']
                    if "entries_type" in config[tab]:
                        config_entries_type = config[tab]['entries_type']
                    else:
                        config_entries_type = {}
                else:
                    config_entries = []
                    config_entries_type = {}
                setattr(self, f"{tab}_entries", config_entries)
                setattr(self, f"{tab}_entries_type", config_entries_type)

    def _gui_configure_window(self, config):
        """ configure the gui in the windows"""
        if "qt_combobox" in config:
            self._gui_configure_combobox(config)
        # set intiail value for the textline input
        if config != {}:
            self._gui_configure_tabs()

    def _gui_configure_tabs(self):
        """ load tabs in gui """
        if "windows" in self.configure:
            self.log.debug("there are multiple windows, will initial tabs for each windows")
            self._gui_configure_tabs_window(self.configure[self.winname])
        else:
            self.log.debug("There is only one window, initial tabs")
            self._gui_configure_tabs_window(self.configure)

    def _gui_configure_tabs_window(self, config):
        """ configure tab in side a windows"""
        if "tabs" in config:
            initabs = []
            for tab in config:
                if tab not in ["qt_combobox", 'qt_combobox_link','tabs']:
                    initabs.append(tab)
            for tab in initabs:
                self.log.debug(f"start to configure windows tab {tab} ")
                if "entries_type" in config[tab]:
                    self.log.debug(f"entires type detected, will initial objects values")
                    if tab != "Main":
                        objlist = [f"{tab.lower()}_{_}" \
                                   for _ in config[tab]['entries_type'].keys()]
                        objlist_ori = list(config[tab]['entries_type'].keys())
                    else:
                        objlist = list(config[tab]['entries_type'].keys())
                        objlist_ori = list(objlist)                        
                    self.log.debug(f"will process the following objects: {objlist}")
                    objvalue = {}
                    for ind_, obj_ in enumerate(objlist):
                        if config[tab]['entries_type'][objlist_ori[ind_]] == "ComboBox":
                            if obj_ in config["qt_combobox"]:
                                objvalue[obj_] = config["qt_combobox"][obj_]
                            else:
                                self.log.debug("no combobox initifalvalue passed")
                                objvalue[obj_] = []
                        else:
                            print('type is not comboxbox, skilp for now,empty')
                            objvalue[obj_] = ""
                    self.log.debug(f"objects list: {objlist} have the following values:\n {objvalue}")
                    self.guiobjs_set(objlist,objvalue)
                    self.log.debug(f"entries type completed for tab {tab}")
                                 
                if "entries_value" in config[tab]:
                    self.log.debug(f"entires value detected, will set the objects value")
                    if tab != "Main":
                        objlist = [f"{tab.lower()}_{_}" \
                                   for _ in config[tab]['entries_value'].keys()]
                        objlist_ori = list(config[tab]['entries_value'].keys())
                    else:
                        objlist = config[tab]['entries_value'].keys()
                        objlist_ori = list(objlist)                        
                    objvalue = {}
                    for ind_, obj_ in enumerate(objlist):
                        objvalue[obj_] = config[tab]['entries_value'][objlist_ori[ind_]]
                    self.log.debug(f"objects list: {objlist} have the following values:\n {objvalue}")
                    self.guiobjs_write(objlist, objvalue)
                    self.log.debug(f"entries value completed for tab {tab}")
                else:
                    self.log.debug(f"no configure found in this tab {tab}")
        else:
            self.log.debug("no tabs in this windows")

    def _gui_configure_combobox(self, config):
        """ load combobox in gui """
        self.log.debug("There are combobox found in config file. Will initial it")
        for combobox_ in config['qt_combobox'].keys():
            self.log.debug(f"initial combobox {combobox_}")
            cb_ins_ = getattr(self.gui, combobox_)
            # there is link between parent and child comobox objects
            if isinstance(config['qt_combobox'][combobox_], dict):
                # get parent obj name first
                print(config)
                print(combobox_)
                combobox_parent_name = config['qt_combobox_link'][combobox_]
                # set child value first
                # use the first one as default value
                combobox_child_first_name = list(config['qt_combobox'][combobox_].keys())[0]
                combobox_child_first_value =\
                    config['qt_combobox'][combobox_][combobox_child_first_name]
                cb_ins_child_ = getattr(self.gui, combobox_)
                self.qt_combobox_set(cb_ins_child_, combobox_child_first_value)
                # set parent and assign value
                cb_ins_parent_ = getattr(self.gui, combobox_parent_name)
                self.qt_combobox_set(cb_ins_parent_,
                                     config['qt_combobox'][combobox_parent_name])
                self.qt_combobox_write(cb_ins_parent_,
                                       combobox_child_first_name)

                value = config['qt_combobox'][combobox_]
                self.qt_comotox_link_initial(cb_ins_parent_,
                                             cb_ins_child_, value)
                #    associated the combobox object change to a action.
            elif isinstance(config['qt_combobox'][combobox_], list):
                self.qt_combobox_set(cb_ins_,
                                     config['qt_combobox'][combobox_])
            else:
                # should log this line for future, nothing will happened
                print("comobox entry type is not valid, emtpy")

    def _gui_objs_initial(self):
        """ intiial GUI basic ojects"""
        if "qt_objs" in self.configure:
            for obj_name in self.configure['qt_objs']:
                obj_ = getattr(self.gui, obj_name)
                obj_.setText(self.configure[obj_name])

    def _gui_tab_set(self, tabname, information):
        """ initial tab object and set values """
        tabentries = getattr(self, f"{tabname}_entries")
        tabentries_type = getattr(self, f"{tabname}_entries_type")

        for itemname in tabentries:
            insname = "{0}_{1}".format(tabname, itemname)
            ins_ = getattr(self.gui, insname)
            try:
                itemvalue = information[itemname]
            except KeyError:
                itemvalue = None
            if itemname not in tabentries_type.keys():  # regular txt field
                ins_.setText(itemvalue)
            else:
                # special handle for different Qt objects
                qt_obj_type = tabentries_type[itemname]
                if qt_obj_type == "ComboBox":
                    obj_index = ins_.findText(itemvalue,
                                              QtCore.Qt.MatchFixedString)
                    if obj_index >= 0:
                        ins_.setCurrentIndex(obj_index)
                    else:
                        print("value is not valid,empty")
                elif qt_obj_type == "TextEdit":
                    pass
                else:
                    print(f"QT tyep {qt_obj_type} is not define in tab set, empty")

    def _gui_tab_read(self, tabname):
        """ read values form different tabs"""
        information = {}
        tabentries = getattr(self, f"{tabname}_entries")
        tabentries_type = getattr(self, f"{tabname}_entries_type")

        for itemname in tabentries:
            insname = "{0}_{1}".format(tabname, itemname)
            ins_ = getattr(self.gui, insname)
            if itemname not in tabentries_type.keys():
                information[itemname] = ins_.text()
            else:
                qt_obj_type = tabentries_type[itemname]
                qt_obj_read = self.qt_mapper[qt_obj_type]['read']
                if qt_obj_type == "ComboBox":
                    information[itemname] = ins_.currentText()
                else:
                    information[itemname] = getattr(ins_, qt_obj_read)()
        return information
