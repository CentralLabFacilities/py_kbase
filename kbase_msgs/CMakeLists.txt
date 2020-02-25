cmake_minimum_required(VERSION 2.8.3)
project(py_kbase_msgs)

## Catkin
find_package(catkin REQUIRED COMPONENTS
  message_generation
  std_msgs
  geometry_msgs
)

add_message_files(FILES
  Location.msg
  Viewpoint.msg
  Person.msg
  Object.msg
  KBaseReturnStatus.msg
  Gender.msg
  ObjectCategory.msg
  State.msg
)

add_service_files(
  FILES
  Dump.srv
  DataOperation.srv
)

generate_messages(DEPENDENCIES
  std_msgs
  geometry_msgs
)

catkin_package(CATKIN_DEPENDS
  message_runtime
  std_msgs
  geometry_msgs
)
