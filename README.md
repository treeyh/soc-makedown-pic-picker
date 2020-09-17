# soc-markdown-pic-picker

使用`Python`+`AutoHotKey`实现快捷键上传剪切板中图片到github，并使用jsdelivr cdn输出markdown格式地址。

## 依赖

Python 3.6+，开发环境为 Python 3.8.5

## 使用方法

安装`Python`略。

使用命令安装依赖：

```bash
pip install -r requirement.txt
```

目前支持github，需要修改如下配置，配置位于代码文件`src/github/github_pic_picker.py`中，需要如下配置：

```python

# github授权token
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

```

安装 `AutoHotkey`  https://www.autohotkey.com/download/ .

`AutoHotkey`脚本，见如下：

```bash

;上传图片github，剪切板markdown
^+v::
{
	runwait, python {base_path}\soc-markdown-pic-picker\src\github\github_pic_picker.py, , Hide
	send ^v
	return
}

```

## 鸣谢

* [mdpicker-qiniu](https://github.com/firejq/mdpicker-qiniu) ：借鉴了该项目的图片处理逻辑。

## License

MIT License.