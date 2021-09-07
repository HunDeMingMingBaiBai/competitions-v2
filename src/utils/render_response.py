from rest_framework.renderers import JSONRenderer

class CustomJsonRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if renderer_context:
            if renderer_context['response'].status_code >= 400:
                res = {
                    'code': 'fail',
                    'fail_message': '服务器处理错误',
                    'error': data
                }
            else:
                res = {
                    'code': 'success',
                    'data': data
                }
            return super().render(res, accepted_media_type, renderer_context)
        else:
            return super().render(data, accepted_media_type, renderer_context)

def success_data(data=None):
    result = {
        'code': 'success',
        'data': data
    }
    return result


