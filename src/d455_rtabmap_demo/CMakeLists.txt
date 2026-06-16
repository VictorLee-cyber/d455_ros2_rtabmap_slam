cmake_minimum_required(VERSION 3.8)
project(d455_rtabmap_demo)

find_package(ament_cmake REQUIRED)

install(DIRECTORY
  launch
  config
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS
  scripts/check_usb3.sh
  scripts/save_rtabmap_db.sh
  scripts/open_rtabmap_db.sh
  scripts/save_2d_map.sh
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
