"""Color themes."""
from dataclasses import dataclass
import numpy as np


@dataclass
class ColorTheme:
    """Represents a color theme for curves."""

    breakpoints: dict[float | None, tuple[str, str]]
    linewidth: float = 4.0
    linewidth_increase: float = 1.1

    @staticmethod
    def highspeed_train() -> 'ColorTheme':
        """Color theme for high-speed trains (data in km/h)."""
        bp = {
            None: ('#9C59FF', '400+'),
            400.0: ('#009B33', '350+'),
            350.0: ('#00D219', '300+'),
            300.0: ('#A1FC00', '250+'),
            250.0: ('#FFFF00', '200+'),
            200.0: ('#FF9500', '160+'),
            160.0: ('#FF0000', '<160'),
        }
        return ColorTheme(breakpoints=bp)

    @staticmethod
    def lowspeed_train() -> 'ColorTheme':
        """Color theme for low-speed trains (data in km/h)."""
        bp = {
            None: ('#9C59FF', '200+'),
            200.0: ('#009B33', '160+'),
            160.0: ('#00D219', '120+'),
            120.0: ('#A1FC00', '100+'),
            100.0: ('#FFFF00', '80+'),
            80.0: ('#FF9500', '60+'),
            60.0: ('#FF0000', '<60'),
        }
        return ColorTheme(breakpoints=bp)

    def plot(self, ax, x, y, color_value):
        """Plot curve with color theme."""
        bp = self.breakpoints
        lw = self.linewidth
        default_color, default_label = bp[None]
        ax.plot(x, y, default_color, linewidth=lw, label=default_label)
        for value_limit, (color, label) in bp.items():
            if value_limit is None:
                continue
            lw = lw * self.linewidth_increase
            mask_fail = color_value < value_limit
            y_fail = y.copy()
            y_fail[np.logical_not(mask_fail)] = np.nan
            ax.plot(x, y_fail, color, linewidth=lw, label=label)
