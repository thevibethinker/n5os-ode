#!/usr/bin/env bash
set -euo pipefail

# Create SQS FIFO queue + DLQ with sensible defaults.
# Requires: awscli configured (AWS_PROFILE / AWS_DEFAULT_REGION)

QUEUE_BASENAME=${1:-parentzo-childzo}
REGION=${AWS_DEFAULT_REGION:-us-east-1}
PROFILE_ARG=${AWS_PROFILE:+--profile "$AWS_PROFILE"}

MAIN_QUEUE_NAME="${QUEUE_BASENAME}.fifo"
DLQ_NAME="${QUEUE_BASENAME}-dlq.fifo"

VISIBILITY_TIMEOUT=60
RECEIVE_WAIT_SECONDS=20
MAX_RECEIVE_COUNT=5

create_queue() {
  local NAME=$1
  local DEDUP=${2:-true}
  aws ${PROFILE_ARG} sqs create-queue \
    --region "$REGION" \
    --queue-name "$NAME" \
    --attributes FifoQueue=true,ContentBasedDeduplication=${DEDUP},VisibilityTimeout=${VISIBILITY_TIMEOUT},ReceiveMessageWaitTimeSeconds=${RECEIVE_WAIT_SECONDS} \
    >/dev/null
  aws ${PROFILE_ARG} sqs get-queue-url --region "$REGION" --queue-name "$NAME" --output text
}

set_redrive() {
  local SRC_URL=$1
  local DLQ_ARN=$2
  local ATTR
  ATTR=$(jq -cn --arg arn "$DLQ_ARN" --argjson mrc ${MAX_RECEIVE_COUNT} '{RedrivePolicy:{deadLetterTargetArn:$arn,maxReceiveCount:$mrc}}')
  aws ${PROFILE_ARG} sqs set-queue-attributes \
    --region "$REGION" \
    --queue-url "$SRC_URL" \
    --attributes "RedrivePolicy=${ATTR}"
}

which jq >/dev/null 2>&1 || { echo "Please install jq"; exit 1; }

echo "Creating DLQ: ${DLQ_NAME}"
DLQ_URL=$(create_queue "$DLQ_NAME")
DLQ_ATTR=$(aws ${PROFILE_ARG} sqs get-queue-attributes --region "$REGION" --queue-url "$DLQ_URL" --attribute-names QueueArn)
DLQ_ARN=$(echo "$DLQ_ATTR" | jq -r '.Attributes.QueueArn')

echo "Creating main queue: ${MAIN_QUEUE_NAME}"
MAIN_URL=$(create_queue "$MAIN_QUEUE_NAME")

echo "Setting redrive policy (maxReceiveCount=${MAX_RECEIVE_COUNT})"
set_redrive "$MAIN_URL" "$DLQ_ARN"

echo "Done. Queues:"
echo "MAIN_URL=$MAIN_URL"
echo "DLQ_URL=$DLQ_URL"
