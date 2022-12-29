bl_info = {
    'name': 'Render Webhook',
    'author': 'vignedev',
    'version': (0, 0, 0),
    'blender': (3, 1, 0),
    'description': 'Send a message post-render to a given webhook.',
    'category': 'Render',
    'warning': 'Mostly for Discord Webhooks.'
}

from email.policy import default
from re import M
import bpy
import json
import requests
import datetime

####################################################################################################

class RenderWebhook_TestOperator(bpy.types.Operator):
    bl_idname = 'render.webhook_test'
    bl_label = 'Send a test message to saved webhook'

    def execute(self, context):
        pref = context.preferences.addons[__name__].preferences
        requests.post(
            pref.webhook_url,
            data=json.dumps({
                'content': '`render-webhook.py` works, congratulations.'
            }),
            headers={'Content-Type': 'application/json'}
        )

        return {'FINISHED'}

class RenderWebhook_Prefs(bpy.types.AddonPreferences):
    bl_idname = __name__
    webhook_url: bpy.props.StringProperty(name='Webhook URL',
                                           description='URL to a webhook endpoint')
    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'webhook_url')
        layout.operator('render.webhook_test')

class RenderWebhook_Settings(bpy.types.PropertyGroup):
    enable_webhook: bpy.props.BoolProperty(
        name='Enable Render Webhook',
        description='Hook up the webhook to the render_complete handler.',
        default=False
    )

    enable_webhook_render_cancel: bpy.props.BoolProperty(
        name='render_cancel',
        description='...on canceling a render job',
        default=True
    )
    enable_webhook_render_complete: bpy.props.BoolProperty(
        name='render_complete',
        description='...on completion of render job',
        default=True
    )
    enable_webhook_render_init: bpy.props.BoolProperty(
        name='render_init',
        description='...on initialization of a render job',
        default=True
    )
    enable_webhook_render_post: bpy.props.BoolProperty(
        name='render_post',
        description='...on render (after)',
        default=False
    )
    enable_webhook_render_pre: bpy.props.BoolProperty(
        name='render_pre',
        description='...on render (before)',
        default=False
    )
    enable_webhook_render_stats: bpy.props.BoolProperty(
        name='render_stats',
        description='...on printing render statistics',
        default=False
    )
    enable_webhook_render_write: bpy.props.BoolProperty(
        name='render_write',
        description='...on writing a render frame (directly after the frame is written)',
        default=False
    )

class RenderWebhook_Panel(bpy.types.Panel):
    bl_label = 'Render Webhook'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'output'
    bl_options = {'DEFAULT_CLOSED'}
    bl_idname = 'RENDERWEBHOOK_PT_OUTPUT'

    def draw_header(self, context):
        self.layout.prop(context.scene.render_webhook_settings, 'enable_webhook', text='')

    def draw(self, context):
        self.layout.label(text='Execute on these events:')
        box = self.layout.box()
        box.enabled = context.scene.render_webhook_settings.enable_webhook

        box.prop(context.scene.render_webhook_settings, 'enable_webhook_render_cancel',   text='On Render Job Cancelled')
        box.prop(context.scene.render_webhook_settings, 'enable_webhook_render_complete', text='On Render Job Completed')
        box.prop(context.scene.render_webhook_settings, 'enable_webhook_render_init',     text='On Render Job started')
        box.prop(context.scene.render_webhook_settings, 'enable_webhook_render_post',     text='After rendering a frame')
        box.prop(context.scene.render_webhook_settings, 'enable_webhook_render_pre',      text='Before rendering a frame')
        box.prop(context.scene.render_webhook_settings, 'enable_webhook_render_stats',    text='After Render Statistics')
        box.prop(context.scene.render_webhook_settings, 'enable_webhook_render_write',    text='After Render Frame Written')
        pass

def RenderWebhook_Execute(scene, event_name):
    pref = bpy.context.preferences.addons[__name__].preferences
    blendname = bpy.data.filepath or 'no name'

    requests.post(
        pref.webhook_url,
        data=json.dumps({
            'content': None,
            'embeds': [
                {
                    'title': f"`{event_name}`",
                    'color': 15110425,
                    'timestamp': datetime.datetime.now().isoformat(),
                    'footer': {
                        'text': scene.name
                    },
                    'fields': [
                        {
                            "name": "file",
                            "value": blendname,
                            "inline": False
                        }
                    ]
                }
            ]
        }),
        headers={'Content-Type': 'application/json'}
    )

