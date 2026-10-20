cmake_minimum_required(VERSION 3.8)
project(r2d2_demo)

find_package(ament_cmake REQUIRED)

install(DIRECTORY launch rviz urdf DESTINATION share/${PROJECT_NAME})

ament_package()
