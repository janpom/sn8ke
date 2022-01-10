import machine

from frozen.alert import alert
from frozen.display import DISPLAY
from frozen.buttons import BUTTON_DOWN


if not BUTTON_DOWN.value():
    DISPLAY.print("starting sn8ke...")
    try:
        import sn8ke
        sn8ke.run()
    except ImportError as e:
        alert("failed to import: %s" % e, no_reset=True)
        machine.reset()
