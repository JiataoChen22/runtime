import os
import json
import datetime

PROJECT_NAME = 'demo'

TARGET_DIR = 'E:\\ClionProjects\\runtime\\src\\test'
GENERATED_DIR = 'E:\\ClionProjects\\runtime\\generated\\'

REPLACE_DIR = ['E:/ClionProjects/runtime', '..']

# 反射标识
RCLASS  = 'RCLASS'
RFIELD  = 'RFIELD'
RMETHOD = 'RMETHOD'

# C++宏定义
args_box      = 'args_box'
attribute_box = 'attribute_box'
stringify     = 'stringify'

method_declare            = 'methodDeclared'
method_declare_none_param = 'methodDeclaredNoneParam'

date_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 分割C++代码
def cplusplus_split(line: str, split_word = ' ') -> list:
    line = line.strip()
    if line.endswith(';'):
        line = line[:-1]

    left_bracket = 0
    left_arrow = 0

    res = []
    last_idx = 0
    for i, c in enumerate(line):
        if c == '<':
            left_bracket += 1
        elif c == '>':
            left_bracket -= 1
        elif c == '(':
            left_arrow += 1
        elif c == ')':
            left_arrow -= 1
        elif c == split_word and left_bracket == 0 and left_arrow == 0:
            temp = line[last_idx:i]
            if '=' in temp and len(temp) > 1:
                idx = temp.index('=')
                res.append(temp[:idx])
                res.append('=')
                res.append(temp[idx + 1:])
            else:
                res.append(temp)

            last_idx = i + 1
    
    temp = line[last_idx:]
    if '=' in temp:
        idx = temp.index('=')
        res.append(temp[:idx])
        res.append('=')
        res.append(temp[idx + 1:])
    else:
        res.append(temp)

    return res

# 解析类的属性
def parse_property(line: str) -> dict:
    if line.endswith(';'):
        line = line[:-1]

    temp = cplusplus_split(line)

    property_info = {}

    if temp[0] == 'static':
        raise Exception('static property is not supported')

    if temp[0] == 'const':
        property_info['const'] = True
        temp = temp[1:]

    property_info['type'] = temp[0]
    property_info['name'] = temp[1]

    # 默认值
    if len(temp) > 3 and temp[2] == '=':
        property_info['default_value'] = temp[3]

    return property_info    

# 解析类的函数
def parse_function(line: str) -> dict:
    line = line.strip()
    if line.endswith(';') or line.endswith('{'):
        line = line[:-1]

    temp = cplusplus_split(line)

    left_bracket = temp[-1].index('(')
    right_bracket = temp[-1].rindex(')')

    # 分割参数签名
    args = cplusplus_split(temp[-1][left_bracket + 1:right_bracket], ',')
    temp[-1] = temp[-1][:left_bracket]

    function_info = {}
    function_info['args'] = []

    if temp[0] == '[[nodiscard]]' or temp[0] == '_NODISCARD':
        temp = temp[1:]

    if temp[0] == 'static':
        raise Exception('static function is not supported')

    # 解析返回类型
    if temp[0] == 'const':
        function_info['return_type'] = 'const ' + temp[1]
        temp = temp[1:]
    else:
        function_info['return_type'] = temp[0]

    if temp[1].startswith('*'):
        function_info['return_type'] += ' *'
        temp[1] = temp[1][1:]
    elif temp[1].startswith('&'):
        function_info['return_type'] += ' &'
        temp[1] = temp[1][1:]
        
    # 函数名    
    function_info['name'] = temp[1]

    # 解析参数
    for arg_str in args:
        arg_type = ''
        arg = cplusplus_split(arg_str)

        if arg[0] == 'const':
            arg_type = 'const ' + arg[1]
            arg = arg[1:]
        else:
            arg_type = arg[0]

        if arg_type.endswith('*') or arg_type.endswith('&'):
            arg_type = arg_type[:-1] + ' ' + arg_type[-1:]    

        if len(arg) > 1:
            if arg[1].startswith('*'):
                arg_type += ' *'
            elif arg[1].startswith('&'):
                arg_type += ' &'

        function_info['args'].append(arg_type)

    return function_info        

