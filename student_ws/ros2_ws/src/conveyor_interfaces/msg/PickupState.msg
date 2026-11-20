# Phase of the timed pickup actuator, published by the simulator every
# control period. Lowering and lifting take fixed times (scenario [pickup]);
# a pickup succeeds only if the tool is close to an object and moving with
# it when lowering ends.

string IDLE="idle"
string LOWERING="lowering"
string LIFTING="lifting"
string HOLDING="holding"
string RELEASING="releasing"

std_msgs/Header header  # stamp: simulated time
string phase            # one of the constants above
