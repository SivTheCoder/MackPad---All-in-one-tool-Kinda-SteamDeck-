import board
import analogio
import busio, time

from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC, Key
from kmk.scanners import DiodeOrientation
from kmk.scanners.keypad import MatrixScanner, KeysScanner
from kmk.modules import Module
from kmk.modules.layers import Layers
from kmk.modules.macros import Delay, Press, Release, Tap, Macros
from kmk.modules.holdtap import HoldTap

from kmk.extensions.RGB import RGB
from kmk.extensions.rgb import AnimationModes
from kmk.extensions.media_keys import MediaKeys
from kmk.extensions.display import Display, TextEntry, ImageEntry
from kmk.extensions.display.ssd1306 import SSD1306


# =========================
# ANALOG ENCODER MODULE
# =========================

class AnalogEncoder(Module):
    def __init__(self, analog_pin, adc_thresholds, key_clockwise, key_counterclockwise):
        self.analog_pin = analog_pin
        self.thresholds = adc_thresholds
        self.key_cw = key_clockwise
        self.key_ccw = key_counterclockwise

        self.adc_input = None
        self.previous_state = None

    def during_bootup(self, keyboard):
        self.adc_input = analogio.AnalogIn(self.analog_pin)

    def before_matrix_scan(self, keyboard):
        adc_value = self.adc_input.value
        current_state = self._determine_state(adc_value)

        if self.previous_state is None:
            print("Initial state:", current_state, "ADC:", adc_value)

        elif current_state != self.previous_state:
            print("STATE CHANGE:", self.previous_state, "→", current_state, "ADC:", adc_value)

            if self.previous_state == 3:
                if current_state == 2:
                    keyboard.tap_key(self.key_ccw)
                elif current_state == 1:
                    keyboard.tap_key(self.key_cw)

        self.previous_state = current_state
        return keyboard

    def _determine_state(self, adc_value):
        for index, threshold in enumerate(self.thresholds):
            if adc_value < threshold:
                return index
        return len(self.thresholds)

    def after_matrix_scan(self, keyboard):
        return keyboard


# =========================
# KEYBOARD CLASS
# =========================

class MackPad(KMKKeyboard):
    def __init__(self):
        super().__init__()

        self.matrix = [
            MatrixScanner(
                column_pins=(board.D1, board.D2, board.D3),
                row_pins=(board.D7, board.D8, board.D9),
                columns_to_anodes=DiodeOrientation.ROW2COL
            ),
            KeysScanner(
                pins=[board.D10],
                value_when_pressed=False,
            ),
        ]


keyboard = MackPad()
keyboard.extensions.append(MediaKeys())


# =========================
# ENCODER SETUP
# =========================

encoder_module = AnalogEncoder(
    analog_pin=board.A0,
    adc_thresholds=[1270, 10000, 40000],
    key_clockwise=KC.VOLU,
    key_counterclockwise=KC.VOLD,
)

keyboard.modules.append(encoder_module)


# =========================
# RGB CONTROL
# =========================

rgb_enabled = True


class LayerBasedRGB(RGB):
    def on_layer_change(self, layer_index):
        if rgb_enabled:
            if layer_index == 0:
                self.set_hsv_fill(79, self.sat_default, self.val_default)
            elif layer_index == 1:
                self.set_hsv_fill(170, self.sat_default, self.val_default)
            elif layer_index == 2:
                self.set_hsv_fill(20, self.sat_default, self.val_default)
            elif layer_index == 3:
                self.set_hsv_fill(180, self.sat_default, self.val_default)
            elif layer_index == 4:
                self.set_hsv_fill(225, self.sat_default, self.val_default)
            elif layer_index == 5:
                self.set_hsv_fill(0, 0, self.val_default)
        else:
            self.set_hsv_fill(0, 0, 0)

        if layer_index == 6:
            self.set_hsv_fill(0, 0, 0)
            self.set_hsv(0, self.sat_default, 100 if rgb_enabled else 40, 8)
            self.set_hsv(0, self.sat_default, 30 if rgb_enabled else 10, 3)

        self.show()

    def on_layer_change_flash(self):
        if rgb_enabled:
            self.set_hsv_fill(0, 255, 15)
        else:
            self.set_hsv_fill(0, 255, 10)
        self.show()


rgb_controller = LayerBasedRGB(
    pixel_pin=board.D6,
    num_pixels=9,
    hue_default=79,
    sat_default=255,
    val_default=67,
)

keyboard.extensions.append(rgb_controller)


# =========================
# LAYER MANAGEMENT
# =========================

