#pragma once

#include <string>
#include <map>
#include <vector>
#include <functional>

namespace runtime {

    using std::string;
    using std::map;
    using std::vector;
    using std::function;

    using AttributeMap = map<string, string>;

    struct ClassField {
        string name;
        string type;
        uint64_t offset;
        AttributeMap attrs;
    };

    struct ClassMethod {
        string name;
        string returnType;
        vector<string> argsType;
        uintptr_t ptr;
        AttributeMap attrs;
    };

    class AbstractGenerated {
    protected:
        explicit AbstractGenerated(string className, AttributeMap attrs = {});
        virtual ~AbstractGenerated();

    public:
        AbstractGenerated(const AbstractGenerated &) = delete;
        AbstractGenerated &operator=(const AbstractGenerated &) = delete;

        AbstractGenerated(AbstractGenerated &&) = delete;
        AbstractGenerated &operator=(AbstractGenerated &&) = delete;

        virtual class RObject *newInstance() = 0;

        [[nodiscard]] const ClassField *getField(const string &name) const;
        [[nodiscard]] const ClassMethod *getMethod(const string &name) const;

        [[nodiscard]] const AttributeMap &getAttrs() const;

        void foreachField(const function<bool(const ClassField *)> &func) const;
        void foreachMethod(const function<bool(const ClassMethod *)> &func) const;

        [[nodiscard]] std::pair<bool, string> getAttribute(const string &name) const;

    protected:
        string mClassName;
        AttributeMap mAttrs;
        map<string, ClassField *> mFieldMap;
        map<string, ClassMethod *> mMethodMap;
    };

#define stringify(...) #__VA_ARGS__

#define attribute_box(...) __VA_ARGS__

#define args_box(...) __VA_ARGS__

#define methodDeclared(className, methodName, returnType, args) \
    std::function<returnType(className*, Args)> m_##methodName##_func;

#define methodDeclaredNoneParam(className, methodName, returnType) \
    std::function<returnType(className*)> m_##methodName##_func;

#define addField(clazz, field, type, attr) \
    mFieldMap.insert(std::make_pair<std::string, ClassField *>( \
        #field, new ClassField { #field, #type, offsetof(clazz, field), {attr} }));

#define addMethod(clazz, method, returnType, args, attr) \
    { \
        m_##method##_func = &clazz::method; \
        mMethodMap.insert(std::make_pair<std::string, ClassMethod *>( \
            #method, {#method, #returnType, reinterpret_cast<uintptr_t>(&m_##method##_func), {args}, {attr}})); \
    } \

} // runtime
