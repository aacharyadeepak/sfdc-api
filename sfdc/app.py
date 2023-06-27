from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools import Logger
from aws_lambda_powertools import Tracer
from aws_lambda_powertools import Metrics
from aws_lambda_powertools.metrics import MetricUnit
import json
from publisher import BasicMessageSender

app = APIGatewayRestResolver()
tracer = Tracer()
logger = Logger()
metrics = Metrics(namespace="Powertools")

@app.get("/sfdc")
@tracer.capture_method
def sfdc():
    # adding custom metrics
    # See: https://awslabs.github.io/aws-lambda-powertools-python/latest/core/metrics/
    metrics.add_metric(name="SFDCAPIInvocations", unit=MetricUnit.Count, value=1)

    # structured log
    # See: https://awslabs.github.io/aws-lambda-powertools-python/latest/core/logger/
    logger.info("SFDC API - HTTP 200")
    return {"message": "SFDC API"}

@app.post("/sfdc")
@tracer.capture_method
def sfdc():
    request_data = json.loads(event['body'])
    basic_message_sender = BasicMessageSender(
        "b-da0ae0ed-3366-4858-9adf-29bf28a65895",
        "sfdcuser",
        "Abc123!!",
        "us-west-2"
    )

    # Declare a queue
    basic_message_sender.declare_queue("sfdc_queue")

    # Send a message to the queue.
    basic_message_sender.send_message(exchange="", routing_key="sfdc_queue", body=request_data)

    # Close connections.
    basic_message_sender.close()


    response = {
        'statusCode': 200,
        'body': json.dumps(response_body)
    }

    return response

# Enrich logging with contextual information from Lambda
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
# Adding tracer
# See: https://awslabs.github.io/aws-lambda-powertools-python/latest/core/tracer/
@tracer.capture_lambda_handler
# ensures metrics are flushed upon request completion/failure and capturing ColdStart metric
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
