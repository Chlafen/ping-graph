
import colorsys
from config import Config


class Colors:
  '''
  A class to hold the colors used in the graph
  '''
  def get_ping_hue(ping):
    '''
    Get the hue of the color to represent the ping time
    '''
    ping = min(120, ping)
    return Config.HUEMIN + (Config.HUEMAX - Config.HUEMIN) * (ping/120) 
  
  def hsv2rgb(h,s,v):
    '''
    Convert hsv to rgb
    '''
    rgb = tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h,s,v))
    return '#%02x%02x%02x' % rgb