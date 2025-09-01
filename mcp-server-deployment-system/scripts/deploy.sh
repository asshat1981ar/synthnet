#!/bin/bash
# Universal MCP Server Deployment Script
# Supports multiple environments and deployment targets

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
LOG_FILE="/tmp/mcp-deploy-${TIMESTAMP}.log"

# Default values
ENVIRONMENT="${ENVIRONMENT:-development}"
TARGET="${TARGET:-kubernetes}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
NAMESPACE="${NAMESPACE:-default}"
CONFIG_FILE=""
DRY_RUN=false
VERBOSE=false
FORCE=false
ROLLBACK=false
HEALTH_CHECK_TIMEOUT=300

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

debug() {
    if [[ "$VERBOSE" == "true" ]]; then
        echo -e "${BLUE}[DEBUG]${NC} $1" | tee -a "$LOG_FILE"
    fi
}

# Usage information
usage() {
    cat << EOF
MCP Server Deployment Script

Usage: $0 [OPTIONS]

Options:
    -e, --environment ENV       Deployment environment (development|staging|production)
    -t, --target TARGET         Deployment target (kubernetes|aws-lambda|aws-ecs|gcp-cloud-run|azure-container-instances|local)
    -i, --image IMAGE           Container image tag (default: latest)
    -n, --namespace NAMESPACE   Kubernetes namespace (default: default)
    -c, --config FILE           Configuration file path
    -d, --dry-run               Perform dry run without actual deployment
    -v, --verbose               Enable verbose logging
    -f, --force                 Force deployment without confirmation
    -r, --rollback              Rollback to previous deployment
    --health-timeout SECONDS    Health check timeout (default: 300)
    -h, --help                  Show this help message

Examples:
    # Deploy to local development environment
    $0 --environment development --target local

    # Deploy to Kubernetes staging
    $0 --environment staging --target kubernetes --namespace mcp-server-staging

    # Deploy to AWS Lambda production
    $0 --environment production --target aws-lambda --image mcp-server:v1.2.3

    # Rollback Kubernetes deployment
    $0 --environment production --target kubernetes --rollback

EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -t|--target)
                TARGET="$2"
                shift 2
                ;;
            -i|--image)
                IMAGE_TAG="$2"
                shift 2
                ;;
            -n|--namespace)
                NAMESPACE="$2"
                shift 2
                ;;
            -c|--config)
                CONFIG_FILE="$2"
                shift 2
                ;;
            -d|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -f|--force)
                FORCE=true
                shift
                ;;
            -r|--rollback)
                ROLLBACK=true
                shift
                ;;
            --health-timeout)
                HEALTH_CHECK_TIMEOUT="$2"
                shift 2
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done
}

# Validate prerequisites
validate_prerequisites() {
    log "Validating prerequisites..."
    
    # Check required tools based on target
    case "$TARGET" in
        kubernetes)
            if ! command -v kubectl &> /dev/null; then
                error "kubectl is required for Kubernetes deployments"
                exit 1
            fi
            if ! command -v helm &> /dev/null; then
                warn "helm not found - basic Kubernetes deployments will be used"
            fi
            ;;
        aws-lambda|aws-ecs)
            if ! command -v aws &> /dev/null; then
                error "AWS CLI is required for AWS deployments"
                exit 1
            fi
            ;;
        gcp-cloud-run)
            if ! command -v gcloud &> /dev/null; then
                error "gcloud CLI is required for GCP deployments"
                exit 1
            fi
            ;;
        azure-container-instances)
            if ! command -v az &> /dev/null; then
                error "Azure CLI is required for Azure deployments"
                exit 1
            fi
            ;;
        local)
            if ! command -v docker &> /dev/null; then
                error "Docker is required for local deployments"
                exit 1
            fi
            ;;
    esac
    
    # Validate environment
    if [[ ! "$ENVIRONMENT" =~ ^(development|staging|production)$ ]]; then
        error "Invalid environment: $ENVIRONMENT"
        exit 1
    fi
    
    # Load configuration file if provided
    if [[ -n "$CONFIG_FILE" ]]; then
        if [[ ! -f "$CONFIG_FILE" ]]; then
            error "Configuration file not found: $CONFIG_FILE"
            exit 1
        fi
        log "Loading configuration from: $CONFIG_FILE"
        # shellcheck source=/dev/null
        source "$CONFIG_FILE"
    fi
}

