import pathlib
import remap_ir
import match_images


if __name__ == '__main__':
    # remap_ir.convert_16_8('FirstFloor/IR/', 'FirstFloor/Thermal_Converted/', 15, 25)

    match_maker = match_images.OverlayImages("FirstFloor/Thermal_Converted/")

    rgb_images = pathlib.Path("FirstFloor/RGB")
    save_path = pathlib.Path("FirstFloor/Resized_Thermal/")

    # for p in rgb_images.glob('*.png'):
    #     match_maker.match(p)

    for p in rgb_images.glob('*.png'):
        match_maker.match(p, save_path=save_path, set_match=False)