class RGBLayerController(Layers):
    def __init__(self):
        super().__init__()
        self.active_layer_index = 0

    def activate_layer(self, keyboard, layer, idx=None):
        super().activate_layer(keyboard, layer, idx)

        if layer != 6:
            rgb_controller.on_layer_change_flash()
            time.sleep(0.15)
            self.active_layer_index = layer

        rgb_controller.on_layer_change(layer)

    def deactivate_layer(self, keyboard, layer):
        super().deactivate_layer(keyboard, layer)
        rgb_controller.on_layer_change_flash()
        rgb_controller.on_layer_change(keyboard.active_layers[0])


layer_controller = RGBLayerController()
keyboard.modules.append(layer_controller)


# =========================
# MACROS
# =========================

macro_module = Macros()
keyboard.modules.append(macro_module)


MACRO_SPAM = KC.MACRO("chargoggagoggmanchauggagoggchaubunagungamaugg")

MACRO_NUMBERS = KC.MACRO(
    " 000000000011111111112222222222333333333344444444445555555555666666666677777777778888888888999999999900000000 "
)

MUTE_DISCORD = KC.MACRO(
    Press(KC.RALT), Press(KC.RSHIFT), Tap(KC.M),
    Release(KC.RALT), Release(KC.RSHIFT)
)

DEAFEN_DISCORD = KC.MACRO(
    Press(KC.RALT), Press(KC.RSHIFT), Tap(KC.D),
    Release(KC.RALT), Release(KC.RSHIFT)
)


# =========================
# HOLD-TAP SETUP
# =========================

hold_tap_module = HoldTap()
keyboard.modules.append(hold_tap_module)


# =========================
# ROTARY BUTTON LOGIC
# =========================

rotary_mode_mute = True

icon_sound = "sound16.bmp"
icon_play = "play16.bmp"

icon_display = ImageEntry(image=icon_sound, x=112)


class EncoderPressKey(Key):
    def __init__(self, primary_key, secondary_key):
        self.primary = primary_key
        self.secondary = secondary_key

    def on_press(self, keyboard, coord_int=None):
        keyboard.add_key(self.primary if rotary_mode_mute else self.secondary)

    def on_release(self, keyboard, coord_int=None):
        keyboard.remove_key(self.primary if rotary_mode_mute else self.secondary)


class EncoderModeToggle(Key):
    def on_press(self, keyboard, coord_int=None):
        global rotary_mode_mute
        rotary_mode_mute = not rotary_mode_mute

        icon_display.setImage(icon_sound if rotary_mode_mute else icon_play)
        display.render(layer_controller.active_layer_index)


class RGBToggle(Key):
    def on_press(self, keyboard, coord_int=None):
        global rgb_enabled
        rgb_enabled = not rgb_enabled


encoder_tap_key = EncoderPressKey(KC.MUTE, KC.MPLY)
encoder_hold_key = EncoderModeToggle()
rgb_toggle_key = RGBToggle()

ENCODER_KEY = KC.HT(encoder_tap_key, encoder_hold_key, prefer_hold=True, tap_time=300)
MODE_KEY = KC.HT(KC.ENTER, KC.MO(6), prefer_hold=True, tap_time=180)


# =========================
# DISPLAY
# =========================

i2c = busio.I2C(board.SCL, board.SDA)

oled_driver = SSD1306(i2c=i2c)

display = Display(
    display=oled_driver,
    width=128,
    height=32,
    brightness=0.4,
)

display.entries = [
    TextEntry(text="MackPad v1.0", x=0, y=0),
    icon_display,
    TextEntry(text="Default", x=0, y=12, layer=0),
    TextEntry(text="Speedrun", x=0, y=12, layer=1),
    TextEntry(text="Editing", x=0, y=12, layer=2),
    TextEntry(text="Custom 1", x=0, y=12, layer=3),
    TextEntry(text="Custom 2", x=0, y=12, layer=4),
    TextEntry(text="Numpad", x=0, y=12, layer=5),
    TextEntry(text="Mode Swap", x=0, y=12, layer=6),
]

keyboard.extensions.append(display)


# =========================
# KEYMAP
# =========================

keyboard.keymap = [
    [
        MACRO_SPAM, MACRO_NUMBERS, KC.SPACE,
        KC.VOLD, KC.MPLY, KC.VOLU,
        MUTE_DISCORD, DEAFEN_DISCORD, MODE_KEY,
        ENCODER_KEY
    ],
]


# =========================
# START
# =========================

if __name__ == "__main__":
    keyboard.go()