# Check deployment confirmation
confirm_deployment() {
    if [[ "$FORCE" == "true" ]] || [[ "$DRY_RUN" == "true" ]]; then
        return 0
    fi
    
    echo -e "${YELLOW}Deployment Configuration:${NC}"
    echo "  Environment: $ENVIRONMENT"
    echo "  Target: $TARGET"
    echo "  Image: $IMAGE_TAG"
    echo "  Namespace: $NAMESPACE"
    echo "  Timestamp: $TIMESTAMP"
    
    echo -n "Continue with deployment? [y/N]: "
    read -r response
    
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        log "Deployment cancelled by user"
        exit 0
    fi
}

# Build container image if needed
build_image() {
    if [[ "$TARGET" == "local" ]] || [[ "$IMAGE_TAG" == "latest" ]]; then
        log "Building container image..."
        
        local dockerfile="$PROJECT_ROOT/containers/Dockerfile.production"
        if [[ "$ENVIRONMENT" == "development" ]]; then
            dockerfile="$PROJECT_ROOT/containers/Dockerfile.development"
        fi
        
        if [[ "$DRY_RUN" == "true" ]]; then
            log "[DRY RUN] Would build image with: docker build -f $dockerfile -t mcp-server:$IMAGE_TAG $PROJECT_ROOT"
        else
            docker build -f "$dockerfile" -t "mcp-server:$IMAGE_TAG" "$PROJECT_ROOT"
        fi
    fi
}

# Deploy to Kubernetes
deploy_kubernetes() {
    log "Deploying to Kubernetes..."
    
    local kustomize_overlay="$PROJECT_ROOT/kubernetes/overlays/$ENVIRONMENT"
    
    if [[ ! -d "$kustomize_overlay" ]]; then
        error "Kubernetes overlay not found for environment: $ENVIRONMENT"
        exit 1
    fi
    
    # Check cluster connectivity
    if ! kubectl cluster-info &> /dev/null; then
        error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    # Create namespace if it doesn't exist
    if [[ "$DRY_RUN" == "true" ]]; then
        log "[DRY RUN] Would ensure namespace: $NAMESPACE"
    else
        kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
    fi
    
    # Apply configuration
    if [[ "$ROLLBACK" == "true" ]]; then
        log "Rolling back deployment..."
        if [[ "$DRY_RUN" == "true" ]]; then
            log "[DRY RUN] Would rollback deployment in namespace: $NAMESPACE"
        else
            kubectl rollout undo deployment/mcp-server -n "$NAMESPACE"
        fi
    else
        # Update image tag in kustomization
        local temp_kustomization="/tmp/kustomization-${TIMESTAMP}.yaml"
        cp "$kustomize_overlay/kustomization.yaml" "$temp_kustomization"
        
        # Use kustomize to set image
        if command -v kustomize &> /dev/null; then
            cd "$kustomize_overlay"
            kustomize edit set image "mcp-server=mcp-server:$IMAGE_TAG"
        fi
        
        if [[ "$DRY_RUN" == "true" ]]; then
            log "[DRY RUN] Would apply Kubernetes manifests:"
            kubectl apply -k "$kustomize_overlay" --dry-run=client
        else
            kubectl apply -k "$kustomize_overlay" -n "$NAMESPACE"
        fi
        
        # Restore original kustomization
        if [[ -f "$temp_kustomization" ]]; then
            mv "$temp_kustomization" "$kustomize_overlay/kustomization.yaml"
        fi
    fi
    
    # Wait for rollout if not dry run
    if [[ "$DRY_RUN" == "false" ]] && [[ "$ROLLBACK" == "false" ]]; then
        log "Waiting for deployment rollout..."
        kubectl rollout status deployment/mcp-server -n "$NAMESPACE" --timeout="${HEALTH_CHECK_TIMEOUT}s"
    fi
}

