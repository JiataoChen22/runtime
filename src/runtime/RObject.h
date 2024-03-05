#pragma once

#include <string>
#include <stdexcept>
#include <fmt/format.h>

#include "AbstractGenerated.h"
#include "ClassFactory.h"

namespace runtime {

    using std::string;

    class RObject {

    public:
        RObject() = default;
        virtual ~RObject() = default;

        [[nodiscard]] const string &getClassName() const;

        template<class T>
        T &getField(const string &name) {
            auto classInfo = ClassFactory::getClassInfo(mClassName);

            if (classInfo == nullptr)
                throw std::runtime_error(fmt::format("Class-{} could not find reflect info!", mClassName));

            auto field = classInfo->getField(name);
            return *reinterpret_cast<T *>(reinterpret_cast<size_t>(this + field->offset));
        }

        template<class T>
        void setField(const string &name, T &&value) {
            auto classInfo = ClassFactory::getClassInfo(mClassName);

            if (classInfo == nullptr)
                throw std::runtime_error(fmt::format("Class-{} could not find reflect info!", mClassName));

            auto field = classInfo->getField(name);
            *reinterpret_cast<T *>(reinterpret_cast<size_t>(this + field->offset)) = std::forward<T>(value);
        }

        template<class RT, class... Args>
        RT invoke(const string &name, Args &&... args) {
            auto classInfo = ClassFactory::getClassInfo(mClassName);

            if (classInfo == nullptr)
                throw std::runtime_error(fmt::format("Class-{} could not find reflect info!", mClassName));

            auto method = classInfo->getMethod(name);
            auto &func = *reinterpret_cast<std::function<RT(RObject *, Args...)> *>(method->ptr);
            return func(this, std::forward<Args>(args)...);
        }

    protected:
        string mClassName;
    };

} // runtime
