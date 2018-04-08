# -*- coding: utf-8 -*- 
import os, shutil, json, zipfile

def printRed(content):
    print("\033[31m" + content + "\033[0m")

def printBlue(content):
    print("\033[36m" + content + "\033[0m")

def delete_path(path):
    if os.path.exists(path):
        shutil.rmtree(path)
        return True
    return False
        

def look_for_file(path, file_info):
    app_path = ""
    for root, dir_name_list, file_name_list in os.walk(path):
        for file_name in file_name_list:
            if file_name.find(file_info) != -1:
                return os.path.join(root, file_name)

        for dir_name in dir_name_list:
            if dir_name.find(file_info) != -1:
                return os.path.join(root, dir_name)
            app_path = look_for_file(dir_name, file_info)
            if app_path != "":
                return app_path
    return ""  

# 获取脚本路径
script_path = os.path.dirname(os.path.abspath('__file__'))
print "Path: " + script_path

# 获取所有.ipa文件
all_file_list = os.listdir(script_path)
ipa_file_list = []
for file_item in all_file_list:
    file_splitext = os.path.splitext(file_item)
    if file_splitext[1] == '.ipa':
        ipa_file_list.append(file_splitext[0])
        print "found " + file_item

# 检查是否存在.ipa文件
if len(ipa_file_list) == 0:
    printRed("not found .ipa file in " + script_path)
    exit(-1)

for file_name in ipa_file_list:
    print "\n" + file_name + ":"
    file_path = os.path.join(script_path, file_name)
    
    # 删除之前的Payload文件夹
    payload_path = file_path + "_Payload"
    if delete_path(payload_path):
        print file_name + ": delete the previous " + payload_path + " file folder"

    # 解压.ipa文件
    print file_name + ": upzip " + file_name + ".ipa ..."
    zip_file = zipfile.ZipFile(file_name + ".ipa")
    if os.path.isdir(payload_path):
        pass
    else:
        os.mkdir(payload_path)
    for names in zip_file.namelist():
        zip_file.extract(names, payload_path + "/")
    print file_name + ": upzip " + file_name + " success." 

    # 找到.app文件
    print file_name + ": look for " + file_name + " .app ..."
    app_path = look_for_file(payload_path, ".app")
    if app_path == "":
        printRed(file_name + ": not found .app file in " + payload_path)
        delete_path(payload_path)
        continue
    else:
        print file_name + ": found .app file in " + payload_path
        
    # 找到Assets.car文件
    print file_name + ": look for " + file_name + " Assets.car ..."
    assets_path = look_for_file(app_path, "Assets.car")
    if assets_path == "":
        printRed(file_name + ": not found Assets.car in " + payload_path)
        delete_path(payload_path)
        continue
    else:
        print file_name + ": found Assets.car in " + payload_path
    
    # 将包文件中的图片信息存储到文件中
    print file_name + ": load picture info ..."
    # assets_path = os.path.join(app_path, "Assets.car")
    assets_json_file = os.path.join(payload_path, "Assets.json")
    assets_info_command = "sudo xcrun --sdk iphoneos assetutil --info " + assets_path + " > " + assets_json_file
    if os.system(assets_info_command) != 0:
        printRed(file_name + " load picture info failure")
        delete_path(payload_path)
        continue
    else:
        print file_name + ": load picture info success"

    # 获取图片信息
    print file_name + ": read picture info ..."
    with open(assets_json_file, 'r') as f:
        picture_info_list = json.load(f)
    print file_name + ": read picture info success"

    # 删除创建的文件夹
    delete_path(payload_path)

    # 获取P3图片的图片名
    print file_name + ": look for P3 picture ..."
    picture_name_list = []
    for picture_info in picture_info_list:
        if picture_info.get("DisplayGamut") == 'P3' or picture_info.get("Encoding") == 'ARGB-16':
            picture_name = picture_info.get("RenditionName")
            picture_name_list.append(picture_name)
    print file_name + ": look for P3 picture success"

    # 检查是否存在P3图片
    print file_name + ": success!"
    print file_name + ": P3 pictures list"
    print "--------------"
    if len(picture_name_list) == 0:
        printBlue(file_name + ": not found P3 picture!")
    else:
    # 打印所有P3图片名
        for picture_name in picture_name_list:
            printBlue(picture_name)
    print "--------------"
