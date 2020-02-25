#!/usr/bin/env python

import rospy
import argparse
import os
import sys
from yaml import load, dump, FullLoader
from py_kbase_msgs.msg import *
from py_kbase_msgs.srv import DataOperation, DataOperationRequest, DataOperationResponse, \
    Dump, DumpRequest, DumpResponse

DEFAULT_TMP_LOC = '/tmp/py_kbase.tmpdb'


def _write_database_to_file(filepath, database):
    with open(filepath, 'w') as out_file:
        dump(database, out_file)


def _read_database_from_file(filepath):
    rospy.logdebug("Loading database from path %s" % filepath)
    with open(filepath, 'r') as in_file:
        return load(in_file, Loader=FullLoader)


class DBServer():
    def __init__(self, filepath, resume):

        rospy.init_node('py_kbase')
        self.database = {'Locations': {}, 'Viewpoints': {}, 'Persons': {}, 'Objects': {}}

        if filepath:
            if os.path.isfile(filepath):
                self.database = _read_database_from_file(filepath)
            else:
                sys.exit(KBaseReturnStatus.FILE_NOT_FOUND)
        elif resume:
            if os.path.isfile(DEFAULT_TMP_LOC):
                self.database = _read_database_from_file(DEFAULT_TMP_LOC)
                rospy.loginfo("Resumed last temp state")
            else:
                rospy.logwarn("Temp file for resuming not found. Starting with empty kbase")

        rospy.Service('KBase/Save', DataOperation, self.handle_save_call)
        rospy.Service('KBase/Delete', DataOperation, self.handle_delete_call)
        rospy.Service('KBase/Dump', DataOperation, self.handle_dump_call)

        self.state_publisher = rospy.Publisher('KBase/state', State, queue_size=1, latch=True)
        self.pub_state()

        rospy.loginfo("KBase up and running!")

    def pub_state(self):
        state = State()
        for entry in self.database.get('Locations'):
            state.locations.append(self.database.get('Locations').get(entry))
        for entry in self.database.get('Viewpoints'):
            state.viewpoints.append(self.database.get('Viewpoints').get(entry))
        for entry in self.database.get('Objects'):
            state.objects.append(self.database.get('Objects').get(entry))
        for entry in self.database.get('Persons'):
            state.persons.append(self.database.get('Persons').get(entry))

        self.state_publisher.publish(state)

    def handle_dump_call(self, req):
        dirname = os.path.dirname(req.filepath)
        if not os.path.exists(dirname):
            rospy.logerr("Path '%s' does not exist!" % dirname)
            return DumpResponse(KBaseReturnStatus.INVALID_PATH)
        _write_database_to_file(req.filepath, self.database)
        rospy.logdebug("Saved database to file: %s" % req.filepath)
        return DumpResponse(KBaseReturnStatus.OK)

    def handle_delete_call(self, req):
        """
        " Delete entities from database.

        :param req: Request with entities to delete
        :type req: DataOperationRequest

        :return: Response with status code
        :rtype: DataOperationResponse "
        """
        rospy.logdebug("Handling delete call")
        for loc in req.state.locations:
            self.database['Locations'].pop(loc.name, None)
        for view_p in req.state.viewpoints:
            self.database['Viewpoints'].pop(view_p.name, None)
        for obj in req.state.objects:
            self.database['Objects'].pop(obj.name, None)
        for pers in req.state.persons:
            self.database['Persons'].pop(pers.name, None)

        _write_database_to_file(DEFAULT_TMP_LOC, self.database)
        self.pub_state()
        return DataOperationResponse(return_value=KBaseReturnStatus(KBaseReturnStatus.OK))

    def handle_save_call(self, req):
        """
        " Save new entities to database.

        :param req: Request with new entities to save
        :type req: DataOperationRequest

        :return: Response with status code
        :rtype: DataOperationResponse "
        """
        rospy.logdebug("Handling save call")
        for loc in req.state.locations:
            self.database['Locations'][loc.name] = loc
        for view_p in req.state.viewpoints:
            if view_p.parent not in self.database.get('Locations'):
                rospy.logwarn("Parent location '%s' is unknown!" % view_p.parent)
            self.database['Viewpoints'][view_p.name] = view_p
        for obj in req.state.objects:
            if obj.default_loc not in self.database.get('Locations'):
                rospy.logwarn("Default location '%s' is unknown!" % obj.default_loc)
            self.database['Objects'][obj.name] = obj
        for pers in req.state.persons:
            self.database['Persons'][pers.name] = pers

        _write_database_to_file(DEFAULT_TMP_LOC, self.database)
        self.pub_state()
        return DataOperationResponse(return_value=KBaseReturnStatus(KBaseReturnStatus.OK))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    mutex_g = parser.add_mutually_exclusive_group(required=False)
    mutex_g.add_argument('-f', '--file', help='Set path to database to load.', dest='file_path')
    mutex_g.add_argument('--resume', help="Enable resuming last tmpdb save.", action='store_true')

    args = parser.parse_args()
    DBServer(args.file_path, args.resume)
    rospy.spin()
