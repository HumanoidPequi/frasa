cmake_minimum_required(VERSION 3.0.2)
project(martha_controller)

## Find catkin macros and libraries
find_package(catkin REQUIRED COMPONENTS
  message_generation
  roscpp
  rospy
  std_msgs
  trajectory_msgs
  marta_msgs
  genmsg
  actionlib_msgs
  actionlib
)

catkin_package(
  CATKIN_DEPENDS roscpp rospy std_msgs trajectory_msgs
)

include_directories(
  ${catkin_INCLUDE_DIRS}
)

## Install Python scripts
catkin_install_python(PROGRAMS
  scripts/kick_controller.py
  scripts/taffarelAction.py  
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

