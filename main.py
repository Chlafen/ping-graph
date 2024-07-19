# an app that gets the ping time to google.com every 1 second and displays the result in a simple GUI graph using tkinter
from threading import Thread
import tkinter as tk
import numpy as np
from colorhsv import Colors
from config import Config
from ping3 import ping

class PingUI:
  def __init__(self, window, graph, address):
    self.graph = graph
    self.address = address
    self.window = window
    self.window.overrideredirect(1)
    self.window.wm_attributes("-topmost", True)
    self.window.wm_attributes("-alpha", 0.6)
    self.window.resizable(False, False)

    self.window.geometry("+{}+{}".format(self.window.winfo_screenwidth()-Config.WIDTH-10, 10))
    self.lastClickX = 0
    self.lastClickY = 0

    self.stop_thread = False
    self.thread = Thread(target=self.get_ping)
    self.thread.start()

    self.bind_events()

    self.window.title("Ping Graph")
    self.canvas = tk.Canvas(self.window, width=Config.WIDTH, height=Config.HEIGHT+4, bg='black', bd=0, highlightthickness=0, relief='ridge')
    # pad canvas
    self.canvas.pack_propagate(0)
    self.canvas.pack()

    self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
    self.update_graph()
    self.window.mainloop()

  def on_closing(self, e=None):
    self.stop_thread = True
    self.thread.join()
    self.window.destroy()

  def on_drag(self, event):
    x, y = event.x - self.lastClickX + self.window.winfo_x(), event.y - self.lastClickY + self.window.winfo_y()
    # clamp the window position to the screen size
    x = min(self.window.winfo_screenwidth() - Config.WIDTH, max(0, x))
    y = min(self.window.winfo_screenheight() - Config.HEIGHT, max(0, y))

    self.window.geometry("+%s+%s" % (x , y))

  def save_last_click(self, event): 
    self.lastClickX = event.x
    self.lastClickY = event.y

  def bind_events(self):
    self.window.bind("<Double-Button-1>", self.on_closing)
    self.window.bind('<Button-1>', self.save_last_click)
    self.window.bind('<B1-Motion>', self.on_drag)

  def draw_graph(self, maxping, packet_loss, bar_height):
    self.canvas.delete("all")
    maxclr = Colors.hsv2rgb(Colors.get_ping_hue(maxping), 1, 1)
    colors = [Colors.hsv2rgb(Colors.get_ping_hue(ping), 1, 1) for ping in self.graph]
    # last & max ping text
    text_x = Config.BARWIDTH * Config.GRAPHLEN + 5
    packet_loss_clr = Colors.hsv2rgb(Colors.get_ping_hue(70+packet_loss), 1, 1)
    last_ping_text = "ms:   {}".format(int(self.graph[-1]) if self.graph[-1] != 500 else 'N/A')
    max_ping_text = "max: {}".format(maxping if maxping != 500 else "N/A")
    packet_loss_text = "loss: {:.1f}%".format(packet_loss)
    self.canvas.create_text(text_x, 3 + Config.HEIGHT/7, text=last_ping_text, fill=colors[-1], anchor="w", font=("Arial", 7, "bold"))
    self.canvas.create_text(text_x, 3 + 3*Config.HEIGHT/7, text=max_ping_text, fill=maxclr, anchor="w", font=("Arial", 7, "bold"))
    self.canvas.create_text(text_x, 3 + 5* Config.HEIGHT/7, text=packet_loss_text, fill=packet_loss_clr, anchor="w", font=("Arial", 7, "bold"))
    # axis
    self.canvas.create_rectangle(0, 0, 4, Config.HEIGHT, fill="#000000", width=0)
    self.canvas.create_rectangle(0, Config.HEIGHT, Config.WIDTH, Config.HEIGHT-2, fill="#000000", width=0)

    # draw bars
    for i in range(Config.GRAPHLEN):
        X0 = (2+i*Config.BARWIDTH, 2+Config.HEIGHT)
        X1 = (X0[0]+Config.BARWIDTH, 2+Config.HEIGHT * bar_height[i])
        self.canvas.create_rectangle(X0[0], X0[1], X1[0], X1[1], fill=colors[i], width=1)

  def update_graph(self):
    bar_height = 1 - (self.graph / max(np.max(self.graph), 1))
    maxping = int(np.max(self.graph))
    packet_loss = 100 * sum(self.graph == 500) / Config.GRAPHLEN
    self.draw_graph(maxping, packet_loss, bar_height)
    self.window.after(Config.DELAY, self.update_graph)

  def get_ping(self):
    while not self.stop_thread:
      try:
        r = int(ping(self.address) * 1000)
        if r is not None:
          self.graph = np.roll(self.graph, -1) 
          self.graph[-1] = r // 1
          self.graph = np.clip(self.graph, 0, 500)
        else:
          self.graph = np.roll(self.graph, -1) 
          self.graph[-1] = 500
      except Exception as e:
          self.graph = np.roll(self.graph, -1) 
          self.graph[-1] = 500


if __name__ == "__main__":
  graph = np.zeros(Config.GRAPHLEN)
  root = tk.Tk()
  PingUI(root, graph, Config.ADR)
