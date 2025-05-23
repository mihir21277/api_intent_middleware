# api_admin/app/crud/crud_client_api_parameter.py
from typing import List, Optional, Dict, Any
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.client_api_parameter import ClientApiParameter

async def create_parameter_template(
    session: AsyncSession,
    client_api_config_id: str,
    template_name: str,
    description: str,
    http_method: str,
    endpoint_path: str,
    parameter_template: Dict[str, Any],
    response_mapping: Optional[Dict[str, str]] = None
) -> ClientApiParameter:
    """Create a new parameter template"""
    
    template = ClientApiParameter(
        id=str(uuid.uuid4()),
        client_api_config_id=client_api_config_id,
        template_name=template_name,
        description=description,
        http_method=http_method,
        endpoint_path=endpoint_path,
        parameter_template=parameter_template,
        response_mapping=response_mapping or {}
    )
    
    session.add(template)
    await session.commit()
    await session.refresh(template)
    return template

async def get_parameter_templates(
    session: AsyncSession, 
    client_api_config_id: str
) -> List[ClientApiParameter]:
    """Get all parameter templates for a specific API config"""
    result = await session.execute(
        select(ClientApiParameter)
        .where(ClientApiParameter.client_api_config_id == client_api_config_id)
        .where(ClientApiParameter.active == 1)
    )
    return result.scalars().all()

async def get_parameter_template(
    session: AsyncSession,
    template_id: str
) -> Optional[ClientApiParameter]:
    """Get a specific parameter template"""
    result = await session.execute(
        select(ClientApiParameter).where(ClientApiParameter.id == template_id)
    )
    return result.scalar_one_or_none()

async def get_parameter_template_by_name(
    session: AsyncSession,
    client_api_config_id: str,
    template_name: str
) -> Optional[ClientApiParameter]:
    """Get parameter template by name for a specific API config"""
    result = await session.execute(
        select(ClientApiParameter)
        .where(ClientApiParameter.client_api_config_id == client_api_config_id)
        .where(ClientApiParameter.template_name == template_name)
        .where(ClientApiParameter.active == 1)
    )
    return result.scalar_one_or_none()

async def update_parameter_template(
    session: AsyncSession,
    template_id: str,
    **kwargs
) -> Optional[ClientApiParameter]:
    """Update a parameter template"""
    template = await get_parameter_template(session, template_id)
    
    if template:
        for key, value in kwargs.items():
            if hasattr(template, key) and value is not None:
                setattr(template, key, value)
        
        await session.commit()
        await session.refresh(template)
    
    return template

async def delete_parameter_template(session: AsyncSession, template_id: str) -> bool:
    """Delete a parameter template"""
    template = await get_parameter_template(session, template_id)
    
    if template:
        await session.delete(template)
        await session.commit()
        return True
    return False

# Utility function for building API calls
def build_api_call(
    template: ClientApiParameter,
    input_data: Dict[str, Any],
    base_url: str
) -> Dict[str, Any]:
    """
    Build API call parameters from template and input data
    
    Args:
        template: The parameter template
        input_data: Data provided by user (e.g., {"employee_id": "234", "include_bonus": True})
        base_url: Base URL of the API
    
    Returns:
        Dictionary with URL, method, headers, params, etc.
    """
    
    # Start with the endpoint path
    endpoint_path = template.endpoint_path
    
    # Handle path parameters
    path_params = template.parameter_template.get('path_params', {})
    for param_name, param_config in path_params.items():
        source_key = param_config.get('source', param_name)
        if source_key in input_data:
            endpoint_path = endpoint_path.replace(f'{{{param_name}}}', str(input_data[source_key]))
    
    # Build query parameters
    query_params = {}
    query_param_configs = template.parameter_template.get('query_params', {})
    
    for param_name, param_config in query_param_configs.items():
        source_key = param_config.get('source', param_name)
        
        # Get value from input data or use default
        if source_key in input_data:
            value = input_data[source_key]
        elif 'default' in param_config:
            value = param_config['default']
        elif param_config.get('required', False):
            raise ValueError(f"Required parameter '{param_name}' not provided")
        else:
            continue
        
        # Type conversion
        param_type = param_config.get('type', 'string')
        if param_type == 'boolean':
            value = str(value).lower()
        elif param_type == 'array':
            value = ','.join(map(str, value)) if isinstance(value, list) else str(value)
        
        query_params[param_name] = value
    
    # Build headers
    headers = template.parameter_template.get('headers', {})
    
    # Construct full URL
    full_url = f"{base_url.rstrip('/')}{endpoint_path}"
    
    return {
        'url': full_url,
        'method': template.http_method,
        'params': query_params,
        'headers': headers,
        'response_mapping': template.response_mapping
    }