class_list = []

for root, dirs, files in os.walk(TARGET_DIR):
    for file in files:
        if not file.endswith('.h') and not file.endswith('.hpp'):
            continue

        class_info = {}

        class_info['properties'] = []
        class_info['functions'] = []

        is_reflection = False
        
        with open(os.path.join(root, file), 'r', encoding='utf-8') as file:
            line = file.readline()
            while line:
                line = line.strip()

                if not is_reflection and line.startswith(RCLASS):
                    is_reflection = True

                    class_info['source_file'] = os.path.join(root, file.name).replace('\\', '/')
                    
                    # 获取类特性
                    attrs = line[7:-1].split(',')
                    class_info['class_attr'] = {}
                    for attr in attrs:
                        attr = attr.strip()
                        if attr != '':
                            if '=' in attr:
                                attr = attr.split('=')
                                class_info['class_attr'][attr[0].strip()] = attr[1].strip()
                            else:
                                class_info['class_attr'][attr.strip()] = 'true'
                        
                    line = file.readline()
                    
                    # 获取类名
                    tmp = line.split(' ')
                    colon_idx = tmp.index(':')
                    class_info['class_name'] = tmp[colon_idx - 1]

                if is_reflection and line.startswith(RFIELD):
                    # 获取属性特性
                    line = line[7:-1].split(',')
                    property_attr = {}
                    for attr in line:
                        attr = attr.strip()
                        if attr != '':
                            if '=' in attr:
                                attr = attr.split('=')
                                property_attr[attr[0].strip()] = attr[1].strip()  
                            else:
                                property_attr[attr.strip()] = 'true'

                    line = file.readline()
                    temp = parse_property(line)
                    temp['property_attr'] = property_attr

                    class_info['properties'].append(temp)

                if is_reflection and line.startswith(RMETHOD):
                    # 获取函数特性
                    function_attr = {}
                    temp = line[8:-1]
                    if temp != '':
                        temp = temp.split(',')
                        for attr in temp:
                            attr = attr.strip()
                            if attr != '':
                                if '=' in attr:
                                    attr = attr.split('=')
                                    function_attr[attr[0].strip()] = attr[1].strip()
                                else:
                                    function_attr[attr.strip()] = 'true'
                    
                    line = file.readline()
                    temp = parse_function(line)
                    temp['function_attr'] = function_attr

                    class_info['functions'].append(temp)    

                line = file.readline()

        if is_reflection:
            class_list.append(class_info)

