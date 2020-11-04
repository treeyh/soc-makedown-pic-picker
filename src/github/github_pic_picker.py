#-*- encoding: utf-8 -*-

import os
import requests
import urllib3

from PIL import ImageGrab, Image, ImageFilter
from Lib import base64, json, traceback
from datetime import datetime
import time
import pyperclip


# github 授权 token
access_token = ''
# github 仓库名
repo_name = ''
# 路径模板，有下面占位符可选
# {year}：年，如：2020
# {month}: 月，如：01
# {date}：日期，如: 17
# {hour}： 小时（24小时制），如：20
# {minute}：分钟，如：34
# {second}：秒，如：47
path_format = 'img/md/{year}/{month}/{date}'
# 是否为图像增加阴影
add_shadow_type = True






_current_path = os.path.split(os.path.realpath(__file__))[0]
_tmp_image = os.path.join(_current_path, 'tmp.png')
_headers = {"Authorization": "token " + access_token}
_user_config_path = os.path.join(_current_path, '.config.json')



def save_from_screen(image_path):
    """将剪贴板的图片保存到本地为临时图片文件

    :return:
    """
    
    image = ImageGrab.grabclipboard() # 获取剪贴板文件
    if image is None:
        print("No image is on the clipboard.")
        return None
    image.save(image_path)
    return image_path


def add_shadow(image_path, offset=(0, 0), background_color=0xffffff,
                shadow_color=0x000000, border=20, iterations=10):
    """为图像添加阴影，即将图像放在一个高斯模糊的背景上

    :param offset: 阴影相对图像的偏移，用(x, y)表示，可以为正数或者负数
    :param background_color: 背景色
    :param shadow_color: 阴影色
    :param border: 图像边框，必须足够用来制作阴影模糊
    :param iterations: 过滤器处理次数，次数越多越模糊，处理过程也越慢
    :return: 添加阴影后的图片
    """

    if add_shadow_type == False:
        return
    # 要放在背景上的原始图像
    original_image = Image.open(image_path)
    # 创建背景块
    total_width = original_image.size[0] + abs(offset[0]) + 2 * border
    total_height = original_image.size[1] + abs(offset[1]) + 2 * border
    background = Image.new(
        original_image.mode,
        (total_width, total_height),
        background_color
    )
    # 放置阴影块，考虑图像偏移
    shadow_left = border + max(offset[0], 0)
    shadow_top = border + max(offset[1], 0)
    background.paste(
        shadow_color,
        [shadow_left, shadow_top,
            shadow_left + original_image.size[0],
            shadow_top + original_image.size[1]]
    )
    # 处理阴影的边缘模糊
    n = 0
    while n < iterations:
        background = background.filter(ImageFilter.BLUR)
        n += 1
    # 把图像粘贴到背景上
    image_left = border - min(offset[0], 0)
    image_top = border - min(offset[1], 0)
    background.paste(original_image, (image_left, image_top))
    # 将处理后的图片覆盖原图片
    background.save(image_path)


def close(file_path):
    """删除保存在本地的临时图片文件

    :return:
    """
    if os.path.exists(file_path):
        os.remove(file_path)


def read_file_data(file_path):
    '''
    读取文件
    '''
    with open(file_path, 'rb') as f:
        return f.read()

def file_base64(data):
    data_b64 = base64.b64encode(data).decode('utf-8')
    return data_b64

def get_user_name_by_github():
    url = 'https://api.github.com/user'
    try:
        r = requests.get(url, headers = _headers, verify = False)
        if r.status_code != 200:
            print('github_api_response_status_'+str(r.status_code))
            return None
    
        data = json.loads(r.text)
        return data['login']
    except Exception as ex:
        print(ex)
        return None


def read_all_file(filePath, method='r'):
    '''
        读取所有文件，一次性读取所有内容，文件不存在返回None
        filePath：文件路径
        method：读取方式，'r'读取，'rb' 二进制方式读取
    '''
    fh = open(filePath, method)
    try:
        c = fh.read()
        return c
    finally:
        fh.close()

def get_user_name(token, user_config_path):
    if os.path.exists(user_config_path):
        content = read_all_file(user_config_path, 'r')
        try:
            config = json.loads(content)
            if token == config['token']:
                return config['user']
        except Exception as ex:
            print(ex)

    user = get_user_name_by_github()
    if None == user:
        return user

    config = {
        'token': token,
        'user': user,
    }
    fh = open(user_config_path, 'w', encoding='utf-8')

    try:
        fh.write(json.dumps(config))
    except:
        print(traceback.format_exc())
    finally:
        fh.close()
        return user
    




def upload_file(file_path, message, user_name, repo, path, file_name):
    '''
    上传文件
    '''
    
    url = 'https://api.github.com/repos/'+user_name+'/'+repo + '/contents'

    if path[:1] == '/':
        url += path
    else:
        url += '/' + path
    
    if path[-1:] != '/':
        url += path + '/'
    url += file_name
    file_data = read_file_data(file_path)
    content = file_base64(file_data)
    data = {
        "message": message,
        "content": content
    }
    data = json.dumps(data)
    req = requests.put(url=url, data=data, headers=_headers, verify = False)
    req.encoding = "utf-8"
    re_data = json.loads(req.text)
    if re_data.get('content', None) == None or re_data['content'].get('path', None) == None:
        return None
    return url
    


    

def format_path(path):
    # {year}：年，如：2020
    # {month}: 月，如：01
    # {date}：日期，如: 17
    # {hour}： 小时（24小时制），如：20
    # {minute}：分钟，如：34
    # {second}：秒，如：47
    dt = datetime.now()
    return path.format(year = str(dt.year), month = '{0:02d}'.format(dt.month), 
                        date = '{0:02d}'.format(dt.day), hour = '{0:02d}'.format(dt.hour), 
                        minute = '{0:02d}'.format(dt.minute), second = '{0:02d}'.format(dt.second))


def run():
    image_path = save_from_screen(_tmp_image)
    try:
        if image_path == None:
            print('clipboard_not_exist_pic')
            pyperclip.copy('clipboard_not_exist_pic')
            return
        image_name = str(int(time.time())) + '.' + os.path.splitext(image_path)[1][1:]
    
        add_shadow(image_path)

        user_name = get_user_name(access_token, _user_config_path)
        if user_name == None:
            print('get_github_user_name_fail')
            pyperclip.copy('pic_upload_github_fail')
            return
        
        file_path =format_path(path_format)

        url = upload_file(image_path, 'commit '+image_name, user_name, repo_name, file_path, image_name)
        if url == None:
            print('upload_pic_fail')
            pyperclip.copy('pic_upload_github_fail')
            return
        md_url = url.replace('https://api.github.com/repos/'+user_name+'/'+repo_name + '/contents', 'https://cdn.jsdelivr.net/gh/'+user_name+'/' + repo_name)        
        pyperclip.copy('![desc]('+md_url+')')
    except:
        print(traceback.format_exc())
        pyperclip.copy('pic_upload_github_fail')
    finally:
        close(image_path)
        pyperclip.paste()

    

    


if __name__ == "__main__":
    urllib3.disable_warnings()
    run()