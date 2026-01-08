from drf_spectacular.openapi import AutoSchema

class NoPaginationSchema(AutoSchema):
    def get_override_parameters(self, path, method):
        params = super().get_override_parameters(path, method)
        return [p for p in params if p.name not in ('page', 'page_size')]
