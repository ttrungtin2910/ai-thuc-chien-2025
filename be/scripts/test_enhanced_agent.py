"""
Test script for Enhanced Virtual Assistant with Agent Architecture
"""

import asyncio
import logging
import sys
import os

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.enhanced_virtual_assistant import enhanced_virtual_assistant

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_enhanced_agent():
    """Test the enhanced virtual assistant with various queries."""
    
    print("🚀 Testing Enhanced Virtual Assistant with Agent Architecture")
    print("=" * 60)
    
    # Test session
    session_id = "test_session_001"
    user_id = "test_user"
    
    # Test queries - mix of casual and RAG queries
    test_queries = [
        # Casual queries
        {
            "message": "Xin chào!",
            "expected_type": "casual",
            "description": "Casual greeting"
        },
        {
            "message": "Bạn tên gì?",
            "expected_type": "casual", 
            "description": "Simple question about assistant"
        },
        
        # RAG queries
        {
            "message": "Thủ tục đăng ký thường trú như thế nào?",
            "expected_type": "rag",
            "description": "Administrative procedure question"
        },
        {
            "message": "Cần những giấy tờ gì để làm căn cước công dân?",
            "expected_type": "rag",
            "description": "Document requirements question"
        },
        {
            "message": "Thời gian xử lý hồ sơ là bao lâu?",
            "expected_type": "rag",
            "description": "Processing time question"
        },
        {
            "message": "Có thể làm online được không?",
            "expected_type": "rag",
            "description": "Follow-up question with context"
        }
    ]
    
    # Test each query
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"🔍 Test {i}: {test_case['description']}")
        print(f"Query: {test_case['message']}")
        print(f"Expected type: {test_case['expected_type']}")
        print("-" * 60)
        
        try:
            # Send message to enhanced assistant
            response = await enhanced_virtual_assistant.chat(
                message=test_case["message"],
                session_id=session_id,
                user_id=user_id
            )
            
            # Display response
            print(f"✅ Response: {response['response']}")
            print(f"📊 Metadata:")
            metadata = response.get('metadata', {})
            for key, value in metadata.items():
                if key == 'extracted_entities' and isinstance(value, list) and value:
                    print(f"   - {key}: {value}")
                elif key == 'source_info' and value:
                    print(f"   - {key}: [Has source information]")
                else:
                    print(f"   - {key}: {value}")
            
            # Verify expected behavior
            rag_used = metadata.get('rag_used', False)
            if test_case['expected_type'] == 'rag' and rag_used:
                print("✅ Correctly routed to RAG")
            elif test_case['expected_type'] == 'casual' and not rag_used:
                print("✅ Correctly routed to casual response")
            else:
                print(f"⚠️  Routing mismatch: expected {test_case['expected_type']}, got {'rag' if rag_used else 'casual'}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            logger.error(f"Test {i} failed: {e}")
    
    # Test session info
    print(f"\n{'='*60}")
    print("📋 Testing Session Info")
    print("-" * 60)
    
    try:
        session_info = enhanced_virtual_assistant.get_session_info(session_id)
        print(f"Session ID: {session_info.get('session_id')}")
        print(f"Message count: {session_info.get('message_count', 0)}")
        print(f"Connected: {session_info.get('connected', False)}")
        print(f"Agent type: {session_info.get('agent_type', 'unknown')}")
        
        recent_messages = session_info.get('recent_messages', [])
        if recent_messages:
            print("Recent messages:")
            for msg in recent_messages[-3:]:  # Last 3
                print(f"  - {msg.get('type')}: {msg.get('content')[:50]}...")
                
    except Exception as e:
        print(f"❌ Session info error: {str(e)}")
    
    # Test service status
    print(f"\n{'='*60}")
    print("🏥 Testing Service Status")
    print("-" * 60)
    
    try:
        status = enhanced_virtual_assistant.get_service_status()
        print(f"Service: {status.get('service')}")
        print(f"Status: {status.get('status')}")
        print(f"Architecture: {status.get('agent_architecture')}")
        print(f"RAG enabled: {status.get('rag_enabled')}")
        print(f"Memory connected: {status.get('memory_connected')}")
        
        features = status.get('features', [])
        if features:
            print("Features:")
            for feature in features:
                print(f"  - {feature}")
                
    except Exception as e:
        print(f"❌ Service status error: {str(e)}")
    
    print(f"\n{'='*60}")
    print("🎉 Enhanced Agent Testing Complete!")
    print("=" * 60)


async def test_routing_logic():
    """Test the routing logic specifically."""
    
    print("\n🔀 Testing Routing Logic")
    print("=" * 40)
    
    # Test routing without full conversation
    from app.agent.nodes.routing_nodes import AnalyzeQueryNode
    from app.agent.state import ChatState
    from langchain_core.messages import HumanMessage
    
    analyze_node = AnalyzeQueryNode()
    
    test_cases = [
        ("Xin chào", "casual"),
        ("Thủ tục đăng ký", "other"), 
        ("Cần giấy tờ gì?", "other"),
        ("Bạn khỏe không?", "casual"),
        ("Phí lệ phí là bao nhiêu?", "other")
    ]
    
    for query, expected in test_cases:
        try:
            state = ChatState(messages=[HumanMessage(content=query)])
            result = await analyze_node(state, {})
            
            route = result.get("route_destination", "unknown")
            print(f"'{query}' -> {route} (expected: {expected}) {'✅' if route == expected else '❌'}")
            
        except Exception as e:
            print(f"'{query}' -> Error: {e}")


if __name__ == "__main__":
    try:
        # Run the tests
        asyncio.run(test_enhanced_agent())
        asyncio.run(test_routing_logic())
        
    except KeyboardInterrupt:
        print("\n⏹️  Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Testing failed: {e}")
        logger.error(f"Main test failed: {e}")
        import traceback
        traceback.print_exc()
