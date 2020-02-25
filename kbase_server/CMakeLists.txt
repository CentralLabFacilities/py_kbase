cmake_minimum_required(VERSION 2.8.3)
project(py_kbase)

## Catkin
find_package(catkin REQUIRED COMPONENTS
  rospy
)

catkin_python_setup()

catkin_package(
   CATKIN_DEPENDS rospy
)

include_directories(${catkin_INCLUDE_DIRS})

install(DIRECTORY launch DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION})

catkin_install_python(PROGRAMS src/py_kbase/server.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION})

CATKIN_INSTALL_PYTHON(PROGRAMS ${CMAKE_CURRENT_SOURCE_DIR}/src/py_kbase/server.py DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION})