# Deploy to AWS Lambda
deploy_aws_lambda() {
    log "Deploying to AWS Lambda..."
    
    local serverless_config="$PROJECT_ROOT/cloud/aws/lambda/serverless.yml"
    
    if [[ ! -f "$serverless_config" ]]; then
        error "Serverless configuration not found: $serverless_config"
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        error "AWS credentials not configured"
        exit 1
    fi
    
    # Install serverless if not present
    if ! command -v serverless &> /dev/null; then
        log "Installing Serverless Framework..."
        npm install -g serverless
    fi
    
    cd "$PROJECT_ROOT/cloud/aws/lambda"
    
    if [[ "$ROLLBACK" == "true" ]]; then
        error "Rollback not supported for AWS Lambda - use version aliases instead"
        exit 1
    fi
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "[DRY RUN] Would deploy to AWS Lambda with stage: $ENVIRONMENT"
    else
        serverless deploy --stage "$ENVIRONMENT" --verbose
    fi
}

# Deploy to AWS ECS
deploy_aws_ecs() {
    log "Deploying to AWS ECS..."
    
    local task_definition="$PROJECT_ROOT/cloud/aws/ecs/task-definition.json"
    local service_definition="$PROJECT_ROOT/cloud/aws/ecs/service.json"
    
    if [[ ! -f "$task_definition" ]] || [[ ! -f "$service_definition" ]]; then
        error "ECS configuration files not found"
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        error "AWS credentials not configured"
        exit 1
    fi
    
    if [[ "$ROLLBACK" == "true" ]]; then
        log "Rolling back ECS service..."
        if [[ "$DRY_RUN" == "true" ]]; then
            log "[DRY RUN] Would rollback ECS service"
        else
            local previous_task_def
            previous_task_def=$(aws ecs list-task-definitions --family-prefix mcp-server --status ACTIVE --sort DESC --max-items 2 --query 'taskDefinitionArns[1]' --output text)
            aws ecs update-service --cluster mcp-server-cluster --service mcp-server-service --task-definition "$previous_task_def"
        fi
    else
        # Substitute environment variables in task definition
        local temp_task_def="/tmp/task-definition-${TIMESTAMP}.json"
        envsubst < "$task_definition" > "$temp_task_def"
        
        if [[ "$DRY_RUN" == "true" ]]; then
            log "[DRY RUN] Would register new task definition and update ECS service"
            cat "$temp_task_def"
        else
            # Register new task definition
            local new_task_def_arn
            new_task_def_arn=$(aws ecs register-task-definition --cli-input-json file://"$temp_task_def" --query 'taskDefinition.taskDefinitionArn' --output text)
            
            # Update service
            aws ecs update-service --cluster mcp-server-cluster --service mcp-server-service --task-definition "$new_task_def_arn"
            
            # Wait for service to stabilize
            aws ecs wait services-stable --cluster mcp-server-cluster --services mcp-server-service
        fi
        
        rm -f "$temp_task_def"
    fi
}

# Deploy locally with Docker Compose
deploy_local() {
    log "Deploying locally with Docker Compose..."
    
    local compose_file="$PROJECT_ROOT/containers/docker-compose.yml"
    
    if [[ ! -f "$compose_file" ]]; then
        error "Docker Compose file not found: $compose_file"
        exit 1
    fi
    
    cd "$PROJECT_ROOT"
    
    if [[ "$ROLLBACK" == "true" ]]; then
        warn "Rollback not applicable for local deployments"
        exit 1
    fi
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "[DRY RUN] Would run: docker-compose up -d"
    else
        # Build and start services
        docker-compose -f "$compose_file" up -d --build
        
        # Show status
        docker-compose -f "$compose_file" ps
    fi
}

# Perform health check
health_check() {
    if [[ "$DRY_RUN" == "true" ]]; then
        log "[DRY RUN] Would perform health check"
        return 0
    fi
    
    log "Performing health check..."
    
    local health_url=""
    local max_attempts=$((HEALTH_CHECK_TIMEOUT / 10))
    local attempt=1
    
    # Determine health check URL based on target
    case "$TARGET" in
        kubernetes)
            # Port-forward to check health
            kubectl port-forward service/mcp-server 8080:8001 -n "$NAMESPACE" &
            local port_forward_pid=$!
            sleep 5
            health_url="http://localhost:8080/health"
            ;;
        local)
            health_url="http://localhost:8001/health"
            ;;
        aws-lambda)
            # Get the API Gateway URL from CloudFormation stack
            local api_url
            api_url=$(aws cloudformation describe-stacks --stack-name "mcp-server-lambda-$ENVIRONMENT" --query 'Stacks[0].Outputs[?OutputKey==`ServiceEndpoint`].OutputValue' --output text)
            health_url="$api_url/health"
            ;;
        *)
            warn "Health check not implemented for target: $TARGET"
            return 0
            ;;
    esac
    
    # Perform health check
    while [[ $attempt -le $max_attempts ]]; do
        debug "Health check attempt $attempt/$max_attempts"
        
        if curl -f -s "$health_url" &> /dev/null; then
            log "Health check passed"
            break
        fi
        
        if [[ $attempt -eq $max_attempts ]]; then
            error "Health check failed after $max_attempts attempts"
            if [[ -n "${port_forward_pid:-}" ]]; then
                kill $port_forward_pid 2>/dev/null || true
            fi
            exit 1
        fi
        
        sleep 10
        ((attempt++))
    done
    
    # Clean up port forwarding
    if [[ -n "${port_forward_pid:-}" ]]; then
        kill $port_forward_pid 2>/dev/null || true
    fi
}

