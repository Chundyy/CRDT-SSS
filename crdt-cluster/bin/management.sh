#!/bin/bash
# CRDT Cluster Management Script

set -e

SCRIPT_NAME="management.sh"
SERVICE_PREFIX="crdt-"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

get_all_services() {
    # Get all services with the crdt- prefix
    systemctl list-unit-files "${SERVICE_PREFIX}*.service" --no-legend | awk '{print $1}' | sed 's/\.service//'
}

get_running_services() {
    # Get running services with the crdt- prefix
    systemctl list-units "${SERVICE_PREFIX}*.service" --no-legend | grep running | awk '{print $1}' | sed 's/\.service//'
}

get_failed_services() {
    # Get failed services with the crdt- prefix
    systemctl list-units "${SERVICE_PREFIX}*.service" --failed --no-legend | awk '{print $1}' | sed 's/\.service//'
}

check_service_exists() {
    local service_name=$1
    systemctl list-unit-files "${service_name}.service" >/dev/null 2>&1
}

show_usage() {
    echo "CRDT Cluster Management Script"
    echo ""
    echo "Usage: $SCRIPT_NAME {start|stop|restart|status|enable|disable|logs|logs-follow|list|clean-logs|help} [service_name]"
    echo ""
    echo "Commands:"
    echo "  start <service>     Start a specific CRDT service or all services"
    echo "  stop <service>      Stop a specific CRDT service or all services"
    echo "  restart <service>   Restart a specific CRDT service or all services"
    echo "  status <service>    Show status of a specific service or all services"
    echo "  enable <service>    Enable a service to start at boot"
    echo "  disable <service>   Disable a service from starting at boot"
    echo "  logs <service>      Show recent logs for a service"
    echo "  logs-follow <service> Follow logs for a service in real-time"
    echo "  list                List all CRDT services"
    echo "  clean-logs          Clean journal logs for all CRDT services"
    echo "  help                Show this help message"
    echo ""
    echo "Examples:"
    echo "  $SCRIPT_NAME start              # Start all CRDT services"
    echo "  $SCRIPT_NAME start node_a       # Start only node_a service"
    echo "  $SCRIPT_NAME status             # Status of all services"
    echo "  $SCRIPT_NAME logs-follow node_a # Follow node_a logs in real-time"
    echo ""
}

start_service() {
    local service=$1
    if check_service_exists "$service"; then
        print_info "Starting $service..."
        if sudo systemctl start "$service"; then
            print_success "$service started successfully"
        else
            print_error "Failed to start $service"
            return 1
        fi
    else
        print_error "Service $service does not exist"
        return 1
    fi
}

stop_service() {
    local service=$1
    if check_service_exists "$service"; then
        print_info "Stopping $service..."
        if sudo systemctl stop "$service"; then
            print_success "$service stopped successfully"
        else
            print_error "Failed to stop $service"
            return 1
        fi
    else
        print_error "Service $service does not exist"
        return 1
    fi
}

restart_service() {
    local service=$1
    if check_service_exists "$service"; then
        print_info "Restarting $service..."
        if sudo systemctl restart "$service"; then
            print_success "$service restarted successfully"
        else
            print_error "Failed to restart $service"
            return 1
        fi
    else
        print_error "Service $service does not exist"
        return 1
    fi
}

enable_service() {
    local service=$1
    if check_service_exists "$service"; then
        print_info "Enabling $service to start at boot..."
        if sudo systemctl enable "$service"; then
            print_success "$service enabled successfully"
        else
            print_error "Failed to enable $service"
            return 1
        fi
    else
        print_error "Service $service does not exist"
        return 1
    fi
}

disable_service() {
    local service=$1
    if check_service_exists "$service"; then
        print_info "Disabling $service from starting at boot..."
        if sudo systemctl disable "$service"; then
            print_success "$service disabled successfully"
        else
            print_error "Failed to disable $service"
            return 1
        fi
    else
        print_error "Service $service does not exist"
        return 1
    fi
}

show_service_status() {
    local service=$1
    if check_service_exists "$service"; then
        echo ""
        echo "=== $service ==="
        sudo systemctl status "$service" --no-pager -l || true
    else
        print_error "Service $service does not exist"
    fi
}

show_service_logs() {
    local service=$1
    if check_service_exists "$service"; then
        print_info "Showing recent logs for $service:"
        sudo journalctl -u "$service" --since "1 hour ago" --no-pager
    else
        print_error "Service $service does not exist"
    fi
}

follow_service_logs() {
    local service=$1
    if check_service_exists "$service"; then
        print_info "Following logs for $service (Ctrl+C to stop):"
        sudo journalctl -u "$service" -f
    else
        print_error "Service $service does not exist"
    fi
}

