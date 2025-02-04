import json

import cv2
import requests
import sys

LIMIT_PX = 1024
LIMIT_BYTE = 1024*1024  # 1MB
LIMIT_BOX = 40


def kakao_ocr_resize(image_path: str):
    """
    ocr detect/recognize api helper
    ocr api의 제약사항이 넘어서는 이미지는 요청 이전에 전처리가 필요.

    pixel 제약사항 초과: resize
    용량 제약사항 초과  : 다른 포맷으로 압축, 이미지 분할 등의 처리 필요. (예제에서 제공하지 않음)

    :param image_path: 이미지파일 경로
    :return:
    """
    image = cv2.imread(image_path)
    height, width, _ = image.shape

    if LIMIT_PX < height or LIMIT_PX < width:
        ratio = float(LIMIT_PX) / max(height, width)
        image = cv2.resize(image, None, fx=ratio, fy=ratio)
        height, width, _ = height, width, _ = image.shape

        # api 사용전에 이미지가 resize된 경우, recognize시 resize된 결과를 사용해야함.
        image_path = "{}_resized.jpg".format(image_path)
        cv2.imwrite('api.png', image)

        return image_path
    return None


def kakao_ocr_detect(image_path: str, appkey: str):
    """
    detect api request example
    :param image_path: 이미지파일 경로
    :param appkey: 카카오 앱 REST API 키
    """
    API_URL = 'https://kapi.kakao.com/v1/vision/text/detect'

    headers = {'Authorization': 'KakaoAK {}'.format('9f69bf7a62e57783e3aa9adef4aa7f5e')}

    image = cv2.imread(image_path)
    jpeg_image = cv2.imencode(".jpg", image)[1]
    data = jpeg_image.tobytes()

    return requests.post(API_URL, headers=headers, files={"file": data})


def kakao_ocr_recognize(image_path: str, boxes: list, appkey: str):
    """
    recognize api request example
    :param boxes: 감지된 영역 리스트. Canvas 좌표계: 좌상단이 (0,0) / 우상단이 (limit,0)
                    감지된 영역중 좌상단 점을 기준으로 시계방향 순서, 좌상->우상->우하->좌하
                    ex) [[[0,0],[1,0],[1,1],[0,1]], [[1,1],[2,1],[2,2],[1,2]], ...]
    :param image_path: 이미지 파일 경로
    :param appkey: 카카오 앱 REST API 키
    """
    API_URL = 'https://kapi.kakao.com/v1/vision/text/recognize'

    headers = {'Authorization': 'KakaoAK {}'.format('9f69bf7a62e57783e3aa9adef4aa7f5e')}

    image = cv2.imread(image_path)
    jpeg_image = cv2.imencode(".jpg", image)[1]
    data = jpeg_image.tobytes()

    return requests.post(API_URL, headers=headers, files={"file": data}, data={"boxes": json.dumps(boxes)})


def main():
    if len(sys.argv) != 3:
        print("Please run with args: $ python example.py /path/to/image appkey")
    print(sys.argv)
    image_path, appkey = sys.argv[1], sys.argv[2]

    resize_impath = kakao_ocr_resize(image_path)
    if resize_impath is not None:
        image_path = resize_impath
        print("원본 대신 리사이즈된 이미지를 사용합니다.")

    output = kakao_ocr_detect(image_path, appkey).json()
    sorted(output['result']['boxes'])
    print("[detect] output:\n{}\n".format(output))
    #
        # boxes = output["result"]["boxes"]
        # boxes = boxes[:min(len(boxes), LIMIT_BOX)]
        # output = kakao_ocr_recognize(image_path, boxes, appkey).json()
        # print("[recognize] output:\n{}\n".format(json.dumps(output, sort_keys=True, indent=2)))


if __name__ == "__main__":
    main()
