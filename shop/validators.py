from django.core.exceptions import ValidationError


def validate_file_size(value):
    filesize= value.size
    
    if filesize > 20971520:
        raise ValidationError("The maximum media size that can be uploaded is 20MB")
    else:
        return value
        
#1048576 - 1MB
#10485760 - 10MB
#20971520 - 20MB
