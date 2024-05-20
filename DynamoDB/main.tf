provider "aws" {
  region = "eu-central-1"
}

# Change the name of the IAM role
resource "aws_iam_role" "save_lambda_role" {
  name = "terraform_aws_save_lambda_role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role_policy.json
}

data "aws_iam_policy_document" "lambda_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    effect = "Allow"
  }
}

# IAM policy for logging from a Lambda
resource "aws_iam_policy" "lambda_logging" {
  name   = "lambda_logging_policy"
  path   = "/"
  policy = data.aws_iam_policy_document.lambda_logging_policy.json
}

data "aws_iam_policy_document" "lambda_logging_policy" {
  statement {
    actions   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["arn:aws:logs:*:*:*"]
    effect    = "Allow"
  }
}

resource "aws_iam_policy" "dynamodb_access_policy" {
  name   = "DynamoDBAccessPolicy"
  path   = "/"
  policy = data.aws_iam_policy_document.dynamodb_access_policy.json
}

data "aws_iam_policy_document" "dynamodb_access_policy" {
  statement {
    actions   = ["dynamodb:PutItem", "dynamodb:GetItem", "dynamodb:UpdateItem", "dynamodb:Query"]
    resources = ["arn:aws:dynamodb:*:*:table/UserOffers"]
    effect    = "Allow"
  }
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.save_lambda_role.name
  policy_arn = aws_iam_policy.lambda_logging.arn
}

resource "aws_iam_role_policy_attachment" "dynamodb_access" {
  role       = aws_iam_role.save_lambda_role.name
  policy_arn = aws_iam_policy.dynamodb_access_policy.arn
}

# Zip the Lambda function code
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/save-lambda"
  output_path = "${path.module}/save-lambda/save_lambda.zip"
}

# Lambda function to save data to DynamoDB
resource "aws_lambda_function" "save_function" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "SaveFunction"
  role             = aws_iam_role.save_lambda_role.arn
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.8"
}

# API Gateway setup
resource "aws_api_gateway_rest_api" "api_gateway" {
  name        = "SaveAPI"
  description = "API Gateway for the Save Lambda Function"
}

resource "aws_api_gateway_resource" "api_resource" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id
  parent_id   = aws_api_gateway_rest_api.api_gateway.root_resource_id
  path_part   = "save"
}

resource "aws_api_gateway_method" "api_method" {
  rest_api_id   = aws_api_gateway_rest_api.api_gateway.id
  resource_id   = aws_api_gateway_resource.api_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api_gateway.id
  resource_id             = aws_api_gateway_resource.api_resource.id
  http_method             = aws_api_gateway_method.api_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.save_function.invoke_arn
}

resource "aws_lambda_permission" "api_gateway_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.save_function.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api_gateway.execution_arn}/*/*/save"
}

resource "aws_api_gateway_deployment" "api_deployment" {
  depends_on = [aws_api_gateway_integration.lambda_integration]
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id
  stage_name  = "prod"
}

# Enable CORS
module "api_gateway_cors" {
  source  = "squidfunk/api-gateway-enable-cors/aws"
  version = "0.3.3"

  api_id          = aws_api_gateway_rest_api.api_gateway.id
  api_resource_id = aws_api_gateway_resource.api_resource.id
}

# DynamoDB Table
resource "aws_dynamodb_table" "user_offers" {
  name         = "UserOffers"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "UserID"
  range_key    = "OfferName"

  attribute {
    name = "UserID"
    type = "S"
  }

  attribute {
    name = "OfferName"
    type = "S"
  }
}

output "api_endpoint" {
  value = "${aws_api_gateway_deployment.api_deployment.invoke_url}/save"
}