list_services() {
    local all_services=$(get_all_services)
    local running_services=$(get_running_services)
    local failed_services=$(get_failed_services)
    
    if [ -z "$all_services" ]; then
        print_warning "No CRDT services found"
        return 0
    fi
    
    echo ""
    echo "CRDT Services:"
    echo "=============="
    
    for service in $all_services; do
        if echo "$running_services" | grep -q "$service"; then
            echo -e "  ${GREEN}●${NC} $service ${GREEN}(running)${NC}"
        elif echo "$failed_services" | grep -q "$service"; then
            echo -e "  ${RED}●${NC} $service ${RED}(failed)${NC}"
        else
            echo -e "  ${YELLOW}●${NC} $service ${YELLOW}(stopped)${NC}"
        fi
    done
    
    echo ""
    
    # Show enabled/disabled status
    echo "Auto-start status:"
    echo "=================="
    for service in $all_services; do
        if systemctl is-enabled "$service" >/dev/null 2>&1; then
            echo -e "  ${GREEN}✓${NC} $service ${GREEN}(enabled)${NC}"
        else
            echo -e "  ${RED}✗${NC} $service ${RED}(disabled)${NC}"
        fi
    done
}

clean_logs() {
    print_info "Cleaning journal logs for CRDT services..."
    local all_services=$(get_all_services)
    
    if [ -z "$all_services" ]; then
        print_warning "No CRDT services found to clean"
        return 0
    fi
    
    for service in $all_services; do
        print_info "Cleaning logs for $service..."
        sudo journalctl --vacuum-time=1s --unit="$service" >/dev/null 2>&1 || true
    done
    
    print_success "Logs cleaned successfully"
}

# Main script logic
COMMAND="${1:-help}"
SERVICE_NAME="${2:-}"

case "$COMMAND" in
    start)
        if [ -z "$SERVICE_NAME" ]; then
            print_info "Starting all CRDT services..."
            all_services=$(get_all_services)
            if [ -z "$all_services" ]; then
                print_warning "No CRDT services found"
                exit 0
            fi
            for service in $all_services; do
                start_service "$service"
            done
            print_success "All services started"
        else
            start_service "${SERVICE_PREFIX}${SERVICE_NAME}"
        fi
        ;;
        
    stop)
        if [ -z "$SERVICE_NAME" ]; then
            print_info "Stopping all CRDT services..."
            all_services=$(get_all_services)
            if [ -z "$all_services" ]; then
                print_warning "No CRDT services found"
                exit 0
            fi
            for service in $all_services; do
                stop_service "$service"
            done
            print_success "All services stopped"
        else
            stop_service "${SERVICE_PREFIX}${SERVICE_NAME}"
        fi
        ;;
        
    restart)
        if [ -z "$SERVICE_NAME" ]; then
            print_info "Restarting all CRDT services..."
            all_services=$(get_all_services)
            if [ -z "$all_services" ]; then
                print_warning "No CRDT services found"
                exit 0
            fi
            for service in $all_services; do
                restart_service "$service"
            done
            print_success "All services restarted"
        else
            restart_service "${SERVICE_PREFIX}${SERVICE_NAME}"
        fi
        ;;
        
    status)
        if [ -z "$SERVICE_NAME" ]; then
            print_info "Status of all CRDT services:"
            all_services=$(get_all_services)
            if [ -z "$all_services" ]; then
                print_warning "No CRDT services found"
                exit 0
            fi
            for service in $all_services; do
                show_service_status "$service"
            done
        else
            show_service_status "${SERVICE_PREFIX}${SERVICE_NAME}"
        fi
        ;;
        
    enable)
        if [ -z "$SERVICE_NAME" ]; then
            print_info "Enabling all CRDT services to start at boot..."
            all_services=$(get_all_services)
            if [ -z "$all_services" ]; then
                print_warning "No CRDT services found"
                exit 0
            fi
            for service in $all_services; do
                enable_service "$service"
            done
            print_success "All services enabled"
        else
            enable_service "${SERVICE_PREFIX}${SERVICE_NAME}"
        fi
        ;;
        
    disable)
        if [ -z "$SERVICE_NAME" ]; then
            print_info "Disabling all CRDT services from starting at boot..."
            all_services=$(get_all_services)
            if [ -z "$all_services" ]; then
                print_warning "No CRDT services found"
                exit 0
            fi
            for service in $all_services; do
                disable_service "$service"
            done
            print_success "All services disabled"
        else
            disable_service "${SERVICE_PREFIX}${SERVICE_NAME}"
        fi
        ;;
        
    logs)
        if [ -z "$SERVICE_NAME" ]; then
            print_error "Please specify a service name for logs"
            echo "Usage: $SCRIPT_NAME logs <service_name>"
            exit 1
        else
            show_service_logs "${SERVICE_PREFIX}${SERVICE_NAME}"
        fi
        ;;
        
    logs-follow)
        if [ -z "$SERVICE_NAME" ]; then
            print_error "Please specify a service name for logs-follow"
            echo "Usage: $SCRIPT_NAME logs-follow <service_name>"
            exit 1
        else
            follow_service_logs "${SERVICE_PREFIX}${SERVICE_NAME}"
        fi
        ;;
        
    list)
        list_services
        ;;
        
    clean-logs)
        clean_logs
        ;;
        
    help|--help|-h)
        show_usage
        ;;
        
    *)
        print_error "Unknown command: $COMMAND"
        show_usage
        exit 1
        ;;
esac
