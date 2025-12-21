from drf_spectacular.openapi import AutoSchema

class NoPaginationSchema(AutoSchema):
    def get_override_parameters(self, path, method):
        # Barcha parametrlarni olamiz
        params = super().get_override_parameters(path, method)
        # page va page_size parametrlari filter qilinadi → Swagger’da chiqmaydi
        return [p for p in params if p.name not in ('page', 'page_size')]