####################################################################################################

@bpy.app.handlers.persistent
def RenderWebhook_Callback_render_cancel(_):
    scene = bpy.context.scene
    settings = scene.render_webhook_settings
    if settings.enable_webhook is False or settings.enable_webhook_render_cancel is False:
        return
    RenderWebhook_Execute(bpy.context.scene, 'render_cancel')
    
@bpy.app.handlers.persistent
def RenderWebhook_Callback_render_complete(_):
    scene = bpy.context.scene
    settings = scene.render_webhook_settings
    if settings.enable_webhook is False or settings.enable_webhook_render_complete is False:
        return
    RenderWebhook_Execute(bpy.context.scene, 'render_complete')
    
@bpy.app.handlers.persistent
def RenderWebhook_Callback_render_init(_):
    scene = bpy.context.scene
    settings = scene.render_webhook_settings
    if settings.enable_webhook is False or settings.enable_webhook_render_init is False:
        return
    RenderWebhook_Execute(bpy.context.scene, 'render_init')
    
@bpy.app.handlers.persistent
def RenderWebhook_Callback_render_post(_):
    scene = bpy.context.scene
    settings = scene.render_webhook_settings
    if settings.enable_webhook is False or settings.enable_webhook_render_post is False:
        return
    RenderWebhook_Execute(bpy.context.scene, 'render_post')
    
@bpy.app.handlers.persistent
def RenderWebhook_Callback_render_pre(_):
    scene = bpy.context.scene
    settings = scene.render_webhook_settings
    if settings.enable_webhook is False or settings.enable_webhook_render_pre is False:
        return
    RenderWebhook_Execute(bpy.context.scene, 'render_pre')
    
@bpy.app.handlers.persistent
def RenderWebhook_Callback_render_stats(_):
    scene = bpy.context.scene
    settings = scene.render_webhook_settings
    if settings.enable_webhook is False or settings.enable_webhook_render_stats is False:
        return
    RenderWebhook_Execute(bpy.context.scene, 'render_stats')
    
@bpy.app.handlers.persistent
def RenderWebhook_Callback_render_write(_):
    scene = bpy.context.scene
    settings = scene.render_webhook_settings
    if settings.enable_webhook is False or settings.enable_webhook_render_write is False:
        return
    RenderWebhook_Execute(bpy.context.scene, 'render_write')
    

def register():
    bpy.utils.register_class(RenderWebhook_Prefs)
    bpy.utils.register_class(RenderWebhook_Settings)
    bpy.utils.register_class(RenderWebhook_TestOperator)
    bpy.utils.register_class(RenderWebhook_Panel)
    bpy.types.Scene.render_webhook_settings = bpy.props.PointerProperty(type=RenderWebhook_Settings)

    bpy.app.handlers.render_cancel.append(RenderWebhook_Callback_render_cancel)
    bpy.app.handlers.render_complete.append(RenderWebhook_Callback_render_complete)
    bpy.app.handlers.render_init.append(RenderWebhook_Callback_render_init)
    bpy.app.handlers.render_post.append(RenderWebhook_Callback_render_post)
    bpy.app.handlers.render_pre.append(RenderWebhook_Callback_render_pre)
    bpy.app.handlers.render_stats.append(RenderWebhook_Callback_render_stats)
    bpy.app.handlers.render_write.append(RenderWebhook_Callback_render_write)

def unregister():
    bpy.utils.unregister_class(RenderWebhook_Prefs)
    bpy.utils.unregister_class(RenderWebhook_Settings)
    bpy.utils.unregister_class(RenderWebhook_TestOperator)
    bpy.utils.unregister_class(RenderWebhook_Panel)
    del bpy.types.Scene.render_webhook_settings

    bpy.app.handlers.render_cancel.remove(RenderWebhook_Callback_render_cancel)
    bpy.app.handlers.render_complete.remove(RenderWebhook_Callback_render_complete)
    bpy.app.handlers.render_init.remove(RenderWebhook_Callback_render_init)
    bpy.app.handlers.render_post.remove(RenderWebhook_Callback_render_post)
    bpy.app.handlers.render_pre.remove(RenderWebhook_Callback_render_pre)
    bpy.app.handlers.render_stats.remove(RenderWebhook_Callback_render_stats)
    bpy.app.handlers.render_write.remove(RenderWebhook_Callback_render_write)

if __name__ == '__main__':
    register()