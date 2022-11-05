#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------
# 预录入目标人脸的特征值
# python ./presrc/gen_feature.py [-c]
# -----------------------------------------------

# 把父级目录（项目根目录）添加到工作路径
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
# ----------------------------------------------------------------------

import argparse
from main import record


def args() :
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        prog='预录入目标人脸的特征值',
        description='提前录入人脸特征值，用于人脸比对时匹配', 
        epilog='\r\n'.join([
            '摄像头拍摄: ', 
            '  python ./presrc/gen_feature.py -c', 
            '上传人脸图片: ', 
            '  python ./presrc/gen_feature.py', 
        ])
    )
    parser.add_argument('-c', '--camera', dest='camera', action='store_true', default=False, help='摄像头模式; 默认为图片上传模式')
    return parser.parse_args()


if '__main__' == __name__ :
    record(args())
