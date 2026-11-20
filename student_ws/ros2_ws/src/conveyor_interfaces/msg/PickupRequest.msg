# What the controller asks the pickup actuator to do next.
# The controller node sends one with every joint-velocity command.
# A request is used once: "pick" starts a pickup only when the actuator is
# idle, and "release" only when it is holding an object.

string HOLD="hold"
string PICK="pick"
string RELEASE="release"

std_msgs/Header header  # stamp: simulated time of the observation it answers
string request          # HOLD, PICK, or RELEASE
