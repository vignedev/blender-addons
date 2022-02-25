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

class RenderWebhook_Panel(bpy.types.Panel):
    bl_label = 'Render Webhook'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'output'
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        self.layout.prop(context.scene.render_webhook_settings, 'enable_webhook', text='')

    def draw(self, context):
        pass

@bpy.app.handlers.persistent
def RenderWebhook_RenderComplete(_):
    scene = bpy.context.scene
    if scene.render_webhook_settings.enable_webhook is False:
        return
    
    pref = bpy.context.preferences.addons[__name__].preferences
    blendname = bpy.data.filepath.split('/')[-1]

    requests.post(
        pref.webhook_url,
        data=json.dumps({
            'content': None,
            'embeds': [
                {
                    'title': f"Render finished (`{blendname or 'no name'}`)",
                    'color': 15110425,
                    'timestamp': datetime.datetime.now().isoformat(),
                    'footer': {
                        'text': scene.name
                    }
                    # 'fields': [
                    #     {
                    #         'name': 'Frame Range',
                    #         'value': f'```{scene.frame_start}/{scene.frame_end}```',
                    #         'inline': True
                    #     },
                    #     {
                    #         'name': 'Format',
                    #         'value': f'```{scene.render.image_settings.file_format}```',
                    #         'inline': True
                    #     }
                    # ]
                }
            ]
        }),
        headers={'Content-Type': 'application/json'}
    )

####################################################################################################

def register():
    bpy.utils.register_class(RenderWebhook_Prefs)
    bpy.utils.register_class(RenderWebhook_Settings)
    bpy.utils.register_class(RenderWebhook_TestOperator)
    bpy.utils.register_class(RenderWebhook_Panel)
    bpy.types.Scene.render_webhook_settings = bpy.props.PointerProperty(type=RenderWebhook_Settings)
    bpy.app.handlers.render_complete.append(RenderWebhook_RenderComplete)

def unregister():
    bpy.utils.unregister_class(RenderWebhook_Prefs)
    bpy.utils.unregister_class(RenderWebhook_Settings)
    bpy.utils.unregister_class(RenderWebhook_TestOperator)
    bpy.utils.unregister_class(RenderWebhook_Panel)
    del bpy.types.Scene.render_webhook_settings
    bpy.app.handlers.render_complete.remove(RenderWebhook_RenderComplete)

if __name__ == '__main__':
    register()