for class_info in class_list:
    # 生成类的头文件
    with open(os.path.join(GENERATED_DIR, class_info['class_name'] + '.generated.h'), 'w', encoding='utf-8') as file:
        file.write('// This file is generated by script. Do not edit!\n')
        file.write('// Source file: %s\n' % class_info['source_file'].replace('\\', '/'))
        file.write('// Generated at: %s\n\n' % date_str)

        file.write('#pragma once\n\n')
        file.write('#include "../src/runtime/AbstractGenerated.h"\n\n')

        # 前向声明
        file.write('class %s;\n\n' % class_info['class_name'])

        file.write('namespace runtime {\n')
        # 类声明
        file.write('\tclass %s_Generated : public AbstractGenerated {\n' % class_info['class_name'])
        # 生成类单例声明
        file.write('\t\tstatic %s_Generated sInstance;\n' % class_info['class_name'])

        file.write('\tpublic:\n')
        file.write('\t\texplicit %s_Generated(const std::string &className, AttributeMap attrs = {});\n' % class_info['class_name'])
        file.write('\t\t~%s_Generated() override;\n' % class_info['class_name'])
        file.write('\t\tstatic %s_Generated *getInstance();\n' % class_info['class_name'])
        file.write('\t\tRObject *newInstance() override;\n')
        file.write('\tprivate:\n')

        for func in class_info['functions']:
            if len(func['args']) > 0:
                file.write('\t\t%s(%s, %s, %s, %s(%s))\n' % (
                    method_declare,
                    class_info['class_name'],
                    func['name'],
                    func['return_type'],
                    args_box,
                    ', '.join([arg for arg in func['args']])
                ))
            else:
                file.write('\t\t%s(%s, %s, %s)\n' % (
                    method_declare_none_param,
                    class_info['class_name'],
                    func['name'],
                    func['return_type']
                ))

        file.write('\t};\n')
        file.write('} // runtime\n\n')

    # 生成类的实现文件
    with open(os.path.join(GENERATED_DIR, class_info['class_name'] + '.generated.cpp'), 'w', encoding='utf-8') as file:
        file.write('// This file is generated by script. Do not edit!\n')
        file.write('// Source file: %s\n' % class_info['source_file'])
        file.write('// Generated at: %s\n\n' % date_str)

        file.write("#include \"%s.generated.h\"\n" % class_info['class_name'])
        file.write("#include \"../src/runtime/RObject.h\"\n\n")
        file.write("#include \"%s\"\n\n" % class_info['source_file'].replace(REPLACE_DIR[0], REPLACE_DIR[1]))
        file.write("#include <utility>\n\n")

        file.write('namespace runtime {\n')

        # 初始化单例
        attr_str = ''
        for key, value in class_info['class_attr'].items():
            attr_str += ', {\"%s\", \"%s\"}' % (key, value)
        if len(attr_str) > 0:
            attr_str = attr_str[2:]    
        file.write('\t%s_Generated %s_Generated::sInstance("%s", {%s});\n\n' % 
                   (class_info['class_name'], class_info['class_name'], class_info['class_name'], attr_str))

        # 在构造函数注册
        file.write('\t%s_Generated::%s_Generated(const std::string &className, AttributeMap attr)\n' % (class_info['class_name'], class_info['class_name']))
        file.write('\t        : AbstractGenerated(className, std::move(attr)) {\n\n')

        file.write('\t\t// Register properties\n')
        for prop in class_info['properties']:
            prop_attr_str = ''
            for key, value in prop['property_attr'].items():
                prop_attr_str += ', {\"%s\", \"%s\"}' % (key, value)
            if len(prop_attr_str) > 0:
                prop_attr_str = prop_attr_str[2:]    
            
            file.write('\t\taddField(%s, %s, %s, %s(%s))\n' % (
                class_info['class_name'],
                prop['name'],
                prop['type'],
                attribute_box,
                prop_attr_str
            ))

        file.write('\n\t\t// Register functions\n')
        for func in class_info['functions']:
            func_attr_str = ''
            for key, value in func['function_attr'].items():
                func_attr_str += ', {\"%s\", \"%s\"}' % (key, value)
            if len(func_attr_str) > 0:
                func_attr_str = func_attr_str[2:]
            
            func_args_str = ''
            if len(func['args']) > 0:
                func_args_str = ', '.join([('%s(%s)' % (stringify, arg)) for arg in func['args']])

            file.write('\t\taddMethod(%s, %s, %s, %s(%s), %s(%s))\n' % (
                class_info['class_name'],
                func['name'],
                func['return_type'],
                args_box,
                func_args_str,
                attribute_box,
                func_attr_str
            ))

        file.write('\n\t\t// Register this class to ClassFactory\n')
        file.write('\t\tClassFactory::getInstance()->registerClass(mClassName, this);\n')

        file.write("\t}\n\n")

        # 生成类剩余实现
        file.write('\t%s_Generated::~%s_Generated() {\n\n' % (class_info['class_name'], class_info['class_name']))
        file.write('\t}\n\n')

        file.write('\tRObject *%s_Generated::newInstance() {\n' % class_info['class_name'])
        file.write('\t\tauto *obj = new %s();\n' % class_info['class_name'])
        file.write('\t\tobj->mClassName = mClassName;\n')
        file.write('\t\treturn obj;\n')
        file.write('\t}\n\n')

        file.write("\t%s_Generated *%s_Generated::getInstance() {\n" % (class_info['class_name'], class_info['class_name']))
        file.write("\t\treturn &sInstance;\n")
        file.write("\t}\n\n")
        
        file.write('} // runtime\n')

with open(os.path.join(GENERATED_DIR, 'reflect.json'), 'w', encoding='utf-8') as file:
    file.write(json.dumps(class_list, indent=4, ensure_ascii=False))