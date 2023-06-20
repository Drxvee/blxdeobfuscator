import random, base64, json, zlib, re, os, sys, ast, astor, string, time, binascii

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

def pr(txt):
    print('\033[92m'+txt+'\033[0m')
def er(txt):
    print('\033[91m'+txt+'\033[0m')
def warn(txt):
    print('\033[93m'+txt+'\033[0m')

print('''
,-----.  ,--.   ,--.   ,--.,------.  ,------.     ,-----. ,-----.  ,------.,--. ,--. ,---.   ,-----.  ,---. ,--------. ,-----. ,------.  
|  |) /_ |  |    \  `.'  / |  .-.  \ |  .---'    '  .-.  '|  |) /_ |  .---'|  | |  |'   .-' '  .--./ /  O  \'--.  .--''  .-.  '|  .--. ' 
|  .-.  \|  |     .'    \  |  |  \  :|  `--,     |  | |  ||  .-.  \|  `--, |  | |  |`.  `-. |  |    |  .-.  |  |  |   |  | |  ||  '--'.' 
|  '--' /|  '--. /  .'.  \ |  '--'  /|  `---.    '  '-'  '|  '--' /|  |`   '  '-'  '.-'    |'  '--'\|  | |  |  |  |   '  '-'  '|  |\  \  
`------' `-----''--'   '--'`-------' `------'     `-----' `------' `--'     `-----' `-----'  `-----'`--' `--'  `--'    `-----' `--' '--' ''')
os.system("title Blxde Obfuscator - Made by Drxve (or Blxde)")
print('')

