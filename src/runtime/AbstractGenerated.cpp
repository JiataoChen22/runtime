#include "AbstractGenerated.h"

#include <stdexcept>
#include <fmt/format.h>

namespace runtime {
    AbstractGenerated::AbstractGenerated(string className, AttributeMap attrs)
            : mClassName(std::move(className)),
              mAttrs(std::move(attrs)) {

    }

    AbstractGenerated::~AbstractGenerated() {
        for (auto &element: mFieldMap)
            delete element.second;
        for (auto &element: mMethodMap)
            delete element.second;
    }

    const ClassField *AbstractGenerated::getField(const string &name) const {
        auto iter = mFieldMap.find(name);
        if (iter != mFieldMap.end())
            return iter->second;
        throw std::runtime_error(fmt::format("Field-{} not found in class-{}", name, mClassName));
    }

    const ClassMethod *AbstractGenerated::getMethod(const string &name) const {
        auto iter = mMethodMap.find(name);
        if (iter != mMethodMap.end())
            return iter->second;
        throw std::runtime_error(fmt::format("Method-{} not found in class-{}", name, mClassName));
    }

    const AttributeMap &AbstractGenerated::getAttrs() const {
        return mAttrs;
    }

    void AbstractGenerated::foreachField(const function<bool(const ClassField *)> &func) const {
        for (auto &element: mFieldMap)
            if (func(element.second))
                break;
    }

    void AbstractGenerated::foreachMethod(const function<bool(const ClassMethod *)> &func) const {
        for (auto &element: mMethodMap)
            if (func(element.second))
                break;
    }

    std::pair<bool, string> AbstractGenerated::getAttribute(const string &name) const {
        auto iter = mAttrs.find(name);
        if (iter != mAttrs.end())
            return {true, iter->second};
        return {false, ""};
    }
} // runtime