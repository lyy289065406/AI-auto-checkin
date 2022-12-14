#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------

import cv2
from src.utils.image import *
from src.cache.face_feature_cache import FACE_FEATURE_CACHE
from src.config import SETTINGS
from color_log.clog import log


class FaceAlignment :

    def __init__(self) :
        pass
    
    
    def handle(self, face_data) :
        '''
        对照标准脸，对输入的人脸进行仿射变换
        [params] face_data: 人脸检测得到的数据
        [return]: 人脸对齐后的图像
        '''
        alignment_frame = None
        if face_data is not None :
            try :
                face_keypoints = face_data.fkp6_coords
                trans_matrix = gen_trans_matrix(        # 计算转换矩阵
                    face_keypoints, 
                    FACE_FEATURE_CACHE.standard_fkp_coords
                )
                alignment_frame = self._face_alignment(face_data, trans_matrix)
            except :
                log.error("人脸对齐模型异常")
        return alignment_frame
        

    def _face_alignment(self, face_data, trans_matrix) :
        '''
        人脸图像仿射变换
        [params] face_data: 人脸检测得到的数据
        [params] trans_matrix: 转换矩阵
        [return]: 人脸对齐后的图像
        '''
        bgr_frame = face_data.copy_BGR()
        alignment_frame = cv2.warpAffine(
            bgr_frame, 
            trans_matrix, 
            SETTINGS.alignment_resize, 
            borderValue = 0.0
        )

        # 显示变换后的图像
        if SETTINGS.show_image :
            show_frame(alignment_frame)

        # 保存图像
        savepath = '%s/%s%s' % (SETTINGS.alignment_dir, face_data.image_id, SETTINGS.image_format)
        save_image(alignment_frame, savepath)

        face_data.alignment_frame = alignment_frame
        face_data.alignment_path = savepath
        return alignment_frame