def slicestring(str1):
    n = len(str1)
    if n%2==0:
        string1=str1[0:n//2]
        string2=str1[n//2:]
    else:
        string1=str1[0:(n//2+1)]
        string2=str1[(n//2+1):]
    return string1,string2

sm=[]
def generate_random_string(length, ilobf):
    if ilobf:
        characters = 'Il'
    else:
        characters = string.ascii_letters
    ready=''.join(random.choices(characters, k=length))
    while True:
        if ready not in sm:
            sm.append(ready)
            return ''.join(random.choices(characters, k=length));break

def obfuscate_imports(tree):
    new_body = []
    for node in tree.body:
        if not isinstance(node, ast.Import):
            new_body.append(node)
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            module_name = node.func.value.id
            node.func.value = ast.Name(id=f"""__import__('{str(module_name)}')""", ctx=ast.Load())
    
    tree.body = new_body

def obfuscate_variables(tree, ilobf):
    generated_names = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            if node.id not in generated_names:
                obfuscated_name = generate_random_string(config['ilcount'], ilobf)
                while obfuscated_name in generated_names.values():
                    obfuscated_name = generate_random_string(config['ilcount'], ilobf)
                generated_names[node.id] = obfuscated_name
            else:
                obfuscated_name = generated_names[node.id]
            node.id = obfuscated_name

        elif isinstance(node, ast.FunctionDef):
            for arg in node.args.args:
                if arg.arg not in generated_names:
                    obfuscated_name = generate_random_string(config['ilcount'], ilobf)
                    while obfuscated_name in generated_names.values():
                        obfuscated_name = generate_random_string(config['ilcount'], ilobf)
                    generated_names[arg.arg] = obfuscated_name
                else:
                    obfuscated_name = generated_names[arg.arg]
                arg.arg = obfuscated_name

        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            if node.id in generated_names:
                node.id = generated_names[node.id]

def obfuscate_methods(tree):
    generated_names = {}
    methodstoobf = ['print', 'exec']
    obfuscated_names=[]
    obfuscated_vars=[]
    dic=[]
    for node in ast.walk(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
            method_name = node.value.func.id
            if method_name in methodstoobf:
                obfuscated_vars.append(method_name)
                if method_name not in generated_names:
                    obfuscated_name = generate_random_string(config['ilcount'], config['ildict'])
                    generated_names[method_name] = obfuscated_name
                else:
                    obfuscated_name = generated_names[method_name]
                if obfuscated_name not in obfuscated_names:
                    obfuscated_names.append(obfuscated_name)
                node.value.func.id = obfuscated_name
                dic.append([method_name, obfuscated_name])
    res=[]
    for i in dic:
        if i not in res:
            res.append(i)
    for n in res:
            method_nam=n[0]
            obfed_nam=n[1]
            assignment_code = ast.parse(obfed_nam + ' = ' + method_nam).body[0]
            tree.body.insert(0, assignment_code)

def insert_obfuscated_name(tree, code):
    assignment_code = ast.parse(code).body[0]
    if isinstance(assignment_code, ast.Assign):
        target = assignment_code.targets[0]
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and node.targets[0].id == target.id:
                return
    tree.body.insert(0, assignment_code)

def obfuscate_strings(tree):
    def replace_string(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            original_string = node.value
            if random.choice([False, True]):
                encoded_string = base64.b64encode(original_string.encode('utf-8')).decode('utf-8')
                replacement_code = "__import__('base64').b64decode(b'{}').decode()".format(encoded_string)
            else:
                original_string1, original_string2 = slicestring(original_string)
                encoded_string1 = base64.b64encode(original_string1.encode('utf-8')).decode('utf-8')
                encoded_string2 = base64.b64encode(original_string2.encode('utf-8')).decode('utf-8')
                replacement_code = (
                    "__import__('base64').b64decode(b'{}').decode()".format(encoded_string1)
                    + "+"
                    + "__import__('base64').b64decode(b'{}').decode()".format(encoded_string2)
                )
            return ast.parse(replacement_code).body[0].value
        elif isinstance(node, ast.AST):
            for field, value in ast.iter_fields(node):
                if isinstance(value, list):
                    setattr(node, field, [replace_string(item) if isinstance(item, ast.AST) else item for item in value])
                elif isinstance(value, ast.AST):
                    setattr(node, field, replace_string(value))
        return node

    tree = replace_string(tree)

def obfuscate_ints(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, int):
            original_int = int(node.value)
            random_int=random.randint(-999999999,999999999)
            if(random.choices([True,False])):
                modified_int=random_int+original_int
                encoded_int=base64.b64encode(str(modified_int).encode('utf-8')).decode('utf-8')
                encoded_random_int=base64.b64encode(str(random_int).encode('utf-8')).decode('utf-8')
                replacement_code = "int(__import__('base64').b64decode(b'{}').decode())".format(encoded_int)+"-int(__import__('base64').b64decode(b'{}').decode())".format(encoded_random_int)
                for parent_node in ast.walk(tree):
                    for field, value in ast.iter_fields(parent_node):
                        if value is node:
                            setattr(parent_node, field, ast.parse(replacement_code).body[0].value)
            else:
                modified_int=random_int-original_int
                encoded_int=base64.b64encode(str(modified_int).encode('utf-8')).decode('utf-8')
                encoded_random_int=base64.b64encode(str(random_int).encode('utf-8')).decode('utf-8')
                replacement_code = "int(__import__('base64').b64decode(b'{}').decode())".format(encoded_int)+"+int(__import__('base64').b64decode(b'{}').decode())".format(encoded_random_int)
                for parent_node in ast.walk(tree):
                    for field, value in ast.iter_fields(parent_node):
                        if value is node:
                            setattr(parent_node, field, ast.parse(replacement_code).body[0].value)

def antideobf(tree):
    obfsrc=astor.to_source(tree)
    if(config['noemptylines']):
        obfsrc="\n".join([ll.rstrip() for ll in obfsrc.splitlines() if ll.strip()])
    if(len(obfsrc)==0):return
    s=base64.b64encode(bytes(obfsrc, 'utf-8'))
    additional=[]
    if(config['msgs']):
        additional.append('''print('Do not even try.')''')
    if(config['suicideondeobf']):
        additional.append('''open(n, 'w').close()''')
    if(config['rudeantideobf']):
        additional.append('''exec('while True:__import__(\\'os\\').system(\\'explorer\\')')''')
    additional=';'.join(additional)
    code=f'''exec("""n=(__import__('os').path.basename(__file__))\\nl=open(n, 'r').read()\\nif(__import__('base64').b64decode({str(s)}).decode() not in l):exec("{str(additional)}")""")'''
    byte=base64.b64encode(bytes(code, 'utf-8'))
    code=f'''exec(__import__('base64').b64decode({byte}).decode())'''
    hx=binascii.b2a_hex(bytes(code,'utf-8'))
    hx=str(hx.decode())
    code=f'''exec(bytes.fromhex('{hx}').decode())'''
    antideobfcode = ast.parse(code).body[0]
    tree.body.insert(0, antideobfcode)

def obfuscate_functions(tree):
    generated_names = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name not in generated_names:
                obfuscated_name = generate_random_string(config['ilcount'], config['ildict'])
                generated_names[node.name] = obfuscated_name
            else:
                obfuscated_name = generated_names[node.name]
            node.name = obfuscated_name
            for arg in node.args.args:
                if arg.arg in generated_names:
                    arg.arg = generated_names[arg.arg]
            obfuscate_variables(node, config['ildict'])
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            function_name = node.func.id
            if function_name in generated_names:
                node.func.id = generated_names[function_name]

def obfuscate():
    now=time.time()
    try:
        with open(config['input'], mode='rb') as f:
            src = f.read().decode('utf-8')
            tree = ast.parse(src)
    except Exception as e:
        er(f'error (file reading): {e}')
        return
    pr(f'the input file was read')
    if config['obfimports']:
        try:
            pr('obfuscating imports')
            obfuscate_imports(tree)
        except Exception as e:
            er(f'error (import obfuscation): {e}')
    if config['obfvars']:
        try:
            pr('obfuscating variables')
            obfuscate_variables(tree, config['ildict'])
        except Exception as e:
            er(f'error (variable obfuscation): {e}')
    if config['obfmethods']:
        try:
            pr('obfuscating methods')
            obfuscate_methods(tree)
        except Exception as e:
            er(f'error (method obfuscation): {e}')
    if config['obfstrings']:
        try:
            pr('obfuscating strings')
            obfuscate_strings(tree)
        except Exception as e:
            er(f'error (string obfuscation): {e}')
    if config['obfints']:
        try:
            pr('obfuscating integers')
            obfuscate_ints(tree)
        except Exception as e:
            er(f'error (integer obfuscation): {e}')
    if config['obffunctions']:
        try:
            pr('obfuscating function names')
            obfuscate_functions(tree)
        except Exception as e:
            er(f'error (function name obfuscation): {e}')
    if config['antideobf']:
        try:
            pr('antideobfuscation integration')
            antideobf(tree)
        except Exception as e:
            er(f'error (antideobfuscation integration): {e}')
    obfuscated_code = astor.to_source(tree)
    with open(config['output'], 'w') as output_file:
        output_file.write(obfuscated_code)
    if config['noemptylines']:
        pr('removing empty lines')
        result = ""
        with open(config['output'], "r+") as file:
            for line in file:
                if not line.isspace():
                    result += line
            file.seek(0)  
            file.write(result)
    now2=time.time()
    elapsed=str(now2-now)
    pr(f'done in {elapsed}s.')

obfuscate()
