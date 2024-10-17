import boto3
import botocore.config
import json
from datetime import datetime

def blog_generate_using_bedrock(blogTopic: str) -> str:
    prompt=f"""<s>[INST]Human: Write a 200 word blog on the topic {blogTopic}
    Assistant:[/INST]
    """

    body = {
        "inputText": prompt,
        "textGenerationConfig": {
            "maxTokenCount": 4096,
            "stopSequences": [],
            "temperature": 0.5,
            "topP": 0.9
        }
    }

    bedrock=boto3.client("bedrock-runtime", region_name="ap-southeast-2",
                             config=botocore.config.Config(read_timeout=300, retries={"max_attempts":3}))
    
    try:
        # Ensure you set the modelId correctly
        response = bedrock.invoke_model(
            modelId="amazon.titan-text-lite-v1",
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body)  # Ensure the body is JSON encoded
        )

        response_content=response['body'].read()
        response_data=json.loads(response_content)
        print(response_data)
        
        blog_details=response_data['generation']
        return blog_details
        
    except Exception as e:
        print(f"Error generating the blog: {e}")
        return ""


def save_blog_details_s3(s3_key, s3_bucket, generate_blog):
    s3=boto3.client('s3')
    try:
        s3.put_object(Bucket=s3_bucket, Key=s3_key, Body=generate_blog)
        print("Code saved to s3")

    except:
        pass



def lambda_handler(event, content):

    event=json.loads(event['body'])
    blogTopic=event['blog_topic']

    generate_blog=blog_generate_using_bedrock(blogTopic=blogTopic)
    body = ""

    if generate_blog:
        body = "Blog Generation Completed."

        current_time=datetime.now().strftime('%H%M%S')
        s3_key=f"blog-output/{current_time}.txt"
        s3_bucket='bedrockawsexample'

        save_blog_details_s3(s3_key, s3_bucket, generate_blog)
        body += "Saved to S3."

    else:
        body = "No blog was generated."
        print(f"No blog was generated.")
    
    return{
        "statusCode": 200,
        "body": json.dumps(body)
    }
