from django.conf import settings
from django.core.signals import setting_changed
from rest_framework import ISO_8601
from rest_framework.settings import APISettings as drf_APISettings
from evercore_grpc import GRPC_TIMESTAMP


DEFAULTS = {
    # Base API policies
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication'
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_THROTTLE_CLASSES': [],
    'DEFAULT_CONTENT_NEGOTIATION_CLASS': 'rest_framework.negotiation.DefaultContentNegotiation',
    'DEFAULT_METADATA_CLASS': 'rest_framework.metadata.SimpleMetadata',
    'DEFAULT_VERSIONING_CLASS': None,

    # Generic view behavior
    'DEFAULT_PAGINATION_CLASS': None,
    'DEFAULT_FILTER_BACKENDS': [],

    # Schema
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.openapi.AutoSchema',

    # Throttling
    'DEFAULT_THROTTLE_RATES': {
        'user': None,
        'anon': None,
    },
    'NUM_PROXIES': None,

    # Pagination
    'PAGE_SIZE': None,

    # Filtering
    'SEARCH_PARAM': 'search',
    'ORDERING_PARAM': 'ordering',

    # Versioning
    'DEFAULT_VERSION': None,
    'ALLOWED_VERSIONS': None,
    'VERSION_PARAM': 'version',

    # Authentication
    'UNAUTHENTICATED_USER': 'django.contrib.auth.models.AnonymousUser',
    'UNAUTHENTICATED_TOKEN': None,

    # View configuration
    'VIEW_NAME_FUNCTION': 'rest_framework.views.get_view_name',
    'VIEW_DESCRIPTION_FUNCTION': 'rest_framework.views.get_view_description',

    # Exception handling
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
    'NON_FIELD_ERRORS_KEY': 'non_field_errors',

    # Testing
    'TEST_REQUEST_RENDERER_CLASSES': [
        'rest_framework.renderers.MultiPartRenderer',
        'rest_framework.renderers.JSONRenderer'
    ],
    'TEST_REQUEST_DEFAULT_FORMAT': 'multipart',

    # Hyperlink settings
    'URL_FORMAT_OVERRIDE': 'format',
    'FORMAT_SUFFIX_KWARG': 'format',
    'URL_FIELD_NAME': 'url',

    # Input and output formats
    'DATE_FORMAT': GRPC_TIMESTAMP,
    'DATE_INPUT_FORMATS': [ISO_8601],

    'DATETIME_FORMAT': GRPC_TIMESTAMP,
    'DATETIME_INPUT_FORMATS': [ISO_8601],

    'TIME_FORMAT': GRPC_TIMESTAMP,
    'TIME_INPUT_FORMATS': [ISO_8601],

    # Encoding
    'UNICODE_JSON': True,
    'COMPACT_JSON': True,
    'STRICT_JSON': True,
    'COERCE_DECIMAL_TO_STRING': True,
    'UPLOADED_FILES_USE_URL': True,

    # Browsable API
    'HTML_SELECT_CUTOFF': 1000,
    'HTML_SELECT_CUTOFF_TEXT': "More than {count} items...",

    # Schemas
    'SCHEMA_COERCE_PATH_PK': True,
    'SCHEMA_COERCE_METHOD_NAMES': {
        'retrieve': 'read',
        'destroy': 'delete'
    },
}


# List of settings that may be in string import notation.
IMPORT_STRINGS = [
    'DEFAULT_RENDERER_CLASSES',
    'DEFAULT_PARSER_CLASSES',
    'DEFAULT_AUTHENTICATION_CLASSES',
    'DEFAULT_PERMISSION_CLASSES',
    'DEFAULT_THROTTLE_CLASSES',
    'DEFAULT_CONTENT_NEGOTIATION_CLASS',
    'DEFAULT_METADATA_CLASS',
    'DEFAULT_VERSIONING_CLASS',
    'DEFAULT_PAGINATION_CLASS',
    'DEFAULT_FILTER_BACKENDS',
    'DEFAULT_SCHEMA_CLASS',
    'EXCEPTION_HANDLER',
    'TEST_REQUEST_RENDERER_CLASSES',
    'UNAUTHENTICATED_USER',
    'UNAUTHENTICATED_TOKEN',
    'VIEW_NAME_FUNCTION',
    'VIEW_DESCRIPTION_FUNCTION'
]


# List of settings that have been removed
REMOVED_SETTINGS = [
    'PAGINATE_BY', 'PAGINATE_BY_PARAM', 'MAX_PAGINATE_BY',
]


class APISettings(drf_APISettings):
    @property
    def user_settings(self):
        if not hasattr(self, '_user_settings'):
            self._user_settings = getattr(settings, 'GRPC_FRAMEWORK', {})
        return self._user_settings


api_settings = APISettings(None, DEFAULTS, IMPORT_STRINGS)


def reload_api_settings(*args, **kwargs):
    setting = kwargs['setting']
    if setting == 'GRPC_FRAMEWORK':
        api_settings.reload()


setting_changed.connect(reload_api_settings)
