# api_admin/scripts/migrate_parameter_templates.py
import sys
import asyncio
from pathlib import Path

# Add parent directory to path so we can import app
sys.path.append(str(Path(__file__).parent.parent))

from app.database import engine, AsyncSessionLocal
from app.models.client_api_config import ClientApiConfig
from app.models.client_api_parameter import ClientApiParameter
from app.crud.crud_client_api_parameter import create_parameter_template
from sqlalchemy import select

# Sample parameter templates for IndiaNIC
SAMPLE_TEMPLATES = {
    "employee": [
        {
            "template_name": "salary_lookup",
            "description": "Get employee salary information",
            "http_method": "GET",
            "endpoint_path": "/payroll",
            "parameter_template": {
                "query_params": {
                    "empid": {
                        "type": "string",
                        "required": True,
                        "source": "employee_id",
                        "description": "Employee ID"
                    },
                    "data": {
                        "type": "string",
                        "required": True,
                        "default": "salary",
                        "description": "Type of data to retrieve"
                    },
                    "include_bonus": {
                        "type": "boolean",
                        "required": False,
                        "default": True,
                        "description": "Include bonus in salary calculation"
                    }
                },
                "headers": {
                    "Content-Type": "application/json"
                }
            },
            "response_mapping": {
                "salary": "$.data.base_salary",
                "bonus": "$.data.bonus_amount",
                "total": "$.data.total_compensation"
            }
        },
        {
            "template_name": "department_lookup",
            "description": "Get employee department information",
            "http_method": "GET",
            "endpoint_path": "/payroll",
            "parameter_template": {
                "query_params": {
                    "empid": {
                        "type": "string",
                        "required": True,
                        "source": "employee_id",
                        "description": "Employee ID"
                    },
                    "data": {
                        "type": "string",
                        "required": True,
                        "default": "department",
                        "description": "Type of data to retrieve"
                    }
                },
                "headers": {
                    "Content-Type": "application/json"
                }
            },
            "response_mapping": {
                "department": "$.data.department_name",
                "department_id": "$.data.department_id"
            }
        },
        {
            "template_name": "designation_lookup",
            "description": "Get employee designation/position information",
            "http_method": "GET",
            "endpoint_path": "/payroll",
            "parameter_template": {
                "query_params": {
                    "empid": {
                        "type": "string",
                        "required": True,
                        "source": "employee_id",
                        "description": "Employee ID"
                    },
                    "data": {
                        "type": "string",
                        "required": True,
                        "default": "designation",
                        "description": "Type of data to retrieve"
                    }
                },
                "headers": {
                    "Content-Type": "application/json"
                }
            },
            "response_mapping": {
                "designation": "$.data.position_title",
                "level": "$.data.position_level"
            }
        }
    ],
    "client": [
        {
            "template_name": "client_info",
            "description": "Get client information",
            "http_method": "GET",
            "endpoint_path": "/clients",
            "parameter_template": {
                "query_params": {
                    "client_id": {
                        "type": "string",
                        "required": True,
                        "source": "client_id",
                        "description": "Client ID"
                    },
                    "fields": {
                        "type": "array",
                        "required": False,
                        "default": ["name", "status", "contact"],
                        "description": "Fields to retrieve"
                    }
                },
                "headers": {
                    "Content-Type": "application/json"
                }
            },
            "response_mapping": {
                "name": "$.client.name",
                "status": "$.client.status",
                "contact": "$.client.contact_email"
            }
        }
    ],
    "project": [
        {
            "template_name": "project_status",
            "description": "Get project status and details",
            "http_method": "GET",
            "endpoint_path": "/projects",
            "parameter_template": {
                "query_params": {
                    "project_id": {
                        "type": "string",
                        "required": True,
                        "source": "project_id",
                        "description": "Project ID"
                    },
                    "include_tasks": {
                        "type": "boolean",
                        "required": False,
                        "default": False,
                        "description": "Include task details"
                    }
                },
                "headers": {
                    "Content-Type": "application/json"
                }
            },
            "response_mapping": {
                "status": "$.project.status",
                "progress": "$.project.completion_percentage",
                "deadline": "$.project.deadline"
            }
        }
    ]
}

async def migrate_parameter_templates():
    """Create the parameter templates table and add sample templates"""
    
    print("🔄 Starting API Parameter Templates migration...")
    
    # Create the new table
    async with engine.begin() as conn:
        from app.database import Base
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Created client_api_parameters table")
    
    # Add sample parameter templates
    async with AsyncSessionLocal() as session:
        try:
            # Get all existing API configurations
            result = await session.execute(select(ClientApiConfig))
            api_configs = result.scalars().all()
            
            print(f"📋 Found {len(api_configs)} API configurations")
            
            total_templates_created = 0
            
            for api_config in api_configs:
                print(f"\n🔧 Adding parameter templates for {api_config.api_name} API")
                
                # Get templates for this API type
                templates = SAMPLE_TEMPLATES.get(api_config.api_name, [])
                
                for template_data in templates:
                    try:
                        template = await create_parameter_template(
                            session=session,
                            client_api_config_id=api_config.id,
                            **template_data
                        )
                        print(f"   ✅ Added '{template_data['template_name']}' template")
                        total_templates_created += 1
                        
                    except Exception as e:
                        print(f"   ❌ Error adding '{template_data['template_name']}': {e}")
            
            print(f"\n🎉 Migration completed successfully!")
            print(f"📊 Total parameter templates created: {total_templates_created}")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error during migration: {e}")
            import traceback
            print("Traceback:")
            print(traceback.format_exc())
            raise

async def show_parameter_templates():
    """Show all parameter templates"""
    print("\n📋 Current API Parameter Templates:")
    print("=" * 80)
    
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(
                select(ClientApiConfig, ClientApiParameter)
                .join(ClientApiParameter, ClientApiConfig.id == ClientApiParameter.client_api_config_id)
                .order_by(ClientApiConfig.api_name, ClientApiParameter.template_name)
            )
            
            current_api = None
            for api_config, template in result:
                if current_api != api_config.api_name:
                    current_api = api_config.api_name
                    print(f"\n🔧 {api_config.api_name.upper()} API ({api_config.api_base_url})")
                
                print(f"   📝 {template.template_name}")
                print(f"      Method: {template.http_method} {template.endpoint_path}")
                print(f"      Description: {template.description}")
                
                # Show required parameters
                query_params = template.parameter_template.get('query_params', {})
                required_params = [p for p, cfg in query_params.items() if cfg.get('required', False)]
                if required_params:
                    print(f"      Required params: {', '.join(required_params)}")
                
                print()
                
        except Exception as e:
            print(f"❌ Error showing templates: {e}")

def main():
    """Main function with user choice"""
    print("🔧 API Parameter Templates Migration Tool")
    print("=" * 50)
    
    choice = input("\nWhat would you like to do?\n1. Run migration (create table + sample templates)\n2. Show current parameter templates\n3. Both\n\nChoice (1-3): ")
    
    if choice == "1":
        asyncio.run(migrate_parameter_templates())
    elif choice == "2":
        asyncio.run(show_parameter_templates())
    elif choice == "3":
        asyncio.run(migrate_parameter_templates())
        asyncio.run(show_parameter_templates())
    else:
        print("Invalid choice. Exiting.")

if __name__ == "__main__":
    main()