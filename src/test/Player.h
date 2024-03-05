#pragma once

#include <string>

#include "../runtime/ClassFactory.h"
#include "../runtime/RObject.h"

#include <Player.generated.h>

RCLASS()
class Player : public runtime::RObject {

    GENERATED_BODY(Player)

private:
    RFIELD()
    int mId;

    RFIELD()
    std::string mName;
};

