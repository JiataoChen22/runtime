#pragma once

#include <string>
#include <map>

namespace runtime {

    class AbstractGenerated;
    class RObject;

    using std::string;
    using std::map;

    class ClassFactory {
        static ClassFactory sInstance;

        ClassFactory();
        ~ClassFactory();

    public:
        ClassFactory(const ClassFactory &) = delete;
        ClassFactory &operator=(const ClassFactory &) = delete;

        ClassFactory(ClassFactory &&) = delete;
        ClassFactory &operator=(ClassFactory &&) = delete;

        static ClassFactory *getInstance();

        void registerClass(const string &name, AbstractGenerated *clazz);

        static const AbstractGenerated *getClassInfo(const string &name);
        static RObject *fromClass(const string &name);

    private:
        [[nodiscard]] const AbstractGenerated *getAbstractGenerated(const string &name) const;
        RObject* newInstance(const string &name);

    private:
        map<string, AbstractGenerated *> mClassMap;
    };

#define RCLASS(...)
#define RFIELD(...)
#define RMETHOD(...)

#define GENERATED_BODY(Class) \
    friend class runtime::Class##_Generated;

} // runtime

