from tkinter import Tk

from zigbear.custom_protocol.scapy_layers import ZigbearLightControlLayer


class Lamp():
    def __init__(self, protocol_stack):
        self.window = Tk()
        self.window.title("Secure Lamp")
        self.window['bg'] = '#000000'
        self.protocol_stack = protocol_stack

    @staticmethod
    def hex_to_rgb(hex):
        hex = hex.lstrip('#')
        hlen = len(hex)
        return tuple(int(hex[i:i + hlen // 3], 16) for i in range(0, hlen, hlen // 3))

    def handle_toggle(self):
        current_color = self.window['bg']
        r, g, b = self.hex_to_rgb(current_color)
        r, g, b = 255 - r, 255 - g, 255 - b
        self.window['bg'] = '#%02x%02x%02x' % (r, g, b)

    def handle_set_brightness(self, brightness):
        self.window['bg'] = '#%02x%02x%02x' % (brightness, brightness, brightness)

    def handle_cmd(self, zlc):
        if zlc.message_type == 0:
            self.handle_toggle()
        elif zlc.message_type == 1:
            self.handle_set_brightness(zlc.brightness)

    def wait_for_input(self):
        def handler(session):
            data = session.receive()
            try:
                zlc = ZigbearLightControlLayer(data)
                self.handle_cmd(zlc)
            except:
                pass
            session.close()

        listener = self.protocol_stack.listen(100, handler)
        self.window.mainloop()
        listener.close()
