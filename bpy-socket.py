import bpy
import socket
import queue
import socketserver
import struct
import threading

bl_info = {
    'name': 'bpy socket',
    'author': 'vignedev',
    'version': (0, 0, 1),
    'blender': (3, 4, 0),
    'description': 'Expose bpy as a TCP server',
    'warning': 'Security was literally at the bottom of the priority list.'
}

# Globals
server: socketserver.TCPServer = None
server_thread: threading.Thread = None
commands = queue.Queue()

# ------------------------------------------------------------------------------------------------ #

class CommandHandler(socketserver.BaseRequestHandler):
    def recvall(self, sock):
        data = bytearray()
        while True:
            packet = sock.recv(4096)
            if not packet:
                break
            data.extend(packet)
        return data if len(data) > 0 else None

    def handle(self):
        global commands

        self.message = self.recvall(self.request)
        if self.message is not None:
            print(f'[bpy.socket] received script of {len(self.message)} bytes')
            commands.put(self.message)
        else:
            print('[bpy.socket] received None as message')

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

def destroy_socket(*args):
    global server
    global server_thread
    global commands

    with commands.mutex:
        commands.queue.clear()

    if server is not None:
        server.shutdown()
        server.server_close()
        server_thread.join()
        server = None
        server_thread = None
        print('[bpy.socket] Destroyed socket')
        return

def create_socket(*args):
    global server
    global server_thread

    pref: BpySocketPrefs = bpy.context.preferences.addons[__name__].preferences

    destroy_socket()

    server = ThreadedTCPServer((pref.address, pref.port), CommandHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    print('[bpy.socket] Created socket')

# ------------------------------------------------------------------------------------------------ #

@bpy.app.handlers.persistent
def on_project_load(*args):
    destroy_socket()

def evaluators(*args):
    global commands

    while not commands.empty() and commands.mutex:
        command = commands.get()
        commands.task_done()
        try:
            exec(command)
        except Exception as ex:
            print(ex)

    pref: BpySocketPrefs = bpy.context.preferences.addons[__name__].preferences
    return pref.refresh_rate

def destroy_socket_bpy(self, context):
    destroy_socket()

# ------------------------------------------------------------------------------------------------ #

class BpySocketToggle(bpy.types.Operator):
    bl_label = 'Toggle bpy.socket'
    bl_idname = 'bpysocket.toggle'
    bl_options = { 'INTERNAL' }
    bl_description = 'Toggles the bpy.socket'

    def execute(self, context):
        global server
        if server is None:
            try:
                create_socket()
            except Exception as ex:
                server = None
                self.report({'ERROR'}, f'Failed to create a TCP Socket:\n{str(ex)}')
                return {'CANCELLED'}

            if bpy.app.timers.is_registered(evaluators):
                bpy.app.timers.unregister(evaluators)
            bpy.app.timers.register(evaluators)
        else:
            destroy_socket()
            if bpy.app.timers.is_registered(evaluators):
                bpy.app.timers.unregister(evaluators)
        return {'FINISHED'}

class BpySocketPrefs(bpy.types.AddonPreferences):
    bl_idname = __name__

    address: bpy.props.StringProperty(
        name='Address',
        description='Address to bind the port to, use localhost or any of its equivalents to make it only local.',
        default='localhost',
        update=destroy_socket_bpy
    )
    port: bpy.props.IntProperty(
        name='Port',
        description='Port to which to bind the port to',
        default=47787,
        update=destroy_socket_bpy
    )
    hide_label: bpy.props.BoolProperty(
        name='Hide Label',
        description='Hides the label and displays only the icon on the menu bar',
        default=False
    )
    refresh_rate: bpy.props.FloatProperty(
        name='Refresh Rate',
        description='Evaluate queued commands every this amount of seconds',
        default=1.0,
        min=0.01
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'address')
        layout.prop(self, 'port')
        layout.prop(self, 'hide_label')
        layout.prop(self, 'refresh_rate')

def bpysocket_drawer(self, context):
    if context.region.alignment == 'RIGHT':
        pref: BpySocketPrefs = context.preferences.addons[__name__].preferences
        layout = self.layout

        text = 'bpy.socket' if not pref.hide_label else ''

        if not server: layout.operator('bpysocket.toggle', icon='PLAY' , text=text, depress=False)
        else:          layout.operator('bpysocket.toggle', icon='PAUSE', text=text, depress=True)

# ------------------------------------------------------------------------------------------------ #

classes = (
    BpySocketToggle,
    BpySocketPrefs
)

def register():
    bpy.app.handlers.load_post.append(on_project_load)
    for c in classes: bpy.utils.register_class(c)
    bpy.types.TOPBAR_HT_upper_bar.prepend(bpysocket_drawer)

def unregister():
    destroy_socket()
    bpy.app.handlers.load_post.remove(on_project_load)
    for c in classes: bpy.utils.unregister_class(c)
    bpy.types.TOPBAR_HT_upper_bar.remove(bpysocket_drawer)

if __name__ == '__main__':
    register()