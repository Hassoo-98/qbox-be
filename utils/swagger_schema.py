"""
Reusable Swagger schema utilities for DRF-YASG.
Import this module in your views to simplify swagger documentation.
"""
from drf_yasg import openapi
from rest_framework import serializers


def get_serializer_schema(serializer_class, many=False):
    """
    Convert a DRF serializer class to an OpenAPI schema.
    This allows using serializers directly in swagger documentation.
    """
    if serializer_class is None:
        return openapi.Schema(type=openapi.TYPE_OBJECT)
    
    # Create an instance to get fields
    if many:
        serializer = serializer_class(many=True)
    else:
        serializer = serializer_class()
    
    properties = {}
    required_fields = []
    
    for field_name, field in serializer.fields.items():
        # Determine field type
        field_type = None
        format_str = None
        
        if isinstance(field, serializers.CharField):
            field_type = openapi.TYPE_STRING
            format_str = 'string'
        elif isinstance(field, serializers.IntegerField):
            field_type = openapi.TYPE_INTEGER
            format_str = 'integer'
        elif isinstance(field, serializers.BooleanField):
            field_type = openapi.TYPE_BOOLEAN
        elif isinstance(field, serializers.EmailField):
            field_type = openapi.TYPE_STRING
            format_str = 'email'
        elif isinstance(field, serializers.URLField):
            field_type = openapi.TYPE_STRING
            format_str = 'uri'
        elif isinstance(field, serializers.DateTimeField):
            field_type = openapi.TYPE_STRING
            format_str = 'date-time'
        elif isinstance(field, serializers.DateField):
            field_type = openapi.TYPE_STRING
            format_str = 'date'
        elif isinstance(field, serializers.DecimalField):
            field_type = openapi.TYPE_NUMBER
            format_str = 'decimal'
        elif isinstance(field, serializers.FloatField):
            field_type = openapi.TYPE_NUMBER
            format_str = 'float'
        elif isinstance(field, serializers.ListField):
            field_type = openapi.TYPE_ARRAY
        elif isinstance(field, serializers.DictField):
            field_type = openapi.TYPE_OBJECT
        elif isinstance(field, serializers.JSONField):
            field_type = openapi.TYPE_OBJECT
        else:
            field_type = openapi.TYPE_STRING
        
        # Create schema for the field
        field_schema = openapi.Schema(type=field_type)
        
        if format_str:
            field_schema.format = format_str
        
        # Add description if available
        if hasattr(field, 'help_text') and field.help_text:
            field_schema.description = field.help_text
        
        # Add default value
        if hasattr(field, 'default') and field.default != serializers.empty:
            field_schema.default = field.default
        
        # Add min/max for numeric fields
        if hasattr(field, 'min_value') and field.min_value is not None:
            field_schema.minimum = field.min_value
        if hasattr(field, 'max_value') and field.max_value is not None:
            field_schema.maximum = field.max_value
        
        # Add min/max length for string fields
        if hasattr(field, 'min_length') and field.min_length is not None:
            field_schema.minLength = field.min_length
        if hasattr(field, 'max_length') and field.max_length is not None:
            field_schema.maxLength = field.max_length
        
        properties[field_name] = field_schema
        
        if field.required:
            required_fields.append(field_name)
    
    schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties=properties
    )
    
    if required_fields:
        schema.required = required_fields
    
    return schema


# ============== Common Schema Types ==============
SuccessBoolean = openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True)
StatusCode = openapi.Schema(type=openapi.TYPE_INTEGER, example=200)
MessageField = openapi.Schema(type=openapi.TYPE_STRING, example="Operation successful")
EmptyDataField = openapi.Schema(type=openapi.TYPE_OBJECT, additional_properties={})


# ============== Common Response Schemas ==============

def create_success_response(data_schema=None, description="Success", message="Operation successful"):
    """Create a standardized success response schema."""
    properties = {
        'success': SuccessBoolean,
        'statusCode': openapi.Schema(type=openapi.TYPE_INTEGER, example=200),
        'message': openapi.Schema(type=openapi.TYPE_STRING, example=message),
    }
    if data_schema:
        properties['data'] = data_schema
    return openapi.Response(
        description=description,
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties=properties
        )
    )


def create_paginated_response(item_schema, tag="Items"):
    """Create a paginated list response schema."""
    return openapi.Response(
        description=f"List of {tag}",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': SuccessBoolean,
                'statusCode': openapi.Schema(type=openapi.TYPE_INTEGER, example=200),
                'message': MessageField,
                'data': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'next': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                        'results': openapi.Schema(type=openapi.TYPE_ARRAY, items=item_schema),
                    }
                ),
            }
        )
    )


# ============== Error Response Schemas ==============

ValidationErrorResponse = openapi.Response(
    description="Validation errors",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
            'statusCode': openapi.Schema(type=openapi.TYPE_INTEGER, example=400),
            'message': openapi.Schema(type=openapi.TYPE_STRING, example="Validation failed"),
            'errors': openapi.Schema(type=openapi.TYPE_OBJECT, additional_properties={}),
        }
    )
)

