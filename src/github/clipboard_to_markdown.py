#-*- encoding: utf-8 -*-

import os
import urllib3
import pyperclip



import github_pic_picker


_excel_convert_cmd = 'soc-excel-convert -p '

def run():
  global _excel_convert_cmd

  content = pyperclip.paste()
  if content != None and content != '':
    # 使用剪贴板中的excel复制数据，制作表格
    os.system(_excel_convert_cmd)    
  else:
    # 使用剪贴板中的图片数据，制作图片链接
    github_pic_picker.run()



if __name__ == "__main__":
  urllib3.disable_warnings()
  run()