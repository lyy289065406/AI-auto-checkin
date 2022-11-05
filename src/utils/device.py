#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------------

import cv2
import mediapipe as mp
from src.config import SETTINGS
from src.utils.upload import *
from src.utils.image import *
from color_log.clog import log


EXIT_KEY = 'q'          # 退出 CV 绘制窗口的按键
SAVE_KEY = 's'          # 保存 CV 绘制窗口的按键


def open_camera(is_face_detection=True, is_face_mesh=False) :
    '''
    开启摄像头拍摄人像
    [params] is_face_detection: 拍摄时是否开启人脸方框检测
    [params] is_face_mesh: 拍摄时是否开启人脸网格检测
    [return] : 拍摄的图像路径; 没有拍摄则返回 None
    '''
    imgpath = None
    face_detection, face_mesh = _init_face_model(is_face_detection, is_face_mesh)
    capture = _init_camera()
    is_open = capture.isOpened()
    if is_open :
        log.info(f'加载摄像头的数据流成功（按 <{EXIT_KEY}> 退出，按 <{SAVE_KEY}> 保存）')
    else :
        log.info('加载摄像头的数据流失败（请确认没有其他程序在读取该数据流）')
        return imgpath

    while is_open:
        is_open, mirror_frame = capture.read()
        if not is_open:
            continue
        
        bgr_frame = cv2.flip(mirror_frame, 1)   # 镜像翻转画面
        annotated_frame = _draw_face_label(bgr_frame, face_detection, face_mesh)
        is_exit, is_save = show_frame(annotated_frame, exit_key=EXIT_KEY, save_key=SAVE_KEY)

        if is_exit :
            break

        elif is_save :
            image_id = gen_file_id()
            imgpath = "%s/%s%s" % (SETTINGS.tmp_dir, image_id, SETTINGS.image_format)
            save_frame(bgr_frame, imgpath)
            break
    
    capture.release()
    _close_face_model(face_detection, face_mesh)
    return imgpath


def _init_camera() :
    '''
    初始化摄像头
    '''
    log.info(f'正在打开视频设备（索引号={SETTINGS.dev_idx}） ...')
    capture = cv2.VideoCapture(SETTINGS.dev_idx)    # 初始化设备时间较长
    capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*SETTINGS.fourcc))
    capture.set(cv2.CAP_PROP_FPS, SETTINGS.fps)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, SETTINGS.frame_width)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, SETTINGS.frame_height)

    log.info('摄像头输入参数：')
    log.info('  视频编码（fourcc/codec）= %d' % int(capture.get(cv2.CAP_PROP_FOURCC)))
    log.info('  帧速率（FPS）= %d' % int(capture.get(cv2.CAP_PROP_FPS)))
    log.info('  帧宽度（width）= %d' % int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)))
    log.info('  帧高度（height）= %d' % int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    return capture


def _init_face_model(is_face_detection, is_face_mesh) :
    '''
    初始化人脸检测模块
    [params] face_detection: 拍摄时是否开启人脸方框检测
    [params] face_mesh: 拍摄时是否开启人脸网格检测
    [return] : (face_detection, face_mesh)
    '''
    model_selection = 0             # 距离模型:  0:短距离模式，适用于 2 米内的人脸; 1:全距离模型，适用于 5 米内的人脸
    static_image_mode = False       # False: 视频流; True: 图片
    max_num_faces = 1               # 检测人脸个数
    min_detection_confidence = 0.5  # 人脸检测模型的最小置信度值
    min_tracking_confidence = 0.5   # 视频流跟踪人脸的最小置信度

    face_detection = None
    face_mesh = None

    # 导入人脸检测模块
    if is_face_detection :
        face_detection = mp.solutions.face_detection.FaceDetection(
            model_selection = model_selection, 
            min_detection_confidence = min_detection_confidence
        )

    # 导入人脸网格模块
    elif is_face_mesh :
        face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode = static_image_mode, 
            max_num_faces = max_num_faces,
            min_detection_confidence = min_detection_confidence, 
            min_tracking_confidence = min_tracking_confidence
        )
    return (face_detection, face_mesh)


def _draw_face_label(bgr_frame, face_detection, face_mesh) :
    '''
    绘制人脸标签
    [params] bgr_frame: 原始帧
    [params] face_detection: 人脸检测模型
    [params] face_mesh: 人脸网格模型
    [return] : 含有标记帧
    '''
    annotated_frame = bgr_frame
    if face_detection is not None or face_mesh is not None :
        mp_drawing = mp.solutions.drawing_utils
        rgb_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        annotated_frame = bgr_frame.copy()
        
    if face_detection is not None :
        results = face_detection.process(rgb_frame)
        if results.detections :
            detection = results.detections[0]
            mp_drawing.draw_detection(annotated_frame, detection)

    elif face_mesh is not None :
        results = face_mesh.process(rgb_frame)
        if results.multi_face_landmarks :
            landmarks = results.multi_face_landmarks[0]
            mp_drawing.draw_landmarks(annotated_frame, landmarks)

    return annotated_frame


def _close_face_model(face_detection, face_mesh) :
    '''
    关闭人脸检测模型
    [params] face_detection: 人脸检测模型
    [params] face_mesh: 人脸网格模型
    [return] : None
    '''
    if face_detection :
        face_detection.close()
    
    if face_mesh :
        face_mesh.close()