#include "ClassFactory.h"
#include "AbstractGenerated.h"

namespace runtime {
    ClassFactory ClassFactory::sInstance;

    ClassFactory::ClassFactory() {}

    ClassFactory::~ClassFactory() {}

    ClassFactory *ClassFactory::getInstance() {
        return &sInstance;
    }

    void ClassFactory::registerClass(const string &name, AbstractGenerated *clazz) {
        mClassMap.insert_or_assign(name, clazz);
    }

    const AbstractGenerated *ClassFactory::getAbstractGenerated(const string &name) const {
        auto it = mClassMap.find(name);
        if (it != mClassMap.end())
            return it->second;
        return nullptr;
    }

    RObject *ClassFactory::newInstance(const string &name) {
        auto it = mClassMap.find(name);
        if (it != mClassMap.end())
            return it->second->newInstance();
        return nullptr;
    }

    const AbstractGenerated *ClassFactory::getClassInfo(const string &name) {
        return sInstance.getAbstractGenerated(name);
    }

    RObject *ClassFactory::fromClass(const string &name) {
        return sInstance.newInstance(name);
    }
} // runtime