NotFoundResponse = openapi.Response(
    description="Resource not found",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
            'statusCode': openapi.Schema(type=openapi.TYPE_INTEGER, example=404),
            'message': openapi.Schema(type=openapi.TYPE_STRING, example="Resource not found"),
        }
    )
)

UnauthorizedResponse = openapi.Response(
    description="Authentication failed",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
            'statusCode': openapi.Schema(type=openapi.TYPE_INTEGER, example=401),
            'message': openapi.Schema(type=openapi.TYPE_STRING, example="Invalid credentials"),
        }
    )
)

ForbiddenResponse = openapi.Response(
    description="Access forbidden",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
            'statusCode': openapi.Schema(type=openapi.TYPE_INTEGER, example=403),
            'message': openapi.Schema(type=openapi.TYPE_STRING, example="Permission denied"),
        }
    )
)

ServerErrorResponse = openapi.Response(
    description="Internal server error",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
            'statusCode': openapi.Schema(type=openapi.TYPE_INTEGER, example=500),
            'message': openapi.Schema(type=openapi.TYPE_STRING, example="Internal server error"),
        }
    )
)


# ============== Standard Response Configurations ==============

COMMON_RESPONSES = {
    400: ValidationErrorResponse,
    404: NotFoundResponse,
    500: ServerErrorResponse,
}

AUTH_RESPONSES = {
    400: ValidationErrorResponse,
    401: UnauthorizedResponse,
    403: ForbiddenResponse,
    404: NotFoundResponse,
    500: ServerErrorResponse,
}


# ============== Decorator Helper ==============

class SwaggerHelper:
    """
    Helper class to create consistent swagger documentation.
    
    Usage:
    from utils.swagger_schema import SwaggerHelper
    
    swagger = SwaggerHelper(tag="Users")
    
    @swagger_auto_schema(
        **swagger.list_operation(summary="List users", serializer=UserSerializer),
        ...
    )
    def get(self, request):
        ...
    """
    
    def __init__(self, tag="API"):
        self.tag = tag
    
    def list_operation(self, summary=None, description=None, serializer=None, responses=None):
        """Generate swagger for list operations (GET)."""
        schema = get_serializer_schema(serializer) if serializer else openapi.Schema(type=openapi.TYPE_OBJECT)
        return {
            'operation_summary': f"[{self.tag}] {summary or f'List {self.tag.lower()}'}",
            'operation_description': description or f"Retrieve a list of all {self.tag.lower()}.",
            'tags': [self.tag],
            'responses': responses or {
                200: create_paginated_response(
                    get_serializer_schema(serializer) if serializer else openapi.Schema(type=openapi.TYPE_OBJECT),
                    tag=self.tag
                ),
                **COMMON_RESPONSES
            }
        }
    
    def retrieve_operation(self, summary=None, description=None, serializer=None, responses=None):
        """Generate swagger for retrieve operations (GET by ID)."""
        return {
            'operation_summary': f"[{self.tag}] {summary or f'Get {self.tag.lower()}'}",
            'operation_description': description or f"Retrieve a specific {self.tag.lower()} by ID.",
            'tags': [self.tag],
            'responses': responses or {
                200: create_success_response(
                    get_serializer_schema(serializer) if serializer else openapi.Schema(type=openapi.TYPE_OBJECT),
                    description="Resource retrieved successfully"
                ),
                **COMMON_RESPONSES
            }
        }
    
    def create_operation(self, summary=None, description=None, serializer=None, responses=None):
        """Generate swagger for create operations (POST)."""
        return {
            'operation_summary': f"[{self.tag}] {summary or f'Create {self.tag.lower()}'}",
            'operation_description': description or f"Create a new {self.tag.lower()}.",
            'tags': [self.tag],
            'request_body': serializer,
            'responses': responses or {
                201: create_success_response(
                    get_serializer_schema(serializer) if serializer else openapi.Schema(type=openapi.TYPE_OBJECT),
                    description="Resource created successfully"
                ),
                **COMMON_RESPONSES
            }
        }
    
    def update_operation(self, summary=None, description=None, serializer=None, responses=None):
        """Generate swagger for update operations (PUT/PATCH)."""
        return {
            'operation_summary': f"[{self.tag}] {summary or f'Update {self.tag.lower()}'}",
            'operation_description': description or f"Update an existing {self.tag.lower()}.",
            'tags': [self.tag],
            'request_body': serializer,
            'responses': responses or {
                200: create_success_response(
                    get_serializer_schema(serializer) if serializer else openapi.Schema(type=openapi.TYPE_OBJECT),
                    description="Resource updated successfully"
                ),
                **COMMON_RESPONSES
            }
        }
    
    def delete_operation(self, summary=None, description=None, responses=None):
        """Generate swagger for delete operations (DELETE)."""
        return {
            'operation_summary': f"[{self.tag}] {summary or f'Delete {self.tag.lower()}'}",
            'operation_description': description or f"Delete a {self.tag.lower()} by ID.",
            'tags': [self.tag],
            'responses': responses or {
                200: create_success_response(description="Resource deleted successfully"),
                **COMMON_RESPONSES
            }
        }
