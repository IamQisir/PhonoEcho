"""
Simple test script to diagnose Azure OpenAI API issues
Run with: python test_azure_api.py
"""

import os
import sys

print("=" * 70)
print("Azure OpenAI API Diagnostic Test")
print("=" * 70)

# Step 1: Check if required packages are installed
print("\n[Step 1] Checking required packages...")
try:
    from openai import AzureOpenAI
    print("✅ openai package is installed")
except ImportError as e:
    print(f"❌ openai package not found: {e}")
    print("   Install with: pip install openai")
    sys.exit(1)

try:
    import toml
    print("✅ toml package is installed")
except ImportError:
    print("❌ toml package not found")
    print("   Install with: pip install toml")
    sys.exit(1)

# Step 2: Load secrets
print("\n[Step 2] Loading secrets from .streamlit/secrets.toml...")
secrets_path = ".streamlit/secrets.toml"

if not os.path.exists(secrets_path):
    print(f"❌ secrets.toml not found at: {os.path.abspath(secrets_path)}")
    print("   Please make sure the file exists with your Azure OpenAI credentials")
    sys.exit(1)

try:
    secrets = toml.load(secrets_path)
    print("✅ secrets.toml loaded successfully")
except Exception as e:
    print(f"❌ Error loading secrets.toml: {e}")
    sys.exit(1)

# Step 3: Extract credentials
print("\n[Step 3] Extracting Azure OpenAI credentials...")
try:
    endpoint = secrets['AzureGPT']['AZURE_OPENAI_ENDPOINT']
    api_key = secrets['AzureGPT']['AZURE_OPENAI_API_KEY']
    
    print(f"   Endpoint: {endpoint}")
    print(f"   API Key: {'*' * (len(api_key) - 4) + api_key[-4:] if len(api_key) > 4 else '***'}")
    print("✅ Credentials extracted")
except KeyError as e:
    print(f"❌ Missing key in secrets.toml: {e}")
    print("   Expected structure:")
    print("   [AzureGPT]")
    print("   AZURE_OPENAI_ENDPOINT = 'your-endpoint'")
    print("   AZURE_OPENAI_API_KEY = 'your-key'")
    sys.exit(1)

# Step 4: Initialize Azure OpenAI client
print("\n[Step 4] Initializing Azure OpenAI client...")
try:
    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version="2024-02-15-preview"
    )
    print("✅ Client initialized")
except Exception as e:
    print(f"❌ Failed to initialize client: {e}")
    sys.exit(1)

# Step 5: Test API call with simple message
print("\n[Step 5] Testing API with simple message...")
print("   Sending: 'Hello, can you hear me? Please respond in Japanese.'")

try:
    response = client.chat.completions.create(
        model="gpt-4o",  # This must match your deployment name in Azure
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, can you hear me? Please respond in Japanese with a short greeting."}
        ],
        temperature=0.7,
        max_tokens=100,
        timeout=30  # 30 second timeout
    )
    
    if response and response.choices:
        answer = response.choices[0].message.content
        print("\n" + "=" * 70)
        print("✅ SUCCESS! API is working correctly!")
        print("=" * 70)
        print(f"\nGPT-4 Response:\n{answer}")
        print("\n" + "=" * 70)
        print("Your Azure OpenAI API is configured correctly! 🎉")
        print("=" * 70)
    else:
        print("❌ Received empty response from API")
        
except Exception as e:
    print("\n" + "=" * 70)
    print("❌ API CALL FAILED")
    print("=" * 70)
    print(f"\nError Type: {type(e).__name__}")
    print(f"Error Message: {str(e)}")
    print("\nPossible Issues:")
    print("1. The deployment name 'gpt-4' doesn't exist in your Azure resource")
    print("   → Check your Azure OpenAI Studio for the correct deployment name")
    print("2. Your API key might be invalid or expired")
    print("   → Verify in Azure Portal")
    print("3. Your endpoint URL might be incorrect")
    print("   → Should be: https://YOUR-RESOURCE-NAME.openai.azure.com/")
    print("4. Your Azure OpenAI resource might be disabled or have quota issues")
    print("   → Check Azure Portal for resource status")
    print("5. Network/firewall issues blocking the connection")
    print("=" * 70)
    sys.exit(1)
