import pulumi
from pulumi import Config, Output
import pulumi_gcp as gcp

# Config
config = Config()
project = config.get("project") or "lunch-line-471014"
region = config.get("region") or "us-central1"
image = config.require("image")  # e.g. us-central1-docker.pkg.dev/<proj>/<repo>/lunch-line:latest
service_name = config.get("serviceName") or "lunch-line"
topic_name = config.get("topicName") or "gmail-menu-events"

# Optional secrets (set later or wire to Secret Manager in a follow-up)
calendar_id = config.get_secret("calendarId")
token_json = config.get_secret("tokenJson")

# Provider (region scoped)
provider = gcp.Provider("gcp", project=project, region=region)

# Pub/Sub topic
topic = gcp.pubsub.Topic(
    "gmailTopic",
    name=topic_name,
    opts=pulumi.ResourceOptions(provider=provider),
)

# Service account for Cloud Run service
run_sa = gcp.serviceaccount.Account(
    "runServiceAccount",
    account_id=f"{service_name}-sa",
    display_name=f"{service_name} runtime",
    opts=pulumi.ResourceOptions(provider=provider),
)

# Cloud Run v2 service
service = gcp.cloudrunv2.Service(
    "runService",
    name=service_name,
    location=region,
    template=gcp.cloudrunv2.ServiceTemplateArgs(
        service_account=run_sa.email,
        containers=[
            gcp.cloudrunv2.ServiceTemplateContainerArgs(
                image=image,
                env=[
                    gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(name="PORT", value="8080"),
                ],
            )
        ],
    ),
    traffic=[gcp.cloudrunv2.ServiceTrafficArgs(type="TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST", percent=100)],
    opts=pulumi.ResourceOptions(provider=provider),
)

invoker_sa = gcp.serviceaccount.Account(
    "pubsubInvokerSa",
    account_id=f"{service_name}-invoker",
    display_name=f"{service_name} invoker",
    opts=pulumi.ResourceOptions(provider=provider),
)

run_invoker_binding = gcp.cloudrunv2.ServiceIamMember(
    "runInvoker",
    name=service.name,
    location=service.location,
    role="roles/run.invoker",
    member=invoker_sa.email.apply(lambda e: f"serviceAccount:{e}"),
    opts=pulumi.ResourceOptions(provider=provider, depends_on=[service]),
)

subscription = gcp.pubsub.Subscription(
    "gmailPushSubscription",
    topic=topic.name,
    push_config=gcp.pubsub.SubscriptionPushConfigArgs(
        oidc_token=gcp.pubsub.SubscriptionPushConfigOidcTokenArgs(
            service_account_email=invoker_sa.email
        ),
        push_endpoint=service.uri.apply(lambda u: f"{u}/pubsub"),
    ),
    ack_deadline_seconds=30,
    opts=pulumi.ResourceOptions(provider=provider, depends_on=[run_invoker_binding]),
)

pulumi.export("project", project)
pulumi.export("region", region)
pulumi.export("serviceUrl", service.uri)
pulumi.export("topic", topic.name)
pulumi.export("subscription", subscription.name)
