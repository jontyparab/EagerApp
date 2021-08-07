from django.core.validators import RegexValidator

tag_validator = RegexValidator(
    regex='^[a-z0-9\-_\s]+$',
    message='Only lowercase alphanumeric, dash, space and hyphens are allowed.',
    code='Enter a valid tag.'
)

username_validator = RegexValidator(
    regex='^[a-zA-Z0-9]+$',
    message='Only alphanumeric characters are allowed.',
    code='Enter a valid username.'
)
