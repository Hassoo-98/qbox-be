"""
Reusable Swagger schema utilities for DRF-YASG.
Import this module in your views to simplify swagger documentation.
"""
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from functools import wraps


# ============== Common Schema Types ==============
SuccessBoolean = openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True)
StatusCode = openapi.Schema(type=openapi.TYPE_INTEGER, example=200)
MessageField = openapi.Schema(type=openapi.TYPE_STRING)
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


# ============== Common HTTP Methods ==============

def create_string_field(description="", required=False, example="sample"):
    return openapi.Schema(
        type=openapi.TYPE_STRING,
        description=description,
        example=example,
    )


def create_email_field(description="Email address", required=True):
    return openapi.Schema(
        type=openapi.TYPE_STRING,
        format='email',
        description=description,
        example='user@example.com',
    )


def create_password_field(description="Password", required=True):
    return openapi.Schema(
        type=openapi.TYPE_STRING,
        format='password',
        description=description,
        example='strongpassword123',
    )


def create_boolean_field(description="", required=False, default=False):
    return openapi.Schema(
        type=openapi.TYPE_BOOLEAN,
        description=description,
        default=default,
    )


def create_integer_field(description="", example=0, minimum=None, maximum=None):
    schema = openapi.Schema(
        type=openapi.TYPE_INTEGER,
        description=description,
        example=example,
    )
    if minimum is not None:
        schema.minimum = minimum
    if maximum is not None:
        schema.maximum = maximum
    return schema


# ============== Helper Functions ==============

def swagger_auto_schema_with_tag(tag_name):
    """
    Decorator factory to add tag to swagger_auto_schema.
    Usage: @swagger_auto_schema_with_tag("Users")
    """
    def decorator(method):
        @swagger_auto_schema(tags=[tag_name])
        @wraps(method)
        def wrapper(*args, **kwargs):
            return method(*args, **kwargs)
        return wrapper
    return decorator


def simple_response(success_code=200, description="Success"):
    """Quick decorator for simple success response."""
    responses = {
        success_code: create_success_response(description=description),
        400: ValidationErrorResponse,
        404: NotFoundResponse,
        500: ServerErrorResponse,
    }
    def decorator(func):
        return swagger_auto_schema(responses=responses)(func)
    return decorator


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


# ============== Standard Request Bodies ==============

EMAIL_REQUEST = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['email'],
    properties={
        'email': create_email_field(),
    }
)

OTP_VERIFY_REQUEST = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['email', 'otp'],
    properties={
        'email': create_email_field(),
        'otp': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='6-digit OTP code',
            example='123456',
        ),
    }
)

LOGIN_REQUEST = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['email', 'password'],
    properties={
        'email': create_email_field(),
        'password': create_password_field(),
    }
)

PASSWORD_RESET_REQUEST = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['email'],
    properties={
        'email': create_email_field(description="Email address for password reset"),
    }
)

PASSWORD_RESET_CONFIRM_REQUEST = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['email', 'otp', 'new_password'],
    properties={
        'email': create_email_field(),
        'otp': openapi.Schema(type=openapi.TYPE_STRING, description='OTP code', example='123456'),
        'new_password': create_password_field(description='New password'),
    }
)


# ============== Decorator Helper ==============

class SwaggerHelper:
    """
    Helper class to create consistent swagger documentation.
    
    Usage:
    from utils.swagger_schema import SwaggerHelper
    
    swagger = SwaggerHelper(tag="Users")
    
    @swagger_auto_schema(
        **swagger.list_operation(summary="List users", description="Get all users"),
        ...
    )
    def get(self, request):
        ...
    """
    
    def __init__(self, tag="API"):
        self.tag = tag
    
    def list_operation(self, summary=None, description=None, responses=None):
        """Generate swagger for list operations (GET)."""
        return {
            'operation_summary': f"[{self.tag}] {summary or f'List {self.tag.lower()}'}",
            'operation_description': description or f"Retrieve a list of all {self.tag.lower()}.",
            'tags': [self.tag],
            'responses': responses or {
                200: create_paginated_response(
                    openapi.Schema(type=openapi.TYPE_OBJECT),
                    tag=self.tag
                ),
                **COMMON_RESPONSES
            }
        }
    
    def retrieve_operation(self, summary=None, description=None, responses=None):
        """Generate swagger for retrieve operations (GET by ID)."""
        return {
            'operation_summary': f"[{self.tag}] {summary or f'Get {self.tag.lower()}'}",
            'operation_description': description or f"Retrieve a specific {self.tag.lower()} by ID.",
            'tags': [self.tag],
            'responses': responses or {
                200: create_success_response(
                    openapi.Schema(type=openapi.TYPE_OBJECT),
                    description="Resource retrieved successfully"
                ),
                **COMMON_RESPONSES
            }
        }
    
    def create_operation(self, summary=None, description=None, request_body=None, responses=None):
        """Generate swagger for create operations (POST)."""
        return {
            'operation_summary': f"[{self.tag}] {summary or f'Create {self.tag.lower()}'}",
            'operation_description': description or f"Create a new {self.tag.lower()}.",
            'tags': [self.tag],
            'request_body': request_body,
            'responses': responses or {
                201: create_success_response(
                    openapi.Schema(type=openapi.TYPE_OBJECT),
                    description="Resource created successfully"
                ),
                **COMMON_RESPONSES
            }
        }
    
    def update_operation(self, summary=None, description=None, request_body=None, responses=None):
        """Generate swagger for update operations (PUT/PATCH)."""
        return {
            'operation_summary': f"[{self.tag}] {summary or f'Update {self.tag.lower()}'}",
            'operation_description': description or f"Update an existing {self.tag.lower()}.",
            'tags': [self.tag],
            'request_body': request_body,
            'responses': responses or {
                200: create_success_response(
                    openapi.Schema(type=openapi.TYPE_OBJECT),
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