# Generate deployment report
generate_report() {
    local report_file="/tmp/mcp-deploy-report-${TIMESTAMP}.json"
    
    cat > "$report_file" << EOF
{
  "deployment": {
    "timestamp": "$TIMESTAMP",
    "environment": "$ENVIRONMENT",
    "target": "$TARGET",
    "image": "$IMAGE_TAG",
    "namespace": "$NAMESPACE",
    "dry_run": $DRY_RUN,
    "rollback": $ROLLBACK,
    "success": true
  },
  "logs": "$LOG_FILE"
}
EOF
    
    log "Deployment report generated: $report_file"
}

# Main deployment function
main() {
    log "Starting MCP Server deployment..."
    log "Log file: $LOG_FILE"
    
    parse_args "$@"
    validate_prerequisites
    confirm_deployment
    build_image
    
    # Route to appropriate deployment function
    case "$TARGET" in
        kubernetes)
            deploy_kubernetes
            ;;
        aws-lambda)
            deploy_aws_lambda
            ;;
        aws-ecs)
            deploy_aws_ecs
            ;;
        gcp-cloud-run)
            error "GCP Cloud Run deployment not yet implemented"
            exit 1
            ;;
        azure-container-instances)
            error "Azure Container Instances deployment not yet implemented"
            exit 1
            ;;
        local)
            deploy_local
            ;;
        *)
            error "Unknown deployment target: $TARGET"
            exit 1
            ;;
    esac
    
    # Perform health check
    if [[ "$ROLLBACK" == "false" ]]; then
        health_check
    fi
    
    generate_report
    log "Deployment completed successfully!"
}

# Run main function with all arguments
main "$@"