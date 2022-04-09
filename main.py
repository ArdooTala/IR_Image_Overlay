import pathlib
import remap_ir
from match_images import MatchMaker


if __name__ == '__main__':
    # Convert and recolor the 16-bit images.
    # remap_ir.convert_16_8('FirstFloor/IR/', 'FirstFloor/Thermal_Converted/', 15, 25)

    match_maker = MatchMaker("FirstFloor/Thermal_Converted/")

    rgb_images = pathlib.Path("FirstFloor/RGB")
    save_path = pathlib.Path("FirstFloor/Resized_Thermal/")

    # For manual adjustment of the matching. The values will be saved.
    # for p in rgb_images.glob('*.png'):
    #     match_maker.match(p)

    # Save the overlays without preview.
    for p in rgb_images.glob('*.png'):
        match_maker.match(p, save_path=save_path, set_match=False)
