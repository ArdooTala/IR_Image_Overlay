import pathlib
import numpy as np
import cv2


def convert(file, min_temp=0, max_temp=40):
    img16 = cv2.imread(file, cv2.IMREAD_ANYDEPTH)
    assert np.issubdtype(img16.dtype, np.uint16)

    temp_values = img16.astype('float') / 100
    temp_values = np.clip(temp_values, min_temp + 273, max_temp + 273)
    print(temp_values.max() - 273, temp_values.min() - 273)
    temp_values = remap_to_range(temp_values, min_temp, max_temp, 0, 255)

    assert temp_values.max() < 256
    return temp_values.astype('uint8')


def visualize_as_heatmap(img, scale=1):
    # Color-maps: https://docs.opencv.org/4.x/d3/d50/group__imgproc__colormap.html#ga9a805d8262bcbe273f16be9ea2055a65
    htm = cv2.applyColorMap(img, cv2.COLORMAP_PLASMA)
    cv2.imshow("8bit_Heat", cv2.resize(htm, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC))


def remap_to_range(ar, s_min=0, s_max=1, t_min=0, t_max=1):
    return ((ar - s_min - 273) * ( (t_max - t_min) / (s_max - s_min) ) + t_min).astype(ar.dtype)


def convert_16_8(input_path, output_path, min_temp, max_temp, heat_map=False):
    input_path = pathlib.Path(input_path)  # 16-bit images folder
    output_path = pathlib.Path(output_path)  # Output folder

    # # Temperature values for remapping (Celsius)
    # min_temperature = 15  # will be represented as a pixel value of 0
    # max_temperature = 25  # will be represented as a pixel value of 255

    for p in input_path.glob("*.png"):
        image = convert(str(p), min_temp=min_temp, max_temp=max_temp)
        cv2.imwrite(str(output_path / p.name), image)

        if heat_map:
            visualize_as_heatmap(image, scale=5)
            cv2.imshow("8bit_Temp", image)
            cv2.waitKey(0)