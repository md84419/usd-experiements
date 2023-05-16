import os
from pathlib import Path

import omni.ext
import omni.ui as ui
from pxr import UsdShade, Tf, Sdf, Usd

CURRENT_PATH = Path(__file__).parent
PROJECT_ROOT = CURRENT_PATH.parent.parent.parent
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
TEST_USDA = os.path.join(DATA_DIR, 'usd-experiements.usda')

# Functions and vars are available to other extension as usual in python: `example.python_ext.some_public_function(x)`
def some_public_function(x: int):
    print("[robotica.usd.experiments] some_public_function was called with x: ", x)
    return x ** x


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class RoboticaUsdExperimentsExtension(omni.ext.IExt):
    def __init__(self):
        self._prim_path = None

    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        print("[robotica.usd.experiments] robotica usd experiments startup")

        self._count = 0

        self._window = ui.Window("My Window", width=300, height=300)
        with self._window.frame:
            with ui.VStack():
                label = ui.Label("")


                def on_click():
                    self._count += 1
                    label.text = f"count: {self._count}"

                    method1()
                    method2()

                
                def method1():
                    # The following is based on code by Michal S in NVIDIA Omniverse Discord:
                    # https://discord.com/channels/827959428476174346/989589513909203014/1108002804695572480

                    reference_path = TEST_USDA
                    name = os.path.splitext(os.path.basename(reference_path))[0]
                    stage = omni.usd.get_context().get_stage()

                    if self._prim_path is None:
                        if stage.HasDefaultPrim():
                            self._prim_path = omni.usd.get_stage_next_free_path(
                                stage, stage.GetDefaultPrim().GetPath().pathString + "/" + Tf.MakeValidIdentifier(name), False
                            )
                        else:
                            self._prim_path = omni.usd.get_stage_next_free_path(stage, "/" + Tf.MakeValidIdentifier(name), False)
                        omni.kit.commands.execute("CreateReference", usd_context=omni.usd.get_context(), path_to=self._prim_path, asset_path=reference_path, instanceable=False)

                    scale = 2.5
                    #some of my attempts
                    if scale is not None and scale != 1:
                        scale = float(scale)
                        UsdShade.Material(stage.GetPrimAtPath(self._prim_path)).CreateInput("texture_scale", Sdf.ValueTypeNames.Float2).Set((scale, scale))
                        for prim in Usd.PrimRange(stage.GetPrimAtPath(self._prim_path)):
                            if prim.IsA(UsdShade.Shader):
                                prim = UsdShade.Shader(prim)
                                inp = prim.GetInput("scale")
                                if inp:
                                    inp.Set(tuple(scale * value for value in inp.Get()))
                                else:
                                    prim.CreateInput("scale", Sdf.ValueTypeNames.Float2).Set((scale, scale))
                    return self._prim_path

                def method2():
                    '''
                    Read from the 'global' section of the usda:

                    ```
                    #usda 1.0
                    (
                        customLayerData = {
                        ...
                        }
                        endTimeCode = 100
                        metersPerUnit = 0.01
                        startTimeCode = 0
                        timeCodesPerSecond = 24
                        upAxis = "Y"
                    )
                    ```
                    '''
                    return self._prim_path
                

                def on_reset():
                    self._count = 0
                    label.text = "empty"

                on_reset()

                with ui.HStack():
                    ui.Button("Experiment", clicked_fn=on_click)
        

    def on_shutdown(self):
        print("[robotica.usd.experiments] robotica usd experiments shutdown")
        self._window = None
