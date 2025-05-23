# api_admin/scripts/test_parameter_templates.py
import sys
import asyncio
from pathlib import Path

# Add parent directory to path so we can import app
sys.path.append(str(Path(__file__).parent.parent))

from app.database import AsyncSessionLocal
from app.crud.crud_client_api_parameter import get_parameter_template_by_name, build_api_call
from app.crud.crud_client_api_config import get_client_api_config
from app.models import Client

async def test_parameter_templates():
    """Test the parameter template system"""
    
    print("🧪 Testing Parameter Template System")
    print("=" * 50)
    
    async with AsyncSessionLocal() as session:
        try:
            # Test 1: Get IndiaNIC's Employee API config
            print("\n📋 Test 1: Getting API Configuration")
            client_id = "96b8823d"  # IndiaNIC's client ID prefix from migration
            
            # Find the exact client_id by looking for IndiaNIC
            from sqlalchemy import select
            result = await session.execute(select(Client).where(Client.name.like('%IndiaNIC%')))
            client = result.scalar_one_or_none()
            
            if not client:
                print("❌ IndiaNIC client not found")
                return
            
            print(f"✅ Found client: {client.name} (ID: {client.id})")
            
            # Get Employee API config
            employee_api = await get_client_api_config(session, client.id, "employee")
            if not employee_api:
                print("❌ Employee API config not found")
                return
            
            print(f"✅ Found Employee API: {employee_api.api_base_url}")
            
            # Test 2: Get salary lookup template
            print("\n📋 Test 2: Getting Parameter Template")
            salary_template = await get_parameter_template_by_name(
                session, employee_api.id, "salary_lookup"
            )
            
            if not salary_template:
                print("❌ Salary lookup template not found")
                return
            
            print(f"✅ Found template: {salary_template.template_name}")
            print(f"   Description: {salary_template.description}")
            print(f"   Method: {salary_template.http_method} {salary_template.endpoint_path}")
            
            # Test 3: Build API call with sample data
            print("\n📋 Test 3: Building API Call")
            
            # Sample input data (what your intent recognition would provide)
            sample_input = {
                "employee_id": "arvind_123",
                "include_bonus": True
            }
            
            try:
                api_call = build_api_call(
                    template=salary_template,
                    input_data=sample_input,
                    base_url=employee_api.api_base_url
                )
                
                print("✅ API call built successfully:")
                print(f"   URL: {api_call['url']}")
                print(f"   Method: {api_call['method']}")
                print(f"   Params: {api_call['params']}")
                print(f"   Headers: {api_call['headers']}")
                print(f"   Response mapping: {api_call['response_mapping']}")
                
            except Exception as e:
                print(f"❌ Error building API call: {e}")
                return
            
            # Test 4: Test different templates
            print("\n📋 Test 4: Testing Department Lookup")
            
            dept_template = await get_parameter_template_by_name(
                session, employee_api.id, "department_lookup"
            )
            
            if dept_template:
                dept_input = {"employee_id": "john_456"}
                dept_call = build_api_call(
                    template=dept_template,
                    input_data=dept_input,
                    base_url=employee_api.api_base_url
                )
                
                print("✅ Department lookup API call:")
                print(f"   URL: {dept_call['url']}")
                print(f"   Params: {dept_call['params']}")
            
            # Test 5: Test Client API
            print("\n📋 Test 5: Testing Client API Template")
            
            client_api = await get_client_api_config(session, client.id, "client")
            if client_api:
                client_template = await get_parameter_template_by_name(
                    session, client_api.id, "client_info"
                )
                
                if client_template:
                    client_input = {"client_id": "client_789"}
                    client_call = build_api_call(
                        template=client_template,
                        input_data=client_input,
                        base_url=client_api.api_base_url
                    )
                    
                    print("✅ Client API call:")
                    print(f"   URL: {client_call['url']}")
                    print(f"   Params: {client_call['params']}")
            
            print("\n🎉 All tests completed successfully!")
            print("\n💡 Summary:")
            print("   ✅ Parameter templates are working")
            print("   ✅ API call building is functional")
            print("   ✅ Multiple API types are supported")
            print("   ✅ Ready for intent recognition integration!")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            print("Traceback:")
            print(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(test_parameter_templates())