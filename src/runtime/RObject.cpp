#include "RObject.h"

namespace runtime {
    const string &RObject::getClassName() const {
        return mClassName;
    }
} // runtime