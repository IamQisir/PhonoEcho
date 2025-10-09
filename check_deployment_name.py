"""
Check which deployment name to use in Azure OpenAI
"""

import toml
from openai import AzureOpenAI

print("=" * 70)
print("Checking Azure OpenAI Deployment Configuration")
print("=" * 70)

# Load secrets
secrets = toml.load(".streamlit/secrets.toml")
endpoint = secrets['AzureGPT']['AZURE_OPENAI_ENDPOINT']
api_key = secrets['AzureGPT']['AZURE_OPENAI_API_KEY']

print(f"\nEndpoint: {endpoint}")

# Initialize client
client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    api_version="2024-02-15-preview"
)

print("\n" + "=" * 70)
print("IMPORTANT: Deployment Name Issue")
print("=" * 70)
print("\nThe timeout error means the deployment name 'gpt-4' is not found.")
print("\nTo fix this, you need to:")
print("\n1. Go to Azure OpenAI Studio: https://oai.azure.com/")
print("2. Navigate to 'Deployments' section")
print("3. Check what your GPT-4 deployment is actually named")
print("   (It might be named: gpt-4o, gpt-4-turbo, gpt-35-turbo, etc.)")
print("\n4. Then update the model name in your code:")
print("   In app/ai_chat.py, line ~100, change:")
print("   model='gpt-4'  →  model='YOUR-ACTUAL-DEPLOYMENT-NAME'")

print("\n" + "=" * 70)
print("Common deployment names:")
print("=" * 70)
common_names = [
    "gpt-4",
    "gpt-4o", 
    "gpt-4-turbo",
    "gpt-4-32k",
    "gpt-35-turbo",
    "gpt-35-turbo-16k"
]

print("\nTrying common deployment names to see which one works...")
print("(This may take a few moments...)\n")

for model_name in common_names:
    try:
        print(f"Trying: {model_name}...", end=" ")
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=5,
            timeout=10
        )
        print(f"✅ WORKS! Use this deployment name: '{model_name}'")
        break
    except Exception as e:
        error_msg = str(e)
        if "DeploymentNotFound" in error_msg or "NotFoundError" in str(type(e)):
            print("❌ Not found")
        elif "timeout" in error_msg.lower():
            print("⏱️ Timeout (deployment may not exist)")
        else:
            print(f"⚠️ Error: {type(e).__name__}")
else:
    print("\n❌ None of the common names worked.")
    print("\nYou MUST check your Azure OpenAI Studio for the correct deployment name.")

print("\n" + "=" * 70)
